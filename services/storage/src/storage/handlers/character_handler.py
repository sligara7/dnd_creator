"""Message handler for character database operations.

This module implements the storage interface for character data through message-based interactions.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from storage.core.errors import NotFoundError
from storage.core.handler import BaseMessageHandler
from storage.repositories.character_repository import CharacterRepository
from storage.schemas.character import (
    CharacterResponse,
    InventoryItemResponse,
    JournalEntryResponse,
    ExperienceEntryResponse,
    QuestResponse,
    NPCRelationshipResponse,
    CampaignEventResponse,
    EventImpactResponse,
    CharacterProgressResponse,
)

class CharacterMessageHandler(BaseMessageHandler):
    """Handler for character database operations via messages."""

    def __init__(self, character_repository: CharacterRepository):
        self.repository = character_repository

    async def handle_message(self, message_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming messages based on type."""
        # Core character operations
        if message_type == "storage.character.get_character":
            character = await self.repository.get_character(UUID(data["id"]))
            return {"character": character.model_dump() if character else None}

        elif message_type == "storage.character.list_characters":
            filters = {
                "user_id": UUID(data["user_id"]) if data.get("user_id") else None,
                "campaign_id": UUID(data["campaign_id"]) if data.get("campaign_id") else None,
                "theme": data.get("theme"),
                "active_only": data.get("active_only", True),
                "limit": data.get("limit", 100),
                "offset": data.get("offset", 0)
            }
            characters = await self.repository.list_characters(**filters)
            return {"characters": [char.model_dump() for char in characters]}

        elif message_type == "storage.character.create_character":
            character = await self.repository.create_character(data)
            return {"character": character.model_dump()}

        elif message_type == "storage.character.update_character":
            character = await self.repository.update_character(
                UUID(data["id"]),
                data["data"]
            )
            return {"character": character.model_dump() if character else None}

        elif message_type == "storage.character.delete_character":
            success = await self.repository.delete_character(UUID(data["id"]))
            return {"success": success}

        # Inventory operations
        elif message_type == "storage.character.get_inventory_item":
            item = await self.repository.get_inventory_item(
                UUID(data["id"]),
                UUID(data["character_id"]) if data.get("character_id") else None
            )
            return {"item": item.model_dump() if item else None}

        elif message_type == "storage.character.list_inventory_items":
            filters = {
                "character_id": UUID(data["character_id"]),
                "equipped_only": data.get("equipped_only", False),
                "container": data.get("container"),
                "include_deleted": data.get("include_deleted", False),
                "limit": data.get("limit", 100),
                "offset": data.get("offset", 0)
            }
            items = await self.repository.list_inventory_items(**filters)
            return {"items": [item.model_dump() for item in items]}

        elif message_type == "storage.character.create_inventory_item":
            item = await self.repository.add_item_to_inventory(
                UUID(data["inventory_id"]),
                data
            )
            return {"item": item.model_dump()}

        elif message_type == "storage.character.update_inventory_item":
            item = await self.repository.update_inventory_item(
                UUID(data["id"]),
                data["data"]
            )
            return {"item": item.model_dump() if item else None}

        elif message_type == "storage.character.delete_inventory_item":
            success = await self.repository.delete_inventory_item(
                UUID(data["id"]),
                UUID(data["character_id"]) if data.get("character_id") else None
            )
            return {"success": success}

        # Journal operations
        elif message_type == "storage.character.get_journal_entry":
            entry = await self.repository.get_journal_entry(
                UUID(data["id"]),
                UUID(data["character_id"]) if data.get("character_id") else None
            )
            return {"entry": entry.model_dump() if entry else None}

        elif message_type == "storage.character.list_journal_entries":
            filters = {
                "character_id": UUID(data["character_id"]),
                "entry_type": data.get("entry_type"),
                "session_number": data.get("session_number"),
                "tags": data.get("tags"),
                "include_deleted": data.get("include_deleted", False),
                "limit": data.get("limit", 100),
                "offset": data.get("offset", 0)
            }
            entries = await self.repository.list_journal_entries(**filters)
            return {"entries": [entry.model_dump() for entry in entries]}

        elif message_type == "storage.character.create_journal_entry":
            entry = await self.repository.add_journal_entry(data)
            return {"entry": entry.model_dump()}

        elif message_type == "storage.character.update_journal_entry":
            entry = await self.repository.update_journal_entry(
                UUID(data["id"]),
                data["data"]
            )
            return {"entry": entry.model_dump() if entry else None}

        elif message_type == "storage.character.delete_journal_entry":
            success = await self.repository.delete_journal_entry(
                UUID(data["id"]),
                UUID(data["character_id"]) if data.get("character_id") else None
            )
            return {"success": success}

        # Experience entries
        elif message_type == "storage.character.get_experience_entry":
            entry = await self.repository.get_experience_entry(
                UUID(data["id"]),
                UUID(data["journal_entry_id"]) if data.get("journal_entry_id") else None
            )
            return {"entry": entry.model_dump() if entry else None}

        elif message_type == "storage.character.list_experience_entries":
            filters = {
                "journal_entry_id": UUID(data["journal_entry_id"]),
                "include_deleted": data.get("include_deleted", False),
                "limit": data.get("limit", 100),
                "offset": data.get("offset", 0)
            }
            entries = await self.repository.list_experience_entries(**filters)
            return {"entries": [entry.model_dump() for entry in entries]}

        elif message_type == "storage.character.create_experience_entry":
            entry = await self.repository.create_experience_entry(data)
            return {"entry": entry.model_dump()}

        elif message_type == "storage.character.update_experience_entry":
            entry = await self.repository.update_experience_entry(
                UUID(data["id"]),
                data["data"]
            )
            return {"entry": entry.model_dump() if entry else None}

        elif message_type == "storage.character.delete_experience_entry":
            success = await self.repository.delete_experience_entry(UUID(data["id"]))
            return {"success": success}

        # Quests
        elif message_type == "storage.character.get_quest":
            quest = await self.repository.get_quest(
                UUID(data["id"]),
                UUID(data["journal_entry_id"]) if data.get("journal_entry_id") else None
            )
            return {"quest": quest.model_dump() if quest else None}

        elif message_type == "storage.character.list_quests":
            filters = {
                "journal_entry_id": UUID(data["journal_entry_id"]),
                "status": data.get("status"),
                "importance": data.get("importance"),
                "include_deleted": data.get("include_deleted", False),
                "limit": data.get("limit", 100),
                "offset": data.get("offset", 0)
            }
            quests = await self.repository.list_quests(**filters)
            return {"quests": [quest.model_dump() for quest in quests]}

        elif message_type == "storage.character.create_quest":
            quest = await self.repository.create_quest(data)
            return {"quest": quest.model_dump()}

        elif message_type == "storage.character.update_quest":
            quest = await self.repository.update_quest(
                UUID(data["id"]),
                data["data"]
            )
            return {"quest": quest.model_dump() if quest else None}

        elif message_type == "storage.character.delete_quest":
            success = await self.repository.delete_quest(UUID(data["id"]))
            return {"success": success}

        # NPC relationships
        elif message_type == "storage.character.get_npc_relationship":
            relationship = await self.repository.get_npc_relationship(
                UUID(data["id"]),
                UUID(data["journal_entry_id"]) if data.get("journal_entry_id") else None
            )
            return {"relationship": relationship.model_dump() if relationship else None}

        elif message_type == "storage.character.list_npc_relationships":
            filters = {
                "journal_entry_id": UUID(data["journal_entry_id"]),
                "relationship_type": data.get("relationship_type"),
                "include_deleted": data.get("include_deleted", False),
                "limit": data.get("limit", 100),
                "offset": data.get("offset", 0)
            }
            relationships = await self.repository.list_npc_relationships(**filters)
            return {"relationships": [rel.model_dump() for rel in relationships]}

        elif message_type == "storage.character.create_npc_relationship":
            relationship = await self.repository.create_npc_relationship(data)
            return {"relationship": relationship.model_dump()}

        elif message_type == "storage.character.update_npc_relationship":
            relationship = await self.repository.update_npc_relationship(
                UUID(data["id"]),
                data["data"]
            )
            return {"relationship": relationship.model_dump() if relationship else None}

        elif message_type == "storage.character.delete_npc_relationship":
            success = await self.repository.delete_npc_relationship(UUID(data["id"]))
            return {"success": success}

        # Campaign events
        elif message_type == "storage.character.get_campaign_event":
            event = await self.repository.get_campaign_event(
                UUID(data["id"]),
                UUID(data["character_id"]) if data.get("character_id") else None,
                UUID(data["journal_entry_id"]) if data.get("journal_entry_id") else None
            )
            return {"event": event.model_dump() if event else None}

        elif message_type == "storage.character.list_campaign_events":
            filters = {
                "character_id": UUID(data["character_id"]),
                "event_type": data.get("event_type"),
                "impact_type": data.get("impact_type"),
                "applied_only": data.get("applied_only", False),
                "include_deleted": data.get("include_deleted", False),
                "limit": data.get("limit", 100),
                "offset": data.get("offset", 0)
            }
            events = await self.repository.list_campaign_events(**filters)
            return {"events": [event.model_dump() for event in events]}

        elif message_type == "storage.character.create_campaign_event":
            event = await self.repository.create_campaign_event(data)
            return {"event": event.model_dump()}

        elif message_type == "storage.character.update_campaign_event":
            event = await self.repository.update_campaign_event(
                UUID(data["id"]),
                data["data"]
            )
            return {"event": event.model_dump() if event else None}

        elif message_type == "storage.character.delete_campaign_event":
            success = await self.repository.delete_campaign_event(UUID(data["id"]))
            return {"success": success}

        # Event impacts
        elif message_type == "storage.character.get_event_impact":
            impact = await self.repository.get_event_impact(
                UUID(data["id"]),
                UUID(data["event_id"]) if data.get("event_id") else None,
                UUID(data["character_id"]) if data.get("character_id") else None
            )
            return {"impact": impact.model_dump() if impact else None}

        elif message_type == "storage.character.list_event_impacts":
            filters = {
                "event_id": UUID(data["event_id"]) if data.get("event_id") else None,
                "character_id": UUID(data["character_id"]) if data.get("character_id") else None,
                "applied_only": data.get("applied_only", False),
                "reverted_only": data.get("reverted_only", False),
                "limit": data.get("limit", 100),
                "offset": data.get("offset", 0)
            }
            impacts = await self.repository.list_event_impacts(**filters)
            return {"impacts": [impact.model_dump() for impact in impacts]}

        elif message_type == "storage.character.create_event_impact":
            impact = await self.repository.create_event_impact(data)
            return {"impact": impact.model_dump()}

        elif message_type == "storage.character.update_event_impact":
            impact = await self.repository.update_event_impact(
                UUID(data["id"]),
                data["data"]
            )
            return {"impact": impact.model_dump() if impact else None}

        # Character progress
        elif message_type == "storage.character.get_character_progress":
            progress = await self.repository.get_character_progress(UUID(data["character_id"]))
            return {"progress": progress.model_dump() if progress else None}

        elif message_type == "storage.character.update_character_progress":
            progress = await self.repository.update_character_progress(
                UUID(data["character_id"]),
                data["data"]
            )
            return {"progress": progress.model_dump() if progress else None}

        raise ValueError(f"Unknown message type: {message_type}")