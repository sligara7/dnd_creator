"""Tests for the storage port interface."""
import json
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import pytest
from pydantic import BaseModel

from campaign_service.core.messaging.client import MessageHubClient
from campaign_service.storage.exceptions import StorageError
from campaign_service.storage.storage_port import StoragePort


# Test models
class TestEntity(BaseModel):
    """Test entity model."""
    model_config = {"table": "test_entities"}
    
    id: UUID
    name: str
    data: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None


class MockMessageHub:
    """Mock Message Hub client for testing."""
    
    def __init__(self, responses: Dict[str, Any]):
        self.responses = responses
        self.requests: List[Dict[str, Any]] = []
    
    async def request(
        self,
        routing_key: str,
        message: Dict[str, Any],
        correlation_id: Optional[str] = None,
        timeout: float = 30.0
    ) -> Optional[Dict]:
        """Mock request method."""
        self.requests.append({
            "routing_key": routing_key,
            "message": message,
            "correlation_id": correlation_id,
        })
        
        if routing_key in self.responses:
            return self.responses[routing_key]
        return None


@pytest.fixture
def test_entity() -> TestEntity:
    """Create a test entity."""
    return TestEntity(
        id=uuid4(),
        name="Test Entity",
        data={"key": "value"},
    )


@pytest.fixture
def mock_message_hub(test_entity: TestEntity) -> MockMessageHub:
    """Create a mock message hub with test responses."""
    responses = {
        "storage.get": {"data": test_entity.model_dump()},
        "storage.query": {"data": [test_entity.model_dump()]},
        "storage.create": {"data": test_entity.model_dump()},
        "storage.update": {"data": test_entity.model_dump()},
        "storage.count": {"count": 1},
        "storage.exists": {"exists": True},
        "storage.batch_create": {"data": [test_entity.model_dump()]},
        "storage.batch_update": {"data": [test_entity.model_dump()]},
    }
    return MockMessageHub(responses)


@pytest.fixture
def storage_port(mock_message_hub: MockMessageHub) -> StoragePort[TestEntity]:
    """Create a storage port instance."""
    return StoragePort(
        message_hub=mock_message_hub,
        model_class=TestEntity,
    )


async def test_get_success(
    storage_port: StoragePort[TestEntity],
    test_entity: TestEntity,
):
    """Test successful get operation."""
    result = await storage_port.get(test_entity.id)
    assert result is not None
    assert result.id == test_entity.id
    assert result.name == test_entity.name


async def test_get_not_found(
    storage_port: StoragePort[TestEntity],
    mock_message_hub: MockMessageHub,
):
    """Test get operation when entity not found."""
    mock_message_hub.responses["storage.get"] = None
    result = await storage_port.get(uuid4())
    assert result is None


async def test_get_all_success(
    storage_port: StoragePort[TestEntity],
    test_entity: TestEntity,
):
    """Test successful get_all operation."""
    results = await storage_port.get_all()
    assert len(results) == 1
    assert results[0].id == test_entity.id


async def test_get_all_filters(
    storage_port: StoragePort[TestEntity],
    mock_message_hub: MockMessageHub,
):
    """Test get_all operation with filters."""
    await storage_port.get_all(name="Test")
    
    assert len(mock_message_hub.requests) == 1
    request = mock_message_hub.requests[0]
    assert request["message"]["filters"]["name"] == "Test"
    assert request["message"]["filters"]["is_deleted"] is False


async def test_create_success(
    storage_port: StoragePort[TestEntity],
    test_entity: TestEntity,
):
    """Test successful create operation."""
    data = {
        "id": str(uuid4()),
        "name": "New Entity",
        "data": {"key": "new value"},
    }
    
    result = await storage_port.create(data)
    assert result is not None
    assert result.id == test_entity.id  # Uses mock response
    assert result.name == test_entity.name


async def test_create_failure(
    storage_port: StoragePort[TestEntity],
    mock_message_hub: MockMessageHub,
):
    """Test create operation failure."""
    mock_message_hub.responses["storage.create"] = None
    
    with pytest.raises(StorageError):
        await storage_port.create({"name": "Failed Entity"})


async def test_update_success(
    storage_port: StoragePort[TestEntity],
    test_entity: TestEntity,
):
    """Test successful update operation."""
    data = {"name": "Updated Name"}
    result = await storage_port.update(test_entity.id, data)
    
    assert result is not None
    assert result.id == test_entity.id


async def test_update_not_found(
    storage_port: StoragePort[TestEntity],
    mock_message_hub: MockMessageHub,
):
    """Test update operation when entity not found."""
    mock_message_hub.responses["storage.update"] = None
    result = await storage_port.update(uuid4(), {"name": "Not Found"})
    assert result is None


async def test_delete_success(
    storage_port: StoragePort[TestEntity],
    mock_message_hub: MockMessageHub,
):
    """Test successful delete operation."""
    mock_message_hub.responses["storage.update"] = {"success": True}
    result = await storage_port.delete(uuid4())
    assert result is True


async def test_count_success(
    storage_port: StoragePort[TestEntity],
):
    """Test successful count operation."""
    count = await storage_port.count(name="Test")
    assert count == 1


async def test_exists_success(
    storage_port: StoragePort[TestEntity],
):
    """Test successful exists operation."""
    exists = await storage_port.exists(uuid4())
    assert exists is True


async def test_batch_operations(
    storage_port: StoragePort[TestEntity],
    test_entity: TestEntity,
):
    """Test batch operations."""
    # Batch create
    items = [
        {"id": str(uuid4()), "name": f"Entity {i}", "data": {}}
        for i in range(3)
    ]
    created = await storage_port.batch_create(items)
    assert len(created) == 1  # Mock returns single item
    
    # Batch update
    updates = [
        {"id": str(uuid4()), "data": {"name": f"Updated {i}"}}
        for i in range(3)
    ]
    updated = await storage_port.batch_update(updates)
    assert len(updated) == 1  # Mock returns single item
    
    # Batch delete
    mock_message_hub = storage_port.message_hub
    mock_message_hub.responses["storage.batch_update"] = {"updated_count": 3}
    deleted = await storage_port.batch_delete([uuid4() for _ in range(3)])
    assert deleted == 3