"""Tests for campaign event models."""
import pytest
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.infrastructure.models.models import CampaignEvent, EventImpact, CharacterProgress
from character_service.domain.models import Character


@pytest.mark.asyncio
async def test_create_campaign_event(db_session: AsyncSession):
    """Test creating a campaign event."""
    # Create test data
    event = CampaignEvent(
        id=uuid4(),
        character_id=uuid4(),
        event_type="combat",
        event_data={"enemy": "goblin", "damage": 5},
        impact_type="hit_points",
        impact_magnitude=-5,
        timestamp=datetime.utcnow(),
    )

    # Save to database
    db_session.add(event)
    await db_session.commit()

    # Query and verify
    result = await db_session.execute(
        select(CampaignEvent).where(CampaignEvent.id == event.id)
    )
    saved_event = result.scalar_one()

    assert saved_event.event_type == "combat"
    assert saved_event.event_data["enemy"] == "goblin"
    assert saved_event.impact_type == "hit_points"
    assert saved_event.impact_magnitude == -5
    assert saved_event.is_deleted is False


@pytest.mark.asyncio
async def test_create_event_impact(db_session: AsyncSession):
    """Test creating an event impact."""
    # Create test data
    event = CampaignEvent(
        id=uuid4(),
        character_id=uuid4(),
        event_type="experience",
        event_data={"source": "quest"},
        impact_type="experience",
        impact_magnitude=100,
        timestamp=datetime.utcnow(),
    )
    db_session.add(event)
    await db_session.commit()

    impact = EventImpact(
        id=uuid4(),
        event_id=event.id,
        character_id=event.character_id,
        impact_type="experience",
        impact_data={"amount": 100},
    )

    # Save to database
    db_session.add(impact)
    await db_session.commit()

    # Query and verify
    result = await db_session.execute(
        select(EventImpact).where(EventImpact.id == impact.id)
    )
    saved_impact = result.scalar_one()

    assert saved_impact.impact_type == "experience"
    assert saved_impact.impact_data["amount"] == 100
    assert saved_impact.applied is False
    assert saved_impact.is_reverted is False


@pytest.mark.asyncio
async def test_create_character_progress(db_session: AsyncSession):
    """Test creating character progress."""
    # Create test data
    progress = CharacterProgress(
        id=uuid4(),
        character_id=uuid4(),
        experience_points=1000,
        current_level=3,
        previous_level=2,
        level_updated_at=datetime.utcnow(),
        milestones=[
            {
                "id": str(uuid4()),
                "title": "First Quest",
                "description": "Completed first quest",
                "type": "quest",
                "achieved_at": datetime.utcnow().isoformat(),
            }
        ],
        achievements=[
            {
                "id": str(uuid4()),
                "title": "Monster Slayer",
                "description": "Defeated first monster",
                "type": "combat",
                "achieved_at": datetime.utcnow().isoformat(),
            }
        ],
    )

    # Save to database
    db_session.add(progress)
    await db_session.commit()

    # Query and verify
    result = await db_session.execute(
        select(CharacterProgress).where(CharacterProgress.id == progress.id)
    )
    saved_progress = result.scalar_one()

    assert saved_progress.experience_points == 1000
    assert saved_progress.current_level == 3
    assert saved_progress.previous_level == 2
    assert len(saved_progress.milestones) == 1
    assert saved_progress.milestones[0]["title"] == "First Quest"
    assert len(saved_progress.achievements) == 1
    assert saved_progress.achievements[0]["title"] == "Monster Slayer"


@pytest.mark.asyncio
async def test_event_relationships(db_session: AsyncSession):
    """Test relationships between events and impacts."""
    # Create test data
    character_id = uuid4()
    event = CampaignEvent(
        id=uuid4(),
        character_id=character_id,
        event_type="combat",
        event_data={"enemy": "dragon"},
        impact_type="hit_points",
        impact_magnitude=-10,
        timestamp=datetime.utcnow(),
    )
    db_session.add(event)
    await db_session.commit()

    impact1 = EventImpact(
        id=uuid4(),
        event_id=event.id,
        character_id=character_id,
        impact_type="hit_points",
        impact_data={"amount": -10},
    )
    impact2 = EventImpact(
        id=uuid4(),
        event_id=event.id,
        character_id=character_id,
        impact_type="status",
        impact_data={"condition": "frightened"},
    )
    db_session.add_all([impact1, impact2])
    await db_session.commit()

    # Query and verify
    result = await db_session.execute(
        select(CampaignEvent).where(CampaignEvent.id == event.id)
    )
    saved_event = result.scalar_one()

    assert len(saved_event.impacts) == 2
    assert any(i.impact_type == "hit_points" for i in saved_event.impacts)
    assert any(i.impact_type == "status" for i in saved_event.impacts)


@pytest.mark.asyncio
async def test_soft_delete(db_session: AsyncSession):
    """Test soft delete functionality."""
    # Create test data
    event = CampaignEvent(
        id=uuid4(),
        character_id=uuid4(),
        event_type="rest",
        event_data={"type": "long"},
        impact_type="hit_points",
        impact_magnitude=10,
        timestamp=datetime.utcnow(),
    )
    db_session.add(event)
    await db_session.commit()

    # Soft delete
    event.is_deleted = True
    event.deleted_at = datetime.utcnow()
    await db_session.commit()

    # Query and verify
    result = await db_session.execute(
        select(CampaignEvent).where(CampaignEvent.id == event.id)
    )
    saved_event = result.scalar_one()

    assert saved_event.is_deleted is True
    assert saved_event.deleted_at is not None
