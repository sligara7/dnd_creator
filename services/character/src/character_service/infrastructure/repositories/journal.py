"""Journal repositories implementation."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.domain.models import (
    ExperienceEntry as ExperienceEntryDomain,
    JournalEntry as JournalEntryDomain,
    NPCRelationship as NPCRelationshipDomain,
    Quest as QuestDomain,
)
from character_service.infrastructure.models.models import (
    ExperienceEntry,
    JournalEntry,
    NPCRelationship,
    Quest,
)
from character_service.infrastructure.repositories.base import BaseRepository


class JournalEntryRepository(BaseRepository[JournalEntryDomain, JournalEntry]):
    """Journal entry repository implementation."""

    def __init__(self, session: AsyncSession):
        """Initialize repository."""
        super().__init__(session, JournalEntry, JournalEntryDomain)

    async def get_by_character_id(self, character_id: UUID) -> List[JournalEntry]:
        """Get all active journal entries for a character."""
        query = select(self._persistence_class).where(
            self._persistence_class.character_id == character_id,
            self._persistence_class.is_deleted == False,  # noqa: E712
        ).order_by(self._persistence_class.timestamp.desc())
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_by_session_number(self, character_id: UUID, session_number: int) -> List[JournalEntry]:
        """Get all active journal entries for a character in a specific session."""
        query = select(self._persistence_class).where(
            self._persistence_class.character_id == character_id,
            self._persistence_class.session_number == session_number,
            self._persistence_class.is_deleted == False,  # noqa: E712
        ).order_by(self._persistence_class.timestamp.desc())
        result = await self._session.execute(query)
        return list(result.scalars().all())

    def _to_domain(self, model: JournalEntry) -> JournalEntryDomain:
        """Convert database model to domain model."""
        return JournalEntryDomain(
            id=model.id,
            character_id=model.character_id,
            entry_type=model.entry_type,
            timestamp=model.timestamp,
            title=model.title,
            content=model.content,
            data=model.data,
            tags=model.tags,
            session_number=model.session_number,
            session_date=model.session_date,
            dm_name=model.dm_name,
            session_summary=model.session_summary,
            is_deleted=model.is_deleted,
            deleted_at=model.deleted_at,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_persistence(self, domain: JournalEntryDomain) -> JournalEntry:
        """Convert domain model to database model."""
        return JournalEntry(
            id=domain.id,
            character_id=domain.character_id,
            entry_type=domain.entry_type,
            timestamp=domain.timestamp,
            title=domain.title,
            content=domain.content,
            data=domain.data,
            tags=domain.tags,
            session_number=domain.session_number,
            session_date=domain.session_date,
            dm_name=domain.dm_name,
            session_summary=domain.session_summary,
            is_deleted=domain.is_deleted,
            deleted_at=domain.deleted_at,
            is_active=domain.is_active,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )


class ExperienceEntryRepository(BaseRepository[ExperienceEntryDomain, ExperienceEntry]):
    """Experience entry repository implementation."""

    def __init__(self, session: AsyncSession):
        """Initialize repository."""
        super().__init__(session, ExperienceEntry, ExperienceEntryDomain)

    async def get_by_journal_entry_id(self, journal_entry_id: UUID) -> List[ExperienceEntry]:
        """Get all active experience entries for a journal entry."""
        query = select(self._persistence_class).where(
            self._persistence_class.journal_entry_id == journal_entry_id,
            self._persistence_class.is_deleted == False,  # noqa: E712
        ).order_by(self._persistence_class.timestamp.desc())
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_by_session_id(self, session_id: UUID) -> List[ExperienceEntry]:
        """Get all active experience entries for a session."""
        query = select(self._persistence_class).where(
            self._persistence_class.session_id == session_id,
            self._persistence_class.is_deleted == False,  # noqa: E712
        ).order_by(self._persistence_class.timestamp.desc())
        result = await self._session.execute(query)
        return list(result.scalars().all())

    def _to_domain(self, model: ExperienceEntry) -> ExperienceEntryDomain:
        """Convert database model to domain model."""
        return ExperienceEntryDomain(
            id=model.id,
            journal_entry_id=model.journal_entry_id,
            amount=model.amount,
            source=model.source,
            reason=model.reason,
            timestamp=model.timestamp,
            session_id=model.session_id,
            data=model.data,
            is_deleted=model.is_deleted,
            deleted_at=model.deleted_at,
        )

    def _to_persistence(self, domain: ExperienceEntryDomain) -> ExperienceEntry:
        """Convert domain model to database model."""
        return ExperienceEntry(
            id=domain.id,
            journal_entry_id=domain.journal_entry_id,
            amount=domain.amount,
            source=domain.source,
            reason=domain.reason,
            timestamp=domain.timestamp,
            session_id=domain.session_id,
            data=domain.data,
            is_deleted=domain.is_deleted,
            deleted_at=domain.deleted_at,
        )


class QuestRepository(BaseRepository[QuestDomain, Quest]):
    """Quest repository implementation."""

    def __init__(self, session: AsyncSession):
        """Initialize repository."""
        super().__init__(session, Quest, QuestDomain)

    async def get_by_journal_entry_id(self, journal_entry_id: UUID) -> List[Quest]:
        """Get all active quests for a journal entry."""
        query = select(self._persistence_class).where(
            self._persistence_class.journal_entry_id == journal_entry_id,
            self._persistence_class.is_deleted == False,  # noqa: E712
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_by_status(self, status: str) -> List[Quest]:
        """Get all active quests with a specific status."""
        query = select(self._persistence_class).where(
            self._persistence_class.status == status,
            self._persistence_class.is_deleted == False,  # noqa: E712
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    def _to_domain(self, model: Quest) -> QuestDomain:
        """Convert database model to domain model."""
        return QuestDomain(
            id=model.id,
            journal_entry_id=model.journal_entry_id,
            title=model.title,
            description=model.description,
            status=model.status,
            importance=model.importance,
            assigned_by=model.assigned_by,
            rewards=model.rewards,
            progress=model.progress,
            data=model.data,
            is_deleted=model.is_deleted,
            deleted_at=model.deleted_at,
        )

    def _to_persistence(self, domain: QuestDomain) -> Quest:
        """Convert domain model to database model."""
        return Quest(
            id=domain.id,
            journal_entry_id=domain.journal_entry_id,
            title=domain.title,
            description=domain.description,
            status=domain.status,
            importance=domain.importance,
            assigned_by=domain.assigned_by,
            rewards=domain.rewards,
            progress=domain.progress,
            data=domain.data,
            is_deleted=domain.is_deleted,
            deleted_at=domain.deleted_at,
        )


class NPCRelationshipRepository(BaseRepository[NPCRelationshipDomain, NPCRelationship]):
    """NPC relationship repository implementation."""

    def __init__(self, session: AsyncSession):
        """Initialize repository."""
        super().__init__(session, NPCRelationship, NPCRelationshipDomain)

    async def get_by_journal_entry_id(self, journal_entry_id: UUID) -> List[NPCRelationship]:
        """Get all active NPC relationships for a journal entry."""
        query = select(self._persistence_class).where(
            self._persistence_class.journal_entry_id == journal_entry_id,
            self._persistence_class.is_deleted == False,  # noqa: E712
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_by_npc_id(self, npc_id: UUID) -> List[NPCRelationship]:
        """Get all active NPC relationships for an NPC."""
        query = select(self._persistence_class).where(
            self._persistence_class.npc_id == npc_id,
            self._persistence_class.is_deleted == False,  # noqa: E712
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    def _to_domain(self, model: NPCRelationship) -> NPCRelationshipDomain:
        """Convert database model to domain model."""
        return NPCRelationshipDomain(
            id=model.id,
            journal_entry_id=model.journal_entry_id,
            npc_id=model.npc_id,
            npc_name=model.npc_name,
            relationship_type=model.relationship_type,
            standing=model.standing,
            notes=model.notes,
            last_interaction=model.last_interaction,
            data=model.data,
            is_deleted=model.is_deleted,
            deleted_at=model.deleted_at,
        )

    def _to_persistence(self, domain: NPCRelationshipDomain) -> NPCRelationship:
        """Convert domain model to database model."""
        return NPCRelationship(
            id=domain.id,
            journal_entry_id=domain.journal_entry_id,
            npc_id=domain.npc_id,
            npc_name=domain.npc_name,
            relationship_type=domain.relationship_type,
            standing=domain.standing,
            notes=domain.notes,
            last_interaction=domain.last_interaction,
            data=domain.data,
            is_deleted=domain.is_deleted,
            deleted_at=domain.deleted_at,
        )
