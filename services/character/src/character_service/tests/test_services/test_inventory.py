"""Test inventory service."""
import uuid
import pytest
from datetime import datetime
from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession
from character_service.core.exceptions import (
    ValidationError,
    InventoryError,
    ResourceExhaustedError,
    StateError,
)
from character_service.services.inventory import InventoryService
from character_service.domain.inventory import (
    InventoryItem,
    Container,
    MagicItem,
    ItemLocation,
    ItemType,
)


@pytest.fixture
async def inventory_service(test_session: AsyncSession) -> InventoryService:
    """Create an inventory service."""
    return InventoryService(test_session)


@pytest.fixture
async def test_character() -> Dict:
    """Create test character data."""
    return {"id": uuid.uuid4()}


@pytest.fixture
async def test_inventory(
    test_session: AsyncSession,
    test_character: Dict,
) -> Dict:
    """Create test inventory data."""
    # Create container
    container = Container(
        character_id=test_character["id"],
        name="Backpack",
        capacity=30.0,
        capacity_type="weight",
    )
    test_session.add(container)

    # Create items
    sword = InventoryItem(
        character_id=test_character["id"],
        name="Sword",
        item_type=ItemType.WEAPON,
        location=ItemLocation.CARRIED,
        weight=3.0,
        value=1500,
    )
    potion = InventoryItem(
        character_id=test_character["id"],
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
    inventory_service: InventoryService,
    test_character: Dict,
    test_inventory: Dict,
):
    """Test getting inventory items."""
    # Get all items
    items = await inventory_service.get_inventory(
        character_id=test_character["id"],
    )
    assert len(items) == 2

    # Filter by location
    carried_items = await inventory_service.get_inventory(
        character_id=test_character["id"],
        location=ItemLocation.CARRIED,
    )
    assert len(carried_items) == 1
    assert carried_items[0].name == "Sword"

    # Filter by type
    potions = await inventory_service.get_inventory(
        character_id=test_character["id"],
        item_type=ItemType.POTION,
    )
    assert len(potions) == 1
    assert potions[0].name == "Healing Potion"

    # Filter by container
    container_items = await inventory_service.get_inventory(
        character_id=test_character["id"],
        container_id=test_inventory["container"].id,
    )
    assert len(container_items) == 1
    assert container_items[0].name == "Healing Potion"


async def test_move_item(
    inventory_service: InventoryService,
    test_character: Dict,
    test_inventory: Dict,
):
    """Test moving items."""
    # Move sword to container
    moved_sword = await inventory_service.move_item(
        character_id=test_character["id"],
        item_id=test_inventory["sword"].id,
        location=ItemLocation.CONTAINER,
        container_id=test_inventory["container"].id,
    )
    assert moved_sword.location == ItemLocation.CONTAINER
    assert moved_sword.container_id == test_inventory["container"].id

    # Move potion to carried
    moved_potion = await inventory_service.move_item(
        character_id=test_character["id"],
        item_id=test_inventory["potion"].id,
        location=ItemLocation.CARRIED,
    )
    assert moved_potion.location == ItemLocation.CARRIED
    assert moved_potion.container_id is None


async def test_update_quantity(
    inventory_service: InventoryService,
    test_character: Dict,
    test_inventory: Dict,
):
    """Test updating item quantity."""
    # Update potion quantity
    updated_potion = await inventory_service.update_quantity(
        character_id=test_character["id"],
        item_id=test_inventory["potion"].id,
        quantity=5,
    )
    assert updated_potion.quantity == 5

    # Invalid quantity
    with pytest.raises(ValidationError):
        await inventory_service.update_quantity(
            character_id=test_character["id"],
            item_id=test_inventory["potion"].id,
            quantity=-1,
        )


async def test_delete_item(
    inventory_service: InventoryService,
    test_character: Dict,
    test_inventory: Dict,
):
    """Test deleting items."""
    # Soft delete
    await inventory_service.delete_item(
        character_id=test_character["id"],
        item_id=test_inventory["sword"].id,
    )
    items = await inventory_service.get_inventory(
        character_id=test_character["id"],
    )
    assert len(items) == 1
    assert test_inventory["sword"].is_deleted
    assert test_inventory["sword"].deleted_at is not None

    # Permanent delete
    await inventory_service.delete_item(
        character_id=test_character["id"],
        item_id=test_inventory["potion"].id,
        permanent=True,
    )
    items = await inventory_service.get_inventory(
        character_id=test_character["id"],
        include_deleted=True,
    )
    assert len(items) == 1


async def test_calculate_weight(
    inventory_service: InventoryService,
    test_character: Dict,
    test_inventory: Dict,
):
    """Test weight calculation."""
    # Calculate total weight
    total_weight = await inventory_service.calculate_weight(
        character_id=test_character["id"],
    )
    assert total_weight == 4.5  # sword(3.0) + 3 potions(0.5 each)

    # Calculate carried weight
    carried_weight = await inventory_service.calculate_weight(
        character_id=test_character["id"],
        location=ItemLocation.CARRIED,
    )
    assert carried_weight == 3.0  # sword only

    # Calculate container weight
    container_weight = await inventory_service.calculate_weight(
        character_id=test_character["id"],
        container_id=test_inventory["container"].id,
    )
    assert container_weight == 1.5  # 3 potions


async def test_manage_currency(
    inventory_service: InventoryService,
    test_character: Dict,
):
    """Test currency management."""
    # Add currency
    currency = await inventory_service.manage_currency(
        character_id=test_character["id"],
        currency_type="gp",
        amount=100,
        operation="add",
    )
    assert currency["gp"] == 100

    # Add more currency
    currency = await inventory_service.manage_currency(
        character_id=test_character["id"],
        currency_type="sp",
        amount=50,
        operation="add",
    )
    assert currency["gp"] == 100
    assert currency["sp"] == 50

    # Remove currency
    currency = await inventory_service.manage_currency(
        character_id=test_character["id"],
        currency_type="gp",
        amount=50,
        operation="remove",
    )
    assert currency["gp"] == 50

    # Invalid operation
    with pytest.raises(ValidationError):
        await inventory_service.manage_currency(
            character_id=test_character["id"],
            currency_type="gp",
            amount=50,
            operation="invalid",
        )

    # Insufficient funds
    with pytest.raises(ValidationError):
        await inventory_service.manage_currency(
            character_id=test_character["id"],
            currency_type="gp",
            amount=100,
            operation="remove",
        )
