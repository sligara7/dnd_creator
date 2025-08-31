"""Journal repository module."""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from character_service.models.models import JournalEntry
from character_service.schemas.schemas import JournalEntryCreate, JournalEntryUpdate

class JournalRepository:
    """Journal repository."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, entry: JournalEntryCreate) -> JournalEntry:
        """Create a new journal entry"""
        db_entry = JournalEntry(**entry.dict())
        self.db.add(db_entry)
        await self.db.flush()
        await self.db.refresh(db_entry)
        return db_entry

    async def get(self, entry_id: int) -> Optional[JournalEntry]:
        """Get a journal entry by ID"""
        query = select(JournalEntry).where(JournalEntry.id == entry_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_by_character(self, character_id: int) -> List[JournalEntry]:
        """Get all journal entries for a character"""
        query = select(JournalEntry).where(JournalEntry.character_id == character_id)
        result = await self.db.execute(query)
        return [row[0] for row in result.all()]

    async def update(self, entry_id: int, entry: JournalEntryUpdate) -> Optional[JournalEntry]:
        """Update a journal entry"""
        db_entry = await self.get(entry_id)
        if not db_entry:
            return None

        for key, value in entry.dict(exclude_unset=True).items():
            setattr(db_entry, key, value)

        await self.db.flush()
        await self.db.refresh(db_entry)
        return db_entry

    async def delete(self, entry_id: int) -> bool:
        """Delete a journal entry"""
        db_entry = await self.get(entry_id)
        if not db_entry:
            return False

        await self.db.delete(db_entry)
        await self.db.flush()
        return True
