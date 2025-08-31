"""Character API Tests"""

import pytest
from fastapi.testclient import TestClient

def test_list_characters(client: TestClient, test_character):
    """Test listing characters."""
    response = client.get("/api/v2/characters")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == test_character.name

def test_get_character(client: TestClient, test_character):
    """Test getting a specific character."""
    response = client.get(f"/api/v2/characters/{test_character.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_character.name
    assert data["user_id"] == test_character.user_id

def test_create_character(client: TestClient):
    """Test character creation."""
    character_data = {
        "name": "New Character",
        "user_id": "test_user",
        "campaign_id": "test_campaign",
        "character_data": {
            "species": "Human",
            "background": "Folk Hero",
            "level": 1,
            "character_classes": {"Fighter": 1},
            "abilities": {
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8
            }
        }
    }
    response = client.post("/api/v2/characters", json=character_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Character"
    assert data["user_id"] == "test_user"

def test_update_character(client: TestClient, test_character):
    """Test character update."""
    update_data = {
        "name": "Updated Character",
        "user_id": test_character.user_id,
        "campaign_id": test_character.campaign_id,
        "character_data": test_character.character_data
    }
    response = client.put(f"/api/v2/characters/{test_character.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Character"

def test_delete_character(client: TestClient, test_character):
    """Test character deletion."""
    response = client.delete(f"/api/v2/characters/{test_character.id}")
    assert response.status_code == 200
    
    # Verify character is deleted
    response = client.get(f"/api/v2/characters/{test_character.id}")
    assert response.status_code == 404

def test_direct_edit_character(client: TestClient, test_character):
    """Test direct character edit."""
    edit_data = {
        "updates": {
            "name": "Directly Edited Character",
            "character_data": {
                **test_character.character_data,
                "level": 2,
                "character_classes": {"Fighter": 2}
            }
        },
        "notes": "Testing direct edit functionality"
    }
    response = client.post(f"/api/v2/characters/{test_character.id}/direct-edit", json=edit_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Directly Edited Character"
    assert data["character_data"]["level"] == 2
    assert data["user_modified"] is True
