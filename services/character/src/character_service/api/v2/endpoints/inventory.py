"""Inventory Management Endpoints"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body, Path, Query
from sqlalchemy.orm import Session

from character_service.core.database import get_db
from character_service.repositories.character_repository import CharacterRepository
from character_service.repositories.inventory_repository import InventoryRepository
from character_service.schemas.schemas import (
    InventoryItem,
    InventoryItemCreate,
    DirectEditRequest
)

router = APIRouter()

@router.get("", response_model=List[InventoryItem])
async def list_inventory_items(
    character_id: str = Query(..., description="ID of the character whose inventory to list."),
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip")
):
    """List all inventory items for a character with pagination."""
    char_repo = CharacterRepository(db)
    character = await char_repo.get(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    inv_repo = InventoryRepository(db)
    return await inv_repo.get_all_by_character(character_id, limit=limit, offset=offset)

@router.get("/{item_id}", response_model=InventoryItem)
async def get_inventory_item(
    character_id: str = Query(..., description="ID of the character."),
    item_id: str = Path(..., description="ID of the inventory item to retrieve."),
    db: Session = Depends(get_db)
):
    """Get a specific inventory item by ID."""
    char_repo = CharacterRepository(db)
    character = await char_repo.get(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    inv_repo = InventoryRepository(db)
    item = await inv_repo.get(item_id)
    if not item or item.character_id != character_id:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item

@router.post("", response_model=InventoryItem)
async def create_inventory_item(
    item: InventoryItemCreate,
    db: Session = Depends(get_db)
):
    """Create a new inventory item."""
    char_repo = CharacterRepository(db)
    character = await char_repo.get(item.character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    inv_repo = InventoryRepository(db)
    return await inv_repo.create(item)

@router.post("/{item_id}/direct-edit", response_model=InventoryItem)
async def direct_edit_inventory_item(
    character_id: str = Query(..., description="ID of the character."),
    item_id: str = Path(..., description="ID of the inventory item to edit directly."),
    edit: DirectEditRequest = Body(..., description="Fields and values to update."),
    db: Session = Depends(get_db)
):
    """Directly edit an inventory item's fields (DM/user override)."""
    char_repo = CharacterRepository(db)
    character = await char_repo.get(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    inv_repo = InventoryRepository(db)
    item = await inv_repo.get(item_id)
    if not item or item.character_id != character_id:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    # Apply updates and set user_modified flag
    updates = edit.updates or {}
    errors = []

    # Only allow updating fields that exist on the item object
    for field, value in updates.items():
        if hasattr(item, field):
            try:
                setattr(item, field, value)
            except Exception as e:
                errors.append(f"Failed to update '{field}': {e}")
        else:
            errors.append(f"Field '{field}' does not exist on inventory item.")

    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})

    # Set user_modified flag and audit trail
    item.user_modified = True
    if not hasattr(item, "audit_trail"):
        item.audit_trail = []

    item.audit_trail.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "fields_changed": list(updates.keys()),
        "notes": edit.notes,
        "username": "dev"  # TODO: Get from auth context
    })

    return await inv_repo.update(item_id, item)

@router.delete("/{item_id}")
async def delete_inventory_item(
    character_id: str = Query(..., description="ID of the character."),
    item_id: str = Path(..., description="ID of the inventory item to delete."),
    db: Session = Depends(get_db)
):
    """Delete an inventory item."""
    char_repo = CharacterRepository(db)
    character = await char_repo.get(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    inv_repo = InventoryRepository(db)
    if not await inv_repo.delete(item_id):
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return {"message": "Inventory item deleted successfully"}
