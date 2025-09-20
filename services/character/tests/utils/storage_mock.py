"""Storage adapter mock for unit tests."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from character_service.storage.storage_adapter import StorageAdapter


class MockStorageAdapter(StorageAdapter):
    """Mock storage adapter for unit tests.
    
    This mock implementation stores data in memory and simulates
    the behavior of the real storage service.
    """

    def __init__(self):
        self.characters: Dict[UUID, Dict] = {}
        self.inventory_items: Dict[UUID, Dict] = {}
        self.journal_entries: Dict[UUID, Dict] = {}
        self.experience_entries: Dict[UUID, Dict] = {}
        self.quests: Dict[UUID, Dict] = {}
        self.npc_relationships: Dict[UUID, Dict] = {}
        self.campaign_events: Dict[UUID, Dict] = {}
        self.event_impacts: Dict[UUID, Dict] = {}
        self.progress: Dict[UUID, Dict] = {}
        self.version_nodes: Dict[UUID, Dict] = {}
        self.version_edges: Dict[UUID, Dict] = {}
        self.version_graphs: Dict[UUID, Dict] = {}

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
        """List characters with filters."""
        chars = list(self.characters.values())
        if user_id:
            chars = [c for c in chars if c.get("user_id") == user_id]
        if campaign_id:
            chars = [c for c in chars if c.get("campaign_id") == campaign_id]
        if theme:
            chars = [c for c in chars if c.get("theme") == theme]
        if active_only:
            chars = [c for c in chars if not c.get("is_deleted", False)]
        return chars[offset:offset + limit]

    async def create_character(self, data: Dict) -> Dict:
        """Create a new character."""
        char_id = data.get("id") or UUID(data["character_id"])
        now = datetime.utcnow()
        char = {
            **data,
            "created_at": now,
            "updated_at": now,
            "is_deleted": False
        }
        self.characters[char_id] = char
        return char

    async def update_character(
        self,
        character_id: UUID,
        data: Dict
    ) -> Optional[Dict]:
        """Update a character."""
        if character_id not in self.characters:
            return None
        char = self.characters[character_id]
        char.update(data)
        char["updated_at"] = datetime.utcnow()
        return char

    async def delete_character(self, character_id: UUID) -> bool:
        """Soft delete a character."""
        if character_id not in self.characters:
            return False
        self.characters[character_id].update({
            "is_deleted": True,
            "deleted_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        return True

    async def get_inventory_item(
        self,
        item_id: UUID,
        character_id: Optional[UUID] = None
    ) -> Optional[Dict]:
        """Get an inventory item."""
        item = self.inventory_items.get(item_id)
        if not item:
            return None
        if character_id and item.get("character_id") != character_id:
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
        items = [
            i for i in self.inventory_items.values()
            if i.get("character_id") == character_id
        ]
        if equipped_only:
            items = [i for i in items if i.get("equipped")]
        if container:
            items = [i for i in items if i.get("container") == container]
        if not include_deleted:
            items = [i for i in items if not i.get("is_deleted", False)]
        return items[offset:offset + limit]

    async def create_inventory_item(self, data: Dict) -> Dict:
        """Create a new inventory item."""
        item_id = data.get("id") or UUID(data["item_id"])
        now = datetime.utcnow()
        item = {
            **data,
            "created_at": now,
            "updated_at": now,
            "is_deleted": False
        }
        self.inventory_items[item_id] = item
        return item

    async def update_inventory_item(
        self,
        item_id: UUID,
        data: Dict
    ) -> Optional[Dict]:
        """Update an inventory item."""
        if item_id not in self.inventory_items:
            return None
        item = self.inventory_items[item_id]
        item.update(data)
        item["updated_at"] = datetime.utcnow()
        return item

    async def delete_inventory_item(self, item_id: UUID) -> bool:
        """Soft delete an inventory item."""
        if item_id not in self.inventory_items:
            return False
        self.inventory_items[item_id].update({
            "is_deleted": True,
            "deleted_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        return True

    async def get_journal_entry(
        self,
        entry_id: UUID,
        character_id: Optional[UUID] = None
    ) -> Optional[Dict]:
        """Get a journal entry."""
        entry = self.journal_entries.get(entry_id)
        if not entry:
            return None
        if character_id and entry.get("character_id") != character_id:
            return None
        return entry

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
        entries = [
            e for e in self.journal_entries.values()
            if e.get("character_id") == character_id
        ]
        if entry_type:
            entries = [e for e in entries if e.get("entry_type") == entry_type]
        if session_number is not None:
            entries = [e for e in entries if e.get("session_number") == session_number]
        if tags:
            entries = [e for e in entries if any(t in e.get("tags", []) for t in tags)]
        if not include_deleted:
            entries = [e for e in entries if not e.get("is_deleted", False)]
        return entries[offset:offset + limit]

    async def create_journal_entry(self, data: Dict) -> Dict:
        """Create a new journal entry."""
        entry_id = data.get("id") or UUID(data["entry_id"])
        now = datetime.utcnow()
        entry = {
            **data,
            "created_at": now,
            "updated_at": now,
            "is_deleted": False
        }
        self.journal_entries[entry_id] = entry
        return entry

    async def update_journal_entry(
        self,
        entry_id: UUID,
        data: Dict
    ) -> Optional[Dict]:
        """Update a journal entry."""
        if entry_id not in self.journal_entries:
            return None
        entry = self.journal_entries[entry_id]
        entry.update(data)
        entry["updated_at"] = datetime.utcnow()
        return entry

    async def delete_journal_entry(self, entry_id: UUID) -> bool:
        """Soft delete a journal entry."""
        if entry_id not in self.journal_entries:
            return False
        self.journal_entries[entry_id].update({
            "is_deleted": True,
            "deleted_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        return True

    async def get_character_progress(self, character_id: UUID) -> Optional[Dict]:
        """Get character progress."""
        return self.progress.get(character_id)

    async def update_character_progress(
        self,
        character_id: UUID,
        data: Dict
    ) -> Dict:
        """Update character progress."""
        progress = self.progress.get(character_id, {})
        progress.update(data)
        progress["updated_at"] = datetime.utcnow()
        self.progress[character_id] = progress
        return progress