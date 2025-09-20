"""Experience entry repository module."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from character_service.models.models import ExperienceEntry
from character_service.schemas.schemas import ExperienceEntryCreate, ExperienceEntryUpdate
from character_service.storage.storage_adapter import StorageAdapter


class ExperienceEntryRepository:
    """Experience entry repository."""

    def __init__(self, storage: StorageAdapter):
        self.storage = storage

    async def create(self, entry: ExperienceEntryCreate) -> ExperienceEntry:
        """Create a new experience entry."""
        # Create using storage service
        result = await self.storage.create_experience_entry(entry.dict())
        return ExperienceEntry(**result)

    async def get(self, entry_id: UUID) -> Optional[ExperienceEntry]:
        """Get a non-deleted experience entry by ID."""
        # Get using storage service
        result = await self.storage.get_experience_entry(entry_id)
        if result:
            return ExperienceEntry(**result)
        return None

    async def get_all_by_journal_entry(self, journal_entry_id: UUID) -> List[ExperienceEntry]:
        """Get all non-deleted experience entries for a journal entry."""
        # List using storage service
        results = await self.storage.list_experience_entries(journal_entry_id)
        return [ExperienceEntry(**entry) for entry in results]

    async def update(self, entry_id: UUID, entry: ExperienceEntryUpdate) -> Optional[ExperienceEntry]:
        """Update a non-deleted experience entry."""
        # Update using storage service
        result = await self.storage.update_experience_entry(
            entry_id,
            entry.dict(exclude_unset=True)
        )
        if result:
            return ExperienceEntry(**result)
        return None

    async def delete(self, entry_id: UUID) -> bool:
        """Soft delete an experience entry."""
        # Delete using storage service
        return await self.storage.delete_experience_entry(entry_id)