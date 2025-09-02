"""Character Management Endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID

from character_service.api.v2.dependencies import get_character_service
from character_service.api.v2.models import (
    CharacterCreate,
    CharacterResponse,
    ErrorResponse,
)
from character_service.services.interfaces import CharacterService

router = APIRouter()

@router.get(
    "",
    response_model=List[CharacterResponse],
    responses={500: {"model": ErrorResponse}},
)
async def list_characters(
    user_id: UUID = Query(..., description="User ID to filter characters by"),
    character_service: CharacterService = Depends(get_character_service),
) -> List[CharacterResponse]:
    """List all characters for a user."""
    try:
        characters = await character_service.get_characters_by_user(user_id)
        return [CharacterResponse.model_validate(c.model_dump()) for c in characters]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

@router.get(
    "/{character_id}",
    response_model=CharacterResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def get_character(
    character_id: UUID,
    character_service: CharacterService = Depends(get_character_service),
) -> CharacterResponse:
    """Get character by ID."""
    character = await character_service.get_character(character_id)
    if not character:
        raise HTTPException(
            status_code=404,
            detail=f"Character {character_id} not found",
        )
    return CharacterResponse.model_validate(character.model_dump())

@router.post(
    "",
    response_model=CharacterResponse,
    responses={500: {"model": ErrorResponse}},
)
async def create_character(
    character_create: CharacterCreate,
    character_service: CharacterService = Depends(get_character_service),
) -> CharacterResponse:
    """Create a new character."""
    try:
        character = await character_service.create_character(
            name=character_create.name,
            theme=character_create.theme,
            user_id=character_create.user_id,
            campaign_id=character_create.campaign_id,
            character_data=character_create.character_data,
        )
        return CharacterResponse.model_validate(character.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

@router.delete(
    "/{character_id}",
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def delete_character(
    character_id: UUID,
    character_service: CharacterService = Depends(get_character_service),
) -> None:
    """Delete character by ID."""
    deleted = await character_service.delete_character(character_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Character {character_id} not found",
        )
