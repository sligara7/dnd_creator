"""Campaign repository tests for advanced operations."""
import pytest
from datetime import datetime, UTC
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from campaign_service.models.campaign import Campaign, CampaignType, CampaignState
from campaign_service.repositories.campaign import CampaignRepository

# Test data generators

@pytest.fixture
def campaign_batch_data():
    """Generate batch of campaign data for testing."""
    return [
        {
            "name": f"Test Campaign {i}",
            "description": f"Campaign description {i}",
            "campaign_type": CampaignType.TRADITIONAL,
            "state": CampaignState.DRAFT,
            "theme_data": {},
            "campaign_metadata": {},
            "creator_id": UUID("00000000-0000-0000-0000-000000000001"),
            "owner_id": UUID("00000000-0000-0000-0000-000000000001"),
        }
        for i in range(1, 21)  # Create 20 test campaigns
    ]

# Batch Operation Tests

@pytest.mark.asyncio
class TestBatchOperations:
    """Test batch operation functionality."""

    async def test_batch_create(self, test_db: AsyncSession, campaign_batch_data):
        """Test creating multiple campaigns in a batch operation."""
        # Arrange
        repo = CampaignRepository(test_db)
        
        # Act
        campaigns = [Campaign(**data) for data in campaign_batch_data[:5]]
        created_campaigns = await repo.batch_create(campaigns)
        
        # Assert
        assert len(created_campaigns) == 5
        for campaign in created_campaigns:
            assert isinstance(campaign.id, UUID)
            assert campaign.name.startswith("Test Campaign")

    async def test_batch_update(self, test_db: AsyncSession, campaign_batch_data):
        """Test updating multiple campaigns in a batch operation."""
        # Arrange
        repo = CampaignRepository(test_db)
        campaigns = [Campaign(**data) for data in campaign_batch_data[:3]]
        created = await repo.batch_create(campaigns)
        
        # Act
        for campaign in created:
            campaign.state = CampaignState.ACTIVE
        updated = await repo.batch_update(created)
        
        # Assert
        assert len(updated) == 3
        for campaign in updated:
            assert campaign.state == CampaignState.ACTIVE

    async def test_batch_soft_delete(self, test_db: AsyncSession, campaign_batch_data):
        """Test soft-deleting multiple campaigns in a batch operation."""
        # Arrange
        repo = CampaignRepository(test_db)
        campaigns = [Campaign(**data) for data in campaign_batch_data[:4]]
        created = await repo.batch_create(campaigns)
        campaign_ids = [c.id for c in created]
        
        # Act
        await repo.batch_soft_delete(campaign_ids)
        
        # Assert
        result = await repo.get_all(include_deleted=True)
        deleted = [c for c in result if c.id in campaign_ids]
        assert len(deleted) == 4
        for campaign in deleted:
            assert campaign.is_deleted
            assert isinstance(campaign.deleted_at, datetime)

# Pagination Tests

@pytest.mark.asyncio
class TestPagination:
    """Test pagination functionality."""

    async def test_get_paginated_campaigns(self, test_db: AsyncSession, campaign_batch_data):
        """Test retrieving campaigns with pagination."""
        # Arrange
        repo = CampaignRepository(test_db)
        campaigns = [Campaign(**data) for data in campaign_batch_data]
        await repo.batch_create(campaigns)
        
        # Act
        page_1 = await repo.get_paginated(page=1, page_size=5)
        page_2 = await repo.get_paginated(page=2, page_size=5)
        
        # Assert
        assert len(page_1.items) == 5
        assert len(page_2.items) == 5
        assert page_1.total_items == 20
        assert page_1.total_pages == 4
        assert page_1.items[0].name != page_2.items[0].name

    async def test_paginate_empty_results(self, test_db: AsyncSession):
        """Test pagination with no results."""
        # Arrange
        repo = CampaignRepository(test_db)
        
        # Act
        page = await repo.get_paginated(page=1, page_size=10)
        
        # Assert
        assert len(page.items) == 0
        assert page.total_items == 0
        assert page.total_pages == 0

    async def test_paginate_with_filter(self, test_db: AsyncSession, campaign_batch_data):
        """Test pagination with filtering."""
        # Arrange
        repo = CampaignRepository(test_db)
        campaigns = [Campaign(**data) for data in campaign_batch_data]
        created = await repo.batch_create(campaigns)
        
        # Update some campaigns to active
        for campaign in created[:10]:
            campaign.state = CampaignState.ACTIVE
        await repo.batch_update(created[:10])
        
        # Act
        page = await repo.get_paginated(
            page=1,
            page_size=5,
            filters={"state": CampaignState.ACTIVE}
        )
        
        # Assert
        assert len(page.items) == 5
        assert page.total_items == 10
        for item in page.items:
            assert item.state == CampaignState.ACTIVE

# Filtering Tests

@pytest.mark.asyncio
class TestFiltering:
    """Test filtering functionality."""

    async def test_filter_by_multiple_states(self, test_db: AsyncSession, campaign_batch_data):
        """Test filtering campaigns by multiple states."""
        # Arrange
        repo = CampaignRepository(test_db)
        campaigns = [Campaign(**data) for data in campaign_batch_data[:6]]
        
        # Set different states
        states = [CampaignState.DRAFT, CampaignState.ACTIVE, CampaignState.PAUSED]
        for i, campaign in enumerate(campaigns):
            campaign.state = states[i % 3]
        created = await repo.batch_create(campaigns)
        
        # Act
        filtered = await repo.filter_by(states=[CampaignState.DRAFT, CampaignState.ACTIVE])
        
        # Assert
        assert len(filtered) == 4  # Should get campaigns in DRAFT and ACTIVE state
        states_found = {c.state for c in filtered}
        assert states_found == {CampaignState.DRAFT, CampaignState.ACTIVE}

    async def test_filter_by_date_range(self, test_db: AsyncSession, campaign_batch_data):
        """Test filtering campaigns by creation date range."""
        # Arrange
        repo = CampaignRepository(test_db)
        campaigns = [Campaign(**data) for data in campaign_batch_data[:5]]
        created = await repo.batch_create(campaigns)
        
        # Get timestamp range
        min_date = min(c.created_at for c in created)
        max_date = max(c.created_at for c in created)
        
        # Act
        filtered = await repo.filter_by_date_range(
            start_date=min_date,
            end_date=max_date
        )
        
        # Assert
        assert len(filtered) == 5
        for campaign in filtered:
            assert min_date <= campaign.created_at <= max_date

    async def test_complex_filter_combination(self, test_db: AsyncSession, campaign_batch_data):
        """Test combining multiple filter conditions."""
        # Arrange
        repo = CampaignRepository(test_db)
        campaigns = [Campaign(**data) for data in campaign_batch_data[:8]]
        
        # Set up test conditions
        for i, campaign in enumerate(campaigns):
            campaign.state = CampaignState.ACTIVE if i < 4 else CampaignState.DRAFT
            campaign.campaign_type = (
                CampaignType.TRADITIONAL if i % 2 == 0
                else CampaignType.ANTITHETICON
            )
        created = await repo.batch_create(campaigns)
        
        # Act
        filtered = await repo.filter_by(
            states=[CampaignState.ACTIVE],
            campaign_types=[CampaignType.TRADITIONAL],
            owner_id=UUID("00000000-0000-0000-0000-000000000001")
        )
        
        # Assert
        assert all(c.state == CampaignState.ACTIVE for c in filtered)
        assert all(c.campaign_type == CampaignType.TRADITIONAL for c in filtered)
        assert all(c.owner_id == UUID("00000000-0000-0000-0000-000000000001") for c in filtered)
