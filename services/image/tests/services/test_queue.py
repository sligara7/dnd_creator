"""Tests for task queue system."""
import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator
from uuid import UUID

import pytest
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from image.models.generation import TaskPriority, TaskStatus, TaskType
from image.services.queue import QueueService
from image.services.batch import BatchProcessor


@pytest.fixture
async def queue_service(
    db_session: AsyncSession,
    redis_client: Redis
) -> AsyncGenerator[QueueService, None]:
    """Fixture for queue service."""
    service = QueueService(redis=redis_client, session=db_session)
    yield service


@pytest.fixture
async def batch_processor(
    queue_service: QueueService
) -> AsyncGenerator[BatchProcessor, None]:
    """Fixture for batch processor."""
    processor = BatchProcessor(queue_service=queue_service)
    yield processor


async def test_task_lifecycle(queue_service: QueueService):
    """Test basic task lifecycle."""
    # Create task
    task = await queue_service.enqueue_task(
        task_type=TaskType.CHARACTER_PORTRAIT,
        parameters={"test": "params"},
        priority=TaskPriority.NORMAL
    )

    assert task.id is not None
    assert task.type == TaskType.CHARACTER_PORTRAIT
    assert task.status == TaskStatus.PENDING
    assert task.priority == TaskPriority.NORMAL
    assert task.parameters == {"test": "params"}

    # Get task from queue
    queued_task = await queue_service.dequeue_task()
    assert queued_task is not None
    assert queued_task.id == task.id
    assert queued_task.status == TaskStatus.IN_PROGRESS
    assert queued_task.started_at is not None

    # Complete task
    await queue_service.complete_task(
        task.id,
        result={"test": "result"}
    )
    
    completed_task = await queue_service.task_repo.get_by_id(task.id)
    assert completed_task is not None
    assert completed_task.status == TaskStatus.COMPLETED
    assert completed_task.completed_at is not None
    assert completed_task.result == {"test": "result"}


async def test_task_priorities(queue_service: QueueService):
    """Test task priority ordering."""
    # Create tasks with different priorities
    low_task = await queue_service.enqueue_task(
        task_type=TaskType.CHARACTER_PORTRAIT,
        parameters={"priority": "low"},
        priority=TaskPriority.LOW
    )
    high_task = await queue_service.enqueue_task(
        task_type=TaskType.CHARACTER_PORTRAIT,
        parameters={"priority": "high"},
        priority=TaskPriority.HIGH
    )
    normal_task = await queue_service.enqueue_task(
        task_type=TaskType.CHARACTER_PORTRAIT,
        parameters={"priority": "normal"},
        priority=TaskPriority.NORMAL
    )

    # Verify tasks are dequeued in priority order
    task1 = await queue_service.dequeue_task()
    assert task1.id == high_task.id

    task2 = await queue_service.dequeue_task()
    assert task2.id == normal_task.id

    task3 = await queue_service.dequeue_task()
    assert task3.id == low_task.id


async def test_task_retry(queue_service: QueueService):
    """Test task retry mechanism."""
    # Create task
    task = await queue_service.enqueue_task(
        task_type=TaskType.CHARACTER_PORTRAIT,
        parameters={"test": "retry"}
    )

    # Simulate failure and retry
    await queue_service.fail_task(
        task.id,
        "Test error",
        retry=True
    )

    # Check task was requeued
    updated_task = await queue_service.task_repo.get_by_id(task.id)
    assert updated_task.retries == 1
    assert updated_task.status == TaskStatus.PENDING
    assert updated_task.error_message == "Test error"

    # Verify task can be dequeued again
    retry_task = await queue_service.dequeue_task()
    assert retry_task.id == task.id


async def test_task_cancellation(queue_service: QueueService):
    """Test task cancellation."""
    # Create task
    task = await queue_service.enqueue_task(
        task_type=TaskType.CHARACTER_PORTRAIT,
        parameters={"test": "cancel"}
    )

    # Cancel pending task
    cancelled = await queue_service.cancel_task(task.id)
    assert cancelled is True

    # Verify task status
    cancelled_task = await queue_service.task_repo.get_by_id(task.id)
    assert cancelled_task.status == TaskStatus.CANCELLED

    # Verify task cannot be dequeued
    next_task = await queue_service.dequeue_task()
    assert next_task is None


async def test_task_progress(queue_service: QueueService):
    """Test task progress updates."""
    # Create task
    task = await queue_service.enqueue_task(
        task_type=TaskType.CHARACTER_PORTRAIT,
        parameters={"test": "progress"}
    )

    # Update progress
    await queue_service.update_progress(
        task.id,
        50.0,
        "Halfway done"
    )

    # Verify progress
    updated_task = await queue_service.task_repo.get_by_id(task.id)
    assert updated_task.progress == 50.0

    # Get task status with events
    status = await queue_service.get_task_status(task.id, include_events=True)
    assert status["progress"] == 50.0
    assert len(status["events"]) > 0
    assert any(
        e["type"] == "progress" and e["details"]["progress"] == 50.0
        for e in status["events"]
    )


@pytest.mark.asyncio
async def test_batch_processing(batch_processor: BatchProcessor):
    """Test batch task processing."""
    # Create batch of tasks
    tasks = [
        {
            "type": TaskType.CHARACTER_PORTRAIT,
            "parameters": {"index": i}
        }
        for i in range(3)
    ]

    batch = await batch_processor.create_batch(
        tasks=tasks,
        priority=TaskPriority.NORMAL,
        group_id="test_batch"
    )

    assert batch.type == TaskType.BATCH
    assert batch.parameters["task_count"] == 3
    assert batch.parameters["group_id"] == "test_batch"

    # Get batch status
    status = await batch_processor.get_batch_status(
        batch.id,
        include_subtasks=True
    )
    assert status["task_count"] == 3
    assert status["completed_count"] == 0
    assert len(status["subtasks"]) == 3

    # Process batch
    await batch_processor.process_batch(batch.id)

    # Verify all subtasks completed
    final_status = await batch_processor.get_batch_status(
        batch.id,
        include_subtasks=True
    )
    assert final_status["completed_count"] == 3
    assert all(
        task["status"] == TaskStatus.COMPLETED.value
        for task in final_status["subtasks"]
    )


async def test_stale_task_cleanup(queue_service: QueueService):
    """Test cleanup of stale tasks."""
    # Create task
    task = await queue_service.enqueue_task(
        task_type=TaskType.CHARACTER_PORTRAIT,
        parameters={"test": "stale"}
    )

    # Start task
    started_task = await queue_service.dequeue_task()
    assert started_task.id == task.id

    # Simulate task being stuck
    started_task.started_at = datetime.utcnow() - timedelta(hours=25)
    await queue_service.session.commit()

    # Run cleanup
    cleaned = await queue_service.cleanup_stale_tasks(max_age_hours=24)
    assert cleaned == 1

    # Verify task was marked for retry
    updated_task = await queue_service.task_repo.get_by_id(task.id)
    assert updated_task.retries == 1
    assert updated_task.status == TaskStatus.PENDING


@pytest.mark.asyncio
async def test_queue_stats(queue_service: QueueService):
    """Test queue statistics."""
    # Create tasks with different priorities
    await queue_service.enqueue_task(
        task_type=TaskType.CHARACTER_PORTRAIT,
        parameters={"priority": "low"},
        priority=TaskPriority.LOW
    )
    await queue_service.enqueue_task(
        task_type=TaskType.CHARACTER_PORTRAIT,
        parameters={"priority": "high"},
        priority=TaskPriority.HIGH
    )

    # Get stats
    stats = await queue_service.get_queue_stats()
    assert stats["queued_tasks"] == 2
    assert stats["processing_tasks"] == 0
    assert sum(stats["priority_breakdown"].values()) == 2
