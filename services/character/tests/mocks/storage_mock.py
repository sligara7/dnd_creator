"""Mock storage service for testing."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from character_service.clients.storage_port import (
    StoragePort,
    CharacterData,
    InventoryItemData,
    JournalEntryData,
    ExperienceEntryData,
    QuestData,
    NPCRelationshipData,
    CampaignEventData,
    EventImpactData,
    CharacterProgressData
)


class MockStorageService(StoragePort):
    """Mock implementation of storage service for testing."""

    def __init__(self):
        self.characters: Dict[UUID, Dict] = {}
        self.inventory_items: Dict[UUID, Dict] = {}
        self.journal_entries: Dict[UUID, Dict] = {}
        self.experience_entries: Dict[UUID, Dict] = {}
        self.quests: Dict[UUID, Dict] = {}
        self.npc_relationships: Dict[UUID, Dict] = {}
        self.campaign_events: Dict[UUID, Dict] = {}
        self.event_impacts: Dict[UUID, Dict] = {}
        self.character_progress: Dict[UUID, Dict] = {}

    # Character operations

    async def get_character(self, character_id: UUID) -> Optional[Dict]:
        """Get a character by ID."""
        return self.characters.get(character_id)

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
        results = list(self.characters.values())

        if user_id:
            results = [c for c in results if c.get("user_id") == user_id]
        if campaign_id:
            results = [c for c in results if c.get("campaign_id") == campaign_id]
        if theme:
            results = [c for c in results if c.get("theme") == theme]
        if active_only:
            results = [c for c in results if c.get("is_active", True)]

        return results[offset:offset + limit]

    async def create_character(self, data: Dict) -> Dict:
        """Create a new character."""
        char_id = UUID(data["id"]) if "id" in data else uuid4()
        user_id = UUID(data["user_id"]) if isinstance(data.get("user_id"), str) else data.get("user_id")
        campaign_id = UUID(data["campaign_id"]) if isinstance(data.get("campaign_id"), str) else data.get("campaign_id")
        char_data = {
            **data,
            "id": char_id,
            "user_id": user_id,
            "campaign_id": campaign_id,
            "is_active": data.get("is_active", True),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        self.characters[char_id] = char_data
        return char_data

    async def update_character(self, character_id: UUID, data: Dict) -> Optional[Dict]:
        """Update a character."""
        if character_id not in self.characters:
            return None
        
        # Merge nested data dict if present
        if "data" in data and isinstance(data["data"], dict):
            existing = self.characters[character_id].get("data", {})
            self.characters[character_id]["data"] = {**existing, **data["data"]}
            data = {k: v for k, v in data.items() if k != "data"}
        
        self.characters[character_id].update(data)
        self.characters[character_id]["updated_at"] = datetime.utcnow()
        return self.characters[character_id]

    async def delete_character(self, character_id: UUID) -> bool:
        """Soft delete a character."""
        if character_id not in self.characters:
            return False
        
        self.characters[character_id]["is_active"] = False
        self.characters[character_id]["updated_at"] = datetime.utcnow()
        return True

    # Inventory operations

    async def get_inventory_item(self, item_id: UUID, character_id: Optional[UUID] = None) -> Optional[Dict]:
        """Get an inventory item by ID."""
        if item_id not in self.inventory_items:
            return None
        
        item = self.inventory_items[item_id]
        if character_id and item["character_id"] != character_id:
            return None
        
        return item

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
        results = [
            item for item in self.inventory_items.values()
            if item["character_id"] == character_id
        ]

        if not include_deleted:
            results = [item for item in results if not item.get("is_deleted", False)]
        if equipped_only:
            results = [item for item in results if item.get("equipped", False)]
        if container is not None:
            results = [item for item in results if item.get("container") == container]

        return results[offset:offset + limit]

    async def create_inventory_item(self, data: Dict) -> Dict:
        """Create a new inventory item."""
        item_id = UUID(data["id"]) if "id" in data else uuid4()
        character_id = UUID(data["character_id"]) if isinstance(data.get("character_id"), str) else data.get("character_id")
        item_data = {
            **data,
            "id": item_id,
            "character_id": character_id,
            "is_deleted": data.get("is_deleted", False),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        self.inventory_items[item_id] = item_data
        return item_data

    async def update_inventory_item(self, item_id: UUID, data: Dict) -> Optional[Dict]:
        """Update an inventory item."""
        if item_id not in self.inventory_items:
            return None
        
        # Merge nested data
        if "data" in data and isinstance(data["data"], dict):
            existing = self.inventory_items[item_id].get("data", {})
            self.inventory_items[item_id]["data"] = {**existing, **data["data"]}
            data = {k: v for k, v in data.items() if k != "data"}
        
        self.inventory_items[item_id].update(data)
        self.inventory_items[item_id]["updated_at"] = datetime.utcnow()
        return self.inventory_items[item_id]

    async def delete_inventory_item(self, item_id: UUID) -> bool:
        """Soft delete an inventory item."""
        if item_id not in self.inventory_items:
            return False
        self.inventory_items[item_id]["is_deleted"] = True
        self.inventory_items[item_id]["updated_at"] = datetime.utcnow()
        return True

    # Journal operations

    async def get_journal_entry(self, entry_id: UUID, character_id: Optional[UUID] = None) -> Optional[Dict]:
        if entry_id not in self.journal_entries:
            return None
        entry = self.journal_entries[entry_id]
        if character_id and entry["character_id"] != character_id:
            return None
        return entry

    async def list_journal_entries(
        self,
        character_id: UUID,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        entries = [e for e in self.journal_entries.values() if e["character_id"] == character_id]
        if not include_deleted:
            entries = [e for e in entries if not e.get("is_deleted", False)]
        return entries[offset:offset + limit]

    async def create_journal_entry(self, data: Dict) -> Dict:
        entry_id = UUID(data["id"]) if "id" in data else uuid4()
        character_id = UUID(data["character_id"]) if isinstance(data.get("character_id"), str) else data.get("character_id")
        entry_data = {
            **data,
            "id": entry_id,
            "character_id": character_id,
            "is_deleted": data.get("is_deleted", False),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        self.journal_entries[entry_id] = entry_data
        return entry_data

    async def update_journal_entry(self, entry_id: UUID, data: Dict) -> Optional[Dict]:
        if entry_id not in self.journal_entries:
            return None
        if "data" in data and isinstance(data["data"], dict):
            existing = self.journal_entries[entry_id].get("data", {})
            self.journal_entries[entry_id]["data"] = {**existing, **data["data"]}
            data = {k: v for k, v in data.items() if k != "data"}
        self.journal_entries[entry_id].update(data)
        self.journal_entries[entry_id]["updated_at"] = datetime.utcnow()
        return self.journal_entries[entry_id]

    async def delete_journal_entry(self, entry_id: UUID) -> bool:
        if entry_id not in self.journal_entries:
            return False
        self.journal_entries[entry_id]["is_deleted"] = True
        self.journal_entries[entry_id]["updated_at"] = datetime.utcnow()
        return True