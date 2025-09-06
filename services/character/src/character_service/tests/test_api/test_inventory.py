"""Test inventory API endpoints."""
import uuid
import pytest
from httpx import AsyncClient
from fastapi import status

from character_service.domain.inventory import (
    InventoryItem,
    Container,
    ItemLocation,
    ItemType,
)


@pytest.fixture
async def test_character(test_session):
    """Create test character data."""
    return {"id": str(uuid.uuid4())}


@pytest.fixture
async def test_inventory(test_session, test_character):
    """Create test inventory data."""
    # Create container
    container = Container(
        character_id=uuid.UUID(test_character["id"]),
        name="Backpack",
        capacity=30.0,
        capacity_type="weight",
    )
    test_session.add(container)

    # Create items
    sword = InventoryItem(
        character_id=uuid.UUID(test_character["id"]),
        name="Sword",
        item_type=ItemType.WEAPON,
        location=ItemLocation.CARRIED,
        weight=3.0,
        value=1500,
    )
    potion = InventoryItem(
        character_id=uuid.UUID(test_character["id"]),
        name="Healing Potion",
        item_type=ItemType.POTION,
        location=ItemLocation.CONTAINER,
        container_id=container.id,
        weight=0.5,
        value=50,
        quantity=3,
    )
    test_session.add_all([sword, potion])
    await test_session.flush()

    return {
        "container": container,
        "sword": sword,
        "potion": potion,
    }


async def test_get_inventory(
    async_client: AsyncClient,
    test_character,
    test_inventory,
):
    """Test GET /characters/{id}/inventory."""
    # Get all items
    response = await async_client.get(
        f"/api/v2/characters/{test_character['id']}/inventory",
    )
    assert response.status_code == status.HTTP_200_OK
    items = response.json()
    assert len(items) == 2

    # Filter by location
    response = await async_client.get(
        f"/api/v2/characters/{test_character['id']}/inventory",
        params={"location": "carried"},
    )
    assert response.status_code == status.HTTP_200_OK
    items = response.json()
    assert len(items) == 1
    assert items[0]["name"] == "Sword"

    # Filter by type
    response = await async_client.get(
        f"/api/v2/characters/{test_character['id']}/inventory",
        params={"item_type": "potion"},
    )
    assert response.status_code == status.HTTP_200_OK
    items = response.json()
    assert len(items) == 1
    assert items[0]["name"] == "Healing Potion"


async def test_add_item(
    async_client: AsyncClient,
    test_character,
):
    """Test POST /characters/{id}/inventory."""
    # Add new item
    item_data = {
        "name": "Dagger",
        "item_type": "weapon",
        "location": "carried",
        "weight": 1.0,
        "value": 200,
    }
    response = await async_client.post(
        f"/api/v2/characters/{test_character['id']}/inventory",
        json=item_data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    created_item = response.json()
    assert created_item["name"] == "Dagger"

    # Invalid item type
    item_data["item_type"] = "invalid"
    response = await async_client.post(
        f"/api/v2/characters/{test_character['id']}/inventory",
        json=item_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_update_item(
    async_client: AsyncClient,
    test_character,
    test_inventory,
):
    """Test PUT /characters/{id}/inventory/{item_id}."""
    # Update quantity
    update_data = {
        "quantity": 5,
    }
    response = await async_client.put(
        f"/api/v2/characters/{test_character['id']}/inventory/{test_inventory['potion'].id}",
        json=update_data,
    )
    assert response.status_code == status.HTTP_200_OK
    updated_item = response.json()
    assert updated_item["quantity"] == 5

    # Invalid quantity
    update_data["quantity"] = -1
    response = await async_client.put(
        f"/api/v2/characters/{test_character['id']}/inventory/{test_inventory['potion'].id}",
        json=update_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_delete_item(
    async_client: AsyncClient,
    test_character,
    test_inventory,
):
    """Test DELETE /characters/{id}/inventory/{item_id}."""
    # Delete item
    response = await async_client.delete(
        f"/api/v2/characters/{test_character['id']}/inventory/{test_inventory['sword'].id}",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify deletion
    response = await async_client.get(
        f"/api/v2/characters/{test_character['id']}/inventory",
    )
    assert response.status_code == status.HTTP_200_OK
    items = response.json()
    assert len(items) == 1


async def test_move_item(
    async_client: AsyncClient,
    test_character,
    test_inventory,
):
    """Test PUT /characters/{id}/inventory/{item_id}/move."""
    # Move sword to container
    response = await async_client.put(
        f"/api/v2/characters/{test_character['id']}/inventory/{test_inventory['sword'].id}/move",
        params={
            "location": "container",
            "container_id": str(test_inventory["container"].id),
        },
    )
    assert response.status_code == status.HTTP_200_OK
    moved_item = response.json()
    assert moved_item["location"] == "container"
    assert moved_item["container_id"] == str(test_inventory["container"].id)


async def test_calculate_weight(
    async_client: AsyncClient,
    test_character,
    test_inventory,
):
    """Test GET /characters/{id}/inventory/weight."""
    # Calculate total weight
    response = await async_client.get(
        f"/api/v2/characters/{test_character['id']}/inventory/weight",
    )
    assert response.status_code == status.HTTP_200_OK
    weight_data = response.json()
    assert weight_data["total_weight"] == 4.5  # sword(3.0) + 3 potions(0.5 each)

    # Calculate carried weight
    response = await async_client.get(
        f"/api/v2/characters/{test_character['id']}/inventory/weight",
        params={"location": "carried"},
    )
    assert response.status_code == status.HTTP_200_OK
    weight_data = response.json()
    assert weight_data["total_weight"] == 3.0  # sword only


async def test_manage_currency(
    async_client: AsyncClient,
    test_character,
):
    """Test currency endpoints."""
    # Add currency
    response = await async_client.post(
        f"/api/v2/characters/{test_character['id']}/inventory/currency/gp",
        params={"amount": 100, "operation": "add"},
    )
    assert response.status_code == status.HTTP_200_OK
    currency_data = response.json()
    assert currency_data["gp"] == 100

    # Get currency
    response = await async_client.get(
        f"/api/v2/characters/{test_character['id']}/inventory/currency",
    )
    assert response.status_code == status.HTTP_200_OK
    currency_data = response.json()
    assert currency_data["gp"] == 100

    # Invalid operation
    response = await async_client.post(
        f"/api/v2/characters/{test_character['id']}/inventory/currency/gp",
        params={"amount": 50, "operation": "invalid"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_container_endpoints(
    async_client: AsyncClient,
    test_character,
):
    """Test container endpoints."""
    # Create container
    container_data = {
        "name": "Chest",
        "capacity": 100.0,
        "capacity_type": "weight",
        "description": "A large wooden chest",
    }
    response = await async_client.post(
        f"/api/v2/characters/{test_character['id']}/inventory/containers",
        json=container_data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    created_container = response.json()
    assert created_container["name"] == "Chest"

    # Get containers
    response = await async_client.get(
        f"/api/v2/characters/{test_character['id']}/inventory/containers",
    )
    assert response.status_code == status.HTTP_200_OK
    containers = response.json()
    assert len(containers) == 1

    # Update container
    update_data = {
        "name": "Large Chest",
        "capacity": 150.0,
    }
    response = await async_client.put(
        f"/api/v2/characters/{test_character['id']}/inventory/containers/{created_container['id']}",
        json=update_data,
    )
    assert response.status_code == status.HTTP_200_OK
    updated_container = response.json()
    assert updated_container["name"] == "Large Chest"
    assert updated_container["capacity"] == 150.0
