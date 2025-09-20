"""Storage adapter implementation for character service."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from character_service.core.exceptions import StorageOperationError
from character_service.domain.messages import MessagePublisher
from character_service.clients.storage_port import (
    CharacterData,
    InventoryItemData,
    JournalEntryData,
    StoragePort
)


class StorageAdapter(ABC):
    """Abstract storage adapter interface."""

    @abstractmethod
    async def get_character(self, character_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a character by ID."""
        pass

    @abstractmethod
    async def list_characters(
        self,
        user_id: Optional[UUID] = None,
        campaign_id: Optional[UUID] = None,
        theme: Optional[str] = None,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List characters with optional filters."""
        pass

    @abstractmethod
    async def create_character(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new character."""
        pass

    @abstractmethod
    async def update_character(
        self,
        character_id: UUID,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a character."""
        pass

    @abstractmethod
    async def delete_character(self, character_id: UUID) -> bool:
        """Soft delete a character."""
        pass

    @abstractmethod
    async def get_inventory_item(
        self,
        item_id: UUID,
        character_id: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """Get an inventory item."""
        pass

    @abstractmethod
    async def list_inventory_items(
        self,
        character_id: UUID,
        equipped_only: bool = False,
        container: Optional[str] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List inventory items for a character."""
        pass

    @abstractmethod
    async def create_inventory_item(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new inventory item."""
        pass

    @abstractmethod
    async def update_inventory_item(
        self,
        item_id: UUID,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an inventory item."""
        pass

    @abstractmethod
    async def delete_inventory_item(self, item_id: UUID) -> bool:
        """Soft delete an inventory item."""
        pass

    @abstractmethod
    async def get_journal_entry(
        self,
        entry_id: UUID,
        character_id: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """Get a journal entry."""
        pass

    @abstractmethod
    async def list_journal_entries(
        self,
        character_id: UUID,
        entry_type: Optional[str] = None,
        session_number: Optional[int] = None,
        tags: Optional[List[str]] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List journal entries for a character."""
        pass

    @abstractmethod
    async def create_journal_entry(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new journal entry."""
        pass

    @abstractmethod
    async def update_journal_entry(
        self,
        entry_id: UUID,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a journal entry."""
        pass

    @abstractmethod
    async def delete_journal_entry(self, entry_id: UUID) -> bool:
        """Soft delete a journal entry."""
        pass

    @abstractmethod
    async def get_character_progress(
        self,
        character_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get character progress."""
        pass

    @abstractmethod
    async def update_character_progress(
        self,
        character_id: UUID,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update character progress."""
        pass


class MessageBasedStorageAdapter(StorageAdapter):
    """Implementation of storage adapter using message-based communication."""

    def __init__(self, message_publisher: MessagePublisher) -> None:
        self.publisher = message_publisher

    async def _publish_storage_request(
        self,
        operation: str,
        data: Dict[str, Any],
        retries: int = 3
    ) -> Dict[str, Any]:
        """Helper to publish storage service requests."""
        for attempt in range(retries):
            try:
                event = {
                    "service": "character",
                    "type": f"storage.character.{operation}",
                    "data": data,
                    "timestamp": datetime.utcnow().isoformat(),
                    "attempt": attempt + 1,
                    "max_attempts": retries
                }
                
                response = await self.publisher.publish_request("storage", event)
                
                if not response:
                    raise StorageOperationError(
                        f"Empty response from storage service for operation: {operation}"
                    )
                
                if error := response.get("error"):
                    raise StorageOperationError(f"Storage operation failed: {error}")
                
                return response
                
            except Exception as e:
                if attempt == retries - 1:
                    raise StorageOperationError(
                        f"Storage operation failed after {retries} attempts: {str(e)}"
                    )
                
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def get_character(self, character_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a character by ID."""
        response = await self._publish_storage_request(
            "get_character",
            {"id": str(character_id)}
        )
        return response.get("character")

    async def list_characters(
        self,
        user_id: Optional[UUID] = None,
        campaign_id: Optional[UUID] = None,
        theme: Optional[str] = None,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
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
        return response.get("characters", [])

    async def create_character(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new character."""
        response = await self._publish_storage_request(
            "create_character",
            data
        )
        return response["character"]

    async def update_character(
        self,
        character_id: UUID,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a character."""
        response = await self._publish_storage_request(
            "update_character",
            {
                "id": str(character_id),
                "data": data
            }
        )
        return response["character"]

    async def delete_character(self, character_id: UUID) -> bool:
        """Soft delete a character."""
        response = await self._publish_storage_request(
            "delete_character",
            {"id": str(character_id)}
        )
        return response.get("success", False)

    async def get_inventory_item(
        self,
        item_id: UUID,
        character_id: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """Get an inventory item."""
        data = {"id": str(item_id)}
        if character_id:
            data["character_id"] = str(character_id)

        response = await self._publish_storage_request(
            "get_inventory_item",
            data
        )
        return response.get("item")

    async def list_inventory_items(
        self,
        character_id: UUID,
        equipped_only: bool = False,
        container: Optional[str] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
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
        return response.get("items", [])

    async def create_inventory_item(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new inventory item."""
        response = await self._publish_storage_request(
            "create_inventory_item",
            data
        )
        return response["item"]

    async def update_inventory_item(
        self,
        item_id: UUID,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an inventory item."""
        response = await self._publish_storage_request(
            "update_inventory_item",
            {
                "id": str(item_id),
                "data": data
            }
        )
        return response["item"]

    async def delete_inventory_item(self, item_id: UUID) -> bool:
        """Soft delete an inventory item."""
        response = await self._publish_storage_request(
            "delete_inventory_item",
            {"id": str(item_id)}
        )
        return response.get("success", False)

    async def get_journal_entry(
        self,
        entry_id: UUID,
        character_id: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """Get a journal entry."""
        data = {"id": str(entry_id)}
        if character_id:
            data["character_id"] = str(character_id)

        response = await self._publish_storage_request(
            "get_journal_entry",
            data
        )
        return response.get("entry")

    async def list_journal_entries(
        self,
        character_id: UUID,
        entry_type: Optional[str] = None,
        session_number: Optional[int] = None,
        tags: Optional[List[str]] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
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
        return response.get("entries", [])

    async def create_journal_entry(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new journal entry."""
        response = await self._publish_storage_request(
            "create_journal_entry",
            data
        )
        return response["entry"]

    async def update_journal_entry(
        self,
        entry_id: UUID,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a journal entry."""
        response = await self._publish_storage_request(
            "update_journal_entry",
            {
                "id": str(entry_id),
                "data": data
            }
        )
        return response["entry"]

    async def delete_journal_entry(self, entry_id: UUID) -> bool:
        """Soft delete a journal entry."""
        response = await self._publish_storage_request(
            "delete_journal_entry",
            {"id": str(entry_id)}
        )
        return response.get("success", False)

    async def get_character_progress(
        self,
        character_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get character progress."""
        response = await self._publish_storage_request(
            "get_character_progress",
            {"character_id": str(character_id)}
        )
        return response.get("progress")

    async def update_character_progress(
        self,
        character_id: UUID,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update character progress."""
        response = await self._publish_storage_request(
            "update_character_progress",
            {
                "character_id": str(character_id),
                "data": data
            }
        )
        return response["progress"]