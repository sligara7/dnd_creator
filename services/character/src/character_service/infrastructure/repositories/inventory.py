"""Inventory repository implementation."""
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.domain.models import InventoryItem as InventoryItemDomain
from character_service.infrastructure.models.models import InventoryItem
from character_service.infrastructure.repositories.base import BaseRepository


class InventoryRepository(BaseRepository[InventoryItemDomain, InventoryItem]):
    """Inventory repository implementation."""

    def __init__(self, session: AsyncSession):
        """Initialize repository."""
        super().__init__(session, InventoryItem, InventoryItemDomain)

    async def get_by_character_id(self, character_id: UUID) -> List[InventoryItem]:
        """Get all active inventory items for a character."""
        query = select(self._persistence_class).where(
            self._persistence_class.character_id == character_id,
            self._persistence_class.is_deleted == False,  # noqa: E712
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_by_container(self, character_id: UUID, container: str) -> List[InventoryItem]:
        """Get all active inventory items in a specific container."""
        query = select(self._persistence_class).where(
            self._persistence_class.character_id == character_id,
            self._persistence_class.container == container,
            self._persistence_class.is_deleted == False,  # noqa: E712
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    def _to_domain(self, model: InventoryItem) -> InventoryItemDomain:
        """Convert database model to domain model."""
        return InventoryItemDomain(
            id=model.id,
            root_id=model.root_id,
            theme=model.theme,
            character_id=model.character_id,
            item_data=model.item_data,
            quantity=model.quantity,
            equipped=model.equipped,
            container=model.container,
            notes=model.notes,
            is_deleted=model.is_deleted,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_persistence(self, domain: InventoryItemDomain) -> InventoryItem:
        """Convert domain model to database model."""
        return InventoryItem(
            id=domain.id,
            root_id=domain.root_id,
            theme=domain.theme,
            character_id=domain.character_id,
            item_data=domain.item_data,
            quantity=domain.quantity,
            equipped=domain.equipped,
            container=domain.container,
            notes=domain.notes,
            is_deleted=domain.is_deleted,
            deleted_at=domain.deleted_at,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )
