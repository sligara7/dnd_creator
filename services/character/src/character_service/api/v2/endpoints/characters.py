"""Character Management Endpoints"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body, Path, Query
from sqlalchemy.orm import Session

from character_service.core.database import get_db
from character_service.repositories.character_repository import CharacterRepository
from character_service.schemas.schemas import (
    Character, 
    CharacterCreate,
    CharacterUpdate,
    DirectEditRequest
)

router = APIRouter()

@router.get("", response_model=List[Character])
async def list_characters(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of characters to return"),
    offset: int = Query(0, ge=0, description="Number of characters to skip")
):
    """List all characters with pagination."""
    repo = CharacterRepository(db)
    return await repo.get_all(limit=limit, offset=offset)

@router.get("/{character_id}", response_model=Character)
async def get_character(
    character_id: str = Path(..., description="ID of the character to retrieve."),
    db: Session = Depends(get_db)
):
    """Get a specific character by ID."""
    repo = CharacterRepository(db)
    character = await repo.get(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character

@router.post("", response_model=Character)
async def create_character(
    character: CharacterCreate,
    db: Session = Depends(get_db)
):
    """Create a new character."""
    repo = CharacterRepository(db)
    return await repo.create(character)

@router.put("/{character_id}", response_model=Character)
async def update_character(
    character_id: str = Path(..., description="ID of the character to update."),
    character: CharacterUpdate = Body(...),
    db: Session = Depends(get_db)
):
    """Update a character."""
    repo = CharacterRepository(db)
    updated_character = await repo.update(character_id, character)
    if not updated_character:
        raise HTTPException(status_code=404, detail="Character not found")
    return updated_character

@router.delete("/{character_id}")
async def delete_character(
    character_id: str = Path(..., description="ID of the character to delete."),
    db: Session = Depends(get_db)
):
    """Delete a character."""
    repo = CharacterRepository(db)
    if not await repo.delete(character_id):
        raise HTTPException(status_code=404, detail="Character not found")
    return {"message": "Character deleted successfully"}

@router.post("/{character_id}/direct-edit", response_model=Character)
async def direct_edit_character(
    character_id: str = Path(..., description="ID of the character to edit directly."),
    edit: DirectEditRequest = Body(..., description="Fields and values to update."),
    db: Session = Depends(get_db)
):
    """Directly edit a character's fields (DM/user override)."""
    repo = CharacterRepository(db)
    character = await repo.get(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Apply updates and set user_modified flag
    updates = edit.updates or {}
    errors = []
    
    # Only allow updating fields that exist on the character object
    for field, value in updates.items():
        if hasattr(character, field):
            try:
                setattr(character, field, value)
            except Exception as e:
                errors.append(f"Failed to update '{field}': {e}")
        else:
            errors.append(f"Field '{field}' does not exist on character.")
    
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    # Set user_modified flag and audit trail
    character.user_modified = True
    if not hasattr(character, "audit_trail"):
        character.audit_trail = []
    
    character.audit_trail.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "fields_changed": list(updates.keys()),
        "notes": edit.notes,
        "username": "dev"  # TODO: Get from auth context
    })
    
    return await repo.update(character_id, character)
