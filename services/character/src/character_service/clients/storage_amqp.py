"""AMQP implementation of the storage port."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from character_service.clients.storage_port import (
    CharacterData,
    InventoryItemData,
    JournalEntryData,
    StoragePort
)
from character_service.domain.messages import MessagePublisher


class AMQPStoragePort(StoragePort):
    """AMQP-based implementation of the storage port interface."""

    def __init__(self, publisher: MessagePublisher) -> None:
        self.publisher = publisher

    async def _publish_storage_request(
        self,
        operation: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Helper to publish storage service requests."""
        event = {
            "service": "character",
            "type": f"storage.character.{operation}",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        return await self.publisher.publish_request("storage", event)

    async def get_character(self, character_id: UUID) -> Optional[CharacterData]:
        """Get a character by ID."""
        response = await self._publish_storage_request(
            "get_character",
            {"character_id": str(character_id)}
        )
        if response and response.get("character"):
            return CharacterData(**response["character"])
        return None

    async def list_characters(
        self,
        user_id: Optional[UUID] = None,
        campaign_id: Optional[UUID] = None,
        theme: Optional[str] = None,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[CharacterData]:
        """List characters with optional filters."""
        filters = {
            "active_only": active_only,
            "limit": limit,
            "offset": offset
        }
        if user_id:
            filters["user_id"] = str(user_id)
        if campaign_id:
            filters["campaign_id"] = str(campaign_id)
        if theme:
            filters["theme"] = theme

        response = await self._publish_storage_request(
            "list_characters",
            filters
        )
        return [CharacterData(**char) for char in response.get("characters", [])]

    async def create_character(self, data: CharacterData) -> CharacterData:
        """Create a new character."""
        response = await self._publish_storage_request(
            "create_character",
            data.model_dump()
        )
        return CharacterData(**response["character"])

    async def update_character(
        self,
        character_id: UUID,
        data: Dict[str, Any],
        version: Optional[UUID] = None
    ) -> CharacterData:
        """Update a character."""
        update_data = {
            "character_id": str(character_id),
            "data": data
        }
        if version:
            update_data["version"] = str(version)

        response = await self._publish_storage_request(
            "update_character",
            update_data
        )
        return CharacterData(**response["character"])

    async def delete_character(self, character_id: UUID) -> bool:
        """Soft delete a character."""
        response = await self._publish_storage_request(
            "delete_character",
            {"character_id": str(character_id)}
        )
        return response.get("success", False)

    # Inventory methods

    async def get_inventory_item(
        self,
        item_id: UUID,
        character_id: Optional[UUID] = None
    ) -> Optional[InventoryItemData]:
        """Get an inventory item by ID."""
        request_data = {"item_id": str(item_id)}
        if character_id:
            request_data["character_id"] = str(character_id)

        response = await self._publish_storage_request(
            "get_inventory_item",
            request_data
        )
        if response and response.get("item"):
            return InventoryItemData(**response["item"])
        return None

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
        filters = {
            "character_id": str(character_id),
            "equipped_only": equipped_only,
            "include_deleted": include_deleted,
            "limit": limit,
            "offset": offset
        }
        if container:
            filters["container"] = container

        response = await self._publish_storage_request(
            "list_inventory_items",
            filters
        )
        return [InventoryItemData(**item) for item in response.get("items", [])]

    async def create_inventory_item(self, data: InventoryItemData) -> InventoryItemData:
        """Create a new inventory item."""
        response = await self._publish_storage_request(
            "create_inventory_item",
            data.model_dump()
        )
        return InventoryItemData(**response["item"])

    async def update_inventory_item(
        self,
        item_id: UUID,
        data: Dict[str, Any]
    ) -> InventoryItemData:
        """Update an inventory item."""
        update_data = {
            "item_id": str(item_id),
            "data": data
        }
        response = await self._publish_storage_request(
            "update_inventory_item",
            update_data
        )
        return InventoryItemData(**response["item"])

    async def delete_inventory_item(
        self,
        item_id: UUID,
        character_id: Optional[UUID] = None
    ) -> bool:
        """Soft delete an inventory item."""
        request_data = {"item_id": str(item_id)}
        if character_id:
            request_data["character_id"] = str(character_id)

        response = await self._publish_storage_request(
            "delete_inventory_item",
            request_data
        )
        return response.get("success", False)

    # Journal methods

    async def get_journal_entry(
        self,
        entry_id: UUID,
        character_id: Optional[UUID] = None
    ) -> Optional[JournalEntryData]:
        """Get a journal entry by ID."""
        request_data = {"entry_id": str(entry_id)}
        if character_id:
            request_data["character_id"] = str(character_id)

        response = await self._publish_storage_request(
            "get_journal_entry",
            request_data
        )
        if response and response.get("entry"):
            return JournalEntryData(**response["entry"])
        return None

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
        filters = {
            "character_id": str(character_id),
            "include_deleted": include_deleted,
            "limit": limit,
            "offset": offset
        }
        if entry_type:
            filters["entry_type"] = entry_type
        if session_number:
            filters["session_number"] = session_number
        if tags:
            filters["tags"] = tags

        response = await self._publish_storage_request(
            "list_journal_entries",
            filters
        )
        return [JournalEntryData(**entry) for entry in response.get("entries", [])]

    async def create_journal_entry(self, data: JournalEntryData) -> JournalEntryData:
        """Create a new journal entry."""
        response = await self._publish_storage_request(
            "create_journal_entry",
            data.model_dump()
        )
        return JournalEntryData(**response["entry"])

    async def update_journal_entry(
        self,
        entry_id: UUID,
        data: Dict[str, Any]
    ) -> JournalEntryData:
        """Update a journal entry."""
        update_data = {
            "entry_id": str(entry_id),
            "data": data
        }
        response = await self._publish_storage_request(
            "update_journal_entry",
            update_data
        )
        return JournalEntryData(**response["entry"])

    async def delete_journal_entry(
        self,
        entry_id: UUID,
        character_id: Optional[UUID] = None
    ) -> bool:
        """Soft delete a journal entry."""
        request_data = {"entry_id": str(entry_id)}
        if character_id:
            request_data["character_id"] = str(character_id)

        response = await self._publish_storage_request(
            "delete_journal_entry",
            request_data
        )
        return response.get("success", False)