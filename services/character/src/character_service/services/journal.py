"""Journal service implementation."""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from character_service.domain.models import (
    ExperienceEntry,
    JournalEntry,
    NPCRelationship,
    Quest,
)
from character_service.infrastructure.repositories.character import CharacterRepository
from character_service.infrastructure.repositories.journal import (
    ExperienceEntryRepository,
    JournalEntryRepository,
    NPCRelationshipRepository,
    QuestRepository,
)
from character_service.services.interfaces import JournalService


class JournalServiceImpl(JournalService):
    """Journal service implementation."""

    def __init__(
        self,
        journal_repository: JournalEntryRepository,
        character_repository: CharacterRepository,
        experience_repository: ExperienceEntryRepository,
        quest_repository: QuestRepository,
        npc_relationship_repository: NPCRelationshipRepository,
    ) -> None:
        """Initialize service."""
        self._journal_repository = journal_repository
        self._character_repository = character_repository
        self._experience_repository = experience_repository
        self._quest_repository = quest_repository
        self._npc_relationship_repository = npc_relationship_repository

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
        # Verify character exists
        character = await self._character_repository.get(character_id)
        if not character:
            raise ValueError(f"Character not found: {character_id}")

        # Create entry domain model
        entry = JournalEntry(
            id=uuid4(),
            character_id=character_id,
            entry_type=entry_type,
            timestamp=datetime.utcnow(),
            title=title,
            content=content,
            data=data or {},
            tags=tags or [],
            session_number=session_number,
            session_date=session_date,
            dm_name=dm_name,
            session_summary=session_summary,
            is_deleted=False,
            deleted_at=None,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Save to database and return domain model
        db_entry = self._journal_repository.to_db_model(entry)
        db_entry = await self._journal_repository.create(db_entry)
        return self._journal_repository.to_domain(db_entry)

    async def get_entry(self, entry_id: UUID) -> Optional[JournalEntry]:
        """Get journal entry by ID."""
        db_entry = await self._journal_repository.get(entry_id)
        if db_entry:
            return self._journal_repository.to_domain(db_entry)
        return None

    async def get_character_entries(self, character_id: UUID) -> List[JournalEntry]:
        """Get all active journal entries for a character."""
        db_entries = await self._journal_repository.get_by_character_id(character_id)
        return [self._journal_repository.to_domain(e) for e in db_entries]

    async def get_session_entries(
        self, character_id: UUID, session_number: int
    ) -> List[JournalEntry]:
        """Get all active journal entries for a character in a specific session."""
        db_entries = await self._journal_repository.get_by_session_number(
            character_id, session_number
        )
        return [self._journal_repository.to_domain(e) for e in db_entries]

    async def update_entry(self, entry: JournalEntry) -> JournalEntry:
        """Update existing journal entry."""
        db_entry = self._journal_repository.to_db_model(entry)
        db_entry = await self._journal_repository.update(db_entry)
        return self._journal_repository.to_domain(db_entry)

    async def delete_entry(self, entry_id: UUID) -> bool:
        """Soft delete journal entry."""
        return await self._journal_repository.delete(entry_id)

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
        # Verify journal entry exists
        journal_entry = await self._journal_repository.get(journal_entry_id)
        if not journal_entry:
            raise ValueError(f"Journal entry not found: {journal_entry_id}")

        # Create experience entry domain model
        experience = ExperienceEntry(
            id=uuid4(),
            journal_entry_id=journal_entry_id,
            amount=amount,
            source=source,
            reason=reason,
            timestamp=datetime.utcnow(),
            session_id=session_id,
            data=data or {},
            is_deleted=False,
            deleted_at=None,
        )

        # Save to database and return domain model
        db_experience = self._experience_repository.to_db_model(experience)
        db_experience = await self._experience_repository.create(db_experience)
        return self._experience_repository.to_domain(db_experience)

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
        # Verify journal entry exists
        journal_entry = await self._journal_repository.get(journal_entry_id)
        if not journal_entry:
            raise ValueError(f"Journal entry not found: {journal_entry_id}")

        # Create quest domain model
        quest = Quest(
            id=uuid4(),
            journal_entry_id=journal_entry_id,
            title=title,
            description=description,
            status=status,
            importance=importance,
            assigned_by=assigned_by,
            rewards=rewards or {},
            progress=[],
            data=data or {},
            is_deleted=False,
            deleted_at=None,
        )

        # Save to database and return domain model
        db_quest = self._quest_repository.to_db_model(quest)
        db_quest = await self._quest_repository.create(db_quest)
        return self._quest_repository.to_domain(db_quest)

    async def update_quest(self, quest: Quest) -> Quest:
        """Update quest entry."""
        db_quest = self._quest_repository.to_db_model(quest)
        db_quest = await self._quest_repository.update(db_quest)
        return self._quest_repository.to_domain(db_quest)

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
        # Verify journal entry exists
        journal_entry = await self._journal_repository.get(journal_entry_id)
        if not journal_entry:
            raise ValueError(f"Journal entry not found: {journal_entry_id}")

        # Create NPC relationship domain model
        relationship = NPCRelationship(
            id=uuid4(),
            journal_entry_id=journal_entry_id,
            npc_id=npc_id,
            npc_name=npc_name,
            relationship_type=relationship_type,
            standing=standing,
            notes=notes,
            last_interaction=datetime.utcnow(),
            data=data or {},
            is_deleted=False,
            deleted_at=None,
        )

        # Save to database and return domain model
        db_relationship = self._npc_relationship_repository.to_db_model(relationship)
        db_relationship = await self._npc_relationship_repository.create(db_relationship)
        return self._npc_relationship_repository.to_domain(db_relationship)

    async def update_npc_relationship(
        self, relationship: NPCRelationship
    ) -> NPCRelationship:
        """Update NPC relationship entry."""
        db_relationship = self._npc_relationship_repository.to_db_model(relationship)
        db_relationship = await self._npc_relationship_repository.update(db_relationship)
        return self._npc_relationship_repository.to_domain(db_relationship)
