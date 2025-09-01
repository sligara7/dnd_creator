"""Tests for core character creation functionality."""
import pytest
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.models.character import Character
from character_service.services.character import CharacterService
from tests.factories.character import create_character_data


@pytest.mark.asyncio
async def test_create_basic_character(db_session: AsyncSession):
    """Test creation of a basic character."""
    # Arrange
    character_service = CharacterService(db_session)
    character_data = create_character_data()

    # Act
    character = await character_service.create_character(character_data)

    # Assert
    assert character is not None
    assert character.name == character_data["name"]
    assert character.species == character_data["species"]
    assert character.character_classes == character_data["character_classes"]
    assert character.background == character_data["background"]
    assert character.level == character_data["level"]


@pytest.mark.asyncio
async def test_create_character_with_custom_ability_scores(db_session: AsyncSession):
    """Test character creation with custom ability scores."""
    # Arrange
    character_service = CharacterService(db_session)
    custom_scores = {
        "strength": 16,
        "dexterity": 15,
        "constitution": 14,
        "intelligence": 13,
        "wisdom": 12,
        "charisma": 10
    }
    character_data = create_character_data(ability_scores=custom_scores)

    # Act
    character = await character_service.create_character(character_data)

    # Assert
    assert character.ability_scores == custom_scores
    # Test ability modifiers are calculated correctly
    assert character.get_ability_modifier("strength") == 3  # 16 -> +3
    assert character.get_ability_modifier("charisma") == 0  # 10 -> +0


@pytest.mark.asyncio
async def test_create_spellcaster_character(db_session: AsyncSession):
    """Test creation of a spellcasting character."""
    # Arrange
    character_service = CharacterService(db_session)
    character_data = create_character_data(
        character_class="Wizard",
        ability_scores={
            "intelligence": 16,  # Primary spellcasting ability
            "constitution": 14,
            "dexterity": 13,
            "wisdom": 12,
            "charisma": 10,
            "strength": 8
        }
    )

    # Act
    character = await character_service.create_character(character_data)

    # Assert
    assert character.character_classes == {"Wizard": 1}
    assert character.spell_save_dc == 13  # 8 + 2 (prof) + 3 (Int mod)
    assert character.spellcasting_ability == "intelligence"


@pytest.mark.asyncio
async def test_create_character_with_invalid_data(db_session: AsyncSession):
    """Test character creation with invalid data."""
    # Arrange
    character_service = CharacterService(db_session)
    invalid_data = create_character_data()
    invalid_data["ability_scores"]["strength"] = 25  # Invalid score > 20

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid ability score"):
        await character_service.create_character(invalid_data)


@pytest.mark.asyncio
async def test_create_character_with_racial_bonuses(db_session: AsyncSession):
    """Test character creation with racial ability score bonuses."""
    # Arrange
    character_service = CharacterService(db_session)
    base_scores = {
        "strength": 15,
        "dexterity": 14,
        "constitution": 13,
        "intelligence": 12,
        "wisdom": 10,
        "charisma": 8
    }
    character_data = create_character_data(
        species="Half-Orc",  # Half-Orcs get +2 Str, +1 Con
        ability_scores=base_scores
    )
    character_data["racial_bonuses"] = {
        "strength": 2,
        "constitution": 1
    }

    # Act
    character = await character_service.create_character(character_data)

    # Assert
    assert character.ability_scores["strength"] == 17  # 15 + 2
    assert character.ability_scores["constitution"] == 14  # 13 + 1
    assert character.get_ability_modifier("strength") == 3  # 17 -> +3


@pytest.mark.asyncio
async def test_create_character_hit_points_calculation(db_session: AsyncSession):
    """Test hit points are calculated correctly for new character."""
    # Arrange
    character_service = CharacterService(db_session)
    character_data = create_character_data(
        character_class="Fighter",
        ability_scores={
            "constitution": 16,  # +3 modifier
            "strength": 15,
            "dexterity": 14,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 8
        }
    )

    # Act
    character = await character_service.create_character(character_data)

    # Assert
    # Fighter gets 10 (base) + 3 (Con mod) = 13 HP at level 1
    assert character.hit_points == 13


@pytest.mark.asyncio
async def test_create_character_armor_class_calculation(db_session: AsyncSession):
    """Test armor class is calculated correctly for new character."""
    # Arrange
    character_service = CharacterService(db_session)
    character_data = create_character_data(
        ability_scores={
            "dexterity": 16,  # +3 modifier
            "strength": 15,
            "constitution": 14,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 8
        }
    )

    # Act
    character = await character_service.create_character(character_data)

    # Assert
    # Base AC 10 + Dex modifier 3 = 13
    assert character.armor_class == 13


@pytest.mark.asyncio
async def test_create_character_proficiency_bonus(db_session: AsyncSession):
    """Test proficiency bonus is set correctly based on level."""
    test_cases = [
        (1, 2),  # Level 1: +2
        (4, 2),  # Level 4: +2
        (5, 3),  # Level 5: +3
        (8, 3),  # Level 8: +3
        (9, 4),  # Level 9: +4
    ]

    character_service = CharacterService(db_session)

    for level, expected_bonus in test_cases:
        # Arrange
        character_data = create_character_data(level=level)

        # Act
        character = await character_service.create_character(character_data)

        # Assert
        assert character.proficiency_bonus == expected_bonus, f"Level {level}"


@pytest.mark.asyncio
async def test_create_duplicate_character_names(db_session: AsyncSession):
    """Test creating characters with duplicate names is allowed but flagged."""
    # Arrange
    character_service = CharacterService(db_session)
    name = "Test Character"
    first_character_data = create_character_data(name=name)
    second_character_data = create_character_data(name=name)

    # Act
    first_character = await character_service.create_character(first_character_data)
    second_character = await character_service.create_character(second_character_data)

    # Assert
    assert first_character.name == second_character.name
    assert first_character.id != second_character.id
    # Check warning flag is set
    assert second_character.warnings and "duplicate_name" in second_character.warnings
