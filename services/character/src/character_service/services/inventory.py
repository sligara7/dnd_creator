"""Inventory service implementation."""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from character_service.domain.models import InventoryItem
from character_service.infrastructure.repositories.inventory import InventoryRepository
from character_service.infrastructure.repositories.character import CharacterRepository
from character_service.services.interfaces import InventoryService


class InventoryServiceImpl(InventoryService):
    """Inventory service implementation."""

    def __init__(
        self, 
        inventory_repository: InventoryRepository,
        character_repository: CharacterRepository,
    ) -> None:
        """Initialize service."""
        self._inventory_repository = inventory_repository
        self._character_repository = character_repository

    async def add_item(
        self,
        character_id: UUID,
        item_data: Dict,
        quantity: int = 1,
        equipped: bool = False,
        container: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> InventoryItem:
        """Add item to inventory."""
        # Verify character exists
        character = await self._character_repository.get(character_id)
        if not character:
            raise ValueError(f"Character not found: {character_id}")

        # Create item domain model
        item = InventoryItem(
            id=uuid4(),
            root_id=None,
            theme=character.theme,
            character_id=character_id,
            item_data=item_data,
            quantity=quantity,
            equipped=equipped,
            container=container,
            notes=notes,
            is_deleted=False,
            deleted_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Save to database and return domain model
        db_item = self._inventory_repository.to_db_model(item)
        db_item = await self._inventory_repository.create(db_item)
        return self._inventory_repository.to_domain(db_item)

    async def get_item(self, item_id: UUID) -> Optional[InventoryItem]:
        """Get inventory item by ID."""
        db_item = await self._inventory_repository.get(item_id)
        if db_item:
            return self._inventory_repository.to_domain(db_item)
        return None

    async def get_character_items(self, character_id: UUID) -> List[InventoryItem]:
        """Get all active inventory items for a character."""
        db_items = await self._inventory_repository.get_by_character_id(character_id)
        return [self._inventory_repository.to_domain(i) for i in db_items]

    async def update_item(
        self,
        item_id: UUID,
        quantity: Optional[int] = None,
        equipped: Optional[bool] = None,
        container: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[InventoryItem]:
        """Update inventory item."""
        # Get existing item
        db_item = await self._inventory_repository.get(item_id)
        if not db_item:
            return None

        # Update fields
        if quantity is not None:
            db_item.quantity = quantity
        if equipped is not None:
            db_item.equipped = equipped
        if container is not None:
            db_item.container = container
        if notes is not None:
            db_item.notes = notes

        # Save changes
        db_item = await self._inventory_repository.update(db_item)
        return self._inventory_repository.to_domain(db_item)

    async def remove_item(self, item_id: UUID) -> bool:
        """Remove item from inventory."""
        return await self._inventory_repository.delete(item_id)
