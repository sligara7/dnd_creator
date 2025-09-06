"""Test inventory models."""
import uuid
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.domain.inventory import (
    InventoryItem,
    Container,
    MagicItem,
    ItemEffect,
    ItemLocation,
    ItemType,
    AttunementState,
    EffectType,
    DurationType,
    ActivationType,
)


async def test_create_inventory_item(test_session: AsyncSession):
    """Test creating an inventory item."""
    # Create test data
    character_id = uuid.uuid4()
    item = InventoryItem(
        character_id=character_id,
        name="Test Item",
        item_type=ItemType.WEAPON,
        location=ItemLocation.CARRIED,
        quantity=1,
        weight=1.5,
        value=100,
        description="A test item",
        metadata={"damage": "1d6"},
    )
    test_session.add(item)
    await test_session.flush()

    # Verify item exists
    query = select(InventoryItem).where(InventoryItem.id == item.id)
    result = await test_session.execute(query)
    stored_item = result.scalar_one()

    # Check all fields
    assert stored_item.character_id == character_id
    assert stored_item.name == "Test Item"
    assert stored_item.item_type == ItemType.WEAPON
    assert stored_item.location == ItemLocation.CARRIED
    assert stored_item.quantity == 1
    assert stored_item.weight == 1.5
    assert stored_item.value == 100
    assert stored_item.description == "A test item"
    assert stored_item.metadata == {"damage": "1d6"}
    assert stored_item.is_deleted is False
    assert stored_item.created_at is not None
    assert stored_item.updated_at is not None


async def test_create_container(test_session: AsyncSession):
    """Test creating a container."""
    # Create test data
    character_id = uuid.uuid4()
    container = Container(
        character_id=character_id,
        name="Backpack",
        capacity=30.0,
        capacity_type="weight",
        description="A sturdy backpack",
        metadata={"material": "leather"},
    )
    test_session.add(container)
    await test_session.flush()

    # Verify container exists
    query = select(Container).where(Container.id == container.id)
    result = await test_session.execute(query)
    stored_container = result.scalar_one()

    # Check all fields
    assert stored_container.character_id == character_id
    assert stored_container.name == "Backpack"
    assert stored_container.capacity == 30.0
    assert stored_container.capacity_type == "weight"
    assert stored_container.description == "A sturdy backpack"
    assert stored_container.metadata == {"material": "leather"}
    assert stored_container.is_deleted is False
    assert stored_container.created_at is not None
    assert stored_container.updated_at is not None


async def test_container_items_relationship(test_session: AsyncSession):
    """Test container-items relationship."""
    # Create test data
    character_id = uuid.uuid4()

    # Create container
    container = Container(
        character_id=character_id,
        name="Backpack",
        capacity=30.0,
        capacity_type="weight",
    )
    test_session.add(container)

    # Create items
    items = [
        InventoryItem(
            character_id=character_id,
            name=f"Item {i}",
            item_type=ItemType.MISC,
            location=ItemLocation.CONTAINER,
            container_id=container.id,
            weight=1.0,
        )
        for i in range(3)
    ]
    test_session.add_all(items)
    await test_session.flush()

    # Verify relationships
    query = select(Container).where(Container.id == container.id)
    result = await test_session.execute(query)
    stored_container = result.scalar_one()

    assert len(stored_container.container_items) == 3
    assert all(item.container_id == container.id for item in stored_container.container_items)


async def test_create_magic_item(test_session: AsyncSession):
    """Test creating a magic item."""
    # Create test data
    character_id = uuid.uuid4()
    magic_item = MagicItem(
        character_id=character_id,
        name="Ring of Protection",
        description="A magical ring that protects its wearer",
        requires_attunement=True,
        max_charges=3,
        charges=3,
        recharge_type="dawn",
        recharge_amount=1,
        restrictions="No evil alignment",
        metadata={"rarity": "rare"},
    )
    test_session.add(magic_item)
    await test_session.flush()

    # Verify item exists
    query = select(MagicItem).where(MagicItem.id == magic_item.id)
    result = await test_session.execute(query)
    stored_item = result.scalar_one()

    # Check all fields
    assert stored_item.character_id == character_id
    assert stored_item.name == "Ring of Protection"
    assert stored_item.description == "A magical ring that protects its wearer"
    assert stored_item.requires_attunement is True
    assert stored_item.max_charges == 3
    assert stored_item.charges == 3
    assert stored_item.recharge_type == "dawn"
    assert stored_item.recharge_amount == 1
    assert stored_item.restrictions == "No evil alignment"
    assert stored_item.metadata == {"rarity": "rare"}
    assert stored_item.attunement_state == AttunementState.NONE
    assert stored_item.attunement_date is None
    assert stored_item.last_recharged is None
    assert stored_item.is_deleted is False
    assert stored_item.created_at is not None
    assert stored_item.updated_at is not None


async def test_magic_item_effects(test_session: AsyncSession):
    """Test magic item effects."""
    # Create test data
    character_id = uuid.uuid4()

    # Create magic item
    magic_item = MagicItem(
        character_id=character_id,
        name="Staff of Healing",
        description="A staff with healing powers",
    )
    test_session.add(magic_item)

    # Create effects
    effects = [
        ItemEffect(
            item_id=magic_item.id,
            name="Cure Wounds",
            description="Heals target for 2d8+2",
            effect_type=EffectType.HEALING,
            duration_type=DurationType.INSTANTANEOUS,
            activation_type=ActivationType.ACTION,
            activation_cost="1 charge",
            saving_throw="None",
            metadata={"range": "touch"},
        ),
        ItemEffect(
            item_id=magic_item.id,
            name="Lesser Restoration",
            description="Removes one condition",
            effect_type=EffectType.HEALING,
            duration_type=DurationType.INSTANTANEOUS,
            activation_type=ActivationType.ACTION,
            activation_cost="2 charges",
            saving_throw="None",
            metadata={"range": "touch"},
        ),
    ]
    test_session.add_all(effects)
    await test_session.flush()

    # Verify relationships
    query = select(MagicItem).where(MagicItem.id == magic_item.id)
    result = await test_session.execute(query)
    stored_item = result.scalar_one()

    assert len(stored_item.effects) == 2
    assert all(effect.item_id == magic_item.id for effect in stored_item.effects)
    assert all(isinstance(effect, ItemEffect) for effect in stored_item.effects)


async def test_inventory_soft_delete(test_session: AsyncSession):
    """Test soft delete functionality."""
    # Create test data
    character_id = uuid.uuid4()
    delete_time = datetime.utcnow()

    # Create items
    items = [
        InventoryItem(
            character_id=character_id,
            name=f"Item {i}",
            item_type=ItemType.MISC,
            is_deleted=i == 0,
            deleted_at=delete_time if i == 0 else None,
        )
        for i in range(2)
    ]
    test_session.add_all(items)
    await test_session.flush()

    # Query all items
    query = select(InventoryItem).where(InventoryItem.character_id == character_id)
    result = await test_session.execute(query)
    all_items = result.scalars().all()

    # Query active items
    active_query = select(InventoryItem).where(
        InventoryItem.character_id == character_id,
        InventoryItem.is_deleted.is_(False),
    )
    active_result = await test_session.execute(active_query)
    active_items = active_result.scalars().all()

    assert len(all_items) == 2
    assert len(active_items) == 1
    assert any(item.is_deleted and item.deleted_at == delete_time for item in all_items)
    assert all(not item.is_deleted and item.deleted_at is None for item in active_items)
