"""Character database sub-service within the storage service.

This module implements the character data storage functionality as a sub-service
within the storage service, maintaining all character-related persistent data.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, not_

from .models.models import (
    Character,
    InventoryItem,
    JournalEntry,
    ExperienceEntry,
    Quest,
    NPCRelationship,
    CampaignEvent,
    EventImpact,
    CharacterProgress
)

class CharacterDBService:
    """Service for managing character data storage."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Character operations

    async def get_character(self, character_id: UUID) -> Optional[Character]:
        """Get a character by ID."""
        result = await self.session.execute(
            select(Character).where(Character.id == character_id)
        )
        return result.scalar_one_or_none()

    async def list_characters(
        self,
        user_id: Optional[UUID] = None,
        campaign_id: Optional[UUID] = None,
        theme: Optional[str] = None,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Character]:
        """List characters with optional filters."""
        query = select(Character)
        filters = []

        if user_id:
            filters.append(Character.user_id == user_id)
        if campaign_id:
            filters.append(Character.campaign_id == campaign_id)
        if theme:
            filters.append(Character.theme == theme)
        if active_only:
            filters.append(Character.is_active == True)

        if filters:
            query = query.where(and_(*filters))

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_character(self, data: Dict[str, Any]) -> Character:
        """Create a new character."""
        character = Character(**data)
        self.session.add(character)
        await self.session.flush()
        return character

    async def update_character(
        self,
        character_id: UUID,
        data: Dict[str, Any],
    ) -> Optional[Character]:
        """Update a character."""
        character = await self.get_character(character_id)
        if not character:
            return None

        for key, value in data.items():
            setattr(character, key, value)
        
        character.updated_at = datetime.utcnow()
        await self.session.flush()
        return character

    async def delete_character(self, character_id: UUID) -> bool:
        """Soft delete a character."""
        character = await self.get_character(character_id)
        if not character:
            return False

        character.is_active = False
        character.updated_at = datetime.utcnow()
        await self.session.flush()
        return True

    # Inventory operations

    async def get_inventory_item(
        self,
        item_id: UUID,
        character_id: Optional[UUID] = None
    ) -> Optional[InventoryItem]:
        """Get an inventory item."""
        query = select(InventoryItem).where(InventoryItem.id == item_id)
        if character_id:
            query = query.where(InventoryItem.character_id == character_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_inventory_items(
        self,
        character_id: UUID,
        equipped_only: bool = False,
        container: Optional[str] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[InventoryItem]:
        """List inventory items for a character."""
        query = select(InventoryItem).where(
            InventoryItem.character_id == character_id
        )

        if equipped_only:
            query = query.where(InventoryItem.equipped == True)
        if container:
            query = query.where(InventoryItem.container == container)
        if not include_deleted:
            query = query.where(not_(InventoryItem.is_deleted))

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return result.scalars().all()

    # Journal operations

    async def get_journal_entry(
        self,
        entry_id: UUID,
        character_id: Optional[UUID] = None
    ) -> Optional[JournalEntry]:
        """Get a journal entry."""
        query = select(JournalEntry).where(JournalEntry.id == entry_id)
        if character_id:
            query = query.where(JournalEntry.character_id == character_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_journal_entries(
        self,
        character_id: UUID,
        entry_type: Optional[str] = None,
        session_number: Optional[int] = None,
        tags: Optional[List[str]] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[JournalEntry]:
        """List journal entries for a character."""
        query = select(JournalEntry).where(
            JournalEntry.character_id == character_id
        )

        if entry_type:
            query = query.where(JournalEntry.entry_type == entry_type)
        if session_number:
            query = query.where(JournalEntry.session_number == session_number)
        if tags:
            # Note: This assumes tags is a JSONB array in PostgreSQL
            query = query.where(JournalEntry.tags.contains(tags))
        if not include_deleted:
            query = query.where(not_(JournalEntry.is_deleted))

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return result.scalars().all()