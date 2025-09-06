"""Tests for D&D 5e (2024) validation rules."""
import pytest
from datetime import datetime
from uuid import uuid4

from character_service.core.validation.rules.dnd5e import (
    AbilityScoreRule,
    ClassProgressionRule,
    FeatsRule,
    ProficiencyRule,
)
from character_service.domain.models import Character


@pytest.fixture
def character() -> Character:
    """Create a basic test character."""
    return Character(
        id=uuid4(),
        character_data={
            "name": "Test Character",
            "level": 1,
            "character_class": "fighter",
            "ability_scores": {
                "strength": 16,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 11,
                "charisma": 10,
            },
            "ability_score_method": "standard_array",
            "saving_throws": {
                "strength": True,
                "constitution": True,
            },
            "skills": {
                "athletics": {"proficient": True},
                "intimidation": {"proficient": True},
            },
            "class_features": [
                {"name": "Fighting Style", "source": "class"},
                {"name": "Second Wind", "source": "class"},
            ],
            "feats": [
                {
                    "name": "Skilled",
                    "source": "background",
                    "epic": False,
                }
            ],
        },
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.mark.asyncio
async def test_ability_score_validation():
    """Test ability score validation."""
    rule = AbilityScoreRule()

    # Test valid standard array
    character = Character(
        id=uuid4(),
        character_data={
            "ability_scores": {
                "strength": 16,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 11,
                "charisma": 10,
            },
            "ability_score_method": "standard_array",
        },
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    result = await rule.validate(character)
    assert result.passed

    # Test invalid standard array
    character.character_data["ability_scores"]["strength"] = 15
    result = await rule.validate(character)
    assert not result.passed
    assert len(result.issues) == 1

    # Test valid point buy
    character.character_data.update({
        "ability_scores": {
            "strength": 15,
            "dexterity": 15,
            "constitution": 15,
            "intelligence": 8,
            "wisdom": 8,
            "charisma": 8,
        },
        "ability_score_method": "point_buy",
    })
    result = await rule.validate(character)
    assert result.passed

    # Test invalid point buy (too many points)
    character.character_data["ability_scores"]["strength"] = 16
    result = await rule.validate(character)
    assert not result.passed


@pytest.mark.asyncio
async def test_class_progression_validation(character: Character):
    """Test class progression validation."""
    rule = ClassProgressionRule()

    # Test level 1 features
    result = await rule.validate(character)
    assert result.passed

    # Test missing required feature
    character.character_data["class_features"].pop()
    result = await rule.validate(character)
    assert not result.passed
    assert len(result.issues) == 1

    # Test subclass requirement
    character.character_data["level"] = 3
    result = await rule.validate(character)
    assert not result.passed
    assert any("subclass required" in i.message.lower() for i in result.issues)

    # Test Epic Boon
    character.character_data["level"] = 20
    result = await rule.validate(character)
    assert not result.passed
    assert any("epic boon" in i.message.lower() for i in result.issues)


@pytest.mark.asyncio
async def test_proficiency_validation(character: Character):
    """Test proficiency validation."""
    rule = ProficiencyRule()

    # Test valid proficiencies
    result = await rule.validate(character)
    assert result.passed

    # Test too many skills
    character.character_data["skills"]["acrobatics"] = {"proficient": True}
    character.character_data["skills"]["arcana"] = {"proficient": True}
    result = await rule.validate(character)
    assert not result.passed
    assert any("too many skill proficiencies" in i.message.lower() for i in result.issues)

    # Test invalid saving throws
    character.character_data["saving_throws"]["dexterity"] = True
    result = await rule.validate(character)
    assert not result.passed
    assert any("invalid saving throw" in i.message.lower() for i in result.issues)


@pytest.mark.asyncio
async def test_feat_validation(character: Character):
    """Test feat validation."""
    rule = FeatsRule()

    # Test valid feats
    result = await rule.validate(character)
    assert result.passed

    # Test epic feat before level 10
    character.character_data["feats"].append({
        "name": "Epic Test",
        "source": "asi",
        "epic": True,
    })
    result = await rule.validate(character)
    assert not result.passed
    assert any("epic feat" in i.message.lower() for i in result.issues)

    # Test missing background feat
    character.character_data["feats"] = []
    character.character_data["background"] = "test"
    result = await rule.validate(character)
    assert not result.passed
    assert any("missing background feat" in i.message.lower() for i in result.issues)
