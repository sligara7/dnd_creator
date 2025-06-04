from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional
from app.models.character import CharacterCreate, CharacterResponse
from app.services.character_service import CharacterService
from app.services.ai_integration import AIService
from app.services.rules_validator import RulesValidator

router = APIRouter()
character_service = CharacterService()
ai_service = AIService()
rules_validator = RulesValidator()

@router.post("/create", response_model=CharacterResponse)
async def create_character(character_data: CharacterCreate):
    """Create a new character"""
    # Validate character against D&D rules
    validation_result = rules_validator.validate_character(character_data)
    if not validation_result["valid"]:
        raise HTTPException(status_code=400, detail=validation_result["errors"])
    
    # Create the character
    character = await character_service.create_character(character_data)
    return character

@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: str):
    """Get character by ID"""
    character = await character_service.get_character_by_id(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character

@router.get("/", response_model=List[CharacterResponse])
async def list_characters(user_id: Optional[str] = None):
    """List characters, optionally filtered by user_id"""
    characters = await character_service.list_characters(user_id)
    return characters

@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(character_id: str, character_data: dict = Body(...)):
    """Update a character"""
    character = await character_service.get_character_by_id(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Validate updates against D&D rules
    validation_result = rules_validator.validate_character_update(character, character_data)
    if not validation_result["valid"]:
        raise HTTPException(status_code=400, detail=validation_result["errors"])
    
    updated_character = await character_service.update_character(character_id, character_data)
    return updated_character

@router.delete("/{character_id}")
async def delete_character(character_id: str):
    """Delete a character"""
    result = await character_service.delete_character(character_id)
    if not result:
        raise HTTPException(status_code=404, detail="Character not found")
    return {"message": "Character deleted successfully"}