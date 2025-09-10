"""Tests for character service validation."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.models.character import Character
from character_service.models.features import Feature, FeatureType, ResourceType
from character_service.repositories.character import CharacterRepository
from character_service.services.character import (
    CharacterCreationError,
    CharacterService,
    CharacterValidationError
)
from tests.service.utils import create_test_ability_scores


@pytest.mark.asyncio
async def test_validate_combat_stats(db_session: AsyncSession):
    """Test validation of combat-related statistics."""
    # Arrange
    repo = CharacterRepository(db_session)
    service = CharacterService(repo)
    character = await service.create_character(
        name="Combat Stats",
        ability_scores=create_test_ability_scores(),
        race="Human",
        character_class="Fighter",
        background="Soldier"
    )
    
    # Test: invalid max HP
    character.max_hit_points = 0
    with pytest.raises(CharacterValidationError, match="Maximum hit points"):
        service.validate_combat_stats(character)
    
    # Test: current HP exceeds max + temp
    character.max_hit_points = 10
    character.current_hit_points = 15
    character.temporary_hit_points = 2
    with pytest.raises(CharacterValidationError, match="Current HP cannot exceed"):
        service.validate_combat_stats(character)
    
    # Test: negative temp HP (set current within bounds to isolate temp HP validation)
    character.current_hit_points = 5
    character.temporary_hit_points = -1
    with pytest.raises(CharacterValidationError, match="Temporary HP cannot be negative"):
        service.validate_combat_stats(character)


@pytest.mark.asyncio
async def test_validate_resource_usage(db_session: AsyncSession):
    """Test validation of feature resource usage."""
    # Arrange
    repo = CharacterRepository(db_session)
    service = CharacterService(repo)
    character = await service.create_character(
        name="Resource Usage",
        ability_scores=create_test_ability_scores(),
        race="Human",
        character_class="Fighter",
        background="Soldier"
    )
    await service.add_class_features(character.id, 1)  # Add Fighter level 1 features
    
    # Test: missing uses_remaining for limited-use feature
    second_wind = next(f for f in character.features if f.name == "Second Wind")
    second_wind.uses_remaining = None
    with pytest.raises(CharacterValidationError, match="must track remaining uses"):
        service.validate_resource_usage(character)
    
    # Test: negative uses
    second_wind.uses_remaining = -1
    with pytest.raises(CharacterValidationError, match="cannot have negative uses"):
        service.validate_resource_usage(character)
    
    # Test: exceeds max uses
    second_wind.uses_max = 1
    second_wind.uses_remaining = 2
    with pytest.raises(CharacterValidationError, match="cannot exceed maximum uses"):
        service.validate_resource_usage(character)


@pytest.mark.asyncio
async def test_validate_character_state(db_session: AsyncSession):
    """Test validation of overall character state."""
    # Arrange
    repo = CharacterRepository(db_session)
    service = CharacterService(repo)
    character = await service.create_character(
        name="State Test",
        ability_scores=create_test_ability_scores(),
        race="Human",
        character_class="Fighter",
        background="Soldier",
        level=3
    )
    
    # Test: missing name
    character.name = ""
    with pytest.raises(CharacterValidationError, match="name is required"):
        service.validate_character_state(character)
    character.name = "State Test"
    
    # Test: invalid level
    character.level = 0
    with pytest.raises(CharacterValidationError, match="Level must be between"):
        service.validate_character_state(character)
    character.level = 3
    
    # Test: multiclass level mismatch
    character.classes = [
        {"class": "Fighter", "level": 2},  # Total 2 != character level 3
    ]
    with pytest.raises(CharacterValidationError, match="Sum of class levels"):
        service.validate_character_state(character)


@pytest.mark.asyncio
async def test_input_data_validation(db_session: AsyncSession):
    """Test validation of input data formats and constraints."""
    # Arrange
    repo = CharacterRepository(db_session)
    service = CharacterService(repo)
    ability_scores = create_test_ability_scores()
    
    # Test: empty name
    with pytest.raises(CharacterCreationError, match="name is required"):
        await service.create_character(
            name="",
            ability_scores=ability_scores,
            race="Human",
            character_class="Fighter",
            background="Soldier"
        )
    
    # Test: invalid character class
    with pytest.raises(CharacterValidationError, match="Invalid character class"):
        await service.create_character(
            name="Invalid Class",
            ability_scores=ability_scores,
            race="Human",
            character_class="InvalidClass",
            background="Soldier"
        )
    
    # Test: invalid level
    with pytest.raises(CharacterCreationError, match="Level must be between"):
        await service.create_character(
            name="Invalid Level",
            ability_scores=ability_scores,
            race="Human",
            character_class="Fighter",
            background="Soldier",
            level=21  # Above max level
        )


@pytest.mark.asyncio
async def test_error_message_clarity(db_session: AsyncSession):
    """Test that validation errors provide clear, actionable messages."""
    # Arrange
    repo = CharacterRepository(db_session)
    service = CharacterService(repo)
    character = await service.create_character(
        name="Error Messages",
        ability_scores=create_test_ability_scores(),
        race="Human",
        character_class="Fighter",
        background="Soldier"
    )
    
    # Test: HP error message includes current and max values
    character.current_hit_points = 15
    character.max_hit_points = 10
    try:
        service.validate_combat_stats(character)
        pytest.fail("Expected validation error")
    except CharacterValidationError as e:
        assert "Current HP" in str(e)
        assert "max HP" in str(e)
    
    # Test: resource usage error includes feature name
    # Ensure features are present and use returned features to avoid lazy load
    features = await service.add_class_features(character.id, 1)
    feature = next(f for f in features if f.name == "Second Wind")
    feature.uses_remaining = 2
    feature.uses_max = 1
    try:
        service.validate_resource_usage(character)
        pytest.fail("Expected validation error")
    except CharacterValidationError as e:
        assert feature.name in str(e)
        assert "maximum uses" in str(e)
