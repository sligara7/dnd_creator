"""Tests for task API endpoints."""
import json
from typing import Dict
from uuid import UUID

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from image.api.tasks import router as tasks_router
from image.core.dependencies import get_queue_service, get_batch_processor
from image.services.batch import BatchProcessor
from image.services.queue import QueueService
from image.models.generation import TaskPriority, TaskStatus, TaskType


@pytest.fixture
def app(
    queue_service: QueueService,
    batch_processor: BatchProcessor
) -> FastAPI:
    """Create test FastAPI application.

    Args:
        queue_service: Queue service instance
        batch_processor: Batch processor instance

    Returns:
        FastAPI test application
    """
    app = FastAPI()
    app.include_router(tasks_router, prefix="/api/v1")

    # Override dependencies
    app.dependency_overrides[get_queue_service] = lambda: queue_service
    app.dependency_overrides[get_batch_processor] = lambda: batch_processor

    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:
    """Create test HTTP client.

    Args:
        app: FastAPI application

    Returns:
        Test HTTP client
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


async def test_create_task(client: AsyncClient):
    """Test task creation endpoint."""
    response = await client.post(
        "/api/v1/tasks",
        json={
            "type": TaskType.CHARACTER_PORTRAIT.value,
            "parameters": {"test": "api"},
            "priority": TaskPriority.NORMAL.value
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert UUID(data["id"])
    assert data["type"] == TaskType.CHARACTER_PORTRAIT.value
    assert data["status"] == TaskStatus.PENDING.value
    assert data["priority"] == TaskPriority.NORMAL.value


async def test_create_batch(client: AsyncClient):
    """Test batch task creation endpoint."""
    response = await client.post(
        "/api/v1/tasks/batch",
        json={
            "tasks": [
                {
                    "type": TaskType.CHARACTER_PORTRAIT.value,
                    "parameters": {"index": 0},
                    "priority": TaskPriority.NORMAL.value
                },
                {
                    "type": TaskType.CHARACTER_PORTRAIT.value,
                    "parameters": {"index": 1},
                    "priority": TaskPriority.NORMAL.value
                }
            ],
            "priority": TaskPriority.NORMAL.value,
            "group_id": "test_group"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert UUID(data["id"])
    assert data["status"] == TaskStatus.PENDING.value
    assert data["task_count"] == 2
    assert data["group_id"] == "test_group"
    assert len(data["subtasks"]) == 2


async def test_get_task_status(client: AsyncClient):
    """Test task status endpoint."""
    # Create task first
    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "type": TaskType.CHARACTER_PORTRAIT.value,
            "parameters": {"test": "status"},
            "priority": TaskPriority.NORMAL.value
        }
    )
    task_id = create_response.json()["id"]

    # Get status
    response = await client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["type"] == TaskType.CHARACTER_PORTRAIT.value
    assert data["status"] in (
        TaskStatus.PENDING.value,
        TaskStatus.IN_PROGRESS.value
    )

    # Get status with events
    response = await client.get(
        f"/api/v1/tasks/{task_id}",
        params={"include_events": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert "events" in data


async def test_get_batch_status(client: AsyncClient):
    """Test batch status endpoint."""
    # Create batch first
    create_response = await client.post(
        "/api/v1/tasks/batch",
        json={
            "tasks": [
                {
                    "type": TaskType.CHARACTER_PORTRAIT.value,
                    "parameters": {"test": "batch"}
                }
            ],
            "priority": TaskPriority.NORMAL.value
        }
    )
    batch_id = create_response.json()["id"]

    # Get status
    response = await client.get(f"/api/v1/tasks/batch/{batch_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == batch_id
    assert data["task_count"] == 1

    # Get status with subtasks
    response = await client.get(
        f"/api/v1/tasks/batch/{batch_id}",
        params={"include_subtasks": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert "subtasks" in data
    assert len(data["subtasks"]) == 1


async def test_cancel_task(client: AsyncClient):
    """Test task cancellation endpoint."""
    # Create task first
    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "type": TaskType.CHARACTER_PORTRAIT.value,
            "parameters": {"test": "cancel"}
        }
    )
    task_id = create_response.json()["id"]

    # Cancel task
    response = await client.delete(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 204

    # Verify task was cancelled
    status_response = await client.get(f"/api/v1/tasks/{task_id}")
    assert status_response.json()["status"] == TaskStatus.CANCELLED.value


async def test_cancel_batch(client: AsyncClient):
    """Test batch cancellation endpoint."""
    # Create batch first
    create_response = await client.post(
        "/api/v1/tasks/batch",
        json={
            "tasks": [
                {
                    "type": TaskType.CHARACTER_PORTRAIT.value,
                    "parameters": {"test": "batch_cancel"}
                }
            ]
        }
    )
    batch_id = create_response.json()["id"]

    # Cancel batch
    response = await client.delete(f"/api/v1/tasks/batch/{batch_id}")
    assert response.status_code == 204

    # Verify batch was cancelled
    status_response = await client.get(f"/api/v1/tasks/batch/{batch_id}")
    assert status_response.json()["status"] == TaskStatus.CANCELLED.value


async def test_get_queue_stats(client: AsyncClient):
    """Test queue statistics endpoint."""
    # Create some tasks
    await client.post(
        "/api/v1/tasks",
        json={
            "type": TaskType.CHARACTER_PORTRAIT.value,
            "parameters": {"test": "stats1"}
        }
    )
    await client.post(
        "/api/v1/tasks",
        json={
            "type": TaskType.CHARACTER_PORTRAIT.value,
            "parameters": {"test": "stats2"}
        }
    )

    # Get stats
    response = await client.get("/api/v1/tasks/queue/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["queued_tasks"] >= 2
    assert "priority_breakdown" in data
    assert "timestamp" in data


async def test_invalid_task_type(client: AsyncClient):
    """Test handling of invalid task type."""
    response = await client.post(
        "/api/v1/tasks",
        json={
            "type": "INVALID_TYPE",
            "parameters": {}
        }
    )
    assert response.status_code == 422


async def test_nonexistent_task(client: AsyncClient):
    """Test handling of non-existent task ID."""
    fake_id = "123e4567-e89b-12d3-a456-426614174000"
    
    response = await client.get(f"/api/v1/tasks/{fake_id}")
    assert response.status_code == 404

    response = await client.delete(f"/api/v1/tasks/{fake_id}")
    assert response.status_code == 404


async def test_batch_validation(client: AsyncClient):
    """Test batch creation validation."""
    # Empty batch
    response = await client.post(
        "/api/v1/tasks/batch",
        json={
            "tasks": []
        }
    )
    assert response.status_code == 422

    # Invalid task type in batch
    response = await client.post(
        "/api/v1/tasks/batch",
        json={
            "tasks": [
                {
                    "type": "INVALID_TYPE",
                    "parameters": {}
                }
            ]
        }
    )
    assert response.status_code == 422
