"""Test cases for campaign model and operations."""
import pytest
from datetime import datetime
from datetime import datetime, timedelta
from uuid import UUID

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from campaign_service.models.campaign import Campaign, CampaignType, CampaignState

@pytest.mark.asyncio
async def test_create_campaign(test_db: AsyncSession) -> None:
    """Test creating a new campaign."""
    # Create a new campaign
    campaign = Campaign(
        name="Test Campaign",
        description="A test campaign for unit testing",
        campaign_type=CampaignType.TRADITIONAL,
        state=CampaignState.DRAFT,
        theme_data={},
        campaign_metadata={},
        creator_id=UUID("00000000-0000-0000-0000-000000000001"),
        owner_id=UUID("00000000-0000-0000-0000-000000000001"),
    )
    
    # Add to database
    test_db.add(campaign)
    await test_db.flush()
    
    # Verify the campaign was created
    assert campaign.id is not None
    assert isinstance(campaign.id, UUID)
    assert campaign.name == "Test Campaign"
    assert campaign.campaign_type == CampaignType.TRADITIONAL
    assert campaign.state == CampaignState.DRAFT
    assert campaign.created_at is not None
    assert isinstance(campaign.created_at, datetime)
    assert campaign.updated_at is not None
    assert isinstance(campaign.updated_at, datetime)
    assert not campaign.is_deleted
    assert campaign.deleted_at is None
    
    # Verify we can retrieve it from the database
    result = await test_db.execute(
        select(Campaign).where(Campaign.id == campaign.id)
    )
    retrieved_campaign = result.scalar_one()
    
    assert retrieved_campaign.id == campaign.id
    assert retrieved_campaign.name == "Test Campaign"
    assert retrieved_campaign.description == "A test campaign for unit testing"
    assert retrieved_campaign.campaign_type == CampaignType.TRADITIONAL
    assert retrieved_campaign.state == CampaignState.DRAFT
    assert retrieved_campaign.theme_data == {}
    assert retrieved_campaign.campaign_metadata == {}
    assert retrieved_campaign.creator_id == UUID("00000000-0000-0000-0000-000000000001")
    assert retrieved_campaign.owner_id == UUID("00000000-0000-0000-0000-000000000001")
    assert not retrieved_campaign.is_deleted
    assert retrieved_campaign.deleted_at is None

@pytest.mark.asyncio
async def test_update_campaign(test_db: AsyncSession) -> None:
    """Test updating a campaign."""
    # Create a test campaign
    campaign = Campaign(
        name="Initial Name",
        description="Initial description",
        campaign_type=CampaignType.TRADITIONAL,
        state=CampaignState.DRAFT,
        theme_data={},
        campaign_metadata={},
        creator_id=UUID("00000000-0000-0000-0000-000000000001"),
        owner_id=UUID("00000000-0000-0000-0000-000000000001"),
    )
    test_db.add(campaign)
    await test_db.flush()
    
    # Store original timestamps
    original_created_at = campaign.created_at
    original_updated_at = campaign.updated_at
    
    # Wait a bit to ensure updated_at will be different
    await test_db.execute(text("SELECT pg_sleep(0.1)"))
    
    # Update the campaign
    campaign.name = "Updated Name"
    campaign.description = "Updated description"
    campaign.state = CampaignState.ACTIVE
    campaign.theme_data = {"primary": "High Fantasy"}
    await test_db.flush()
    
    # Fetch the campaign from the database
    result = await test_db.execute(
        select(Campaign).where(Campaign.id == campaign.id)
    )
    updated_campaign = result.scalar_one()
    
    # Verify the updates
    assert updated_campaign.name == "Updated Name"
    assert updated_campaign.description == "Updated description"
    assert updated_campaign.state == CampaignState.ACTIVE
    assert updated_campaign.theme_data == {"primary": "High Fantasy"}
    
    # Verify timestamps
    assert updated_campaign.created_at == original_created_at
    assert updated_campaign.updated_at > original_updated_at
    
    # Verify unchanged fields
    assert updated_campaign.campaign_type == CampaignType.TRADITIONAL
    assert updated_campaign.creator_id == UUID("00000000-0000-0000-0000-000000000001")
    assert updated_campaign.owner_id == UUID("00000000-0000-0000-0000-000000000001")
    assert not updated_campaign.is_deleted
    assert updated_campaign.deleted_at is None

@pytest.mark.asyncio
async def test_cannot_update_campaign_without_name(test_db: AsyncSession) -> None:
    """Test that a campaign cannot be updated to have no name."""
    # Create a test campaign
    campaign = Campaign(
        name="Test Campaign",
        description="Test description",
        campaign_type=CampaignType.TRADITIONAL,
        state=CampaignState.DRAFT,
        theme_data={},
        campaign_metadata={},
        creator_id=UUID("00000000-0000-0000-0000-000000000001"),
        owner_id=UUID("00000000-0000-0000-0000-000000000001"),
    )
    test_db.add(campaign)
    await test_db.flush()
    
    # Try to update the name to None inside a savepoint
    sp = await test_db.begin_nested()
    campaign.name = None

    # This should raise an IntegrityError within the savepoint
    with pytest.raises(IntegrityError):
        await test_db.flush()

    # Roll back to savepoint to restore previous valid state
    await sp.rollback()

    # Reset to valid name and ensure we can flush again
    campaign.name = "Test Campaign"
    await test_db.flush()

    # Verify in DB
    result = await test_db.execute(
        select(Campaign).where(Campaign.id == campaign.id)
    )
    campaign = result.scalar_one()
    assert campaign.name == "Test Campaign"

@pytest.mark.asyncio
    async def test_update_campaign_state_transition(test_db: AsyncSession) -> None:
        """Test valid campaign state transitions.
    
        Additional tests needed:
        1. Theme application and consistency:
           - Theme inheritance to chapters/NPCs/locations
           - Theme change validation and propagation
           - Theme conflict resolution
           - Theme versioning support
        
        2. Content generation validation:
           - Campaign factory edge cases
           - Chapter generation constraints
           - NPC/location coherence
           - Content reuse patterns
        
        3. Plot branching logic:
           - Branch creation and validation
           - State tracking per branch
           - Branch merging logic
           - Choice tracking system
        
        4. Chapter state transitions:
           - Valid/invalid transitions
           - Dependency validation
           - Resource locking
           - Concurrent modifications
        
        5. Event handling and integration:
           - Message Hub integration
           - Event validation and processing
           - Service communication patterns
           - Event replay and recovery
        """
    # Create a test campaign in DRAFT state
    campaign = Campaign(
        name="Test Campaign",
        description="Test description",
        campaign_type=CampaignType.TRADITIONAL,
        state=CampaignState.DRAFT,  # Start in DRAFT
        theme_data={},
        campaign_metadata={},
        creator_id=UUID("00000000-0000-0000-0000-000000000001"),
        owner_id=UUID("00000000-0000-0000-0000-000000000001"),
    )
    test_db.add(campaign)
    await test_db.flush()
    
    # Valid state transitions
    valid_transitions = [
        CampaignState.ACTIVE,     # DRAFT -> ACTIVE
        CampaignState.PAUSED,     # ACTIVE -> PAUSED
        CampaignState.ACTIVE,     # PAUSED -> ACTIVE
        CampaignState.COMPLETED,  # ACTIVE -> COMPLETED
    ]
    
    for new_state in valid_transitions:
        campaign.state = new_state
        await test_db.flush()
        
        # Verify the state changed
        result = await test_db.execute(
            select(Campaign).where(Campaign.id == campaign.id)
        )
        updated_campaign = result.scalar_one()
        assert updated_campaign.state == new_state
