"""Tests for storage-based repositories."""
from datetime import datetime, timedelta, UTC
from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest

from campaign_service.models.campaign import Campaign, Chapter, CampaignState, CampaignType
from campaign_service.models.pagination import PaginationResult
from campaign_service.repositories.storage_campaign import CampaignRepository, ChapterRepository
from campaign_service.storage import StorageClient
from campaign_service.storage.exceptions import StorageError


@pytest.fixture
def mock_storage():
    """Create mock storage client."""
    return AsyncMock(spec=StorageClient)


@pytest.fixture
def campaign_repo(mock_storage):
    """Create campaign repository."""
    return CampaignRepository(mock_storage)


@pytest.fixture
def chapter_repo(mock_storage):
    """Create chapter repository."""
    return ChapterRepository(mock_storage)


@pytest.fixture
def test_campaign():
    """Create test campaign data."""
    return {
        "id": "00000000-0000-0000-0000-000000000001",
        "name": "Test Campaign",
        "description": "Test description",
        "creator_id": "00000000-0000-0000-0000-000000000002",
        "owner_id": "00000000-0000-0000-0000-000000000002",
        "state": CampaignState.DRAFT.value,
        "campaign_type": CampaignType.TRADITIONAL.value,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "is_deleted": False,
        "deleted_at": None,
    }


@pytest.mark.asyncio
class TestCampaignRepository:
    """Test campaign repository."""
    
    async def test_get_campaign(
        self,
        campaign_repo: CampaignRepository,
        mock_storage: AsyncMock,
        test_campaign: dict,
    ):
        """Test getting campaign by ID."""
        mock_storage.execute.return_value = [test_campaign]
        
        campaign = await campaign_repo.get(
            UUID("00000000-0000-0000-0000-000000000001")
        )
        
        assert campaign is not None
        assert campaign.id == UUID(test_campaign["id"])
        assert campaign.name == test_campaign["name"]
        assert campaign.state == CampaignState.DRAFT
        
        mock_storage.execute.assert_called_once()
    
    async def test_get_nonexistent_campaign(
        self,
        campaign_repo: CampaignRepository,
        mock_storage: AsyncMock,
    ):
        """Test getting non-existent campaign."""
        mock_storage.execute.return_value = []
        
        campaign = await campaign_repo.get(
            UUID("00000000-0000-0000-0000-000000000001")
        )
        
        assert campaign is None
        mock_storage.execute.assert_called_once()
    
    async def test_create_campaign(
        self,
        campaign_repo: CampaignRepository,
        mock_storage: AsyncMock,
        test_campaign: dict,
    ):
        """Test creating campaign."""
        mock_storage.execute.return_value = [test_campaign]
        
        campaign_data = {
            "name": "New Campaign",
            "description": "New description",
            "creator_id": UUID("00000000-0000-0000-0000-000000000002"),
            "owner_id": UUID("00000000-0000-0000-0000-000000000002"),
            "state": CampaignState.DRAFT,
            "campaign_type": CampaignType.TRADITIONAL,
        }
        
        campaign = await campaign_repo.create(campaign_data)
        
        assert campaign is not None
        assert campaign.name == test_campaign["name"]
        mock_storage.execute.assert_called_once()
    
    async def test_update_campaign(
        self,
        campaign_repo: CampaignRepository,
        mock_storage: AsyncMock,
        test_campaign: dict,
    ):
        """Test updating campaign."""
        # Mock get and update
        mock_storage.execute.side_effect = [
            [test_campaign],  # get
            [{"id": test_campaign["id"], "name": "Updated Name"}],  # update
        ]
        
        campaign = await campaign_repo.update(
            UUID(test_campaign["id"]),
            {"name": "Updated Name"},
        )
        
        assert campaign is not None
        assert campaign.name == "Updated Name"
        assert mock_storage.execute.call_count == 2
    
    async def test_delete_campaign(
        self,
        campaign_repo: CampaignRepository,
        mock_storage: AsyncMock,
        test_campaign: dict,
    ):
        """Test deleting campaign."""
        mock_storage.execute.return_value = [test_campaign]
        
        result = await campaign_repo.delete(UUID(test_campaign["id"]))
        
        assert result is True
        mock_storage.execute.assert_called_once()
    
    async def test_get_paginated(
        self,
        campaign_repo: CampaignRepository,
        mock_storage: AsyncMock,
        test_campaign: dict,
    ):
        """Test paginated campaign retrieval."""
        # Mock count and select
        mock_storage.execute.side_effect = [
            [{"count": 1}],  # count
            [test_campaign],  # select
        ]
        
        result = await campaign_repo.get_paginated(
            page=1,
            page_size=10,
        )
        
        assert isinstance(result, PaginationResult)
        assert len(result.items) == 1
        assert result.total_items == 1
        assert result.page_number == 1
        assert mock_storage.execute.call_count == 2
    
    async def test_filter_by(
        self,
        campaign_repo: CampaignRepository,
        mock_storage: AsyncMock,
        test_campaign: dict,
    ):
        """Test campaign filtering."""
        mock_storage.execute.return_value = [test_campaign]
        
        campaigns = await campaign_repo.filter_by(
            states=[CampaignState.DRAFT],
            campaign_types=[CampaignType.TRADITIONAL],
            owner_id=UUID("00000000-0000-0000-0000-000000000002"),
        )
        
        assert len(campaigns) == 1
        assert campaigns[0].state == CampaignState.DRAFT
        mock_storage.execute.assert_called_once()
    
    async def test_filter_by_date_range(
        self,
        campaign_repo: CampaignRepository,
        mock_storage: AsyncMock,
        test_campaign: dict,
    ):
        """Test date range filtering."""
        mock_storage.execute.return_value = [test_campaign]
        
        start_date = datetime(2025, 1, 1, tzinfo=UTC)
        end_date = start_date + timedelta(days=1)
        
        campaigns = await campaign_repo.filter_by_date_range(
            start_date=start_date,
            end_date=end_date,
        )
        
        assert len(campaigns) == 1
        mock_storage.execute.assert_called_once()
    
    async def test_get_with_chapters(
        self,
        campaign_repo: CampaignRepository,
        mock_storage: AsyncMock,
        test_campaign: dict,
    ):
        """Test getting campaign with chapters."""
        chapter = {
            "id": "00000000-0000-0000-0000-000000000003",
            "campaign_id": test_campaign["id"],
            "title": "Test Chapter",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "is_deleted": False,
        }
        
        # Mock campaign and chapter queries
        mock_storage.execute.side_effect = [
            [test_campaign],  # get campaign
            [chapter],  # get chapters
        ]
        
        campaign = await campaign_repo.get_with_chapters(
            UUID(test_campaign["id"])
        )
        
        assert campaign is not None
        assert len(campaign.chapters) == 1
        assert campaign.chapters[0].title == "Test Chapter"
        assert mock_storage.execute.call_count == 2


@pytest.mark.asyncio
class TestChapterRepository:
    """Test chapter repository."""
    
    @pytest.fixture
    def test_chapter(self):
        """Create test chapter data."""
        return {
            "id": "00000000-0000-0000-0000-000000000003",
            "campaign_id": "00000000-0000-0000-0000-000000000001",
            "title": "Test Chapter",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "is_deleted": False,
            "prerequisites": ["00000000-0000-0000-0000-000000000004"],
        }
    
    async def test_get_by_campaign(
        self,
        chapter_repo: ChapterRepository,
        mock_storage: AsyncMock,
        test_chapter: dict,
    ):
        """Test getting chapters by campaign."""
        mock_storage.execute.return_value = [test_chapter]
        
        chapters = await chapter_repo.get_by_campaign(
            UUID("00000000-0000-0000-0000-000000000001")
        )
        
        assert len(chapters) == 1
        assert chapters[0].title == "Test Chapter"
        mock_storage.execute.assert_called_once()
    
    async def test_get_prerequisites(
        self,
        chapter_repo: ChapterRepository,
        mock_storage: AsyncMock,
        test_chapter: dict,
    ):
        """Test getting chapter prerequisites."""
        prereq = {
            "id": "00000000-0000-0000-0000-000000000004",
            "title": "Prerequisite Chapter",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "is_deleted": False,
        }
        
        # Mock chapter and prerequisite queries
        mock_storage.execute.side_effect = [
            [test_chapter],  # get chapter
            [prereq],  # get prerequisites
        ]
        
        chapters = await chapter_repo.get_prerequisites(
            UUID(test_chapter["id"])
        )
        
        assert len(chapters) == 1
        assert chapters[0].title == "Prerequisite Chapter"
        assert mock_storage.execute.call_count == 2