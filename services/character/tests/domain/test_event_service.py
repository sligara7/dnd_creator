"""Tests for event and progress services."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from character_service.core.exceptions import (CharacterNotFoundError,
                                          EventApplicationError,
                                          EventNotFoundError)
from character_service.domain.event import EventImpactService
from character_service.domain.progress import ProgressTrackingService
from character_service.domain.models import Character, CampaignEvent, EventImpact


@pytest.fixture
def event_repo():
    """Mock event repository."""
    return AsyncMock()


@pytest.fixture
def impact_repo():
    """Mock impact repository."""
    return AsyncMock()


@pytest.fixture
def char_repo():
    """Mock character repository."""
    return AsyncMock()


@pytest.fixture
def event_service(event_repo, impact_repo, char_repo):
    """Event service with mocked dependencies."""
    return EventImpactService(event_repo, impact_repo, char_repo)


@pytest.fixture
def progress_service(char_repo, event_repo, impact_repo):
    """Progress service with mocked dependencies."""
    return ProgressTrackingService(char_repo, event_repo, impact_repo)


@pytest.mark.asyncio
async def test_create_event(event_service, char_repo):
    """Test creating a campaign event."""
    character_id = uuid4()
    character = Character.create_new("Test", uuid4(), uuid4())
    character.id = character_id

    char_repo.get.return_value = character

    event = await event_service.create_event(
        character_id=character_id,
        event_type="combat",
        event_data={"enemy": "goblin"},
        impact_type="hit_points",
        impact_magnitude=-5,
    )

    assert event.character_id == character_id
    assert event.event_type == "combat"
    assert event.impact_type == "hit_points"
    assert event.impact_magnitude == -5
    assert event.applied is False


@pytest.mark.asyncio
async def test_create_event_character_not_found(event_service, char_repo):
    """Test creating event for non-existent character."""
    char_repo.get.return_value = None

    with pytest.raises(CharacterNotFoundError):
        await event_service.create_event(
            character_id=uuid4(),
            event_type="combat",
            event_data={},
            impact_type="hit_points",
            impact_magnitude=0,
        )


@pytest.mark.asyncio
async def test_apply_event(event_service, event_repo, char_repo):
    """Test applying a campaign event."""
    character_id = uuid4()
    event_id = uuid4()

    # Setup character
    character = Character.create_new("Test", uuid4(), uuid4())
    character.id = character_id
    character.character_data["hit_points"] = {"current": 20, "maximum": 20}

    # Setup event
    event = CampaignEvent(
        id=event_id,
        character_id=character_id,
        event_type="combat",
        event_data={"enemy": "goblin"},
        impact_type="hit_points",
        impact_magnitude=-5,
        timestamp=datetime.utcnow(),
    )

    event_repo.get.return_value = event
    char_repo.get.return_value = character

    impacts = await event_service.apply_event(event_id)

    assert len(impacts) == 1
    assert impacts[0].event_id == event_id
    assert impacts[0].character_id == character_id
    assert impacts[0].impact_type == "hit_points"
    assert character.character_data["hit_points"]["current"] == 15


@pytest.mark.asyncio
async def test_add_experience(progress_service, char_repo):
    """Test adding experience points."""
    character_id = uuid4()
    character = Character.create_new("Test", uuid4(), uuid4())
    character.id = character_id
    character.character_data["experience_points"] = 0
    character.character_data["level"] = 1

    char_repo.get.return_value = character

    xp, leveled_up, level_data = await progress_service.add_experience(
        character_id=character_id,
        amount=1000,
        source="quest",
        reason="Completed quest",
    )

    assert xp == 1000
    assert leveled_up is True
    assert level_data["previous_level"] == 1
    assert level_data["new_level"] == 3  # 1000 XP should reach level 3
    assert character.character_data["level"] == 3


@pytest.mark.asyncio
async def test_add_milestone(progress_service, char_repo):
    """Test adding a milestone."""
    character_id = uuid4()
    character = Character.create_new("Test", uuid4(), uuid4())
    character.id = character_id

    char_repo.get.return_value = character

    progress = await progress_service.add_milestone(
        character_id=character_id,
        title="First Quest",
        description="Completed first quest",
        milestone_type="quest",
    )

    assert len(progress.milestones) == 1
    assert progress.milestones[0]["title"] == "First Quest"
    assert progress.milestones[0]["type"] == "quest"


@pytest.mark.asyncio
async def test_add_achievement(progress_service, char_repo):
    """Test adding an achievement."""
    character_id = uuid4()
    character = Character.create_new("Test", uuid4(), uuid4())
    character.id = character_id

    char_repo.get.return_value = character

    progress = await progress_service.add_achievement(
        character_id=character_id,
        title="Monster Slayer",
        description="Defeated first monster",
        achievement_type="combat",
    )

    assert len(progress.achievements) == 1
    assert progress.achievements[0]["title"] == "Monster Slayer"
    assert progress.achievements[0]["type"] == "combat"


@pytest.mark.asyncio
async def test_duplicate_achievement(progress_service, char_repo):
    """Test adding duplicate achievement."""
    character_id = uuid4()
    character = Character.create_new("Test", uuid4(), uuid4())
    character.id = character_id

    char_repo.get.return_value = character

    await progress_service.add_achievement(
        character_id=character_id,
        title="Monster Slayer",
        description="Defeated first monster",
        achievement_type="combat",
    )

    with pytest.raises(ValidationError):
        await progress_service.add_achievement(
            character_id=character_id,
            title="Monster Slayer",  # Same title
            description="Different description",
            achievement_type="combat",
        )
