"""Tests for custom content validation rules."""
import pytest
from typing import Dict

from character_service.core.validation.rules.dnd5e import CustomContentRule
from character_service.domain.models import Character


@pytest.fixture
def custom_class_data() -> Dict:
    """Sample custom class data."""
    return {
        "name": "Spellblade",
        "custom": True,
        "hit_die": 8,
        "proficiencies": {
            "armor": ["light", "medium"],
            "weapons": ["martial"]
        },
        "spellcasting": {
            "caster_type": "half",
            "ability": "intelligence",
            "preparation_method": "known",
            "spell_slots": {
                "1": 2,  # Level 1 slots
                "2": 2,  # Level 2 slots
                "3": 1,  # etc.
            },
            "spells": {
                "max_known": 11,  # Matches Ranger
                "by_level": {
                    "1": 2,
                    "2": 3,
                    "3": 4,
                }
            },
            "special_features": ["ritual_casting", "spell_flexibility"]
        },
        "features": [
            {
                "name": "Combat Magic",
                "level": 1,
                "description": "You can cast spells while wielding weapons"
            },
            {
                "name": "Arcane Strike",
                "level": 2,
                "description": "Channel spells through weapon attacks"
            }
        ]
    }


@pytest.fixture
def custom_race_data() -> Dict:
    """Sample custom race data."""
    return {
        "name": "Starborn",
        "custom": True,
        "ability_score_increases": {
            "intelligence": 2,
            "wisdom": 1
        },
        "features": [
            {
                "name": "Celestial Heritage",
                "description": "You know the Light cantrip"
            },
            {
                "name": "Starlight Step",
                "description": "Short-range teleportation"
            }
        ]
    }


@pytest.fixture
def custom_magic_data() -> Dict:
    """Sample custom magic system data."""
    return {
        "custom": True,
        "name": "Astral Magic",
        "resources": {
            "max_points": 20,
            "points_per_level": 2
        },
        "spells": [
            {
                "name": "Stellar Burst",
                "custom": True,
                "level": 3,
                "damage": {
                    "average": 25,
                    "type": "radiant"
                }
            }
        ]
    }


@pytest.mark.asyncio
async def test_valid_custom_class(custom_class_data: Dict):
    """Test validation of a well-formed custom class."""
    rule = CustomContentRule()
    character = Character(character_data={"character_class": custom_class_data})
    
    result = await rule.validate(character)
    assert result.passed
    assert not result.issues


@pytest.mark.asyncio
async def test_custom_class_spell_progression(custom_class_data: Dict):
    """Test spell progression validation for custom classes."""
    rule = CustomContentRule()
    
    # Test invalid spell level for half-caster
    custom_class_data["spellcasting"]["spell_slots"]["6"] = 1
    character = Character(character_data={"character_class": custom_class_data})
    
    result = await rule.validate(character)
    assert not result.passed
    assert any(
        "half casters cannot have level 6 slots" in issue.message
        for issue in result.issues
    )


@pytest.mark.asyncio
async def test_custom_class_spellcasting_ability(custom_class_data: Dict):
    """Test spellcasting ability validation."""
    rule = CustomContentRule()
    
    # Test invalid ability score
    custom_class_data["spellcasting"]["ability"] = "strength"
    character = Character(character_data={"character_class": custom_class_data})
    
    result = await rule.validate(character)
    assert not result.passed
    assert any(
        "Invalid spellcasting ability" in issue.message
        for issue in result.issues
    )


@pytest.mark.asyncio
async def test_custom_class_special_features(custom_class_data: Dict):
    """Test validation of special spellcasting features."""
    rule = CustomContentRule()
    
    # Test too many powerful features
    custom_class_data["spellcasting"]["special_features"].extend([
        "enhanced_slots",
        "unique_resource",
        "focus_benefits"
    ])
    character = Character(character_data={"character_class": custom_class_data})
    
    result = await rule.validate(character)
    assert not result.passed
    assert any(
        "Special casting features may be too powerful" in issue.message
        for issue in result.issues
    )


@pytest.mark.asyncio
async def test_valid_custom_race(custom_race_data: Dict):
    """Test validation of a well-formed custom race."""
    rule = CustomContentRule()
    character = Character(character_data={"race": custom_race_data})
    
    result = await rule.validate(character)
    assert result.passed
    assert not result.issues


@pytest.mark.asyncio
async def test_custom_race_ability_scores(custom_race_data: Dict):
    """Test ability score increase validation for custom races."""
    rule = CustomContentRule()
    
    # Test excessive ability score increases
    custom_race_data["ability_score_increases"]["charisma"] = 2
    character = Character(character_data={"race": custom_race_data})
    
    result = await rule.validate(character)
    assert not result.passed
    assert any(
        "ability score bonuses exceed standard amount" in issue.message
        for issue in result.issues
    )


@pytest.mark.asyncio
async def test_valid_custom_magic(custom_magic_data: Dict):
    """Test validation of a well-formed custom magic system."""
    rule = CustomContentRule()
    character = Character(character_data={"magic_system": custom_magic_data})
    
    result = await rule.validate(character)
    assert result.passed
    assert not result.issues


@pytest.mark.asyncio
async def test_custom_magic_damage(custom_magic_data: Dict):
    """Test spell damage validation for custom magic."""
    rule = CustomContentRule()
    
    # Test excessive spell damage
    custom_magic_data["spells"][0]["damage"]["average"] = 50
    character = Character(character_data={"magic_system": custom_magic_data})
    
    result = await rule.validate(character)
    assert not result.passed
    assert any(
        "Spell damage may be too high" in issue.message
        for issue in result.issues
    )


@pytest.mark.asyncio
async def test_pact_magic_compatibility(custom_class_data: Dict):
    """Test Pact Magic compatibility validation."""
    rule = CustomContentRule()
    
    # Test invalid combination of Pact Magic and standard slots
    custom_class_data["spellcasting"]["special_features"].append("pact_magic")
    character = Character(character_data={"character_class": custom_class_data})
    
    result = await rule.validate(character)
    assert not result.passed
    assert any(
        "Pact Magic cannot be combined with standard spell slots" in issue.message
        for issue in result.issues
    )
