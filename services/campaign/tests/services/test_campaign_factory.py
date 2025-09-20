"""Tests for the campaign factory service."""
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
from campaign_service.storage.storage_port import StoragePort
from campaign_service.services.campaign_factory import CampaignFactoryService
from campaign_service.services.theme import ThemeService


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


class MockThemeService:
    """Mock theme service for testing."""
    
    async def get_theme(self, theme_id: UUID) -> Optional[Dict[str, Any]]:
        """Mock theme data retrieval."""
        return {
            "id": str(theme_id),
            "name": "Test Theme",
            "description": "Test theme for campaigns",
            "data": {"key": "value"},
        }
    
    async def get_theme_profile(self, theme_id: str) -> Dict[str, Any]:
        """Mock theme profile retrieval."""
        return {
            "id": theme_id,
            "name": "Test Theme",
            "profile": {
                "style": "fantasy",
                "tone": "serious",
            },
        }


@pytest.fixture
def mock_message_hub() -> MockMessageHub:
    """Create mock message hub with test responses."""
    responses = {
        "llm.generate_chapter_content": {
            "content": {
                "description": "Generated chapter content",
                "encounters": [],
                "npcs": [],
                "locations": [],
            }
        }
    }
    return MockMessageHub(responses)


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


@pytest.fixture
def theme_service() -> ThemeService:
    """Create mock theme service."""
    return MockThemeService()


@pytest.fixture
def factory_service(
    campaign_storage: StoragePort[Campaign],
    chapter_storage: StoragePort[Chapter],
    theme_service: ThemeService,
    mock_message_hub: MockMessageHub,
) -> CampaignFactoryService:
    """Create campaign factory service."""
    return CampaignFactoryService(
        campaign_storage=campaign_storage,
        chapter_storage=chapter_storage,
        theme_service=theme_service,
        message_hub_client=mock_message_hub,
    )


@pytest.fixture
def test_campaign_data() -> Dict[str, Any]:
    """Create test campaign data."""
    return {
        "id": uuid4(),
        "name": "Test Campaign",
        "description": "A test campaign",
        "campaign_type": CampaignType.TRADITIONAL,
        "creator_id": uuid4(),
        "owner_id": uuid4(),
        "state": CampaignState.DRAFT,
        "theme_id": uuid4(),
        "metadata": {"test": True},
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "is_deleted": False,
    }


async def test_create_campaign(
    factory_service: CampaignFactoryService,
    test_campaign_data: Dict[str, Any],
):
    """Test campaign creation."""
    campaign = await factory_service.create_campaign(
        name=test_campaign_data["name"],
        description=test_campaign_data["description"],
        campaign_type=test_campaign_data["campaign_type"],
        creator_id=test_campaign_data["creator_id"],
        owner_id=test_campaign_data["owner_id"],
        theme_id=test_campaign_data["theme_id"],
        metadata=test_campaign_data["metadata"],
    )

    assert campaign is not None
    assert campaign.name == test_campaign_data["name"]
    assert campaign.description == test_campaign_data["description"]
    assert campaign.campaign_type == test_campaign_data["campaign_type"]
    assert campaign.creator_id == test_campaign_data["creator_id"]
    assert campaign.owner_id == test_campaign_data["owner_id"]
    assert campaign.theme_id == test_campaign_data["theme_id"]
    assert campaign.state == CampaignState.DRAFT
    assert campaign.metadata == test_campaign_data["metadata"]
    assert not campaign.is_deleted


async def test_create_campaign_with_theme(
    factory_service: CampaignFactoryService,
    test_campaign_data: Dict[str, Any],
    theme_service: ThemeService,
):
    """Test campaign creation with theme data."""
    theme_data = await theme_service.get_theme(test_campaign_data["theme_id"])
    assert theme_data is not None

    campaign = await factory_service.create_campaign(
        name=test_campaign_data["name"],
        description=test_campaign_data["description"],
        campaign_type=test_campaign_data["campaign_type"],
        creator_id=test_campaign_data["creator_id"],
        owner_id=test_campaign_data["owner_id"],
        theme_id=test_campaign_data["theme_id"],
        metadata=test_campaign_data["metadata"],
    )

    assert campaign is not None
    assert campaign.theme_id == test_campaign_data["theme_id"]
    assert campaign.theme_data is not None
    assert campaign.theme_data["name"] == "Test Theme"


async def test_create_initial_chapters(
    factory_service: CampaignFactoryService,
    test_campaign_data: Dict[str, Any],
):
    """Test initial chapter creation."""
    # Create campaign first
    campaign = await factory_service.create_campaign(
        name=test_campaign_data["name"],
        description=test_campaign_data["description"],
        campaign_type=test_campaign_data["campaign_type"],
        creator_id=test_campaign_data["creator_id"],
        owner_id=test_campaign_data["owner_id"],
        theme_id=test_campaign_data["theme_id"],
        metadata=test_campaign_data["metadata"],
    )

    assert campaign is not None

    chapters = await factory_service._create_initial_chapters(campaign.id)
    assert len(chapters) == 3

    # Verify introduction chapter
    intro = chapters[0]
    assert intro.title == "Introduction"
    assert intro.chapter_type == ChapterType.INTRODUCTION
    assert intro.state == ChapterState.DRAFT
    assert intro.sequence_number == 1
    assert not intro.prerequisites

    # Verify chapter 1
    ch1 = chapters[1]
    assert ch1.title == "Chapter 1"
    assert ch1.chapter_type == ChapterType.STORY
    assert ch1.state == ChapterState.DRAFT
    assert ch1.sequence_number == 2
    assert intro.id in ch1.prerequisites

    # Verify chapter 2
    ch2 = chapters[2]
    assert ch2.title == "Chapter 2"
    assert ch2.chapter_type == ChapterType.STORY
    assert ch2.state == ChapterState.DRAFT
    assert ch2.sequence_number == 3
    assert ch1.id in ch2.prerequisites


async def test_generate_chapter_contents(
    factory_service: CampaignFactoryService,
    mock_message_hub: MockMessageHub,
    test_campaign_data: Dict[str, Any],
):
    """Test chapter content generation."""
    # Create campaign first
    campaign = await factory_service.create_campaign(
        name=test_campaign_data["name"],
        description=test_campaign_data["description"],
        campaign_type=test_campaign_data["campaign_type"],
        creator_id=test_campaign_data["creator_id"],
        owner_id=test_campaign_data["owner_id"],
        theme_id=test_campaign_data["theme_id"],
        metadata=test_campaign_data["metadata"],
    )

    assert campaign is not None

    # Create chapters
    chapters = await factory_service._create_initial_chapters(campaign.id)
    assert len(chapters) == 3

    # Generate chapter contents
    await factory_service._generate_chapter_contents(chapters, campaign.id)

    # Verify LLM requests
    assert len(mock_message_hub.requests) == 3
    for request in mock_message_hub.requests:
        assert request["routing_key"] == "llm.generate_chapter_content"
        assert "theme" in request["message"]
        assert "campaign_context" in request["message"]
        assert "requirements" in request["message"]

    # Verify content was saved
    for chapter in chapters:
        assert chapter.content is not None
        assert "encounters" in chapter.content
        assert "npcs" in chapter.content
        assert "locations" in chapter.content