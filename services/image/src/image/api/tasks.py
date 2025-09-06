"""API endpoints for task management."""
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

from image.models.generation import TaskPriority, TaskStatus, TaskType
from image.services.batch import BatchProcessor
from image.services.queue import QueueService
from image.core.dependencies import get_batch_processor, get_queue_service

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response Models
class TaskCreate(BaseModel):
    """Model for task creation request."""

    type: TaskType
    parameters: dict
    priority: TaskPriority = TaskPriority.NORMAL


class BatchTaskCreate(BaseModel):
    """Model for batch task creation request."""

    tasks: List[TaskCreate] = Field(..., min_items=1)
    priority: TaskPriority = TaskPriority.NORMAL
    group_id: Optional[str] = None


class TaskResponse(BaseModel):
    """Model for task response."""

    id: UUID
    type: str
    status: str
    priority: str
    progress: Optional[float]
    error_message: Optional[str]
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]


class BatchTaskResponse(BaseModel):
    """Model for batch task response."""

    id: UUID
    status: str
    priority: str
    task_count: int
    completed_count: int
    group_id: Optional[str]
    created_at: str
    updated_at: str
    subtasks: Optional[List[TaskResponse]]


class QueueStats(BaseModel):
    """Model for queue statistics."""

    queued_tasks: int
    processing_tasks: int
    priority_breakdown: dict
    timestamp: str


@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new generation task",
    response_description="The created task"
)
async def create_task(
    task: TaskCreate,
    queue: QueueService = Depends(get_queue_service)
) -> dict:
    """Create a new image generation task.

    Args:
        task: Task creation details
        queue: Queue service instance

    Returns:
        Created task details
    """
    try:
        task_obj = await queue.enqueue_task(
            task_type=task.type,
            parameters=task.parameters,
            priority=task.priority
        )
        return await queue.get_task_status(task_obj.id)
    except Exception as e:
        logger.exception("Error creating task")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/tasks/batch",
    response_model=BatchTaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a batch of tasks",
    response_description="The created batch task"
)
async def create_batch_tasks(
    batch: BatchTaskCreate,
    processor: BatchProcessor = Depends(get_batch_processor)
) -> dict:
    """Create a batch of related tasks.

    Args:
        batch: Batch creation details
        processor: Batch processor instance

    Returns:
        Created batch task details
    """
    try:
        # Convert TaskCreate models to dicts
        task_dicts = [
            {
                "type": task.type,
                "parameters": task.parameters,
                "priority": task.priority
            }
            for task in batch.tasks
        ]

        task_obj = await processor.create_batch(
            tasks=task_dicts,
            priority=batch.priority,
            group_id=batch.group_id
        )
        return await processor.get_batch_status(
            task_obj.id,
            include_subtasks=True
        )
    except Exception as e:
        logger.exception("Error creating batch")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Get task status",
    response_description="The task status"
)
async def get_task_status(
    task_id: UUID,
    include_events: bool = Query(False, description="Include task events"),
    queue: QueueService = Depends(get_queue_service)
) -> dict:
    """Get the status of a task.

    Args:
        task_id: ID of task to check
        include_events: Whether to include task events
        queue: Queue service instance

    Returns:
        Task status details
    """
    status = await queue.get_task_status(task_id, include_events)
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return status


@router.get(
    "/tasks/batch/{batch_id}",
    response_model=BatchTaskResponse,
    summary="Get batch task status",
    response_description="The batch task status"
)
async def get_batch_status(
    batch_id: UUID,
    include_subtasks: bool = Query(False, description="Include subtask details"),
    processor: BatchProcessor = Depends(get_batch_processor)
) -> dict:
    """Get the status of a batch task.

    Args:
        batch_id: ID of batch to check
        include_subtasks: Whether to include subtask details
        processor: Batch processor instance

    Returns:
        Batch status details
    """
    status = await processor.get_batch_status(batch_id, include_subtasks)
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch task not found"
        )
    return status


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel a task",
    response_description="Task cancelled successfully"
)
async def cancel_task(
    task_id: UUID,
    queue: QueueService = Depends(get_queue_service)
) -> Response:
    """Cancel a pending or in-progress task.

    Args:
        task_id: ID of task to cancel
        queue: Queue service instance

    Returns:
        Empty response on success
    """
    cancelled = await queue.cancel_task(task_id)
    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or cannot be cancelled"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/tasks/batch/{batch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel a batch task",
    response_description="Batch task cancelled successfully"
)
async def cancel_batch_task(
    batch_id: UUID,
    processor: BatchProcessor = Depends(get_batch_processor)
) -> Response:
    """Cancel a batch task and all its subtasks.

    Args:
        batch_id: ID of batch to cancel
        processor: Batch processor instance

    Returns:
        Empty response on success
    """
    cancelled = await processor.cancel_batch(batch_id)
    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch task not found or cannot be cancelled"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/tasks/queue/stats",
    response_model=QueueStats,
    summary="Get queue statistics",
    response_description="Current queue statistics"
)
async def get_queue_stats(
    queue: QueueService = Depends(get_queue_service)
) -> dict:
    """Get statistics about the current queue state.

    Args:
        queue: Queue service instance

    Returns:
        Queue statistics
    """
    return await queue.get_queue_stats()
