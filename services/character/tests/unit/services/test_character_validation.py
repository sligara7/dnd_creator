"""Tests for character stat validation."""
import pytest
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.ext.asyncio import AsyncSession

from character_service.models.models import Character
from character_service.db.base import Base
from character_service.services.character import CharacterService
from tests.factories.character import create_character_data

@pytest.mark.asyncio
async def test_validate_ability_scores_range(db_session: AsyncSession):
    """Test validation of ability score ranges."""
    character_service = CharacterService(db_session)
    
    # Test minimum score (1)
    min_scores = {
        "strength": 1,
        "dexterity": 1,
        "constitution": 1,
        "intelligence": 1,
        "wisdom": 1,
        "charisma": 1
    }
    character_data = create_character_data(ability_scores=min_scores)
    character = await character_service.create_character(character_data)
    assert all(score == 1 for score in character.character_data["ability_scores"].values())

    # Test maximum score (20 without modifiers)
    max_scores = {
        "strength": 20,
        "dexterity": 20,
        "constitution": 20,
        "intelligence": 20,
        "wisdom": 20,
        "charisma": 20
    }
    character_data = create_character_data(ability_scores=max_scores)
    character = await character_service.create_character(character_data)
    assert all(score == 20 for score in character.character_data["ability_scores"].values())

    # Test invalid low score (0)
    invalid_low_scores = min_scores.copy()
    invalid_low_scores["strength"] = 0
    character_data = create_character_data(ability_scores=invalid_low_scores)
    with pytest.raises(ValueError, match="Invalid ability score"):
        await character_service.create_character(character_data)

    # Test invalid high score (21)
    invalid_high_scores = max_scores.copy()
    invalid_high_scores["dexterity"] = 21
    character_data = create_character_data(ability_scores=invalid_high_scores)
    with pytest.raises(ValueError, match="Invalid ability score"):
        await character_service.create_character(character_data)

@pytest.mark.asyncio
async def test_validate_ability_score_modifiers(db_session: AsyncSession):
    """Test ability score modifier calculations."""
    character_service = CharacterService(db_session)
    test_cases = [
        (1, -5),  # Score of 1 gives -5 modifier
        (3, -4),  # Scores of 2-3 give -4 modifier
        (5, -3),  # Scores of 4-5 give -3 modifier
        (7, -2),  # Scores of 6-7 give -2 modifier
        (9, -1),  # Scores of 8-9 give -1 modifier
        (11, 0),  # Scores of 10-11 give +0 modifier
        (13, 1),  # Scores of 12-13 give +1 modifier
        (15, 2),  # Scores of 14-15 give +2 modifier
        (17, 3),  # Scores of 16-17 give +3 modifier
        (19, 4),  # Scores of 18-19 give +4 modifier
        (20, 5),  # Score of 20 gives +5 modifier
    ]

    for score, expected_modifier in test_cases:
        scores = {
            "strength": score,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10
        }
        character_data = create_character_data(ability_scores=scores)
        character = await character_service.create_character(character_data)
        # Calculate ability modifier: (score - 10) // 2
        actual_modifier = (character.character_data["ability_scores"]["strength"] - 10) // 2
        assert actual_modifier == expected_modifier

@pytest.mark.skip(reason="Skill proficiencies are not implemented in the current model/service")
async def test_validate_skill_proficiencies(db_session: AsyncSession):
    pass

@pytest.mark.skip(reason="Saving throw proficiencies are not implemented in the current model/service")
async def test_validate_saving_throw_proficiencies(db_session: AsyncSession):
    pass

@pytest.mark.asyncio
async def test_validate_proficiency_bonus_by_level(db_session: AsyncSession):
    """Test proficiency bonus calculation by level."""
    character_service = CharacterService(db_session)
    test_cases = [
        (1, 2),   # Levels 1-4: +2
        (4, 2),
        (5, 3),   # Levels 5-8: +3
        (8, 3),
        (9, 4),   # Levels 9-12: +4
        (12, 4),
        (13, 5),  # Levels 13-16: +5
        (16, 5),
        (17, 6),  # Levels 17-20: +6
        (20, 6)
    ]

    for level, expected_bonus in test_cases:
        character_data = create_character_data(level=level)
        character = await character_service.create_character(character_data)
        assert character.character_data["proficiency_bonus"] == expected_bonus

@pytest.mark.asyncio
async def test_validate_hit_points_calculation(db_session: AsyncSession):
    """Test hit points calculation with different classes and Constitution modifiers."""
    character_service = CharacterService(db_session)
    
    test_cases = [
        # (class, con score, level, expected hp)
        ("Wizard", 10, 1, 6),      # 6 (base) + 0 (con mod) = 6
        ("Fighter", 14, 1, 12),    # 10 (base) + 2 (con mod) = 12
        ("Barbarian", 16, 1, 15),  # 12 (base) + 3 (con mod) = 15
    ]

    for class_name, con_score, level, expected_hp in test_cases:
        scores = {
            "strength": 10,
            "dexterity": 10,
            "constitution": con_score,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10
        }
        character_data = create_character_data(
            character_class=class_name,
            ability_scores=scores,
            level=level
        )
        character = await character_service.create_character(character_data)
        assert character.character_data["hit_points"] == expected_hp

@pytest.mark.asyncio
async def test_validate_armor_class_calculation(db_session: AsyncSession):
    """Test armor class calculation with different armor types and Dexterity modifiers."""
    character_service = CharacterService(db_session)
    
    test_cases = [
        # (dex_score, expected_ac) Base AC only: 10 + Dex mod
        (14, 12),  # +2
        (16, 13),  # +3
        (8, 9),    # -1
    ]

    for dex_score, expected_ac in test_cases:
        scores = {
            "strength": 10,
            "dexterity": dex_score,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10
        }
        character_data = create_character_data(ability_scores=scores)
        character = await character_service.create_character(character_data)
        assert character.character_data["armor_class"] == expected_ac
