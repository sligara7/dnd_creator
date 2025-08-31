"""Inventory API Tests"""

import pytest
from fastapi.testclient import TestClient

def test_list_inventory_items(client: TestClient, test_character, test_inventory_item):
    """Test listing inventory items."""
    response = client.get(f"/api/v2/inventory?character_id={test_character.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["item_data"]["name"] == "Test Sword"

def test_get_inventory_item(client: TestClient, test_character, test_inventory_item):
    """Test getting a specific inventory item."""
    response = client.get(
        f"/api/v2/inventory/{test_inventory_item.id}?character_id={test_character.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["item_data"]["name"] == "Test Sword"
    assert data["character_id"] == test_character.id
    assert data["quantity"] == 1

def test_create_inventory_item(client: TestClient, test_character):
    """Test inventory item creation."""
    item_data = {
        "character_id": test_character.id,
        "item_data": {
            "name": "New Bow",
            "type": "weapon",
            "damage": "1d8",
            "properties": ["ammunition", "range"]
        },
        "quantity": 1
    }
    response = client.post("/api/v2/inventory", json=item_data)
    assert response.status_code == 200
    data = response.json()
    assert data["item_data"]["name"] == "New Bow"
    assert data["character_id"] == test_character.id
    assert data["quantity"] == 1

def test_direct_edit_inventory_item(client: TestClient, test_character, test_inventory_item):
    """Test direct inventory item edit."""
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
        f"/api/v2/inventory/{test_inventory_item.id}/direct-edit?character_id={test_character.id}"
        json=edit_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["item_data"]["name"] == "Enchanted Sword"
    assert data["item_data"]["damage"] == "2d8"
    assert "magical" in data["item_data"]["properties"]
    assert data["quantity"] == 2
    assert data["user_modified"] is True

def test_delete_inventory_item(client: TestClient, test_character, test_inventory_item):
    """Test inventory item deletion."""
    response = client.delete(
        f"/api/v2/inventory/{test_inventory_item.id}?character_id={test_character.id}"
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Inventory item deleted successfully"

    # Verify item is deleted
    response = client.get(
        f"/api/v2/inventory/{test_inventory_item.id}?character_id={test_character.id}"
    )
    assert response.status_code == 404

def test_list_inventory_items_invalid_character(client: TestClient):
    """Test listing inventory items for invalid character."""
    response = client.get("/api/v2/inventory?character_id=999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Character not found"

def test_create_inventory_item_invalid_character(client: TestClient):
    """Test creating inventory item for invalid character."""
    item_data = {
        "character_id": 999999,
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
