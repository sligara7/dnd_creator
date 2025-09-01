"""Tests for character progression system."""
import pytest
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.services.character import CharacterService
from tests.factories.character import create_character_data


@pytest.mark.asyncio
async def test_level_up_single_class(db_session: AsyncSession):
    """Test single-class character level up."""
    character_service = CharacterService(db_session)

    # Create a level 1 character
    character_data = create_character_data(character_class="Fighter", level=1)
    character = await character_service.create_character(character_data)

    # Test level up changes
    level_up_data = {
        "level": 2,
        "character_classes": {"Fighter": 2},
        "hp_roll": 6  # Rolled a 6 on the d10
    }

    await character_service.level_up(character.id, level_up_data)
    updated_character = await character_service.get_character(character.id)

    # Verify level up changes
    assert updated_character.level == 2
    assert updated_character.character_classes["Fighter"] == 2
    assert updated_character.hit_points == 18  # Base 10 + Con mod(1) + Rolled(6) + Con mod(1)


@pytest.mark.asyncio
async def test_level_up_multiclass(db_session: AsyncSession):
    """Test multiclass character level up."""
    character_service = CharacterService(db_session)

    # Create a level 2 Fighter
    character_data = create_character_data(
        character_class="Fighter",
        level=2,
        ability_scores={
            "strength": 15,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 12,
            "wisdom": 13,  # Meets Cleric requirement
            "charisma": 10
        }
    )
    character = await character_service.create_character(character_data)

    # Test multiclass level up to Cleric
    level_up_data = {
        "level": 3,
        "character_classes": {
            "Fighter": 2,
            "Cleric": 1
        },
        "hp_roll": 4  # Rolled a 4 on Cleric's d8
    }

    await character_service.level_up(character.id, level_up_data)
    updated_character = await character_service.get_character(character.id)

    # Verify multiclass changes
    assert updated_character.level == 3
    assert updated_character.character_classes == {"Fighter": 2, "Cleric": 1}
    # Fighter HP: Base 10 + Con mod(1) + Level 2 roll(assumed 6) + Con mod(1)
    # Cleric HP: Level 3 roll(4) + Con mod(1)
    assert updated_character.hit_points == 23  
    assert updated_character.spellcasting_ability == "wisdom"


@pytest.mark.asyncio
async def test_level_up_invalid_multiclass(db_session: AsyncSession):
    """Test invalid multiclass attempt (not meeting requirements)."""
    character_service = CharacterService(db_session)

    # Create a level 2 Fighter with low Wisdom
    character_data = create_character_data(
        character_class="Fighter",
        level=2,
        ability_scores={
            "strength": 15,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 12,
            "wisdom": 11,  # Too low for Cleric
            "charisma": 10
        }
    )
    character = await character_service.create_character(character_data)

    # Attempt invalid multiclass
    level_up_data = {
        "level": 3,
        "character_classes": {
            "Fighter": 2,
            "Cleric": 1
        },
        "hp_roll": 4
    }

    with pytest.raises(ValueError, match="Does not meet requirements for Cleric multiclass"):
        await character_service.level_up(character.id, level_up_data)


@pytest.mark.asyncio
async def test_level_up_invalid_level_skip(db_session: AsyncSession):
    """Test invalid level up attempt (skipping levels)."""
    character_service = CharacterService(db_session)

    # Create a level 1 character
    character_data = create_character_data(character_class="Fighter", level=1)
    character = await character_service.create_character(character_data)

    # Attempt to skip to level 3
    level_up_data = {
        "level": 3,
        "character_classes": {"Fighter": 3},
        "hp_roll": 6
    }

    with pytest.raises(ValueError, match="Cannot skip levels"):
        await character_service.level_up(character.id, level_up_data)


@pytest.mark.asyncio
async def test_level_up_spellcasting(db_session: AsyncSession):
    """Test spellcasting features gained from level up."""
    character_service = CharacterService(db_session)

    # Create a level 1 Wizard
    character_data = create_character_data(
        character_class="Wizard",
        level=1,
        ability_scores={
            "strength": 10,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 16,  # High Int for spellcasting
            "wisdom": 13,
            "charisma": 8
        }
    )
    character = await character_service.create_character(character_data)
    
    assert character.spellcasting_ability == "intelligence"
    assert character.spell_save_dc == 13  # 8 + prof(2) + int mod(3)

    # Level up to 2
    level_up_data = {
        "level": 2,
        "character_classes": {"Wizard": 2},
        "hp_roll": 4,
        "spells_added": ["Magic Missile", "Shield"]
    }

    await character_service.level_up(character.id, level_up_data)
    updated_character = await character_service.get_character(character.id)

    # Verify spellcasting progression
    assert "Magic Missile" in updated_character.spells_known
    assert "Shield" in updated_character.spells_known
    assert updated_character.spell_save_dc == 13  # Same at level 2
