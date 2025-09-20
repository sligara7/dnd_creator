"""Inventory repository module."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from character_service.models.models import InventoryItem
from character_service.schemas.schemas import InventoryItemCreate, InventoryItemUpdate
from character_service.clients.storage_port import StoragePort

class InventoryRepository:
    """Inventory repository."""

    def __init__(self, storage: StoragePort):
        self.storage = storage

    async def create(self, item: InventoryItemCreate) -> InventoryItem:
        """Create a new inventory item"""
        # Create using storage service
        result = await self.storage.create_inventory_item(item.dict())
        return InventoryItem(**result)

    async def get(self, item_id: UUID) -> Optional[InventoryItem]:
        """Get a non-deleted inventory item by ID"""
        # Get using storage service
        result = await self.storage.get_inventory_item(item_id)
        if result:
            return InventoryItem(**result)
        return None

    async def get_all_by_character(self, character_id: UUID) -> List[InventoryItem]:
        """Get all non-deleted inventory items for a character"""
        # List using storage service
        results = await self.storage.list_inventory_items(character_id)
        return [InventoryItem(**item) for item in results]

    async def update(self, item_id: UUID, item: InventoryItemUpdate) -> Optional[InventoryItem]:
        """Update a non-deleted inventory item"""
        # Update using storage service
        result = await self.storage.update_inventory_item(
            item_id,
            item.dict(exclude_unset=True)
        )
        if result:
            return InventoryItem(**result)
        return None

    async def delete(self, item_id: UUID) -> bool:
        """Soft delete an inventory item"""
        # Delete using storage service
        return await self.storage.delete_inventory_item(item_id)
