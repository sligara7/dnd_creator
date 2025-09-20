"""Character repository using message-based storage service."""

from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4

from character_service.clients.storage_port import (
    StoragePort,
    CharacterData,
    InventoryItemData,
    JournalEntryData
)
from character_service.schemas.schemas import CharacterCreate, CharacterUpdate

class CharacterStorageRepository:
    """Character repository using the storage service."""

    def __init__(self, storage: StoragePort):
        self.storage = storage

    def _get_safe_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get only the fields that are valid for character data."""
        valid_fields = {
            "name",
            "user_id",
            "campaign_id",
            "parent_id",
            "theme",
            "character_data",
            "is_active",
        }
        return {k: v for k, v in data.items() if k in valid_fields}

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[CharacterData]:
        """Get all active characters with pagination."""
        return await self.storage.list_characters(
            active_only=True,
            limit=limit,
            offset=offset
        )

    async def get(self, character_id: UUID) -> Optional[CharacterData]:
        """Get an active character by ID."""
        return await self.storage.get_character(character_id)

    async def create(self, character: CharacterCreate) -> CharacterData:
        """Create a new character."""
        # Get validated data
        payload = character.model_dump()
        
        # Filter to just the valid fields
        payload = self._get_safe_fields(payload)
        
        # Ensure an ID is generated
        char_data = CharacterData(
            character_id=uuid4(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            **payload
        )
        return await self.storage.create_character(char_data)

    async def update(self, character_id: UUID, character: CharacterUpdate) -> Optional[CharacterData]:
        """Update a character."""
        # Get updates and filter to valid fields
        updates = character.model_dump(exclude_unset=True)
        updates = self._get_safe_fields(updates)

        # For character_data, we need to merge with existing
        if "character_data" in updates and isinstance(updates["character_data"], dict):
            existing = await self.get(character_id)
            if existing:
                current = dict(existing.data or {})
                current.update(updates["character_data"])
                updates["character_data"] = current

        return await self.storage.update_character(
            character_id=character_id,
            data=updates
        )

    async def delete(self, character_id: UUID) -> bool:
        """Soft delete a character by marking it as inactive."""
        return await self.storage.delete_character(character_id)

    async def update_evolution(self, character_id: UUID, evolution_data: dict) -> Optional[CharacterData]:
        """Update a character's evolution data."""
        # Get current character data
        character = await self.get(character_id)
        if not character:
            return None

        # Merge evolution data with existing character data
        current = dict(character.data or {})
        current.update(evolution_data)

        return await self.storage.update_character(
            character_id=character_id,
            data={"character_data": current}
        )

    # Inventory operations

    async def get_inventory_item(
        self,
        item_id: UUID,
        character_id: Optional[UUID] = None
    ) -> Optional[InventoryItemData]:
        """Get an inventory item by ID."""
        return await self.storage.get_inventory_item(item_id, character_id)

    async def list_inventory_items(
        self,
        character_id: UUID,
        equipped_only: bool = False,
        container: Optional[str] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[InventoryItemData]:
        """List inventory items for a character."""
        return await self.storage.list_inventory_items(
            character_id=character_id,
            equipped_only=equipped_only,
            container=container,
            include_deleted=include_deleted,
            limit=limit,
            offset=offset
        )

    # Journal operations

    async def get_journal_entry(
        self,
        entry_id: UUID,
        character_id: Optional[UUID] = None
    ) -> Optional[JournalEntryData]:
        """Get a journal entry by ID."""
        return await self.storage.get_journal_entry(entry_id, character_id)

    async def list_journal_entries(
        self,
        character_id: UUID,
        entry_type: Optional[str] = None,
        session_number: Optional[int] = None,
        tags: Optional[List[str]] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[JournalEntryData]:
        """List journal entries for a character."""
        return await self.storage.list_journal_entries(
            character_id=character_id,
            entry_type=entry_type,
            session_number=session_number,
            tags=tags,
            include_deleted=include_deleted,
            limit=limit,
            offset=offset
        )