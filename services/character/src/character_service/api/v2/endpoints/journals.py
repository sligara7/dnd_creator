"""Journal Management Endpoints"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from character_service.api.v2.dependencies import get_journal_service
from character_service.api.v2.models import (
    ExperienceEntryCreate,
    ExperienceEntryResponse,
    JournalEntryCreate,
    JournalEntryResponse,
    NPCRelationshipCreate,
    NPCRelationshipResponse,
    QuestCreate,
    QuestResponse,
    ErrorResponse,
)
from character_service.services.interfaces import JournalService

router = APIRouter()

@router.get(
    "/{character_id}",
    response_model=List[JournalEntryResponse],
    responses={500: {"model": ErrorResponse}},
)
async def get_character_journal(
    character_id: UUID,
    journal_service: JournalService = Depends(get_journal_service),
) -> List[JournalEntryResponse]:
    """Get character journal entries."""
    try:
        entries = await journal_service.get_character_entries(character_id)
        return [JournalEntryResponse.model_validate(e.model_dump()) for e in entries]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

@router.get(
    "/{character_id}/session/{session_number}",
    response_model=List[JournalEntryResponse],
    responses={500: {"model": ErrorResponse}},
)
async def get_session_entries(
    character_id: UUID,
    session_number: int,
    journal_service: JournalService = Depends(get_journal_service),
) -> List[JournalEntryResponse]:
    """Get journal entries for a specific session."""
    try:
        entries = await journal_service.get_session_entries(character_id, session_number)
        return [JournalEntryResponse.model_validate(e.model_dump()) for e in entries]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

@router.post(
    "/{character_id}",
    response_model=JournalEntryResponse,
    responses={500: {"model": ErrorResponse}},
)
async def create_journal_entry(
    character_id: UUID,
    entry: JournalEntryCreate,
    journal_service: JournalService = Depends(get_journal_service),
) -> JournalEntryResponse:
    """Create journal entry."""
    try:
        new_entry = await journal_service.create_entry(
            character_id=character_id,
            entry_type=entry.entry_type,
            title=entry.title,
            content=entry.content,
            data=entry.data,
            tags=entry.tags,
            session_number=entry.session_number,
            session_date=entry.session_date,
            dm_name=entry.dm_name,
            session_summary=entry.session_summary,
        )
        return JournalEntryResponse.model_validate(new_entry.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

@router.get(
    "/entries/{entry_id}",
    response_model=JournalEntryResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def get_journal_entry(
    entry_id: UUID,
    journal_service: JournalService = Depends(get_journal_service),
) -> JournalEntryResponse:
    """Get journal entry by ID."""
    entry = await journal_service.get_entry(entry_id)
    if not entry:
        raise HTTPException(
            status_code=404,
            detail=f"Journal entry {entry_id} not found",
        )
    return JournalEntryResponse.model_validate(entry.model_dump())

@router.put(
    "/entries/{entry_id}",
    response_model=JournalEntryResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def update_journal_entry(
    entry_id: UUID,
    entry: JournalEntryCreate,
    journal_service: JournalService = Depends(get_journal_service),
) -> JournalEntryResponse:
    """Update journal entry."""
    try:
        current_entry = await journal_service.get_entry(entry_id)
        if not current_entry:
            raise HTTPException(
                status_code=404,
                detail=f"Journal entry {entry_id} not found",
            )
        
        # Update fields
        current_entry.entry_type = entry.entry_type
        current_entry.title = entry.title
        current_entry.content = entry.content
        current_entry.data = entry.data
        current_entry.tags = entry.tags
        current_entry.session_number = entry.session_number
        current_entry.session_date = entry.session_date
        current_entry.dm_name = entry.dm_name
        current_entry.session_summary = entry.session_summary

        updated_entry = await journal_service.update_entry(current_entry)
        return JournalEntryResponse.model_validate(updated_entry.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

@router.delete(
    "/entries/{entry_id}",
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def delete_journal_entry(
    entry_id: UUID,
    journal_service: JournalService = Depends(get_journal_service),
) -> None:
    """Delete journal entry."""
    deleted = await journal_service.delete_entry(entry_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Journal entry {entry_id} not found",
        )

# Experience routes
@router.post(
    "/entries/{entry_id}/experience",
    response_model=ExperienceEntryResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def add_experience(
    entry_id: UUID,
    experience: ExperienceEntryCreate,
    journal_service: JournalService = Depends(get_journal_service),
) -> ExperienceEntryResponse:
    """Add experience entry to journal entry."""
    try:
        # Verify journal entry exists
        entry = await journal_service.get_entry(entry_id)
        if not entry:
            raise HTTPException(
                status_code=404,
                detail=f"Journal entry {entry_id} not found",
            )

        experience_entry = await journal_service.add_experience(
            journal_entry_id=entry_id,
            amount=experience.amount,
            source=experience.source,
            reason=experience.reason,
            session_id=experience.session_id,
            data=experience.data,
        )
        return ExperienceEntryResponse.model_validate(experience_entry.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

# Quest routes
@router.post(
    "/entries/{entry_id}/quests",
    response_model=QuestResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def add_quest(
    entry_id: UUID,
    quest: QuestCreate,
    journal_service: JournalService = Depends(get_journal_service),
) -> QuestResponse:
    """Add quest to journal entry."""
    try:
        # Verify journal entry exists
        entry = await journal_service.get_entry(entry_id)
        if not entry:
            raise HTTPException(
                status_code=404,
                detail=f"Journal entry {entry_id} not found",
            )

        quest_entry = await journal_service.add_quest(
            journal_entry_id=entry_id,
            title=quest.title,
            description=quest.description,
            status=quest.status,
            importance=quest.importance,
            assigned_by=quest.assigned_by,
            rewards=quest.rewards,
            data=quest.data,
        )
        return QuestResponse.model_validate(quest_entry.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

@router.put(
    "/quests/{quest_id}",
    response_model=QuestResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def update_quest(
    quest_id: UUID,
    quest: QuestCreate,
    journal_service: JournalService = Depends(get_journal_service),
) -> QuestResponse:
    """Update quest."""
    try:
        quest_entry = await journal_service.get_quest(quest_id)
        if not quest_entry:
            raise HTTPException(
                status_code=404,
                detail=f"Quest {quest_id} not found",
            )

        # Update quest fields
        quest_entry.title = quest.title
        quest_entry.description = quest.description
        quest_entry.status = quest.status
        quest_entry.importance = quest.importance
        quest_entry.assigned_by = quest.assigned_by
        quest_entry.rewards = quest.rewards
        quest_entry.data = quest.data

        updated_quest = await journal_service.update_quest(quest_entry)
        return QuestResponse.model_validate(updated_quest.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

# NPC relationship routes
@router.post(
    "/entries/{entry_id}/npcs",
    response_model=NPCRelationshipResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def add_npc_relationship(
    entry_id: UUID,
    relationship: NPCRelationshipCreate,
    journal_service: JournalService = Depends(get_journal_service),
) -> NPCRelationshipResponse:
    """Add NPC relationship to journal entry."""
    try:
        # Verify journal entry exists
        entry = await journal_service.get_entry(entry_id)
        if not entry:
            raise HTTPException(
                status_code=404,
                detail=f"Journal entry {entry_id} not found",
            )

        npc_relationship = await journal_service.add_npc_relationship(
            journal_entry_id=entry_id,
            npc_id=relationship.npc_id,
            npc_name=relationship.npc_name,
            relationship_type=relationship.relationship_type,
            standing=relationship.standing,
            notes=relationship.notes,
            data=relationship.data,
        )
        return NPCRelationshipResponse.model_validate(npc_relationship.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

@router.put(
    "/npcs/{relationship_id}",
    response_model=NPCRelationshipResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def update_npc_relationship(
    relationship_id: UUID,
    relationship: NPCRelationshipCreate,
    journal_service: JournalService = Depends(get_journal_service),
) -> NPCRelationshipResponse:
    """Update NPC relationship."""
    try:
        npc_relationship = await journal_service.get_npc_relationship(relationship_id)
        if not npc_relationship:
            raise HTTPException(
                status_code=404,
                detail=f"NPC relationship {relationship_id} not found",
            )

        # Update fields
        npc_relationship.npc_id = relationship.npc_id
        npc_relationship.npc_name = relationship.npc_name
        npc_relationship.relationship_type = relationship.relationship_type
        npc_relationship.standing = relationship.standing
        npc_relationship.notes = relationship.notes
        npc_relationship.data = relationship.data
        npc_relationship.last_interaction = datetime.utcnow()

        updated_relationship = await journal_service.update_npc_relationship(npc_relationship)
        return NPCRelationshipResponse.model_validate(updated_relationship.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
