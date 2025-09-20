"""Integration with storage service for character data and asset management."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from pydantic import BaseModel

from character_service.core.config import settings
from character_service.domain.messages import MessagePublisher


class AssetMetadata(BaseModel):
    """Asset metadata for storage service."""
    content_type: str
    filename: str
    character_id: UUID
    asset_type: str
    tags: list[str]


class StorageServiceClient:
"""Client for interacting with storage service via Message Hub."""
    
    def __init__(self, message_publisher: MessagePublisher) -> None:
        self.publisher = message_publisher

    async def get_character(self, character_id: UUID) -> Optional[Dict]:
        """Get a character by ID."""
        event = {
            "service": "character",
            "type": "storage.character.get_character",
            "data": {
                "id": str(character_id)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("character")

    async def list_characters(
        self,
        user_id: Optional[UUID] = None,
        campaign_id: Optional[UUID] = None,
        theme: Optional[str] = None,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """List characters with optional filters."""
        event = {
            "service": "character",
            "type": "storage.character.list_characters",
            "data": {
                "user_id": str(user_id) if user_id else None,
                "campaign_id": str(campaign_id) if campaign_id else None,
                "theme": theme,
                "active_only": active_only,
                "limit": limit,
                "offset": offset
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("characters", [])

    async def create_character(self, data: Dict) -> Dict:
        """Create a new character."""
        event = {
            "service": "character",
            "type": "storage.character.create_character",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response["character"]

    async def update_character(
        self,
        character_id: UUID,
        data: Dict
    ) -> Optional[Dict]:
        """Update a character."""
        event = {
            "service": "character",
            "type": "storage.character.update_character",
            "data": {
                "id": str(character_id),
                "data": data
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("character")

    async def delete_character(self, character_id: UUID) -> bool:
        """Soft delete a character."""
        event = {
            "service": "character",
            "type": "storage.character.delete_character",
            "data": {
                "id": str(character_id)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("success", False)

    async def get_inventory_item(
        self,
        item_id: UUID,
        character_id: Optional[UUID] = None
    ) -> Optional[Dict]:
        """Get an inventory item."""
        event = {
            "service": "character",
            "type": "storage.character.get_inventory_item",
            "data": {
                "id": str(item_id),
                "character_id": str(character_id) if character_id else None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("item")

    async def list_inventory_items(
        self,
        character_id: UUID,
        equipped_only: bool = False,
        container: Optional[str] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """List inventory items for a character."""
        event = {
            "service": "character",
            "type": "storage.character.list_inventory_items",
            "data": {
                "character_id": str(character_id),
                "equipped_only": equipped_only,
                "container": container,
                "include_deleted": include_deleted,
                "limit": limit,
                "offset": offset
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("items", [])

    async def create_inventory_item(self, data: Dict) -> Dict:
        """Create a new inventory item."""
        event = {
            "service": "character",
            "type": "storage.character.create_inventory_item",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response["item"]

    async def update_inventory_item(
        self,
        item_id: UUID,
        data: Dict
    ) -> Optional[Dict]:
        """Update an inventory item."""
        event = {
            "service": "character",
            "type": "storage.character.update_inventory_item",
            "data": {
                "id": str(item_id),
                "data": data
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("item")

    async def delete_inventory_item(self, item_id: UUID) -> bool:
        """Soft delete an inventory item."""
        event = {
            "service": "character",
            "type": "storage.character.delete_inventory_item",
            "data": {
                "id": str(item_id)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("success", False)

    async def get_journal_entry(
        self,
        entry_id: UUID,
        character_id: Optional[UUID] = None
    ) -> Optional[Dict]:
        """Get a journal entry."""
        event = {
            "service": "character",
            "type": "storage.character.get_journal_entry",
            "data": {
                "id": str(entry_id),
                "character_id": str(character_id) if character_id else None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
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
    ) -> List[Dict]:
        """List journal entries for a character."""
        event = {
            "service": "character",
            "type": "storage.character.list_journal_entries",
            "data": {
                "character_id": str(character_id),
                "entry_type": entry_type,
                "session_number": session_number,
                "tags": tags,
                "include_deleted": include_deleted,
                "limit": limit,
                "offset": offset
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("entries", [])

    async def create_journal_entry(self, data: Dict) -> Dict:
        """Create a new journal entry."""
        event = {
            "service": "character",
            "type": "storage.character.create_journal_entry",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response["entry"]

    async def update_journal_entry(
        self,
        entry_id: UUID,
        data: Dict
    ) -> Optional[Dict]:
        """Update a journal entry."""
        event = {
            "service": "character",
            "type": "storage.character.update_journal_entry",
            "data": {
                "id": str(entry_id),
                "data": data
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("entry")

    async def delete_journal_entry(self, entry_id: UUID) -> bool:
        """Soft delete a journal entry."""
        event = {
            "service": "character",
            "type": "storage.character.delete_journal_entry",
            "data": {
                "id": str(entry_id)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("success", False)

    async def get_experience_entry(
        self,
        entry_id: UUID,
        journal_entry_id: Optional[UUID] = None
    ) -> Optional[Dict]:
        """Get an experience entry."""
        event = {
            "service": "character",
            "type": "storage.character.get_experience_entry",
            "data": {
                "id": str(entry_id),
                "journal_entry_id": str(journal_entry_id) if journal_entry_id else None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("entry")

    async def list_experience_entries(
        self,
        journal_entry_id: UUID,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """List experience entries for a journal entry."""
        event = {
            "service": "character",
            "type": "storage.character.list_experience_entries",
            "data": {
                "journal_entry_id": str(journal_entry_id),
                "include_deleted": include_deleted,
                "limit": limit,
                "offset": offset
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("entries", [])

    async def create_experience_entry(self, data: Dict) -> Dict:
        """Create a new experience entry."""
        event = {
            "service": "character",
            "type": "storage.character.create_experience_entry",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response["entry"]

    async def update_experience_entry(
        self,
        entry_id: UUID,
        data: Dict
    ) -> Optional[Dict]:
        """Update an experience entry."""
        event = {
            "service": "character",
            "type": "storage.character.update_experience_entry",
            "data": {
                "id": str(entry_id),
                "data": data
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("entry")

    async def delete_experience_entry(self, entry_id: UUID) -> bool:
        """Soft delete an experience entry."""
        event = {
            "service": "character",
            "type": "storage.character.delete_experience_entry",
            "data": {
                "id": str(entry_id)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("success", False)

    async def get_quest(
        self,
        quest_id: UUID,
        journal_entry_id: Optional[UUID] = None
    ) -> Optional[Dict]:
        """Get a quest."""
        event = {
            "service": "character",
            "type": "storage.character.get_quest",
            "data": {
                "id": str(quest_id),
                "journal_entry_id": str(journal_entry_id) if journal_entry_id else None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("quest")

    async def list_quests(
        self,
        journal_entry_id: UUID,
        status: Optional[str] = None,
        importance: Optional[str] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """List quests for a journal entry."""
        event = {
            "service": "character",
            "type": "storage.character.list_quests",
            "data": {
                "journal_entry_id": str(journal_entry_id),
                "status": status,
                "importance": importance,
                "include_deleted": include_deleted,
                "limit": limit,
                "offset": offset
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("quests", [])

    async def create_quest(self, data: Dict) -> Dict:
        """Create a new quest."""
        event = {
            "service": "character",
            "type": "storage.character.create_quest",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response["quest"]

    async def update_quest(
        self,
        quest_id: UUID,
        data: Dict
    ) -> Optional[Dict]:
        """Update a quest."""
        event = {
            "service": "character",
            "type": "storage.character.update_quest",
            "data": {
                "id": str(quest_id),
                "data": data
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("quest")

    async def delete_quest(self, quest_id: UUID) -> bool:
        """Soft delete a quest."""
        event = {
            "service": "character",
            "type": "storage.character.delete_quest",
            "data": {
                "id": str(quest_id)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("success", False)

    async def get_npc_relationship(
        self,
        relationship_id: UUID,
        journal_entry_id: Optional[UUID] = None
    ) -> Optional[Dict]:
        """Get an NPC relationship."""
        event = {
            "service": "character",
            "type": "storage.character.get_npc_relationship",
            "data": {
                "id": str(relationship_id),
                "journal_entry_id": str(journal_entry_id) if journal_entry_id else None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("relationship")

    async def list_npc_relationships(
        self,
        journal_entry_id: UUID,
        relationship_type: Optional[str] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """List NPC relationships for a journal entry."""
        event = {
            "service": "character",
            "type": "storage.character.list_npc_relationships",
            "data": {
                "journal_entry_id": str(journal_entry_id),
                "relationship_type": relationship_type,
                "include_deleted": include_deleted,
                "limit": limit,
                "offset": offset
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("relationships", [])

    async def create_npc_relationship(self, data: Dict) -> Dict:
        """Create a new NPC relationship."""
        event = {
            "service": "character",
            "type": "storage.character.create_npc_relationship",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response["relationship"]

    async def update_npc_relationship(
        self,
        relationship_id: UUID,
        data: Dict
    ) -> Optional[Dict]:
        """Update an NPC relationship."""
        event = {
            "service": "character",
            "type": "storage.character.update_npc_relationship",
            "data": {
                "id": str(relationship_id),
                "data": data
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("relationship")

    async def delete_npc_relationship(self, relationship_id: UUID) -> bool:
        """Soft delete an NPC relationship."""
        event = {
            "service": "character",
            "type": "storage.character.delete_npc_relationship",
            "data": {
                "id": str(relationship_id)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("success", False)

    async def get_campaign_event(
        self,
        event_id: UUID,
        character_id: Optional[UUID] = None,
        journal_entry_id: Optional[UUID] = None
    ) -> Optional[Dict]:
        """Get a campaign event."""
        event = {
            "service": "character",
            "type": "storage.character.get_campaign_event",
            "data": {
                "id": str(event_id),
                "character_id": str(character_id) if character_id else None,
                "journal_entry_id": str(journal_entry_id) if journal_entry_id else None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("event")

    async def list_campaign_events(
        self,
        character_id: UUID,
        event_type: Optional[str] = None,
        impact_type: Optional[str] = None,
        applied_only: bool = False,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """List campaign events for a character."""
        event = {
            "service": "character",
            "type": "storage.character.list_campaign_events",
            "data": {
                "character_id": str(character_id),
                "event_type": event_type,
                "impact_type": impact_type,
                "applied_only": applied_only,
                "include_deleted": include_deleted,
                "limit": limit,
                "offset": offset
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("events", [])

    async def create_campaign_event(self, data: Dict) -> Dict:
        """Create a new campaign event."""
        event = {
            "service": "character",
            "type": "storage.character.create_campaign_event",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response["event"]

    async def update_campaign_event(
        self,
        event_id: UUID,
        data: Dict
    ) -> Optional[Dict]:
        """Update a campaign event."""
        event = {
            "service": "character",
            "type": "storage.character.update_campaign_event",
            "data": {
                "id": str(event_id),
                "data": data
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("event")

    async def delete_campaign_event(self, event_id: UUID) -> bool:
        """Soft delete a campaign event."""
        event = {
            "service": "character",
            "type": "storage.character.delete_campaign_event",
            "data": {
                "id": str(event_id)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("success", False)

    async def get_event_impact(
        self,
        impact_id: UUID,
        event_id: Optional[UUID] = None,
        character_id: Optional[UUID] = None
    ) -> Optional[Dict]:
        """Get an event impact."""
        event = {
            "service": "character",
            "type": "storage.character.get_event_impact",
            "data": {
                "id": str(impact_id),
                "event_id": str(event_id) if event_id else None,
                "character_id": str(character_id) if character_id else None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("impact")

    async def list_event_impacts(
        self,
        event_id: Optional[UUID] = None,
        character_id: Optional[UUID] = None,
        applied_only: bool = False,
        reverted_only: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """List event impacts."""
        event = {
            "service": "character",
            "type": "storage.character.list_event_impacts",
            "data": {
                "event_id": str(event_id) if event_id else None,
                "character_id": str(character_id) if character_id else None,
                "applied_only": applied_only,
                "reverted_only": reverted_only,
                "limit": limit,
                "offset": offset
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("impacts", [])

    async def create_event_impact(self, data: Dict) -> Dict:
        """Create a new event impact."""
        event = {
            "service": "character",
            "type": "storage.character.create_event_impact",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response["impact"]

    async def update_event_impact(
        self,
        impact_id: UUID,
        data: Dict
    ) -> Optional[Dict]:
        """Update an event impact."""
        event = {
            "service": "character",
            "type": "storage.character.update_event_impact",
            "data": {
                "id": str(impact_id),
                "data": data
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("impact")

    async def get_character_progress(
        self,
        character_id: UUID
    ) -> Optional[Dict]:
        """Get character progress."""
        event = {
            "service": "character",
            "type": "storage.character.get_character_progress",
            "data": {
                "character_id": str(character_id)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("progress")

    async def update_character_progress(
        self,
        character_id: UUID,
        data: Dict
    ) -> Optional[Dict]:
        """Update character progress."""
        event = {
            "service": "character",
            "type": "storage.character.update_character_progress",
            "data": {
                "character_id": str(character_id),
                "data": data
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("progress")

    async def upload_portrait(self, character_id: UUID, file_data: bytes,
                            filename: str) -> Dict[str, Any]:
        """Upload character portrait to storage service."""
        metadata = AssetMetadata(
            content_type="image/png",
            filename=filename,
            character_id=character_id,
            asset_type="portrait",
            tags=["portrait", "character"]
        )

        # Publish upload request event
        event = {
            "service": "character",
            "type": "storage.asset.upload",
            "data": {
                "file_data": file_data,
                "metadata": metadata.model_dump(),
                "options": {
                    "versioning": True,
                    "compression": True,
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response

    async def upload_character_sheet(self, character_id: UUID, file_data: bytes,
                                   filename: str) -> Dict[str, Any]:
        """Upload character sheet PDF to storage service."""
        metadata = AssetMetadata(
            content_type="application/pdf",
            filename=filename,
            character_id=character_id,
            asset_type="character_sheet",
            tags=["character_sheet"]
        )

        event = {
            "service": "character",
            "type": "storage.asset.upload",
            "data": {
                "file_data": file_data,
                "metadata": metadata.model_dump(),
                "options": {
                    "versioning": True,
                    "compression": True,
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response

    async def get_asset(self, asset_id: UUID) -> Optional[Dict[str, Any]]:
        """Get asset from storage service."""
        event = {
            "service": "character",
            "type": "storage.asset.get",
            "data": {
                "asset_id": str(asset_id)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response

    async def delete_asset(self, asset_id: UUID) -> bool:
        """Delete asset from storage service."""
        event = {
            "service": "character",
            "type": "storage.asset.delete",
            "data": {
                "asset_id": str(asset_id)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response.get("success", False)

    async def update_asset(self, asset_id: UUID, file_data: bytes,
                          metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update existing asset in storage service."""
        event = {
            "service": "character",
            "type": "storage.asset.update",
            "data": {
                "asset_id": str(asset_id),
                "file_data": file_data,
                "metadata": metadata or {}
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await self.publisher.publish_request("storage", event)
        return response