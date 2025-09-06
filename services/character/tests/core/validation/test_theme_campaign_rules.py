"""Tests for theme and campaign validation rules."""
import pytest
from datetime import datetime
from uuid import uuid4

from character_service.core.validation.rules.theme import (
    ThemeCompatibilityRule,
    ThemeTransitionRule,
)
from character_service.core.validation.rules.campaign import (
    CampaignContextRule,
    AntithenticonRule,
)
from character_service.domain.models import Character


@pytest.fixture
def character() -> Character:
    """Create a test character with theme and campaign data."""
    return Character(
        id=uuid4(),
        character_data={
            "name": "Test Character",
            "level": 5,
            "character_class": "fighter",
            "subclass": "champion",
            "ability_scores": {
                "strength": 16,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 11,
                "charisma": 10,
            },
            "theme": {
                "name": "veteran",
                "level": 2,
                "features": [
                    {"name": "Battle Scarred", "type": "passive"},
                    {"name": "War Stories", "type": "active"},
                ],
            },
            "theme_features": [
                {"name": "Battle Scarred", "type": "passive"},
                {"name": "War Stories", "type": "active"},
            ],
            "campaign": {
                "name": "Test Campaign",
                "allowed_themes": ["novice", "veteran", "hero"],
                "requirements": {
                    "minimum_level": 3,
                    "maximum_level": 10,
                    "allowed_classes": ["fighter", "paladin", "ranger"],
                },
                "theme_progression": {
                    "maximum_level": 3,
                },
                "character_options": {
                    "feats": {
                        "banned": ["Lucky"],
                        "epic_feat_min_level": 10,
                    },
                    "equipment": {
                        "banned": ["Sword of Sharpness"],
                        "magic_item_limits": {"total": 3},
                    },
                },
            },
        },
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.mark.asyncio
async def test_theme_compatibility(character: Character):
    """Test theme compatibility validation."""
    rule = ThemeCompatibilityRule()

    # Test valid theme
    result = await rule.validate(character)
    assert result.passed

    # Test missing theme features
    character.character_data["theme_features"].pop()
    result = await rule.validate(character)
    assert not result.passed
    assert any("missing theme feature" in i.message.lower() for i in result.issues)

    # Test class restriction
    character.character_data["theme"]["restrictions"] = {
        "forbidden_classes": ["fighter"],
    }
    result = await rule.validate(character)
    assert not result.passed
    assert any("class is not allowed" in i.message.lower() for i in result.issues)


@pytest.mark.asyncio
async def test_theme_transition(character: Character):
    """Test theme transition validation."""
    rule = ThemeTransitionRule()

    # Set up transition
    character.character_data["theme_transition"] = {
        "target_theme": "hero",
        "requirements": {
            "minimum_level": 5,
            "milestones": ["veteran_deed"],
        },
        "costs": {
            "resources": {"inspiration": 3},
            "features": ["Old War Story"],
        },
    }

    # Test valid transition
    character.character_data.update({
        "milestones": [{"id": "veteran_deed"}],
        "resources": {"inspiration": 3},
    })
    result = await rule.validate(character)
    assert result.passed

    # Test missing milestone
    character.character_data["milestones"] = []
    result = await rule.validate(character)
    assert not result.passed
    assert any("missing required milestone" in i.message.lower() for i in result.issues)

    # Test insufficient resources
    character.character_data["resources"]["inspiration"] = 1
    result = await rule.validate(character)
    assert not result.passed
    assert any("insufficient" in i.message.lower() for i in result.issues)


@pytest.mark.asyncio
async def test_campaign_context(character: Character):
    """Test campaign context validation."""
    rule = CampaignContextRule()

    # Test valid campaign context
    result = await rule.validate(character)
    assert result.passed

    # Test level requirements
    character.character_data["level"] = 2
    result = await rule.validate(character)
    assert not result.passed
    assert any("below campaign minimum" in i.message.lower() for i in result.issues)

    # Test class restrictions
    character.character_data["character_class"] = "wizard"
    result = await rule.validate(character)
    assert not result.passed
    assert any("not allowed in campaign" in i.message.lower() for i in result.issues)

    # Test theme restrictions
    character.character_data["theme"]["name"] = "legend"
    result = await rule.validate(character)
    assert not result.passed
    assert any("not allowed in campaign" in i.message.lower() for i in result.issues)


@pytest.mark.asyncio
async def test_antitheticon(character: Character):
    """Test Antitheticon-specific rules."""
    rule = AntithenticonRule()

    # Setup Antitheticon character
    character.character_data.update({
        "campaign": {"antitheticon_enabled": True},
        "identity_network": {
            "identities": [
                {
                    "name": "Ser John",
                    "relationships": [
                        {"target": "Merchant Mark", "type": "business"},
                    ],
                },
                {
                    "name": "Merchant Mark",
                    "relationships": [
                        {"target": "Ser John", "type": "business"},
                    ],
                },
            ],
        },
        "plot_impacts": [
            {
                "severity": "minor",
                "resolved": False,
            },
        ],
        "deceptions": [
            {
                "name": "Noble Identity",
                "active": True,
                "last_maintained": datetime.utcnow().isoformat(),
            },
        ],
    })

    # Test valid configuration
    result = await rule.validate(character)
    assert result.passed

    # Test disconnected network
    character.character_data["identity_network"]["identities"][1]["relationships"] = []
    result = await rule.validate(character)
    assert not result.passed
    assert any("network is not fully connected" in i.message.lower() for i in result.issues)

    # Test too many unresolved impacts
    character.character_data["plot_impacts"].extend([
        {"severity": "minor", "resolved": False},
        {"severity": "minor", "resolved": False},
        {"severity": "minor", "resolved": False},
    ])
    result = await rule.validate(character)
    assert not result.passed
    assert any("too many unresolved plot impacts" in i.message.lower() for i in result.issues)

    # Test too many active deceptions
    character.character_data["deceptions"].extend([
        {"name": f"Deception {i}", "active": True} for i in range(5)
    ])
    result = await rule.validate(character)
    assert not result.passed
    assert any("too many active deceptions" in i.message.lower() for i in result.issues)
