"""Inventory API Tests"""

from fastapi.testclient import TestClient
from tests.api.test_characters import create_test_character

def create_test_item(client: TestClient, character_id: str, name: str = "Test Sword") -> dict:
    """Helper to create a test inventory item via HTTP."""
    item_data = {
        "character_id": character_id,
        "item_data": {
            "name": name,
            "type": "weapon",
            "damage": "1d8",
            "properties": ["versatile"]
        },
        "quantity": 1
    }
    response = client.post("/api/v2/inventory", json=item_data)
    assert response.status_code == 200
    return response.json()

def test_list_inventory_items(client: TestClient):
    """Test listing inventory items."""
    # Create test character and item
    character = create_test_character(client)
    item = create_test_item(client, character["id"])
    
    # Test listing
    response = client.get(f"/api/v2/inventory?character_id={character['id']}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(i["id"] == item["id"] for i in data)

def test_get_inventory_item(client: TestClient):
    """Test getting a specific inventory item."""
    # Create test character and item
    character = create_test_character(client)
    item = create_test_item(client, character["id"])
    
    # Test retrieval
    response = client.get(f"/api/v2/inventory/{item['id']}?character_id={character['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["item_data"]["name"] == item["item_data"]["name"]

def test_create_inventory_item(client: TestClient):
    """Test inventory item creation."""
    character = create_test_character(client)
    item = create_test_item(client, character["id"], name="New Bow")
    assert item["item_data"]["name"] == "New Bow"
    assert item["character_id"] == character["id"]

def test_direct_edit_inventory_item(client: TestClient):
    """Test direct inventory item edit."""
    # Create test character and item
    character = create_test_character(client)
    item = create_test_item(client, character["id"])
    
    # Test direct edit
    edit_data = {
        "updates": {
            "item_data": {
                "name": "Enchanted Sword",
                "type": "weapon",
                "damage": "2d8",
                "properties": ["versatile", "magical"]
            },
            "quantity": 2
        },
        "notes": "Testing inventory item direct edit"
    }
    response = client.post(
        f"/api/v2/inventory/{item['id']}/direct-edit?character_id={character['id']}",
        json=edit_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["item_data"]["name"] == "Enchanted Sword"
    assert data["quantity"] == 2

def test_delete_inventory_item(client: TestClient):
    """Test inventory item deletion."""
    # Create test character and item
    character = create_test_character(client)
    item = create_test_item(client, character["id"])
    
    # Test deletion
    response = client.delete(f"/api/v2/inventory/{item['id']}?character_id={character['id']}")
    assert response.status_code == 200
    
    # Verify item is deleted
    response = client.get(f"/api/v2/inventory/{item['id']}?character_id={character['id']}")
    assert response.status_code == 404

def test_list_inventory_items_invalid_character(client: TestClient):
    """Test listing inventory items for invalid character."""
    response = client.get("/api/v2/inventory?character_id=999999")
    assert response.status_code == 404

def test_create_inventory_item_invalid_character(client: TestClient):
    """Test creating inventory item for invalid character."""
    item_data = {
"character_id": "999999",
        "item_data": {
            "name": "Invalid Item",
            "type": "weapon",
            "damage": "1d8"
        },
        "quantity": 1
    }
    response = client.post("/api/v2/inventory", json=item_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Character not found"
