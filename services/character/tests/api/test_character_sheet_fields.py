"""Tests for character sheet field access and management through the API."""

import pytest
from unittest.mock import ANY, patch
from fastapi import status
from fastapi.testclient import TestClient

from character_service.api.v2.router import router
from character_service.models.models import Character
from character_service.schemas.schemas import CombatState, ResourceState
# TODO: Import enums from correct location once they are ported
from ...app.models.enums import AbilityScore, Skill

@pytest.fixture
def test_client():
    """Create a test client for the API."""
    from ...app.main import app
    return TestClient(app)

@pytest.fixture
def mock_character():
    """Create a mock character for testing."""
    return Character(
        id="test-uuid",
        name="Test Character",
        theme="traditional",
        character_data={
            "species": "Human",
            "class_name": "Fighter",
            "level": 1,
            "ability_scores": {
                AbilityScore.STRENGTH: 16,
                AbilityScore.DEXTERITY: 14,
                AbilityScore.CONSTITUTION: 15,
                AbilityScore.INTELLIGENCE: 12,
                AbilityScore.WISDOM: 13,
                AbilityScore.CHARISMA: 11
            },
            "current_hit_points": 12,
            "temporary_hit_points": 0,
            "hit_dice": {"d10": {"total": 1, "used": 0}},
            "death_saves": {"successes": 0, "failures": 0},
            "exhaustion_level": 0,
            "inspiration": 0,
            "proficiencies": {
                "languages": ["Common"],
                "tools": ["Smith's Tools"],
                "weapons": ["Simple Weapons", "Martial Weapons"],
                "armor": ["Light Armor", "Medium Armor", "Heavy Armor", "Shields"]
            },
            "conditions": [],
            "concentration": {"active": False, "spell": None}
        },
        user_id="user-test-uuid",
        campaign_id="campaign-test-uuid",
        is_active=True
    )

class TestCharacterSheetFields:
    """Tests for accessing and modifying character sheet fields."""

    def test_get_independent_field(self, test_client, mock_character):
        """Test getting an independent field like character name."""
        with patch('app.services.character_service.get_character') as mock_get:
            mock_get.return_value = mock_character
            response = test_client.get("/api/v2/characters/test-uuid/fields/name")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["field_name"] == "name"
            assert data["value"] == "Test Character"
            assert data["type"] == "independent"

    def test_get_derived_field(self, test_client, mock_character):
        """Test getting a derived field like ability score modifier."""
        with patch('app.services.character_service.get_character') as mock_get:
            mock_get.return_value = mock_character
            response = test_client.get("/api/v2/characters/test-uuid/fields/strength_modifier")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["field_name"] == "strength_modifier"
            assert data["value"] == 3  # (16 - 10) // 2
            assert data["type"] == "derived"

    def test_update_independent_field(self, test_client, mock_character):
        """Test updating an independent field like current HP."""
        with patch('app.services.character_service.update_character_field') as mock_update:
            mock_update.return_value = True
            response = test_client.put(
                "/api/v2/characters/test-uuid/fields/current_hp",
                json={"value": 10, "reason": "Took damage"}
            )
            assert response.status_code == status.HTTP_200_OK
            mock_update.assert_called_once_with(
                "test-uuid",
                "current_hp",
                10,
                "Took damage"
            )

    def test_update_derived_field_fails(self, test_client, mock_character):
        """Test that attempting to update a derived field fails."""
        with patch('app.services.character_service.get_character') as mock_get:
            mock_get.return_value = mock_character
            response = test_client.put(
                "/api/v2/characters/test-uuid/fields/strength_modifier",
                json={"value": 5, "reason": "Should fail"}
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Cannot modify derived field" in response.json()["error"]["message"]

    def test_get_combat_state(self, test_client, mock_character):
        """Test retrieving current combat state."""
        expected_state = CombatState(
            current_hp=15,
            temp_hp=0,
            conditions=[],
            death_saves={"successes": 0, "failures": 0},
            concentration={"active": False, "spell": None},
            exhaustion=0
        )
        with patch('app.services.character_service.get_combat_state') as mock_get:
            mock_get.return_value = expected_state
            response = test_client.get("/api/v2/characters/test-uuid/combat-state")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["current_hp"] == 15
            assert data["conditions"] == []
            assert not data["concentration"]["active"]

    def test_update_combat_state(self, test_client, mock_character):
        """Test updating combat state."""
        update_data = {
            "hp_delta": -5,
            "temp_hp": 3,
            "add_conditions": ["prone"],
            "remove_conditions": [],
            "death_save_result": None,
            "concentration": {"check_dc": 10, "save_result": 15},
            "exhaustion_delta": 1
        }
        with patch('app.services.character_service.update_combat_state') as mock_update:
            response = test_client.put(
                "/api/v2/characters/test-uuid/combat-state",
                json=update_data
            )
            assert response.status_code == status.HTTP_200_OK
            mock_update.assert_called_once_with("test-uuid", ANY)

    def test_get_resources(self, test_client, mock_character):
        """Test retrieving character resources."""
        expected_resources = ResourceState(
            hit_dice={
                "d10": {"total": 1, "used": 0}  # Fighter's hit die
            },
            spell_slots={},  # No spell slots for a fighter
            class_resources=[
                {
                    "name": "Second Wind",
                    "current": 1,
                    "maximum": 1,
                    "recharge": "short_rest"
                }
            ]
        )
        with patch('app.services.character_service.get_resources') as mock_get:
            mock_get.return_value = expected_resources
            response = test_client.get("/api/v2/characters/test-uuid/resources")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["hit_dice"]["d10"]["total"] == 1
            assert len(data["class_resources"]) == 1
            assert data["class_resources"][0]["name"] == "Second Wind"

    def test_update_resources(self, test_client, mock_character):
        """Test updating character resources."""
        update_data = {
            "hit_dice_used": {"d10": 1},
            "spell_slots_used": {},
            "class_resources": [
                {"name": "Second Wind", "delta": -1}
            ]
        }
        with patch('app.services.character_service.update_resources') as mock_update:
            response = test_client.put(
                "/api/v2/characters/test-uuid/resources",
                json=update_data
            )
            assert response.status_code == status.HTTP_200_OK
            mock_update.assert_called_once_with("test-uuid", ANY)

    def test_short_rest(self, test_client, mock_character):
        """Test taking a short rest."""
        request_data = {
            "hit_dice_used": [
                {"die_type": "d10", "count": 1, "bonus": 2}
            ]
        }
        expected_response = {
            "hp_restored": 8,
            "hit_dice_regained": {"d10": 0},
            "resources_reset": ["Second Wind"],
            "conditions_removed": []
        }
        with patch('app.services.character_service.take_short_rest') as mock_rest:
            mock_rest.return_value = expected_response
            response = test_client.post(
                "/api/v2/characters/test-uuid/rest/short",
                json=request_data
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["hp_restored"] == 8
            assert "Second Wind" in data["resources_reset"]

    def test_long_rest(self, test_client, mock_character):
        """Test taking a long rest."""
        expected_response = {
            "hp_restored": 15,
            "hit_dice_regained": {"d10": 1},
            "resources_reset": ["Second Wind"],
            "conditions_removed": ["exhaustion"]
        }
        with patch('app.services.character_service.take_long_rest') as mock_rest:
            mock_rest.return_value = expected_response
            response = test_client.post("/api/v2/characters/test-uuid/rest/long")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["hp_restored"] == 15
            assert data["hit_dice_regained"]["d10"] == 1

    def test_field_validation(self, test_client, mock_character):
        """Test validation of field updates."""
        test_cases = [
            # Invalid ability score
            {
                "field": "strength",
                "value": 35,
                "expected_status": status.HTTP_400_BAD_REQUEST,
                "error_message": "Ability score cannot exceed 30"
            },
            # Invalid hit points
            {
                "field": "current_hp",
                "value": -10,
                "expected_status": status.HTTP_400_BAD_REQUEST,
                "error_message": "Current HP cannot be negative"
            },
            # Invalid level
            {
                "field": "level",
                "value": 25,
                "expected_status": status.HTTP_400_BAD_REQUEST,
                "error_message": "Level must be between 1 and 20"
            }
        ]

        for case in test_cases:
            with patch('app.services.character_service.get_character') as mock_get:
                mock_get.return_value = mock_character
                response = test_client.put(
                    f"/api/v2/characters/test-uuid/fields/{case['field']}",
                    json={"value": case["value"], "reason": "Testing validation"}
                )
                assert response.status_code == case["expected_status"]
                assert case["error_message"] in response.json()["error"]["message"]
