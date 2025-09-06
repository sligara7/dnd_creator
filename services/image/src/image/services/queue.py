"""Queue service for managing image generation tasks."""
import json
import logging
from datetime import datetime
from typing import AsyncIterator, List, Optional, Set, Tuple
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from image.core.metrics import (
    record_task_queued, record_task_started, record_task_completed,
    record_task_failed, record_queue_size, record_cache_operation
)
from image.db.repositories.task import TaskRepository
from image.models.generation import GenerationTask, TaskEvent, TaskPriority, TaskStatus

logger = logging.getLogger(__name__)


class QueueService:
    """Service for managing task queues using Redis."""

    def __init__(self, redis: Redis, session: AsyncSession) -> None:
        """Initialize the queue service.

        Args:
            redis: Redis client instance
            session: SQLAlchemy async session
        """
        self.redis = redis
        self.session = session
        self.task_repo = TaskRepository(session)

        # Redis key prefixes
        self.task_queue_key = "image:task_queue"  # Sorted set for priority queue
        self.processing_set_key = "image:processing"  # Set of tasks being processed
        self.task_lock_prefix = "image:task_lock:"  # Lock prefix for tasks

    async def enqueue_task(
        self,
        task_type: str,
        parameters: dict,
        priority: TaskPriority = TaskPriority.NORMAL,
        parent_id: Optional[UUID] = None,
    ) -> GenerationTask:
        """Create and enqueue a new task.

        Args:
            task_type: Type of generation task
            parameters: Task parameters
            priority: Task priority level
            parent_id: Optional parent task ID for batch operations

        Returns:
            The created task
        """
        # Create task in database
        task = await self.task_repo.create(
            type=task_type,
            parameters=parameters,
            priority=priority,
            parent_id=parent_id
        )

        # Add task to Redis queue with priority score
        priority_score = self._get_priority_score(priority, task.created_at)
        await self.redis.zadd(
            self.task_queue_key,
            {str(task.id): priority_score}
        )

        # Record metrics
        record_task_queued(str(task.type))
        await self._update_queue_size_metrics()

        # Create task queued event
        await self._create_task_event(
            task_id=task.id,
            event_type="queued",
            details={"priority": priority.value}
        )

        return task

    async def dequeue_task(self) -> Optional[GenerationTask]:
        """Dequeue the highest priority task from the queue.

        Returns:
            The next task to process, or None if queue is empty
        """
        # Get highest priority task ID from Redis
        result = await self.redis.zpopmax(self.task_queue_key)
        if not result:
            return None

        task_id_str = result[0][0].decode()
        task_id = UUID(task_id_str)

        # Add to processing set
        await self.redis.sadd(self.processing_set_key, task_id_str)

        # Update task status
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            # Task was deleted, remove from processing
            await self.redis.srem(self.processing_set_key, task_id_str)
            return None

        task.status = TaskStatus.IN_PROGRESS
        now = datetime.utcnow()
        task.started_at = now
        await self.session.commit()

        # Record metrics
        queue_time = (now - task.created_at).total_seconds()
        record_task_started(str(task.type), queue_time)
        await self._update_queue_size_metrics()

        # Create task started event
        await self._create_task_event(
            task_id=task.id,
            event_type="started",
            details={}
        )

        return task

    async def complete_task(
        self,
        task_id: UUID,
        result: Optional[dict] = None
    ) -> None:
        """Mark a task as completed.

        Args:
            task_id: ID of task to complete
            result: Optional task result data
        """
        # Update task in database
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            logger.warning(f"Attempted to complete non-existent task: {task_id}")
            return

        now = datetime.utcnow()
        task.status = TaskStatus.COMPLETED
        task.completed_at = now
        if result:
            task.result = result
        await self.session.commit()

        # Remove from processing set
        await self.redis.srem(self.processing_set_key, str(task_id))

        # Record metrics
        processing_time = (now - task.started_at).total_seconds()
        # Calculate pixels if result contains image dimensions
        pixels = None
        if result and isinstance(result, dict):
            width = result.get("width")
            height = result.get("height")
            if width and height:
                pixels = width * height
        record_task_completed(str(task.type), processing_time, pixels)

        # Create task completed event
        await self._create_task_event(
            task_id=task_id,
            event_type="completed",
            details={"result": result} if result else {}
        )

    async def fail_task(
        self,
        task_id: UUID,
        error_message: str,
        retry: bool = True
    ) -> None:
        """Mark a task as failed, optionally retrying.

        Args:
            task_id: ID of task that failed
            error_message: Error message to store
            retry: Whether to retry the task if retries remain
        """
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            logger.warning(f"Attempted to fail non-existent task: {task_id}")
            return

        task.error_message = error_message
        
        if retry and task.retries < task.max_retries:
            # Increment retry count and requeue
            task.retries += 1
            task.status = TaskStatus.PENDING
            await self.session.commit()

            # Re-add to queue with adjusted priority
            priority_score = self._get_priority_score(
                task.priority,
                datetime.utcnow(),
                retry_count=task.retries
            )
            await self.redis.zadd(
                self.task_queue_key,
                {str(task_id): priority_score}
            )

            # Record metrics
            record_task_failed(str(task.type), error_message, retried=True)

            # Create task retry event
            await self._create_task_event(
                task_id=task_id,
                event_type="retry",
                details={
                    "error": error_message,
                    "retry_count": task.retries
                }
            )
        else:
            # Mark as permanently failed
            task.status = TaskStatus.FAILED
            await self.session.commit()

            # Record metrics
            record_task_failed(str(task.type), error_message, retried=False)

            # Create task failed event
            await self._create_task_event(
                task_id=task_id,
                event_type="failed",
                details={"error": error_message}
            )

        # Remove from processing set
        await self.redis.srem(self.processing_set_key, str(task_id))

    async def cancel_task(self, task_id: UUID) -> bool:
        """Cancel a pending or in-progress task.

        Args:
            task_id: ID of task to cancel

        Returns:
            True if task was cancelled, False if task couldn't be cancelled
        """
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            return False

        # Only allow cancelling pending or in-progress tasks
        if task.status not in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS):
            return False

        # Update task status
        task.status = TaskStatus.CANCELLED
        await self.session.commit()

        # Remove from Redis queue and processing set
        await self.redis.zrem(self.task_queue_key, str(task_id))
        await self.redis.srem(self.processing_set_key, str(task_id))

        # Create task cancelled event
        await self._create_task_event(
            task_id=task_id,
            event_type="cancelled",
            details={}
        )

        return True

    async def get_task_status(
        self,
        task_id: UUID,
        include_events: bool = False
    ) -> Optional[dict]:
        """Get the current status of a task.

        Args:
            task_id: ID of task to check
            include_events: Whether to include task events

        Returns:
            Task status dict or None if task not found
        """
        # Get task with optional events
        query = self.task_repo.get_query()
        if include_events:
            query = query.options(joinedload(GenerationTask.events))
        task = await self.task_repo.get_by_id(task_id, query=query)

        if not task:
            return None

        status = {
            "id": str(task.id),
            "type": task.type.value,
            "status": task.status.value,
            "priority": task.priority.value,
            "progress": task.progress,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "error_message": task.error_message,
            "retry_count": task.retries,
        }

        if include_events:
            status["events"] = [
                {
                    "type": event.event_type,
                    "details": event.details,
                    "created_at": event.created_at.isoformat()
                }
                for event in sorted(task.events, key=lambda e: e.created_at)
            ]

        return status

    async def update_progress(
        self,
        task_id: UUID,
        progress: float,
        status_message: Optional[str] = None
    ) -> None:
        """Update the progress of a task.

        Args:
            task_id: ID of task to update
            progress: Progress percentage (0-100)
            status_message: Optional status message
        """
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            logger.warning(f"Attempted to update non-existent task: {task_id}")
            return

        task.progress = min(100, max(0, progress))  # Clamp to 0-100
        await self.session.commit()

        # Create progress event
        await self._create_task_event(
            task_id=task_id,
            event_type="progress",
            details={
                "progress": progress,
                "message": status_message
            }
        )

    async def get_queue_stats(self) -> dict:
        """Get statistics about the current queue state.

        Returns:
            Dict containing queue statistics
        """
        # Get counts from Redis
        queued_count = await self.redis.zcard(self.task_queue_key)
        processing_count = await self.redis.scard(self.processing_set_key)

        # Get priority breakdowns
        priorities = {}
        for priority in TaskPriority:
            min_score = self._get_priority_score(priority, datetime.min)
            max_score = self._get_priority_score(priority, datetime.max)
            count = await self.redis.zcount(
                self.task_queue_key,
                min_score,
                max_score
            )
            priorities[priority.value] = count

        return {
            "queued_tasks": queued_count,
            "processing_tasks": processing_count,
            "priority_breakdown": priorities,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _get_priority_score(
        self,
        priority: TaskPriority,
        timestamp: datetime,
        retry_count: int = 0
    ) -> float:
        """Calculate a Redis sorted set score for task priority ordering.

        Higher scores = higher priority. Combines priority level, timestamp,
        and retry count to ensure consistent ordering.

        Args:
            priority: Task priority level
            timestamp: Task creation/update time
            retry_count: Number of retries (reduces priority slightly)

        Returns:
            Float score for Redis sorted set
        """
        # Priority base scores (higher = more priority)
        priority_scores = {
            TaskPriority.LOW: 1000000,
            TaskPriority.NORMAL: 2000000,
            TaskPriority.HIGH: 3000000,
            TaskPriority.URGENT: 4000000
        }

        # Convert timestamp to Unix timestamp
        time_score = timestamp.timestamp()

        # Retry penalty (small reduction in priority per retry)
        retry_penalty = retry_count * 1000

        # Combine into final score
        # Priority base + timestamp - retry penalty
        return priority_scores[priority] + time_score - retry_penalty

    async def _create_task_event(
        self,
        task_id: UUID,
        event_type: str,
        details: dict
    ) -> None:
        """Create a new task event.

        Args:
            task_id: ID of associated task
            event_type: Type of event
            details: Event details dict
        """
        event = TaskEvent(
            task_id=task_id,
            event_type=event_type,
            details=details
        )
        self.session.add(event)
        await self.session.commit()

    async def cleanup_stale_tasks(self, max_age_hours: int = 24) -> int:
        """Clean up stale processing tasks.

        Args:
            max_age_hours: Maximum age in hours for processing tasks

        Returns:
            Number of tasks cleaned up
        """
        # Get all processing task IDs
        processing_ids = await self.redis.smembers(self.processing_set_key)
        if not processing_ids:
            return 0

        # Convert to UUIDs
        task_ids = {UUID(id_bytes.decode()) for id_bytes in processing_ids}

        # Get tasks from database
        tasks = await self.task_repo.get_by_ids(list(task_ids))
        
        cleanup_count = 0
        cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)

        for task in tasks:
            # Check if task is stale
            if (task.started_at and
                task.started_at.timestamp() < cutoff_time and
                task.status == TaskStatus.IN_PROGRESS):
                # Mark as failed and retry
                await self.fail_task(
                    task.id,
                    "Task timed out",
                    retry=True
                )
                cleanup_count += 1

        return cleanup_count

    async def _update_queue_size_metrics(self) -> None:
        """Update queue size metrics for all priority levels."""
        for priority in TaskPriority:
            min_score = self._get_priority_score(priority, datetime.min)
            max_score = self._get_priority_score(priority, datetime.max)
            size = await self.redis.zcount(
                self.task_queue_key,
                min_score,
                max_score
            )
            record_queue_size(priority.value, size)
