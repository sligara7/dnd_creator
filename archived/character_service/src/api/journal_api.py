"""
Journal API Endpoints

This module provides the API endpoints for managing character journals,
including journal entries, session records, and character development.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from src.core.logging_config import get_logger
from src.models.database_models import get_db
from src.models.journal_models import (
    JournalEntry, ExperienceEntry, Quest,
    NPCRelationship, SessionEntry
)
from src.services.journal_service import JournalService

logger = get_logger(__name__)
router = APIRouter()

@router.post("/characters/{character_id}/journal")
async def create_journal_entry(
    character_id: str = Path(..., description="ID of the character"),
    entry: JournalEntry = ...,
    db: Session = Depends(get_db)
) -> JournalEntry:
    """Create a new journal entry."""
    try:
        service = JournalService(db)
        entry = await service.create_journal_entry(character_id, entry)
        return entry
    except Exception as e:
        logger.error(
            "create_journal_entry_failed",
            character_id=character_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create journal entry: {str(e)}"
        )

@router.get("/characters/{character_id}/journal")
async def get_character_journal(
    character_id: str = Path(..., description="ID of the character"),
    entry_type: Optional[str] = Query(None, description="Type of journal entry to filter by"),
    start_date: Optional[datetime] = Query(None, description="Start date for filtering entries"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering entries"),
    tags: Optional[List[str]] = Query(None, description="Tags to filter by"),
    limit: int = Query(100, description="Maximum number of entries to return"),
    offset: int = Query(0, description="Number of entries to skip"),
    db: Session = Depends(get_db)
) -> List[JournalEntry]:
    """Get journal entries for a character."""
    try:
        service = JournalService(db)
        entries = await service.get_character_journal(
            character_id=character_id,
            entry_type=entry_type,
            start_date=start_date,
            end_date=end_date,
            tags=tags,
            limit=limit,
            offset=offset
        )
        return entries
    except Exception as e:
        logger.error(
            "get_character_journal_failed",
            character_id=character_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get journal entries: {str(e)}"
        )

@router.get("/characters/{character_id}/journal/{entry_id}")
async def get_journal_entry(
    character_id: str = Path(..., description="ID of the character"),
    entry_id: str = Path(..., description="ID of the journal entry"),
    db: Session = Depends(get_db)
) -> JournalEntry:
    """Get a specific journal entry."""
    try:
        service = JournalService(db)
        entry = await service.get_journal_entry(character_id, entry_id)
        if not entry:
            raise HTTPException(
                status_code=404,
                detail=f"Journal entry {entry_id} not found"
            )
        return entry
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "get_journal_entry_failed",
            character_id=character_id,
            entry_id=entry_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get journal entry: {str(e)}"
        )

@router.put("/characters/{character_id}/journal/{entry_id}")
async def update_journal_entry(
    character_id: str = Path(..., description="ID of the character"),
    entry_id: str = Path(..., description="ID of the journal entry"),
    updates: Dict[str, Any] = ...,
    db: Session = Depends(get_db)
) -> JournalEntry:
    """Update a journal entry."""
    try:
        service = JournalService(db)
        entry = await service.update_journal_entry(character_id, entry_id, updates)
        if not entry:
            raise HTTPException(
                status_code=404,
                detail=f"Journal entry {entry_id} not found"
            )
        return entry
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "update_journal_entry_failed",
            character_id=character_id,
            entry_id=entry_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update journal entry: {str(e)}"
        )

@router.delete("/characters/{character_id}/journal/{entry_id}")
async def delete_journal_entry(
    character_id: str = Path(..., description="ID of the character"),
    entry_id: str = Path(..., description="ID of the journal entry"),
    db: Session = Depends(get_db)
) -> Dict[str, bool]:
    """Delete a journal entry."""
    try:
        service = JournalService(db)
        success = await service.delete_journal_entry(character_id, entry_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Journal entry {entry_id} not found"
            )
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "delete_journal_entry_failed",
            character_id=character_id,
            entry_id=entry_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete journal entry: {str(e)}"
        )

@router.get("/characters/{character_id}/experience")
async def get_character_experience(
    character_id: str = Path(..., description="ID of the character"),
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    source: Optional[str] = Query(None, description="Source of experience"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    db: Session = Depends(get_db)
) -> List[ExperienceEntry]:
    """Get experience entries for a character."""
    try:
        service = JournalService(db)
        entries = await service.get_character_experience(
            character_id=character_id,
            start_date=start_date,
            end_date=end_date,
            source=source,
            session_id=session_id
        )
        return entries
    except Exception as e:
        logger.error(
            "get_character_experience_failed",
            character_id=character_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get character experience: {str(e)}"
        )

@router.get("/characters/{character_id}/quests")
async def get_character_quests(
    character_id: str = Path(..., description="ID of the character"),
    status: Optional[str] = Query(None, description="Filter by quest status"),
    importance: Optional[str] = Query(None, description="Filter by quest importance"),
    db: Session = Depends(get_db)
) -> List[Quest]:
    """Get quests for a character."""
    try:
        service = JournalService(db)
        quests = await service.get_character_quests(
            character_id=character_id,
            status=status,
            importance=importance
        )
        return quests
    except Exception as e:
        logger.error(
            "get_character_quests_failed",
            character_id=character_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get character quests: {str(e)}"
        )

@router.get("/characters/{character_id}/relationships")
async def get_character_relationships(
    character_id: str = Path(..., description="ID of the character"),
    relationship_type: Optional[str] = Query(None, description="Filter by relationship type"),
    min_standing: Optional[int] = Query(None, description="Minimum relationship standing"),
    max_standing: Optional[int] = Query(None, description="Maximum relationship standing"),
    db: Session = Depends(get_db)
) -> List[NPCRelationship]:
    """Get NPC relationships for a character."""
    try:
        service = JournalService(db)
        relationships = await service.get_character_relationships(
            character_id=character_id,
            relationship_type=relationship_type,
            min_standing=min_standing,
            max_standing=max_standing
        )
        return relationships
    except Exception as e:
        logger.error(
            "get_character_relationships_failed",
            character_id=character_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get character relationships: {str(e)}"
        )
