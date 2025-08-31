"""Inventory repository module."""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from character_service.models.models import InventoryItem
from character_service.schemas.schemas import InventoryItemCreate, InventoryItemUpdate

class InventoryRepository:
    """Inventory repository."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, item: InventoryItemCreate) -> InventoryItem:
        """Create a new inventory item"""
        db_item = InventoryItem(**item.dict())
        self.db.add(db_item)
        await self.db.flush()
        await self.db.refresh(db_item)
        return db_item

    async def get(self, item_id: int) -> Optional[InventoryItem]:
        """Get an inventory item by ID"""
        query = select(InventoryItem).where(InventoryItem.id == item_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_by_character(self, character_id: int) -> List[InventoryItem]:
        """Get all inventory items for a character"""
        query = select(InventoryItem).where(InventoryItem.character_id == character_id)
        result = await self.db.execute(query)
        return [row[0] for row in result.all()]

    async def update(self, item_id: int, item: InventoryItemUpdate) -> Optional[InventoryItem]:
        """Update an inventory item"""
        db_item = await self.get(item_id)
        if not db_item:
            return None

        for key, value in item.dict(exclude_unset=True).items():
            setattr(db_item, key, value)

        await self.db.flush()
        await self.db.refresh(db_item)
        return db_item

    async def delete(self, item_id: int) -> bool:
        """Delete an inventory item"""
        db_item = await self.get(item_id)
        if not db_item:
            return False

        await self.db.delete(db_item)
        await self.db.flush()
        return True
