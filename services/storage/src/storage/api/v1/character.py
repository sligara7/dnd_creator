"""API endpoints for character database operations."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from storage.core.database import get_session
from storage.repositories.character_repository import CharacterRepository
from storage.schemas.character import (
    CharacterCreate,
    CharacterUpdate,
    CharacterResponse,
    ThemeCreate,
    ThemeResponse,
    InventoryCreate,
    InventoryItemCreate,
    InventoryResponse,
    SpellcastingCreate,
    SpellcastingResponse,
    JournalEntryCreate,
    JournalEntryResponse,
    ConditionCreate,
    ConditionResponse,
    ClassResourceCreate,
    ClassResourceResponse,
    VersionGraphCreate,
    VersionGraphResponse,
)

router = APIRouter(prefix="/characters", tags=["characters"])

@router.post("/", response_model=CharacterResponse)
async def create_character(
    character: CharacterCreate,
    session: AsyncSession = Depends(get_session)
) -> CharacterResponse:
    """Create a new character."""
    repository = CharacterRepository(session)
    character_data = character.model_dump()
    db_character = await repository.create_character(character_data)
    return CharacterResponse.model_validate(db_character)

@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: UUID,
    session: AsyncSession = Depends(get_session)
) -> CharacterResponse:
    """Get a character by ID."""
    repository = CharacterRepository(session)
    db_character = await repository.get_character(character_id)
    if not db_character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    return CharacterResponse.model_validate(db_character)

@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: UUID,
    character: CharacterUpdate,
    session: AsyncSession = Depends(get_session)
) -> CharacterResponse:
    """Update a character."""
    repository = CharacterRepository(session)
    character_data = character.model_dump(exclude_unset=True)
    db_character = await repository.update_character(character_id, character_data)
    if not db_character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    return CharacterResponse.model_validate(db_character)

@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(
    character_id: UUID,
    session: AsyncSession = Depends(get_session)
) -> None:
    """Delete a character."""
    repository = CharacterRepository(session)
    deleted = await repository.delete_character(character_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )

@router.post("/{character_id}/inventory", response_model=InventoryResponse)
async def create_inventory(
    character_id: UUID,
    inventory: InventoryCreate,
    session: AsyncSession = Depends(get_session)
) -> InventoryResponse:
    """Create an inventory for a character."""
    repository = CharacterRepository(session)
    inventory_data = inventory.model_dump() | {"character_id": character_id}
    db_inventory = await repository.create_inventory(inventory_data)
    return InventoryResponse.model_validate(db_inventory)

@router.post("/{character_id}/inventory/{inventory_id}/items", response_model=InventoryResponse)
async def add_inventory_item(
    character_id: UUID,
    inventory_id: UUID,
    item: InventoryItemCreate,
    session: AsyncSession = Depends(get_session)
) -> InventoryResponse:
    """Add an item to a character's inventory."""
    repository = CharacterRepository(session)
    item_data = item.model_dump()
    db_item = await repository.add_item_to_inventory(inventory_id, item_data)
    return InventoryResponse.model_validate(db_item)

@router.post("/{character_id}/spellcasting", response_model=SpellcastingResponse)
async def create_spellcasting(
    character_id: UUID,
    spellcasting: SpellcastingCreate,
    session: AsyncSession = Depends(get_session)
) -> SpellcastingResponse:
    """Create spellcasting information for a character."""
    repository = CharacterRepository(session)
    spellcasting_data = spellcasting.model_dump() | {"character_id": character_id}
    db_spellcasting = await repository.create_spellcasting(spellcasting_data)
    return SpellcastingResponse.model_validate(db_spellcasting)

@router.post("/{character_id}/journal", response_model=JournalEntryResponse)
async def add_journal_entry(
    character_id: UUID,
    entry: JournalEntryCreate,
    session: AsyncSession = Depends(get_session)
) -> JournalEntryResponse:
    """Add a journal entry for a character."""
    repository = CharacterRepository(session)
    entry_data = entry.model_dump() | {"character_id": character_id}
    db_entry = await repository.add_journal_entry(entry_data)
    return JournalEntryResponse.model_validate(db_entry)

@router.get("/{character_id}/journal", response_model=List[JournalEntryResponse])
async def get_journal_entries(
    character_id: UUID,
    session: AsyncSession = Depends(get_session)
) -> List[JournalEntryResponse]:
    """Get all journal entries for a character."""
    repository = CharacterRepository(session)
    entries = await repository.get_journal_entries(character_id)
    return [JournalEntryResponse.model_validate(entry) for entry in entries]

@router.post("/{character_id}/conditions", response_model=ConditionResponse)
async def add_character_condition(
    character_id: UUID,
    condition: ConditionCreate,
    session: AsyncSession = Depends(get_session)
) -> ConditionResponse:
    """Add a condition to a character."""
    repository = CharacterRepository(session)
    condition_data = condition.model_dump() | {"character_id": character_id}
    db_condition = await repository.create_character_condition(condition_data)
    return ConditionResponse.model_validate(db_condition)

@router.get("/{character_id}/conditions", response_model=List[ConditionResponse])
async def get_active_conditions(
    character_id: UUID,
    session: AsyncSession = Depends(get_session)
) -> List[ConditionResponse]:
    """Get all active conditions for a character."""
    repository = CharacterRepository(session)
    conditions = await repository.get_active_conditions(character_id)
    return [ConditionResponse.model_validate(condition) for condition in conditions]

@router.post("/{character_id}/resources", response_model=ClassResourceResponse)
async def add_class_resource(
    character_id: UUID,
    resource: ClassResourceCreate,
    session: AsyncSession = Depends(get_session)
) -> ClassResourceResponse:
    """Add a class resource to a character."""
    repository = CharacterRepository(session)
    resource_data = resource.model_dump() | {"character_id": character_id}
    db_resource = await repository.add_class_resource(resource_data)
    return ClassResourceResponse.model_validate(db_resource)

@router.put("/{character_id}/resources/{resource_id}", response_model=ClassResourceResponse)
async def update_class_resource(
    character_id: UUID,
    resource_id: UUID,
    updates: Dict,
    session: AsyncSession = Depends(get_session)
) -> ClassResourceResponse:
    """Update a class resource."""
    repository = CharacterRepository(session)
    db_resource = await repository.update_class_resource(resource_id, updates)
    if not db_resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    return ClassResourceResponse.model_validate(db_resource)

@router.post("/version-graphs", response_model=VersionGraphResponse)
async def create_version_graph(
    graph: VersionGraphCreate,
    session: AsyncSession = Depends(get_session)
) -> VersionGraphResponse:
    """Create a new version graph."""
    repository = CharacterRepository(session)
    graph_data = graph.model_dump()
    db_graph = await repository.create_version_graph(graph_data)
    return VersionGraphResponse.model_validate(db_graph)

@router.post("/themes", response_model=ThemeResponse)
async def create_theme(
    theme: ThemeCreate,
    session: AsyncSession = Depends(get_session)
) -> ThemeResponse:
    """Create a new theme."""
    repository = CharacterRepository(session)
    theme_data = theme.model_dump()
    db_theme = await repository.create_theme(theme_data)
    return ThemeResponse.model_validate(db_theme)

@router.get("/themes/{theme_id}", response_model=ThemeResponse)
async def get_theme(
    theme_id: UUID,
    session: AsyncSession = Depends(get_session)
) -> ThemeResponse:
    """Get a theme by ID."""
    repository = CharacterRepository(session)
    db_theme = await repository.get_theme(theme_id)
    if not db_theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )
    return ThemeResponse.model_validate(db_theme)