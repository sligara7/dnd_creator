"""Integration tests for event and progress functionality."""
from datetime import datetime
import pytest
from uuid import uuid4

from character_service.domain.event import EventImpactService
from character_service.domain.progress import ProgressTrackingService
from character_service.domain.models import Character
from character_service.infrastructure.repositories.character import CharacterRepository
from character_service.infrastructure.repositories.event import (
    CampaignEventRepository, EventImpactRepository)


@pytest.fixture
async def char_repo(db_session) -> CharacterRepository:
    """Create character repository."""
    return CharacterRepository(db_session)


@pytest.fixture
async def event_repo(db_session) -> CampaignEventRepository:
    """Create event repository."""
    return CampaignEventRepository(db_session)


@pytest.fixture
async def impact_repo(db_session) -> EventImpactRepository:
    """Create impact repository."""
    return EventImpactRepository(db_session)


@pytest.fixture
async def event_service(
    char_repo: CharacterRepository,
    event_repo: CampaignEventRepository,
    impact_repo: EventImpactRepository,
) -> EventImpactService:
    """Create event service."""
    return EventImpactService(event_repo, impact_repo, char_repo)


@pytest.fixture
async def progress_service(
    char_repo: CharacterRepository,
    event_repo: CampaignEventRepository,
    impact_repo: EventImpactRepository,
) -> ProgressTrackingService:
    """Create progress service."""
    return ProgressTrackingService(char_repo, event_repo, impact_repo)


@pytest.fixture
async def test_character(char_repo: CharacterRepository) -> Character:
    """Create test character."""
    character = Character.create_new("Test", uuid4(), uuid4())
    character.character_data["hit_points"] = {"current": 20, "maximum": 20}
    character.character_data["ability_scores"] = {
        "strength": 10,
        "dexterity": 10,
        "constitution": 10,
        "intelligence": 10,
        "wisdom": 10,
        "charisma": 10,
    }
    await char_repo.create(character)
    return character


@pytest.mark.asyncio
async def test_combat_event_flow(
    event_service: EventImpactService,
    test_character: Character,
):
    """Test complete combat event flow."""
    # Create combat event
    event = await event_service.create_event(
        character_id=test_character.id,
        event_type="combat",
        event_data={"enemy": "goblin", "damage": 5},
        impact_type="hit_points",
        impact_magnitude=-5,
    )

    assert event.character_id == test_character.id
    assert event.event_type == "combat"
    assert not event.applied

    # Apply event
    impacts = await event_service.apply_event(event.id)
    assert len(impacts) == 1
    assert impacts[0].impact_type == "hit_points"
    assert impacts[0].applied

    # Verify character state
    character = await event_service._char_repo.get(test_character.id)
    assert character.character_data["hit_points"]["current"] == 15

    # Revert event
    reverted = await event_service.revert_event(event.id)
    assert len(reverted) == 1
    assert reverted[0].is_reverted

    # Verify character state restored
    character = await event_service._char_repo.get(test_character.id)
    assert character.character_data["hit_points"]["current"] == 20


@pytest.mark.asyncio
async def test_experience_and_level_up(
    progress_service: ProgressTrackingService,
    test_character: Character,
):
    """Test experience gain and level up flow."""
    # Add experience that should trigger level up
    xp, leveled_up, level_data = await progress_service.add_experience(
        character_id=test_character.id,
        amount=1000,
        source="quest",
        reason="Completed major quest",
    )

    assert xp == 1000
    assert leveled_up
    assert level_data["previous_level"] == 1
    assert level_data["new_level"] == 3

    # Verify character state
    character = await progress_service._char_repo.get(test_character.id)
    assert character.character_data["level"] == 3

    # Add more XP but not enough to level
    xp, leveled_up, level_data = await progress_service.add_experience(
        character_id=test_character.id,
        amount=100,
        source="combat",
        reason="Defeated enemies",
    )

    assert xp == 1100
    assert not leveled_up
    assert level_data is None


@pytest.mark.asyncio
async def test_milestone_and_achievement_tracking(
    progress_service: ProgressTrackingService,
    test_character: Character,
):
    """Test tracking milestones and achievements."""
    # Add milestone
    progress = await progress_service.add_milestone(
        character_id=test_character.id,
        title="First Quest",
        description="Completed first quest",
        milestone_type="quest",
    )

    assert len(progress.milestones) == 1
    milestone = progress.milestones[0]
    assert milestone["title"] == "First Quest"
    assert milestone["type"] == "quest"

    # Add achievement
    progress = await progress_service.add_achievement(
        character_id=test_character.id,
        title="Monster Slayer",
        description="Defeated first monster",
        achievement_type="combat",
    )

    assert len(progress.achievements) == 1
    achievement = progress.achievements[0]
    assert achievement["title"] == "Monster Slayer"
    assert achievement["type"] == "combat"

    # Verify progress state
    progress = await progress_service.get_character_progress(test_character.id)
    assert len(progress.milestones) == 1
    assert len(progress.achievements) == 1


@pytest.mark.asyncio
async def test_multiple_events_with_dependencies(
    event_service: EventImpactService,
    progress_service: ProgressTrackingService,
    test_character: Character,
):
    """Test handling multiple related events."""
    # Create and apply a combat event
    combat_event = await event_service.create_event(
        character_id=test_character.id,
        event_type="combat",
        event_data={"enemy": "dragon", "damage": 10},
        impact_type="hit_points",
        impact_magnitude=-10,
    )
    await event_service.apply_event(combat_event.id)

    # Add experience for the combat
    await progress_service.add_experience(
        character_id=test_character.id,
        amount=500,
        source="combat",
        reason="Defeated dragon",
    )

    # Add milestone and achievement
    await progress_service.add_milestone(
        character_id=test_character.id,
        title="Dragon Slayer",
        description="Defeated first dragon",
        milestone_type="combat",
    )

    await progress_service.add_achievement(
        character_id=test_character.id,
        title="Dragon Slayer",
        description="Defeated first dragon",
        achievement_type="combat",
    )

    # Verify final state
    character = await event_service._char_repo.get(test_character.id)
    progress = await progress_service.get_character_progress(test_character.id)

    assert character.character_data["hit_points"]["current"] == 10
    assert progress.experience_points == 500
    assert len(progress.milestones) == 1
    assert len(progress.achievements) == 1

    # Reverting the combat event should not affect XP or achievements
    await event_service.revert_event(combat_event.id)

    character = await event_service._char_repo.get(test_character.id)
    progress = await progress_service.get_character_progress(test_character.id)

    assert character.character_data["hit_points"]["current"] == 20  # HP restored
    assert progress.experience_points == 500  # XP remains
    assert len(progress.milestones) == 1  # Milestone remains
    assert len(progress.achievements) == 1  # Achievement remains
