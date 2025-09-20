"""Message handler for character_db service.

This module handles incoming messages related to character data storage,
integrating with the storage service's message handling system.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .service import CharacterDBService

class CharacterDBMessageHandler:
    """Handles character_db-related messages in the storage service."""

    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    async def handle_message(self, message_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an incoming message for the character_db service."""
        async with self.session_factory() as session:
            service = CharacterDBService(session)
            
            try:
                handler = self._get_handler(message_type)
                if not handler:
                    return {
                        "error": f"Unknown message type: {message_type}",
                        "success": False
                    }

                result = await handler(service, data)
                await session.commit()
                return {
                    "success": True,
                    "data": result
                }

            except Exception as e:
                await session.rollback()
                return {
                    "error": str(e),
                    "success": False
                }

    def _get_handler(self, message_type: str):
        """Get the appropriate handler function for a message type."""
        handlers = {
            "storage.character.get_character": self._handle_get_character,
            "storage.character.list_characters": self._handle_list_characters,
            "storage.character.create_character": self._handle_create_character,
            "storage.character.update_character": self._handle_update_character,
            "storage.character.delete_character": self._handle_delete_character,
            "storage.character.get_inventory_item": self._handle_get_inventory_item,
            "storage.character.list_inventory_items": self._handle_list_inventory_items,
            "storage.character.get_journal_entry": self._handle_get_journal_entry,
            "storage.character.list_journal_entries": self._handle_list_journal_entries,
        }
        return handlers.get(message_type)

    async def _handle_get_character(
        self,
        service: CharacterDBService,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle get_character messages."""
        character_id = UUID(data["character_id"])
        character = await service.get_character(character_id)
        return {"character": character.model_dump() if character else None}

    async def _handle_list_characters(
        self,
        service: CharacterDBService,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle list_characters messages."""
        user_id = UUID(data["user_id"]) if "user_id" in data else None
        campaign_id = UUID(data["campaign_id"]) if "campaign_id" in data else None
        theme = data.get("theme")
        active_only = data.get("active_only", True)
        limit = data.get("limit", 100)
        offset = data.get("offset", 0)

        characters = await service.list_characters(
            user_id=user_id,
            campaign_id=campaign_id,
            theme=theme,
            active_only=active_only,
            limit=limit,
            offset=offset
        )
        return {"characters": [char.model_dump() for char in characters]}

    async def _handle_create_character(
        self,
        service: CharacterDBService,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle create_character messages."""
        character = await service.create_character(data)
        return {"character": character.model_dump()}

    async def _handle_update_character(
        self,
        service: CharacterDBService,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle update_character messages."""
        character_id = UUID(data["character_id"])
        update_data = data["data"]
        character = await service.update_character(character_id, update_data)
        return {"character": character.model_dump() if character else None}

    async def _handle_delete_character(
        self,
        service: CharacterDBService,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle delete_character messages."""
        character_id = UUID(data["character_id"])
        success = await service.delete_character(character_id)
        return {"success": success}

    async def _handle_get_inventory_item(
        self,
        service: CharacterDBService,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle get_inventory_item messages."""
        item_id = UUID(data["item_id"])
        character_id = UUID(data["character_id"]) if "character_id" in data else None
        item = await service.get_inventory_item(item_id, character_id)
        return {"item": item.model_dump() if item else None}

    async def _handle_list_inventory_items(
        self,
        service: CharacterDBService,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle list_inventory_items messages."""
        character_id = UUID(data["character_id"])
        equipped_only = data.get("equipped_only", False)
        container = data.get("container")
        include_deleted = data.get("include_deleted", False)
        limit = data.get("limit", 100)
        offset = data.get("offset", 0)

        items = await service.list_inventory_items(
            character_id=character_id,
            equipped_only=equipped_only,
            container=container,
            include_deleted=include_deleted,
            limit=limit,
            offset=offset
        )
        return {"items": [item.model_dump() for item in items]}

    async def _handle_get_journal_entry(
        self,
        service: CharacterDBService,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle get_journal_entry messages."""
        entry_id = UUID(data["entry_id"])
        character_id = UUID(data["character_id"]) if "character_id" in data else None
        entry = await service.get_journal_entry(entry_id, character_id)
        return {"entry": entry.model_dump() if entry else None}

    async def _handle_list_journal_entries(
        self,
        service: CharacterDBService,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle list_journal_entries messages."""
        character_id = UUID(data["character_id"])
        entry_type = data.get("entry_type")
        session_number = data.get("session_number")
        tags = data.get("tags")
        include_deleted = data.get("include_deleted", False)
        limit = data.get("limit", 100)
        offset = data.get("offset", 0)

        entries = await service.list_journal_entries(
            character_id=character_id,
            entry_type=entry_type,
            session_number=session_number,
            tags=tags,
            include_deleted=include_deleted,
            limit=limit,
            offset=offset
        )
        return {"entries": [entry.model_dump() for entry in entries]}