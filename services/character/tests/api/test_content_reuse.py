"""Tests for verifying content reuse and branching behavior."""

import pytest
from unittest.mock import ANY, patch
from fastapi import status
from fastapi.testclient import TestClient

from ...app.api.v2.character_routes import router
from ...app.models.character import Character, CharacterSheet
from ...app.models.enums import CharacterType, ContentType, AdaptationLevel
from ...app.schemas.character import CreationPrompt, BranchRequest

@pytest.fixture
def test_client():
    """Create a test client for the API."""
    from ...app.main import app
    return TestClient(app)

@pytest.fixture
def mock_catalog():
    """Create mock catalog entries."""
    return {
        "items": [
            {
                "id": "longsword-1",
                "type": "weapon",
                "name": "Longsword",
                "properties": {
                    "damage": "1d8",
                    "damage_type": "slashing",
                    "weight": "3 lb.",
                    "properties": ["versatile"]
                }
            },
            {
                "id": "fireball-1",
                "type": "spell",
                "name": "Fireball",
                "properties": {
                    "level": 3,
                    "school": "evocation",
                    "casting_time": "1 action",
                    "range": "150 feet"
                }
            }
        ]
    }

class TestContentReuse:
    """Tests for content reuse and branching behavior."""

    def test_create_character_uses_existing_content(self, test_client, mock_catalog):
        """Test that character creation first tries to use existing content."""
        creation_prompt = CreationPrompt(
            creation_type=CharacterType.PC,
            prompt="Create a human fighter who uses a longsword",
            theme="traditional",
            level=1,
            preferences={
                "use_custom_content": False,
                "prioritize_official": True
            }
        )

        with patch('app.services.catalog_service.search_semantic') as mock_search, \
             patch('app.services.character_service.create_character') as mock_create:
            # Mock catalog search to return longsword
            mock_search.return_value = {
                "matches": [{
                    "content_id": "longsword-1",
                    "match_score": 0.95,
                    "adaptation_needed": "none",
                    "theme_alignment": 1.0
                }]
            }

            response = test_client.post("/api/v2/factory/create", json=creation_prompt.dict())
            assert response.status_code == status.HTTP_201_CREATED

            # Verify catalog was searched for matching items
            mock_search.assert_called_with(
                query="longsword",
                content_type="weapon",
                theme="traditional",
                adaptation_allowed=True
            )

            # Verify created character uses existing longsword
            data = response.json()
            equipment = data["character"]["equipment"]
            assert any(item["id"] == "longsword-1" for item in equipment)
            assert not any(item.get("custom") for item in equipment)

    def test_create_character_with_custom_content(self, test_client, mock_catalog):
        """Test that character creation generates custom content when no matches exist."""
        creation_prompt = CreationPrompt(
            creation_type=CharacterType.PC,
            prompt="Create a character who uses an energy blade",
            theme="cyberpunk",
            level=1,
            preferences={
                "use_custom_content": True,
                "prioritize_official": False
            }
        )

        with patch('app.services.catalog_service.search_semantic') as mock_search, \
             patch('app.services.character_service.create_character') as mock_create, \
             patch('app.services.content_service.create_content') as mock_create_content:
            # Mock catalog search to return no matches
            mock_search.return_value = {"matches": []}

            # Mock content creation
            mock_create_content.return_value = {
                "id": "energy-blade-1",
                "type": "weapon",
                "name": "Energy Blade",
                "properties": {
                    "damage": "1d8",
                    "damage_type": "force",
                    "custom": True
                }
            }

            response = test_client.post("/api/v2/factory/create", json=creation_prompt.dict())
            assert response.status_code == status.HTTP_201_CREATED

            # Verify catalog was searched first
            mock_search.assert_called_with(
                query="energy blade",
                content_type="weapon",
                theme="cyberpunk",
                adaptation_allowed=True
            )

            # Verify custom content was created
            mock_create_content.assert_called()
            data = response.json()
            equipment = data["character"]["equipment"]
            assert any(item["id"] == "energy-blade-1" for item in equipment)
            assert any(item.get("custom") for item in equipment)

    def test_adapt_existing_content_for_theme(self, test_client, mock_catalog):
        """Test that existing content can be adapted for a new theme."""
        with patch('app.services.catalog_service.get_content') as mock_get, \
             patch('app.services.content_service.adapt_content') as mock_adapt:
            # Mock original content
            mock_get.return_value = mock_catalog["items"][0]  # Longsword

            # Mock adapted content
            mock_adapt.return_value = {
                "id": "vibro-sword-1",
                "type": "weapon",
                "name": "Vibro-sword",
                "properties": {
                    "damage": "1d8",
                    "damage_type": "slashing",
                    "theme": "cyberpunk",
                    "root_id": "longsword-1"
                }
            }

            request = BranchRequest(
                theme="cyberpunk",
                branch_name="cyberpunk-adaptation",
                adaptation_level=AdaptationLevel.MINOR
            )

            response = test_client.post(
                "/api/v2/content/longsword-1/branches",
                json=request.dict()
            )
            assert response.status_code == status.HTTP_201_CREATED

            data = response.json()
            assert data["content"]["root_id"] == "longsword-1"
            assert data["content"]["name"] == "Vibro-sword"
            assert data["content"]["properties"]["theme"] == "cyberpunk"

    def test_character_branching_with_memory(self, test_client):
        """Test that character branches maintain memory/history."""
        branch_request = BranchRequest(
            theme="western",
            branch_name="western-adaptation",
            preserve_memory=True
        )

        with patch('app.services.character_service.create_branch') as mock_branch:
            # Simulate a character with history
            original_character = {
                "id": "char-1",
                "name": "Gandalf",
                "class_name": "Wizard",
                "journal": [
                    {"id": "entry-1", "content": "Fought a Balrog"}
                ],
                "relationships": [
                    {"id": "rel-1", "name": "Frodo", "type": "friend"}
                ]
            }

            # Mock branched character
            mock_branch.return_value = {
                "id": "char-2",
                "name": "Gandalf",
                "class_name": "Wandslinger",  # Themed adaptation
                "journal": [
                    {"id": "entry-1", "content": "Fought a Balrog"}  # Preserved
                ],
                "relationships": [
                    {"id": "rel-1", "name": "Frodo", "type": "friend"}  # Preserved
                ]
            }

            response = test_client.post(
                "/api/v2/characters/char-1/branches",
                json=branch_request.dict()
            )
            assert response.status_code == status.HTTP_201_CREATED

            data = response.json()
            assert data["character"]["journal"] == original_character["journal"]
            assert data["character"]["relationships"] == original_character["relationships"]

    def test_content_branching_resets_to_root(self, test_client):
        """Test that branched content resets to root version."""
        branch_request = BranchRequest(
            theme="western",
            branch_name="western-adaptation",
            adaptation_level=AdaptationLevel.MINOR
        )

        with patch('app.services.content_service.create_branch') as mock_branch:
            # Simulate content with modifications
            original_content = {
                "id": "item-1",
                "type": "weapon",
                "name": "Enchanted Sword",
                "properties": {
                    "damage": "1d8+1",
                    "magic": True,
                    "theme": "fantasy"
                },
                "root_id": "sword-root"
            }

            # Mock branched content - should derive from root
            mock_branch.return_value = {
                "id": "item-2",
                "type": "weapon",
                "name": "Six-shooter",
                "properties": {
                    "damage": "1d8",
                    "theme": "western"
                },
                "root_id": "sword-root"  # Same root as original
            }

            response = test_client.post(
                "/api/v2/content/item-1/branches",
                json=branch_request.dict()
            )
            assert response.status_code == status.HTTP_201_CREATED

            data = response.json()
            assert data["content"]["root_id"] == original_content["root_id"]
            # Verify it's a fresh adaptation, not building on enchanted version
            assert "magic" not in data["content"]["properties"]
