"""Integration tests for Message Hub communication."""
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import pytest
from pydantic import BaseModel

from campaign_service.models.storage_campaign import (
    Campaign,
    CampaignState,
    CampaignType,
    Chapter,
    ChapterState,
    ChapterType,
)
from campaign_service.core.messaging.client import MessageHubClient
from campaign_service.storage.storage_port import StoragePort
from campaign_service.storage.exceptions import StorageError


# Mock response data
CAMPAIGN_DATA = {
    "id": str(uuid4()),
    "name": "Test Campaign",
    "description": "Test campaign for integration",
    "campaign_type": CampaignType.TRADITIONAL.value,
    "creator_id": str(uuid4()),
    "owner_id": str(uuid4()),
    "state": CampaignState.DRAFT.value,
    "theme_id": str(uuid4()),
    "metadata": {"integration": True},
    "created_at": datetime.now(UTC).isoformat(),
    "updated_at": datetime.now(UTC).isoformat(),
    "is_deleted": False,
}

CHAPTER_DATA = {
    "id": str(uuid4()),
    "campaign_id": CAMPAIGN_DATA["id"],
    "title": "Test Chapter",
    "description": "Test chapter for integration",
    "chapter_type": ChapterType.STORY.value,
    "state": ChapterState.DRAFT.value,
    "sequence_number": 1,
    "prerequisites": [],
    "content": {},
    "metadata": {"integration": True},
    "created_at": datetime.now(UTC).isoformat(),
    "updated_at": datetime.now(UTC).isoformat(),
    "is_deleted": False,
}


class MockMessageHub(MessageHubClient):
    """Mock Message Hub client for integration testing."""
    
    def __init__(self, responses: Dict[str, Any]):
        """Initialize mock client."""
        self.responses = responses
        self.requests: List[Dict[str, Any]] = []
        self._initialized = True
    
    async def request(
        self,
        routing_key: str,
        message: Dict[str, Any],
        correlation_id: Optional[str] = None,
        timeout: float = 30.0
    ) -> Optional[Dict]:
        """Mock request method.
        
        Args:
            routing_key: Storage request type
            message: Request data
            correlation_id: Optional correlation ID
            timeout: Request timeout (unused)

        Returns:
            Mock response data
        """
        self.requests.append({
            "routing_key": routing_key,
            "message": message,
            "correlation_id": correlation_id,
        })
        
        if routing_key == "storage.get":
            # Return campaign/chapter data based on table
            table = message["table"]
            if table == "campaigns":
                return {"data": CAMPAIGN_DATA}
            elif table == "chapters":
                return {"data": CHAPTER_DATA}
        
        elif routing_key == "storage.query":
            # Return list of items for queries
            table = message["table"]
            if table == "campaigns":
                return {"data": [CAMPAIGN_DATA]}
            elif table == "chapters":
                return {"data": [CHAPTER_DATA]}
        
        elif routing_key == "storage.create":
            # Return newly created item
            table = message["table"]
            if table == "campaigns":
                return {"data": {**CAMPAIGN_DATA, **message["data"]}}
            elif table == "chapters":
                return {"data": {**CHAPTER_DATA, **message["data"]}}
        
        elif routing_key == "storage.update":
            # Return updated item
            table = message["table"]
            if table == "campaigns":
                return {"data": {**CAMPAIGN_DATA, **message["data"]}}
            elif table == "chapters":
                return {"data": {**CHAPTER_DATA, **message["data"]}}
        
        elif routing_key == "storage.count":
            # Return count
            return {"count": 1}
        
        elif routing_key == "storage.exists":
            # Return existence check
            return {"exists": True}
        
        return self.responses.get(routing_key)


@pytest.fixture
def mock_message_hub() -> MockMessageHub:
    """Create mock message hub."""
    return MockMessageHub({})


@pytest.fixture
def campaign_storage(mock_message_hub: MockMessageHub) -> StoragePort[Campaign]:
    """Create campaign storage port."""
    return StoragePort[Campaign](
        message_hub=mock_message_hub,
        model_class=Campaign,
        database="campaign_db",
    )


@pytest.fixture
def chapter_storage(mock_message_hub: MockMessageHub) -> StoragePort[Chapter]:
    """Create chapter storage port."""
    return StoragePort[Chapter](
        message_hub=mock_message_hub,
        model_class=Chapter,
        database="campaign_db",
    )


async def test_campaign_storage_get(campaign_storage: StoragePort[Campaign]):
    """Test campaign retrieval through storage port."""
    campaign = await campaign_storage.get(UUID(CAMPAIGN_DATA["id"]))
    
    assert campaign is not None
    assert str(campaign.id) == CAMPAIGN_DATA["id"]
    assert campaign.name == CAMPAIGN_DATA["name"]
    assert campaign.campaign_type == CampaignType.TRADITIONAL
    assert campaign.state == CampaignState.DRAFT
    assert not campaign.is_deleted


async def test_campaign_storage_get_all(campaign_storage: StoragePort[Campaign]):
    """Test campaign list retrieval through storage port."""
    campaigns = await campaign_storage.get_all()
    
    assert len(campaigns) == 1
    campaign = campaigns[0]
    assert str(campaign.id) == CAMPAIGN_DATA["id"]
    assert campaign.name == CAMPAIGN_DATA["name"]
    assert campaign.campaign_type == CampaignType.TRADITIONAL
    assert campaign.state == CampaignState.DRAFT
    assert not campaign.is_deleted


async def test_campaign_storage_create(campaign_storage: StoragePort[Campaign]):
    """Test campaign creation through storage port."""
    data = {
        "name": "New Campaign",
        "description": "Newly created campaign",
        "campaign_type": CampaignType.TRADITIONAL,
        "creator_id": uuid4(),
        "owner_id": uuid4(),
        "theme_id": uuid4(),
    }
    
    campaign = await campaign_storage.create(data)
    assert campaign is not None
    assert campaign.name == data["name"]
    assert campaign.description == data["description"]
    assert campaign.campaign_type == data["campaign_type"]
    assert campaign.state == CampaignState.DRAFT


async def test_campaign_storage_update(campaign_storage: StoragePort[Campaign]):
    """Test campaign update through storage port."""
    campaign_id = UUID(CAMPAIGN_DATA["id"])
    data = {
        "name": "Updated Campaign",
        "state": CampaignState.ACTIVE,
    }
    
    campaign = await campaign_storage.update(campaign_id, data)
    assert campaign is not None
    assert campaign.name == data["name"]
    assert campaign.state == data["state"]


async def test_chapter_storage_operations(chapter_storage: StoragePort[Chapter]):
    """Test chapter operations through storage port."""
    # Create
    data = {
        "campaign_id": UUID(CAMPAIGN_DATA["id"]),
        "title": "New Chapter",
        "description": "New test chapter",
        "chapter_type": ChapterType.STORY,
        "state": ChapterState.DRAFT,
        "sequence_number": 1,
    }
    
    chapter = await chapter_storage.create(data)
    assert chapter is not None
    assert chapter.title == data["title"]
    assert chapter.description == data["description"]
    assert chapter.chapter_type == data["chapter_type"]
    
    # Get
    chapter = await chapter_storage.get(UUID(CHAPTER_DATA["id"]))
    assert chapter is not None
    assert chapter.title == CHAPTER_DATA["title"]
    
    # Update
    update_data = {"title": "Updated Chapter"}
    updated = await chapter_storage.update(chapter.id, update_data)
    assert updated is not None
    assert updated.title == update_data["title"]
    
    # List
    chapters = await chapter_storage.get_all()
    assert len(chapters) == 1
    assert str(chapters[0].id) == CHAPTER_DATA["id"]


async def test_storage_error_handling(campaign_storage: StoragePort[Campaign]):
    """Test storage error handling."""
    # Try to get non-existent campaign
    campaign = await campaign_storage.get(uuid4())
    assert campaign is None

    # Try invalid update
    invalid_id = uuid4()
    with pytest.raises(StorageError):
        await campaign_storage.update(invalid_id, {"invalid": True})


async def test_message_hub_communication(
    campaign_storage: StoragePort[Campaign],
    mock_message_hub: MockMessageHub,
):
    """Test Message Hub communication patterns."""
    # Create campaign
    data = {
        "name": "Communication Test",
        "description": "Test campaign",
        "campaign_type": CampaignType.TRADITIONAL,
        "creator_id": uuid4(),
        "owner_id": uuid4(),
    }
    
    await campaign_storage.create(data)
    
    # Verify create request
    create_request = next(r for r in mock_message_hub.requests if r["routing_key"] == "storage.create")
    assert create_request["message"]["database"] == "campaign_db"
    assert create_request["message"]["table"] == "campaigns"
    assert create_request["message"]["data"]["name"] == data["name"]
    
    # List campaigns
    await campaign_storage.get_all()
    
    # Verify query request
    query_request = next(r for r in mock_message_hub.requests if r["routing_key"] == "storage.query")
    assert query_request["message"]["database"] == "campaign_db"
    assert query_request["message"]["table"] == "campaigns"
    assert query_request["message"]["filters"].get("is_deleted") is False