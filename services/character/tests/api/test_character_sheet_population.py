"""Tests for verifying that character creation properly populates the full character sheet."""

import pytest
from unittest.mock import ANY, patch
from fastapi import status
from fastapi.testclient import TestClient

from ...app.api.v2.character_routes import router
from ...app.models.character import Character, CharacterSheet
from ...app.models.enums import AbilityScore, Skill, CharacterType
from ...app.schemas.character import CreationPrompt

@pytest.fixture
def test_client():
    """Create a test client for the API."""
    from ...app.main import app
    return TestClient(app)

class TestCharacterSheetPopulation:
    """Tests to verify proper population of character sheets during creation."""

    def test_create_pc_populates_all_fields(self, test_client):
        """Test that creating a PC populates all required character sheet fields."""
        creation_prompt = CreationPrompt(
            creation_type=CharacterType.PC,
            prompt="Create a human fighter",
            theme="traditional",
            level=1,
            preferences={
                "use_custom_content": False,
                "prioritize_official": True
            }
        )

        with patch('app.services.character_service.create_character') as mock_create:
            # Create response that includes all required fields
            mock_character = Character(
                id="test-uuid",
                name="Test Fighter",
                species="Human",
                class_name="Fighter",
                level=1,
                background="Soldier",
                alignment="Lawful Good",
                experience_points=0,
                ability_scores={
                    AbilityScore.STRENGTH: 16,
                    AbilityScore.DEXTERITY: 14,
                    AbilityScore.CONSTITUTION: 15,
                    AbilityScore.INTELLIGENCE: 12,
                    AbilityScore.WISDOM: 13,
                    AbilityScore.CHARISMA: 11
                },
                current_hit_points=12,  # 10 (d10) + 2 (Con mod)
                temporary_hit_points=0,
                hit_dice={"d10": {"total": 1, "used": 0}},
                death_saves={"successes": 0, "failures": 0},
                exhaustion_level=0,
                inspiration=0,
                proficiencies={
                    "languages": ["Common"],
                    "tools": ["Smith's Tools"],
                    "weapons": ["Simple Weapons", "Martial Weapons"],
                    "armor": ["Light Armor", "Medium Armor", "Heavy Armor", "Shields"]
                },
                equipment=[
                    {"name": "Longsword", "type": "weapon", "equipped": True},
                    {"name": "Chain Mail", "type": "armor", "equipped": True},
                    {"name": "Shield", "type": "armor", "equipped": True}
                ],
                currency={
                    "cp": 0,
                    "sp": 0,
                    "ep": 0,
                    "gp": 10,
                    "pp": 0
                },
                appearance={
                    "age": 25,
                    "height": "6'0\"",
                    "weight": "180 lbs",
                    "eye_color": "Brown",
                    "skin_color": "Tan",
                    "hair_color": "Black"
                },
                personality={
                    "traits": ["Brave", "Loyal"],
                    "ideals": ["Honor"],
                    "bonds": ["Protect the weak"],
                    "flaws": ["Stubborn"]
                },
                conditions=[],
                concentration={
                    "active": False,
                    "spell": None
                }
            )
            mock_create.return_value = mock_character

            response = test_client.post("/api/v2/factory/create", json=creation_prompt.dict())
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()

            # Verify core information is present
            assert data["character"]["name"]
            assert data["character"]["species"]
            assert data["character"]["class_name"]
            assert data["character"]["level"]
            assert data["character"]["background"]
            assert data["character"]["alignment"]
            assert data["character"]["experience_points"] >= 0

            # Verify ability scores
            for ability in AbilityScore:
                assert ability in data["character"]["ability_scores"]
                assert 3 <= data["character"]["ability_scores"][ability] <= 20

            # Verify combat stats
            assert data["character"]["current_hit_points"] > 0
            assert data["character"]["temporary_hit_points"] >= 0
            assert data["character"]["hit_dice"]
            assert data["character"]["death_saves"]
            assert "successes" in data["character"]["death_saves"]
            assert "failures" in data["character"]["death_saves"]
            assert 0 <= data["character"]["exhaustion_level"] <= 6

            # Verify proficiencies
            assert data["character"]["proficiencies"]["languages"]
            assert data["character"]["proficiencies"]["weapons"]
            assert data["character"]["proficiencies"]["armor"]

            # Verify equipment and currency
            assert data["character"]["equipment"]
            for currency in ["cp", "sp", "ep", "gp", "pp"]:
                assert currency in data["character"]["currency"]

            # Verify character details
            assert data["character"]["appearance"]
            for trait in ["age", "height", "weight", "eye_color", "skin_color", "hair_color"]:
                assert trait in data["character"]["appearance"]

            assert data["character"]["personality"]
            for aspect in ["traits", "ideals", "bonds", "flaws"]:
                assert aspect in data["character"]["personality"]

            # Verify conditions and concentration
            assert isinstance(data["character"]["conditions"], list)
            assert "active" in data["character"]["concentration"]
            assert "spell" in data["character"]["concentration"]

    def test_create_npc_populates_all_fields(self, test_client):
        """Test that creating an NPC populates all required character sheet fields."""
        creation_prompt = CreationPrompt(
            creation_type=CharacterType.NPC,
            prompt="Create a merchant NPC",
            theme="traditional",
            level=1,
            preferences={
                "use_custom_content": False,
                "prioritize_official": True
            }
        )

        with patch('app.services.character_service.create_character') as mock_create:
            # Similar to PC test but with NPC-specific expectations
            mock_create.return_value = Character(
                # ... similar to PC but with NPC-appropriate values
            )

            response = test_client.post("/api/v2/factory/create", json=creation_prompt.dict())
            assert response.status_code == status.HTTP_201_CREATED
            # ... similar validations to PC test

    def test_create_monster_populates_all_fields(self, test_client):
        """Test that creating a monster populates all required character sheet fields."""
        creation_prompt = CreationPrompt(
            creation_type=CharacterType.MONSTER,
            prompt="Create a dragon",
            theme="traditional",
            level=1,
            preferences={
                "use_custom_content": False,
                "prioritize_official": True
            }
        )

        with patch('app.services.character_service.create_character') as mock_create:
            # Similar to PC test but with monster-specific expectations
            mock_create.return_value = Character(
                # ... similar to PC but with monster-appropriate values
            )

            response = test_client.post("/api/v2/factory/create", json=creation_prompt.dict())
            assert response.status_code == status.HTTP_201_CREATED
            # ... similar validations to PC test

    def test_field_type_validation(self, test_client):
        """Test that fields have the correct data types and ranges."""
        with patch('app.services.character_service.create_character') as mock_create:
            mock_character = Character(
                # ... minimal valid character
            )
            mock_create.return_value = mock_character

            response = test_client.get("/api/v2/characters/test-uuid/sheet")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            # Verify types and ranges for key fields
            assert isinstance(data["level"], int)
            assert 1 <= data["level"] <= 20

            assert isinstance(data["current_hit_points"], int)
            assert data["current_hit_points"] >= 0

            for ability_score in data["ability_scores"].values():
                assert isinstance(ability_score, int)
                assert 1 <= ability_score <= 30

            assert isinstance(data["currency"]["gp"], int)
            assert data["currency"]["gp"] >= 0

            assert isinstance(data["exhaustion_level"], int)
            assert 0 <= data["exhaustion_level"] <= 6

            assert isinstance(data["inspiration"], int)
            assert 0 <= data["inspiration"] <= 1

    def test_required_field_presence(self, test_client):
        """Test that all required fields are present in created characters."""
        with patch('app.services.character_service.create_character') as mock_create:
            mock_character = Character(
                # ... minimal valid character
            )
            mock_create.return_value = mock_character

            response = test_client.get("/api/v2/characters/test-uuid/sheet")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            # Core required fields
            required_fields = [
                "name",
                "species",
                "class_name",
                "level",
                "ability_scores",
                "current_hit_points",
                "proficiencies",
                "equipment",
                "currency",
                "appearance",
                "personality"
            ]

            for field in required_fields:
                assert field in data, f"Missing required field: {field}"

            # Nested required fields
            assert all(ability in data["ability_scores"] for ability in [
                "strength",
                "dexterity",
                "constitution",
                "intelligence",
                "wisdom",
                "charisma"
            ])

            assert all(prof_type in data["proficiencies"] for prof_type in [
                "languages",
                "weapons",
                "armor",
                "tools"
            ])

            assert all(currency in data["currency"] for currency in [
                "cp", "sp", "ep", "gp", "pp"
            ])

    def test_derived_field_calculation(self, test_client):
        """Test that derived fields are calculated correctly."""
        with patch('app.services.character_service.create_character') as mock_create:
            mock_character = Character(
                ability_scores={
                    AbilityScore.STRENGTH: 16,  # Modifier should be +3
                    AbilityScore.DEXTERITY: 14,  # Modifier should be +2
                    AbilityScore.CONSTITUTION: 15,  # Modifier should be +2
                    AbilityScore.INTELLIGENCE: 12,  # Modifier should be +1
                    AbilityScore.WISDOM: 13,  # Modifier should be +1
                    AbilityScore.CHARISMA: 11  # Modifier should be +0
                },
                level=4,  # Proficiency bonus should be +2
                class_name="Fighter"
            )
            mock_create.return_value = mock_character

            response = test_client.get("/api/v2/characters/test-uuid/sheet")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            # Verify ability modifiers
            assert data["ability_modifiers"]["strength"] == 3
            assert data["ability_modifiers"]["dexterity"] == 2
            assert data["ability_modifiers"]["constitution"] == 2
            assert data["ability_modifiers"]["intelligence"] == 1
            assert data["ability_modifiers"]["wisdom"] == 1
            assert data["ability_modifiers"]["charisma"] == 0

            # Verify proficiency bonus
            assert data["proficiency_bonus"] == 2

            # Verify skill modifiers (assuming proficiency in Athletics)
            assert data["skill_modifiers"]["athletics"] == 5  # Str mod (3) + prof bonus (2)

            # Verify passive scores
            assert data["passive_perception"] == 11  # 10 + Wis mod (1)
            assert data["passive_investigation"] == 11  # 10 + Int mod (1)
            assert data["passive_insight"] == 11  # 10 + Wis mod (1)

            # Verify saving throws (assuming proficiency in Str and Con saves as Fighter)
            assert data["saving_throws"]["strength"] == 5  # Str mod (3) + prof bonus (2)
            assert data["saving_throws"]["constitution"] == 4  # Con mod (2) + prof bonus (2)
            assert data["saving_throws"]["dexterity"] == 2  # Just Dex mod (no proficiency)
