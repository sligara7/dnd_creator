"""Tests for theme transitions and content branching behavior."""

import pytest
from unittest.mock import ANY, patch
from fastapi import status
from fastapi.testclient import TestClient
from uuid import UUID

from ...app.api.v2.character_routes import router
from ...app.models.character import Character, CharacterSheet
from ...app.models.enums import CharacterType, ContentType, AdaptationLevel

@pytest.fixture
def test_client():
    """Create a test client for the API."""
    from ...app.main import app
    return TestClient(app)

@pytest.fixture
def mock_yoda_cyberpunk():
    """Create a mock cyberpunk Yoda character with equipment."""
    return {
        "id": "yoda-cyber-a",
        "name": "Yoda",
        "species": "Unknown Alien",
        "class_name": "Tech Master",
        "theme": "cyberpunk",
        "equipment": [
            {
                "id": "lightsaber-cyber-a",
                "name": "Energy Blade",
                "type": "weapon",
                "theme": "cyberpunk",
                "properties": {
                    "damage": "1d10",
                    "damage_type": "energy",
                    "tech_level": "advanced"
                }
            }
        ],
        "journal": [
            {
                "id": "entry-1",
                "content": "Fought in the cyber wars"
            }
        ]
    }

class TestThemeTransitions:
    """Tests for theme transitions and content versioning."""

    def test_transition_to_fantasy(self, test_client, mock_yoda_cyberpunk):
        """Test transitioning from cyberpunk to fantasy theme."""
        transition_request = {
            "new_theme": "fantasy",
            "chapter_id": "chapter-2",
            "preserve_memory": True,
            "equipment_transitions": [
                {
                    "equipment_id": "lightsaber-cyber-a",
                    "transition_type": "theme_reset"
                }
            ]
        }

        with patch('app.services.character_service.get_character') as mock_get, \
             patch('app.services.theme_service.transition_theme') as mock_transition:
            # Setup current character
            mock_get.return_value = mock_yoda_cyberpunk

            # Mock theme transition response
            mock_transition.return_value = {
                "character": {
                    "id": "yoda-fantasy-a",
                    "parent_id": "yoda-cyber-a",
                    "theme": "fantasy",
                    "name": "Yoda",
                    "species": "Unknown Species",
                    "class_name": "Mystic",
                    "equipment": [
                        {
                            "id": "lightsaber-fantasy-a",
                            "root_id": "lightsaber-cyber-a",
                            "name": "Energy Staff",
                            "type": "weapon",
                            "theme": "fantasy",
                            "properties": {
                                "damage": "1d10",
                                "damage_type": "force",
                                "magical": True
                            }
                        }
                    ],
                    "journal": [
                        {
                            "id": "entry-1",
                            "content": "Fought in the cyber wars"  # Preserved
                        }
                    ]
                },
                "version_graph": {
                    "nodes": [
                        {
                            "id": "yoda-cyber-a",
                            "type": "character",
                            "theme": "cyberpunk"
                        },
                        {
                            "id": "yoda-fantasy-a",
                            "type": "character",
                            "theme": "fantasy",
                            "parent_id": "yoda-cyber-a"
                        },
                        {
                            "id": "lightsaber-cyber-a",
                            "type": "equipment",
                            "theme": "cyberpunk"
                        },
                        {
                            "id": "lightsaber-fantasy-a",
                            "type": "equipment",
                            "theme": "fantasy",
                            "root_id": "lightsaber-cyber-a"
                        }
                    ],
                    "edges": [
                        {
                            "from": "yoda-fantasy-a",
                            "to": "yoda-cyber-a",
                            "type": "parent"
                        },
                        {
                            "from": "lightsaber-fantasy-a",
                            "to": "lightsaber-cyber-a",
                            "type": "root"
                        }
                    ]
                }
            }

            response = test_client.post(
                f"/api/v2/characters/yoda-cyber-a/theme-transition",
                json=transition_request
            )
            assert response.status_code == status.HTTP_200_OK

            # Verify the response structure
            data = response.json()
            assert data["character"]["id"] == "yoda-fantasy-a"
            assert data["character"]["parent_id"] == "yoda-cyber-a"
            
            # Verify character version linkage
            nodes = data["version_graph"]["nodes"]
            character_node = next(n for n in nodes if n["id"] == "yoda-fantasy-a")
            assert character_node["parent_id"] == "yoda-cyber-a"

            # Verify equipment version linkage
            equipment_node = next(n for n in nodes if n["id"] == "lightsaber-fantasy-a")
            assert equipment_node["root_id"] == "lightsaber-cyber-a"

            # Verify journal/memory preservation
            assert len(data["character"]["journal"]) == 1
            assert "cyber wars" in data["character"]["journal"][0]["content"]

    def test_return_to_cyberpunk(self, test_client):
        """Test returning to cyberpunk theme from fantasy."""
        transition_request = {
            "new_theme": "cyberpunk",
            "chapter_id": "chapter-3",
            "preserve_memory": True,
            "equipment_transitions": [
                {
                    "equipment_id": "lightsaber-fantasy-a",
                    "transition_type": "theme_reset"
                }
            ]
        }

        with patch('app.services.character_service.get_character') as mock_get, \
             patch('app.services.theme_service.transition_theme') as mock_transition:
            # Mock current fantasy character
            mock_get.return_value = {
                "id": "yoda-fantasy-a",
                "parent_id": "yoda-cyber-a",
                "name": "Yoda",
                "species": "Unknown Species",
                "class_name": "Mystic",
                "theme": "fantasy",
                "equipment": [
                    {
                        "id": "lightsaber-fantasy-a",
                        "root_id": "lightsaber-cyber-a",
                        "name": "Energy Staff",
                        "type": "weapon",
                        "theme": "fantasy"
                    }
                ],
                "journal": [
                    {
                        "id": "entry-1",
                        "content": "Fought in the cyber wars"
                    },
                    {
                        "id": "entry-2",
                        "content": "Defended the mystical temple"
                    }
                ]
            }

            # Mock theme transition response
            mock_transition.return_value = {
                "character": {
                    "id": "yoda-cyber-b",
                    "parent_id": "yoda-fantasy-a",
                    "name": "Yoda",
                    "species": "Unknown Alien",
                    "class_name": "Tech Master",
                    "theme": "cyberpunk",
                    "equipment": [
                        {
                            "id": "lightsaber-cyber-a",  # Original cyber version
                            "name": "Energy Blade",
                            "type": "weapon",
                            "theme": "cyberpunk"
                        }
                    ],
                    "journal": [
                        {
                            "id": "entry-1",
                            "content": "Fought in the cyber wars"
                        },
                        {
                            "id": "entry-2",
                            "content": "Defended the mystical temple"
                        }
                    ]
                },
                "version_graph": {
                    "nodes": [
                        {
                            "id": "yoda-cyber-a",
                            "type": "character",
                            "theme": "cyberpunk"
                        },
                        {
                            "id": "yoda-fantasy-a",
                            "type": "character",
                            "theme": "fantasy",
                            "parent_id": "yoda-cyber-a"
                        },
                        {
                            "id": "yoda-cyber-b",
                            "type": "character",
                            "theme": "cyberpunk",
                            "parent_id": "yoda-fantasy-a"
                        },
                        {
                            "id": "lightsaber-cyber-a",
                            "type": "equipment",
                            "theme": "cyberpunk"
                        }
                    ],
                    "edges": [
                        {
                            "from": "yoda-fantasy-a",
                            "to": "yoda-cyber-a",
                            "type": "parent"
                        },
                        {
                            "from": "yoda-cyber-b",
                            "to": "yoda-fantasy-a",
                            "type": "parent"
                        }
                    ]
                }
            }

            response = test_client.post(
                f"/api/v2/characters/yoda-fantasy-a/theme-transition",
                json=transition_request
            )
            assert response.status_code == status.HTTP_200_OK

            # Verify the response structure
            data = response.json()
            assert data["character"]["id"] == "yoda-cyber-b"
            assert data["character"]["parent_id"] == "yoda-fantasy-a"
            
            # Verify full version chain
            nodes = data["version_graph"]["nodes"]
            cyber_b = next(n for n in nodes if n["id"] == "yoda-cyber-b")
            fantasy_a = next(n for n in nodes if n["id"] == "yoda-fantasy-a")
            assert cyber_b["parent_id"] == "yoda-fantasy-a"
            assert fantasy_a["parent_id"] == "yoda-cyber-a"

            # Verify equipment reset to original cyberpunk version
            equipment = data["character"]["equipment"][0]
            assert equipment["id"] == "lightsaber-cyber-a"
            assert equipment["theme"] == "cyberpunk"

            # Verify all journal entries are preserved
            journal = data["character"]["journal"]
            assert len(journal) == 2
            assert any("cyber wars" in entry["content"] for entry in journal)
            assert any("mystical temple" in entry["content"] for entry in journal)

    def test_equipment_only_theme_change(self, test_client):
        """Test changing just equipment theme without full character transition."""
        transition_request = {
            "theme": "steampunk",
            "adaptation_level": "minor"
        }

        with patch('app.services.content_service.adapt_theme') as mock_adapt:
            # Mock theme adaptation response
            mock_adapt.return_value = {
                "id": "lightsaber-steam-a",
                "root_id": "lightsaber-cyber-a",
                "name": "Steam-powered Energy Blade",
                "type": "weapon",
                "theme": "steampunk",
                "properties": {
                    "damage": "1d10",
                    "damage_type": "energy",
                    "power_source": "steam"
                }
            }

            response = test_client.post(
                f"/api/v2/content/lightsaber-cyber-a/theme-transition",
                json=transition_request
            )
            assert response.status_code == status.HTTP_200_OK

            # Verify the adapted equipment
            data = response.json()
            assert data["id"] == "lightsaber-steam-a"
            assert data["root_id"] == "lightsaber-cyber-a"  # Links back to original
            assert "steam" in data["properties"]["power_source"].lower()
