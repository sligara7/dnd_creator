"""Service interfaces."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from character_service.domain.models import (
    Character,
    ExperienceEntry,
    InventoryItem,
    JournalEntry,
    NPCRelationship,
    Quest,
)


class CharacterService(ABC):
    """Character service interface."""

    @abstractmethod
    async def create_character(
        self,
        name: str,
        theme: str,
        user_id: UUID,
        campaign_id: UUID,
        character_data: Optional[Dict] = None,
    ) -> Character:
        """Create a new character."""
        pass

    @abstractmethod
    async def get_character(self, character_id: UUID) -> Optional[Character]:
        """Get character by ID."""
        pass

    @abstractmethod
    async def get_characters_by_user(self, user_id: UUID) -> List[Character]:
        """Get all active characters for a user."""
        pass

    @abstractmethod
    async def get_characters_by_campaign(self, campaign_id: UUID) -> List[Character]:
        """Get all active characters in a campaign."""
        pass

    @abstractmethod
    async def update_character(self, character: Character) -> Character:
        """Update existing character."""
        pass

    @abstractmethod
    async def delete_character(self, character_id: UUID) -> bool:
        """Soft delete character."""
        pass


class InventoryService(ABC):
    """Inventory service interface."""

    @abstractmethod
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
        pass

    @abstractmethod
    async def get_item(self, item_id: UUID) -> Optional[InventoryItem]:
        """Get inventory item by ID."""
        pass

    @abstractmethod
    async def get_character_items(self, character_id: UUID) -> List[InventoryItem]:
        """Get all active inventory items for a character."""
        pass

    @abstractmethod
    async def update_item(
        self,
        item_id: UUID,
        quantity: Optional[int] = None,
        equipped: Optional[bool] = None,
        container: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[InventoryItem]:
        """Update inventory item."""
        pass

    @abstractmethod
    async def remove_item(self, item_id: UUID) -> bool:
        """Remove item from inventory."""
        pass


class JournalService(ABC):
    """Journal service interface."""

    @abstractmethod
    async def create_entry(
        self,
        character_id: UUID,
        entry_type: str,
        title: str,
        content: str,
        data: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
        session_number: Optional[int] = None,
        session_date: Optional[datetime] = None,
        dm_name: Optional[str] = None,
        session_summary: Optional[str] = None,
    ) -> JournalEntry:
        """Create new journal entry."""
        pass

    @abstractmethod
    async def get_entry(self, entry_id: UUID) -> Optional[JournalEntry]:
        """Get journal entry by ID."""
        pass

    @abstractmethod
    async def get_character_entries(self, character_id: UUID) -> List[JournalEntry]:
        """Get all active journal entries for a character."""
        pass

    @abstractmethod
    async def get_session_entries(
        self, character_id: UUID, session_number: int
    ) -> List[JournalEntry]:
        """Get all active journal entries for a character in a specific session."""
        pass

    @abstractmethod
    async def update_entry(self, entry: JournalEntry) -> JournalEntry:
        """Update existing journal entry."""
        pass

    @abstractmethod
    async def delete_entry(self, entry_id: UUID) -> bool:
        """Soft delete journal entry."""
        pass

    @abstractmethod
    async def add_experience(
        self,
        journal_entry_id: UUID,
        amount: int,
        source: str,
        reason: str,
        session_id: Optional[UUID] = None,
        data: Optional[Dict] = None,
    ) -> ExperienceEntry:
        """Add experience entry."""
        pass

    @abstractmethod
    async def add_quest(
        self,
        journal_entry_id: UUID,
        title: str,
        description: str,
        status: str = "active",
        importance: str = "normal",
        assigned_by: Optional[str] = None,
        rewards: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> Quest:
        """Add quest entry."""
        pass

    @abstractmethod
    async def update_quest(self, quest: Quest) -> Quest:
        """Update quest entry."""
        pass

    @abstractmethod
    async def add_npc_relationship(
        self,
        journal_entry_id: UUID,
        npc_id: UUID,
        npc_name: str,
        relationship_type: str,
        standing: int = 0,
        notes: Optional[str] = None,
        data: Optional[Dict] = None,
    ) -> NPCRelationship:
        """Add NPC relationship entry."""
        pass

    @abstractmethod
    async def update_npc_relationship(
        self, relationship: NPCRelationship
    ) -> NPCRelationship:
        """Update NPC relationship entry."""
        pass
