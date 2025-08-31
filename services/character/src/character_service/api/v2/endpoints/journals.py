"""Journal Entry Management Endpoints"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body, Path, Query
from sqlalchemy.orm import Session

from character_service.core.database import get_db
from character_service.repositories.character_repository import CharacterRepository
from character_service.repositories.journal_repository import JournalRepository
from character_service.schemas.schemas import (
    JournalEntry,
    JournalEntryCreate,
    DirectEditRequest
)

router = APIRouter()

@router.get("", response_model=List[JournalEntry])
async def list_journal_entries(
    character_id: str = Query(..., description="ID of the character whose journal entries to list."),
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of entries to return"),
    offset: int = Query(0, ge=0, description="Number of entries to skip")
):
    """List all journal entries for a character with pagination."""
    char_repo = CharacterRepository(db)
    character = await char_repo.get(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    journal_repo = JournalRepository(db)
    return await journal_repo.get_all_by_character(character_id, limit=limit, offset=offset)

@router.get("/{entry_id}", response_model=JournalEntry)
async def get_journal_entry(
    character_id: str = Query(..., description="ID of the character."),
    entry_id: str = Path(..., description="ID of the journal entry to retrieve."),
    db: Session = Depends(get_db)
):
    """Get a specific journal entry by ID."""
    char_repo = CharacterRepository(db)
    character = await char_repo.get(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    journal_repo = JournalRepository(db)
    entry = await journal_repo.get(entry_id)
    if not entry or entry.character_id != character_id:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return entry

@router.post("", response_model=JournalEntry)
async def create_journal_entry(
    entry: JournalEntryCreate,
    db: Session = Depends(get_db)
):
    """Create a new journal entry."""
    char_repo = CharacterRepository(db)
    character = await char_repo.get(entry.character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    journal_repo = JournalRepository(db)
    return await journal_repo.create(entry)

@router.post("/{entry_id}/direct-edit", response_model=JournalEntry)
async def direct_edit_journal_entry(
    character_id: str = Query(..., description="ID of the character."),
    entry_id: str = Path(..., description="ID of the journal entry to edit directly."),
    edit: DirectEditRequest = Body(..., description="Fields and values to update."),
    db: Session = Depends(get_db)
):
    """Directly edit a journal entry's fields (DM/user override)."""
    char_repo = CharacterRepository(db)
    character = await char_repo.get(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    journal_repo = JournalRepository(db)
    entry = await journal_repo.get(entry_id)
    if not entry or entry.character_id != character_id:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    # Apply updates and set user_modified flag
    updates = edit.updates or {}
    errors = []

    # Only allow updating fields that exist on the entry object
    for field, value in updates.items():
        if hasattr(entry, field):
            try:
                setattr(entry, field, value)
            except Exception as e:
                errors.append(f"Failed to update '{field}': {e}")
        else:
            errors.append(f"Field '{field}' does not exist on journal entry.")

    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})

    # Set user_modified flag and audit trail
    entry.user_modified = True
    if not hasattr(entry, "audit_trail"):
        entry.audit_trail = []

    entry.audit_trail.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "fields_changed": list(updates.keys()),
        "notes": edit.notes,
        "username": "dev"  # TODO: Get from auth context
    })

    return await journal_repo.update(entry_id, entry)
