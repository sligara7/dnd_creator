"""Journal repository module."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from character_service.models.models import JournalEntry
from character_service.schemas.schemas import JournalEntryCreate, JournalEntryUpdate
from character_service.clients.storage_port import StoragePort

class JournalRepository:
    """Journal repository."""

    def __init__(self, storage: StoragePort):
        self.storage = storage

    async def create(self, entry: JournalEntryCreate) -> JournalEntry:
        """Create a new journal entry"""
        # Create using storage service
        result = await self.storage.create_journal_entry(entry.dict())
        return JournalEntry(**result)

    async def get(self, entry_id: UUID) -> Optional[JournalEntry]:
        """Get a non-deleted journal entry by ID"""
        # Get using storage service
        result = await self.storage.get_journal_entry(entry_id)
        if result:
            return JournalEntry(**result)
        return None

    async def get_all_by_character(self, character_id: UUID) -> List[JournalEntry]:
        """Get all non-deleted journal entries for a character"""
        # List using storage service
        results = await self.storage.list_journal_entries(character_id)
        return [JournalEntry(**entry) for entry in results]

    async def update(self, entry_id: UUID, entry: JournalEntryUpdate) -> Optional[JournalEntry]:
        """Update a non-deleted journal entry"""
        # Update using storage service
        result = await self.storage.update_journal_entry(
            entry_id,
            entry.dict(exclude_unset=True)
        )
        if result:
            return JournalEntry(**result)
        return None

    async def delete(self, entry_id: UUID) -> bool:
        """Soft delete a journal entry"""
        # Delete using storage service
        return await self.storage.delete_journal_entry(entry_id)
