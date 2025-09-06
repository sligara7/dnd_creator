"""Queue service for image generation tasks."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from image_service.core.config import get_settings
from image_service.core.constants import (
    QUEUE_PRIORITY_HIGH,
    QUEUE_PRIORITY_LOW,
    QUEUE_PRIORITY_NORMAL,
)
from image_service.core.logging import get_logger
from image_service.core.utils import now_utc
from image_service.models.image import GenerationTask

settings = get_settings()
logger = get_logger(__name__)


class AsyncQueueService:
    """Asynchronous queue service for image generation tasks."""

    def __init__(
        self,
        redis: Redis,
        db: AsyncSession,
        prefix: str = "image_queue:",
        max_retries: int = 3,
    ):
        """Initialize queue service."""
        self.redis = redis
        self.db = db
        self.prefix = prefix
        self.max_retries = max_retries

        # Queue keys
        self.queue_key = f"{prefix}tasks"
        self.processing_key = f"{prefix}processing"
        self.failed_key = f"{prefix}failed"

        # Task keys
        self.task_key = f"{prefix}task:"
        self.status_key = f"{prefix}status:"
        self.progress_key = f"{prefix}progress:"

    async def add_task(
        self,
        task_type: str,
        params: Dict[str, Any],
        priority: Optional[int] = None,
    ) -> str:
        """Add a task to the queue.
        
        Args:
            task_type: Type of generation task
            params: Task parameters
            priority: Task priority (higher is more important)

        Returns:
            Task ID
        """
        # Create task record
        task = GenerationTask(
            type=task_type,
            status="pending",
            priority=priority or QUEUE_PRIORITY_NORMAL,
            params=params,
        )
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)

        task_id = str(task.id)

        # Add task data to Redis
        task_data = {
            "id": task_id,
            "type": task_type,
            "params": params,
            "priority": priority or QUEUE_PRIORITY_NORMAL,
            "added_at": now_utc().isoformat(),
        }

        async with self.redis.pipeline() as pipe:
            # Store task data
            await pipe.set(
                f"{self.task_key}{task_id}",
                json.dumps(task_data),
                ex=settings.QUEUE_TIMEOUT,
            )
            # Add to queue with priority
            await pipe.zadd(self.queue_key, {task_id: priority or QUEUE_PRIORITY_NORMAL})
            # Initialize status
            await pipe.set(
                f"{self.status_key}{task_id}",
                "pending",
                ex=settings.QUEUE_TIMEOUT,
            )
            await pipe.execute()

        logger.info(
            "Added task to queue",
            task_id=task_id,
            type=task_type,
            priority=priority,
        )

        return task_id

    async def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get the next task from the queue."""
        async with self.redis.pipeline() as pipe:
            # Get highest priority task
            task_id = await self.redis.zpopmax(self.queue_key)
            if not task_id:
                return None

            task_id = task_id[0][0].decode()

            # Get task data
            task_data = await self.redis.get(f"{self.task_key}{task_id}")
            if not task_data:
                return None

            # Move to processing set
            await pipe.sadd(self.processing_key, task_id)
            # Update status
            await pipe.set(
                f"{self.status_key}{task_id}",
                "processing",
                ex=settings.QUEUE_TIMEOUT,
            )
            await pipe.execute()

        return json.loads(task_data)

    async def complete_task(
        self,
        task_id: str,
        result: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Mark a task as completed."""
        async with self.redis.pipeline() as pipe:
            # Remove from processing set
            await pipe.srem(self.processing_key, task_id)
            # Update status
            await pipe.set(
                f"{self.status_key}{task_id}",
                "completed",
                ex=settings.QUEUE_TIMEOUT,
            )
            # Store result
            if result:
                await pipe.set(
                    f"{self.task_key}{task_id}:result",
                    json.dumps(result),
                    ex=settings.QUEUE_TIMEOUT,
                )
            await pipe.execute()

        # Update database record
        task = await self.db.get(GenerationTask, UUID(task_id))
        if task:
            task.status = "completed"
            task.result = result
            await self.db.commit()

        logger.info("Task completed", task_id=task_id)

    async def fail_task(
        self,
        task_id: str,
        error: str,
        retry: bool = True,
    ) -> None:
        """Mark a task as failed."""
        task = await self.db.get(GenerationTask, UUID(task_id))
        if not task:
            logger.warning("Task not found", task_id=task_id)
            return

        task.last_error = error
        task.attempts += 1

        if retry and task.attempts < self.max_retries:
            # Calculate retry delay with exponential backoff
            delay = task.retry_delay * (2 ** (task.attempts - 1))
            next_attempt = now_utc() + timedelta(seconds=delay)

            logger.info(
                "Scheduling task retry",
                task_id=task_id,
                attempt=task.attempts,
                delay=delay,
                next_attempt=next_attempt,
            )

            # Update task for retry
            task.status = "pending"
            task.last_attempt = now_utc()
            task.retry_count += 1

            # Re-queue task with lower priority
            priority = max(
                QUEUE_PRIORITY_LOW,
                task.priority - (10 * task.attempts)
            )
            async with self.redis.pipeline() as pipe:
                await pipe.srem(self.processing_key, task_id)
                await pipe.zadd(self.queue_key, {task_id: priority})
                await pipe.set(
                    f"{self.status_key}{task_id}",
                    "pending",
                    ex=settings.QUEUE_TIMEOUT,
                )
                await pipe.execute()

        else:
            # Mark task as failed permanently
            task.status = "failed"
            async with self.redis.pipeline() as pipe:
                await pipe.srem(self.processing_key, task_id)
                await pipe.sadd(self.failed_key, task_id)
                await pipe.set(
                    f"{self.status_key}{task_id}",
                    "failed",
                    ex=settings.QUEUE_TIMEOUT,
                )
                await pipe.execute()

            logger.error(
                "Task failed permanently",
                task_id=task_id,
                attempts=task.attempts,
                error=error,
            )

        await self.db.commit()

    async def get_task_status(self, task_id: str) -> Optional[str]:
        """Get task status."""
        status = await self.redis.get(f"{self.status_key}{task_id}")
        return status.decode() if status else None

    async def get_task_progress(self, task_id: str) -> Optional[float]:
        """Get task progress (0-100)."""
        progress = await self.redis.get(f"{self.progress_key}{task_id}")
        return float(progress) if progress else None

    async def update_task_progress(
        self,
        task_id: str,
        progress: float,
        stage: Optional[str] = None,
    ) -> None:
        """Update task progress."""
        async with self.redis.pipeline() as pipe:
            await pipe.set(
                f"{self.progress_key}{task_id}",
                str(progress),
                ex=settings.QUEUE_TIMEOUT,
            )
            if stage:
                await pipe.set(
                    f"{self.status_key}{task_id}:stage",
                    stage,
                    ex=settings.QUEUE_TIMEOUT,
                )
            await pipe.execute()

    async def get_queue_stats(self) -> Dict[str, int]:
        """Get queue statistics."""
        async with self.redis.pipeline() as pipe:
            # Get counts for different queues
            await pipe.zcard(self.queue_key)
            await pipe.scard(self.processing_key)
            await pipe.scard(self.failed_key)
            pending, processing, failed = await pipe.execute()

            return {
                "pending": pending,
                "processing": processing,
                "failed": failed,
                "total": pending + processing + failed,
            }

    async def cleanup_expired_tasks(self) -> None:
        """Clean up expired tasks from Redis."""
        # This method can be called periodically to clean up tasks
        # that have exceeded their TTL but weren't properly completed
        logger.info("Starting queue cleanup")

        # Get all processing tasks
        processing_tasks = await self.redis.smembers(self.processing_key)
        for task_id in processing_tasks:
            task_id = task_id.decode()
            
            # Check if task data still exists
            if not await self.redis.exists(f"{self.task_key}{task_id}"):
                logger.warning(
                    "Found orphaned processing task",
                    task_id=task_id,
                )
                await self.fail_task(
                    task_id,
                    "Task expired while processing",
                    retry=True,
                )

        logger.info("Queue cleanup completed")
