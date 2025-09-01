"""Character API Tests"""

import pytest
from uuid import uuid4
from httpx import AsyncClient

async def create_test_character(client: AsyncClient, name: str = "Test Character") -> dict:
    """Helper to create a test character via HTTP."""
    character_data = {
        "name": name,
        "user_id": str(uuid4()),
        "campaign_id": str(uuid4()),
        "character_data": {
            "species": "Human",
            "background": "Folk Hero",
            "level": 1,
            "class_": "Fighter",
            "alignment": "Lawful Good",
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
    response = await client.post("/api/v2/characters", json=character_data)
    assert response.status_code == 200
    return response.json()

@pytest.mark.asyncio
async def test_list_characters(client: AsyncClient):
    """Test listing characters."""
    # Create a test character first
    character = await create_test_character(client)
    
    # Test listing
    response = await client.get("/api/v2/characters")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(c["id"] == character["id"] for c in data)

@pytest.mark.asyncio
async def test_get_character(client: AsyncClient):
    """Test getting a specific character."""
    # Create a test character first
    character = await create_test_character(client)
    
    # Test retrieval
    response = await client.get(f"/api/v2/characters/{character['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == character["name"]
    assert isinstance(data["user_id"], str)  # Should be a UUID string

@pytest.mark.asyncio
async def test_create_character(client: AsyncClient):
    """Test character creation."""
    character = await create_test_character(client, name="New Character")
    assert character["name"] == "New Character"
    assert isinstance(character["user_id"], str)  # Should be a UUID string
    assert isinstance(character["campaign_id"], str)  # Should be a UUID string
    assert character["character_data"]["species"] == "Human"

@pytest.mark.asyncio
async def test_update_character(client: AsyncClient):
    """Test character update."""
    # Create a test character first
    character = await create_test_character(client)
    
    # Test update
    update_data = {
        "name": "Updated Character",
        "user_id": character["user_id"],
        "campaign_id": character["campaign_id"],
        "character_data": character["character_data"]
    }
    response = await client.put(f"/api/v2/characters/{character['id']}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Character"

@pytest.mark.asyncio
async def test_delete_character(client: AsyncClient):
    """Test character deletion."""
    # Create a test character first
    character = await create_test_character(client)
    
    # Test deletion
    response = await client.delete(f"/api/v2/characters/{character['id']}")
    assert response.status_code == 200
    
    # Verify character is deleted
    response = await client.get(f"/api/v2/characters/{character['id']}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_direct_edit_character(client: AsyncClient):
    """Test direct character edit."""
    # Create a test character first
    character = await create_test_character(client)
    
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
    response = await client.post(f"/api/v2/characters/{character['id']}/direct-edit", json=edit_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Directly Edited Character"
    assert data["character_data"]["level"] == 2  # Level is in character_data
    assert data["character_data"]["character_classes"]["Fighter"] == 2
