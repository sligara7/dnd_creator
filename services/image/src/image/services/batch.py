"""Batch processing system for image generation tasks."""
import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Sequence
from uuid import UUID

from image.core.metrics import record_batch_processed
from image.models.generation import GenerationTask, TaskPriority, TaskStatus, TaskType
from image.services.queue import QueueService

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Service for managing batches of related image generation tasks."""

    def __init__(self, queue_service: QueueService) -> None:
        """Initialize the batch processor.

        Args:
            queue_service: Queue service for task management
        """
        self.queue = queue_service

    async def create_batch(
        self,
        tasks: List[dict],
        priority: TaskPriority = TaskPriority.NORMAL,
        group_id: Optional[str] = None,
    ) -> GenerationTask:
        """Create a batch of related tasks.

        Args:
            tasks: List of task specifications
            priority: Priority level for the batch
            group_id: Optional identifier for the task group

        Returns:
            The parent batch task
        """
        # Create parent batch task
        batch_params = {
            "task_count": len(tasks),
            "group_id": group_id,
            "completed_count": 0
        }
        parent_task = await self.queue.enqueue_task(
            task_type=TaskType.BATCH,
            parameters=batch_params,
            priority=priority
        )

        # Create child tasks
        for task_spec in tasks:
            task_type = task_spec.pop("type", None)
            if not task_type:
                continue

            # Inherit priority from batch but allow override
            task_priority = task_spec.pop("priority", priority)

            await self.queue.enqueue_task(
                task_type=task_type,
                parameters=task_spec,
                priority=task_priority,
                parent_id=parent_task.id
            )

        return parent_task

    async def get_batch_status(
        self,
        batch_id: UUID,
        include_subtasks: bool = False
    ) -> Optional[dict]:
        """Get the status of a batch task and its subtasks.

        Args:
            batch_id: ID of batch task
            include_subtasks: Whether to include subtask details

        Returns:
            Batch status dict or None if not found
        """
        batch = await self.queue.task_repo.get_by_id(batch_id)
        if not batch or batch.type != TaskType.BATCH:
            return None

        status = {
            "id": str(batch.id),
            "status": batch.status.value,
            "priority": batch.priority.value,
            "task_count": batch.parameters.get("task_count", 0),
            "completed_count": batch.parameters.get("completed_count", 0),
            "group_id": batch.parameters.get("group_id"),
            "created_at": batch.created_at.isoformat(),
            "updated_at": batch.updated_at.isoformat(),
        }

        if include_subtasks:
            subtasks = await self.queue.task_repo.get_subtasks(batch_id)
            status["subtasks"] = [
                {
                    "id": str(task.id),
                    "type": task.type.value,
                    "status": task.status.value,
                    "progress": task.progress,
                    "error_message": task.error_message
                }
                for task in subtasks
            ]

        return status

    async def cancel_batch(self, batch_id: UUID) -> bool:
        """Cancel a batch task and all its subtasks.

        Args:
            batch_id: ID of batch to cancel

        Returns:
            True if batch was cancelled, False otherwise
        """
        batch = await self.queue.task_repo.get_by_id(batch_id)
        if not batch or batch.type != TaskType.BATCH:
            return False

        # Cancel parent batch task
        await self.queue.cancel_task(batch_id)

        # Cancel all subtasks
        subtasks = await self.queue.task_repo.get_subtasks(
            batch_id,
            include_completed=False
        )
        for task in subtasks:
            await self.queue.cancel_task(task.id)

        return True

    async def process_batch(self, batch_id: UUID) -> None:
        """Process a batch of tasks.

        Args:
            batch_id: ID of batch to process
        """
        batch = await self.queue.task_repo.get_by_id(batch_id)
        if not batch or batch.type != TaskType.BATCH:
            return

        start_time = datetime.utcnow()

        try:
            # Get all subtasks
            subtasks = await self.queue.task_repo.get_subtasks(batch_id)
            
            # Process subtasks with resource limits
            semaphore = asyncio.Semaphore(5)  # Limit concurrent tasks
            tasks = []

            for task in subtasks:
                # Skip completed/failed tasks
                if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                    continue

                tasks.append(
                    self._process_subtask(task.id, semaphore)
                )

            # Wait for all tasks to complete
            await asyncio.gather(*tasks, return_exceptions=True)

            # Update batch status
            completed = await self.queue.task_repo.count_by_status(
                TaskStatus.COMPLETED
            )
            batch.parameters["completed_count"] = completed

            if completed == batch.parameters["task_count"]:
                await self.queue.complete_task(batch_id)
            else:
                # Some tasks failed, mark batch as failed
                await self.queue.fail_task(
                    batch_id,
                    "Some subtasks failed",
                    retry=False
                )

            # Record batch metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            record_batch_processed(len(subtasks), processing_time)

        except Exception as e:
            logger.exception(f"Error processing batch {batch_id}")
            await self.queue.fail_task(
                batch_id,
                str(e),
                retry=True
            )

    async def _process_subtask(
        self,
        task_id: UUID,
        semaphore: asyncio.Semaphore
    ) -> None:
        """Process a single task within a batch.

        Args:
            task_id: ID of task to process
            semaphore: Semaphore for resource control
        """
        async with semaphore:
            task = await self.queue.task_repo.get_by_id(task_id)
            if not task:
                return

            try:
                # Process task based on type
                if task.type == TaskType.CHARACTER_PORTRAIT:
                    await self._process_portrait(task)
                elif task.type == TaskType.MAP:
                    await self._process_map(task)
                elif task.type == TaskType.ITEM:
                    await self._process_item(task)
                # Add handlers for other task types...

            except Exception as e:
                logger.exception(f"Error processing subtask {task_id}")
                await self.queue.fail_task(task_id, str(e))
