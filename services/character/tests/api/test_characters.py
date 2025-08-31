"""Character API Tests"""

from fastapi.testclient import TestClient

def create_test_character(client: TestClient, name: str = "Test Character") -> dict:
    """Helper to create a test character via HTTP."""
    character_data = {
        "name": name,
        "race": "Human",
        "class_": "Fighter",
        "background": "Folk Hero",
        "alignment": "Lawful Good",
        "data": {
            "abilities": {
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8
            },
            "skills": ["Athletics", "Intimidation"],
            "equipment": {"weapons": ["Longsword", "Shield"]}
        }
    }
    response = client.post("/api/v2/characters", json=character_data)
    assert response.status_code == 200
    return response.json()

def test_list_characters(client: TestClient):
    """Test listing characters."""
    # Create a test character first
    character = create_test_character(client)
    
    # Test listing
    response = client.get("/api/v2/characters")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(c["id"] == character["id"] for c in data)

def test_get_character(client: TestClient):
    """Test getting a specific character."""
    # Create a test character first
    character = create_test_character(client)
    
    # Test retrieval
    response = client.get(f"/api/v2/characters/{character['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == character["name"]
    assert data["user_id"] == character["user_id"]

def test_create_character(client: TestClient):
    """Test character creation."""
    character = create_test_character(client, name="New Character")
    assert character["name"] == "New Character"
    assert character["user_id"] == "test_user"
    assert character["character_data"]["species"] == "Human"

def test_update_character(client: TestClient):
    """Test character update."""
    # Create a test character first
    character = create_test_character(client)
    
    # Test update
    update_data = {
        "name": "Updated Character",
        "race": character["race"],
        "class_": character["class_"],
        "background": character["background"],
        "alignment": character["alignment"],
        "data": character["data"]
    }
    response = client.put(f"/api/v2/characters/{character['id']}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Character"

def test_delete_character(client: TestClient):
    """Test character deletion."""
    # Create a test character first
    character = create_test_character(client)
    
    # Test deletion
    response = client.delete(f"/api/v2/characters/{character['id']}")
    assert response.status_code == 200
    
    # Verify character is deleted
    response = client.get(f"/api/v2/characters/{character['id']}")
    assert response.status_code == 404

def test_direct_edit_character(client: TestClient):
    """Test direct character edit."""
    # Create a test character first
    character = create_test_character(client)
    
    # Test direct edit
    edit_data = {
        "updates": {
            "name": "Directly Edited Character",
            "character_data": {
                **character["character_data"],
                "level": 2,
                "character_classes": {"Fighter": 2}
            }
        },
        "notes": "Testing direct edit functionality"
    }
    response = client.post(f"/api/v2/characters/{character['id']}/direct-edit", json=edit_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Directly Edited Character"
    assert data["level"] == 2  # Level is now a top-level field
    assert data["user_modified"] is True
