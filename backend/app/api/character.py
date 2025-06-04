from fastapi import APIRouter, HTTPException, Body, Query, Depends
from typing import List, Optional, Dict, Any

from backend.core.character.character import Character
from backend.core.character.llm_character_advisor import LLMCharacterAdvisor
from backend.core.services.data_exporter import DataExporter
from backend.app.dependencies.auth import get_current_user
from backend.app.models.character import CharacterCreate, CharacterResponse, CharacterUpdate
from backend.app.models.user import User

# Create router with appropriate prefix and tags
router = APIRouter(
    prefix="/api/characters",
    tags=["characters"],
    responses={404: {"description": "Character not found"}}
)

# Initialize services
character_service = Character()
character_advisor = LLMCharacterAdvisor()
data_exporter = DataExporter()

@router.post("/", response_model=CharacterResponse)
async def create_character(
    character_data: CharacterCreate,
    enhance: bool = Query(False, description="Use AI to enhance character details"),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new character with optional AI enhancement
    """
    # Add user reference
    character_data_dict = character_data.dict()
    character_data_dict["user_id"] = current_user.id
    
    # Validate character against D&D rules
    validation_result = character_service.validate_character(character_data_dict)
    if not validation_result["valid"]:
        raise HTTPException(status_code=400, detail=validation_result["errors"])
    
    # Apply AI enhancement if requested
    if enhance:
        enhanced_data = character_advisor.enhance_character_concept(character_data_dict)
        character_data_dict.update(enhanced_data)
    
    # Create the character
    character_id = character_service.create_character(character_data_dict)
    return character_service.get_character(character_id)

@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get character by ID"""
    character = character_service.get_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Verify ownership
    if character.get("user_id") != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this character")
    
    return character

@router.get("/", response_model=List[CharacterResponse])
async def list_characters(
    current_user: User = Depends(get_current_user)
):
    """List characters for the current user"""
    characters = character_service.list_characters(user_id=current_user.id)
    return characters

@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: str,
    character_update: CharacterUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a character"""
    # Check if character exists and user owns it
    character = character_service.get_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    if character.get("user_id") != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to modify this character")
    
    # Validate updates against D&D rules
    update_data = character_update.dict(exclude_unset=True)
    validation_result = character_service.validate_character_update(character, update_data)
    if not validation_result["valid"]:
        raise HTTPException(status_code=400, detail=validation_result["errors"])
    
    # Apply the update
    character_service.update_character(character_id, update_data)
    return character_service.get_character(character_id)

@router.delete("/{character_id}")
async def delete_character(
    character_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a character"""
    # Check if character exists and user owns it
    character = character_service.get_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    if character.get("user_id") != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this character")
    
    character_service.delete_character(character_id)
    return {"message": "Character deleted successfully"}

@router.post("/{character_id}/export")
async def export_character(
    character_id: str,
    format: str = Query("json", description="Export format (json, pdf, markdown)"),
    current_user: User = Depends(get_current_user)
):
    """Export character to the specified format"""
    # Check if character exists and user has access
    character = character_service.get_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    if character.get("user_id") != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to export this character")
    
    # Export the character
    result = data_exporter.export_data(
        data=character,
        entity_type="character",
        format=format
    )
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return {
        "success": True,
        "message": result["message"],
        "filepath": result["filepath"]
    }

@router.post("/{character_id}/enhance")
async def enhance_character(
    character_id: str,
    aspects: List[str] = Query(["personality", "backstory"], description="Aspects to enhance"),
    current_user: User = Depends(get_current_user)
):
    """Use AI to enhance specific aspects of a character"""
    # Check if character exists and user has access
    character = character_service.get_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    if character.get("user_id") != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to modify this character")
    
    # Apply AI enhancement to requested aspects
    enhanced_data = {}
    for aspect in aspects:
        if aspect == "personality":
            enhanced_data.update(character_advisor.generate_personality_traits(character))
        elif aspect == "backstory":
            enhanced_data.update(character_advisor.generate_backstory(character))
        elif aspect == "motivations":
            enhanced_data.update(character_advisor.generate_motivations(character))
        elif aspect == "appearance":
            enhanced_data.update(character_advisor.generate_appearance_details(character))
    
    # Update the character with enhanced information
    character_service.update_character(character_id, enhanced_data)
    
    return {
        "success": True,
        "enhanced_aspects": aspects,
        "character": character_service.get_character(character_id)
    }

@router.post("/{character_id}/level-up")
async def level_up_character(
    character_id: str,
    options: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Level up a character with specified options"""
    # Check if character exists and user has access
    character = character_service.get_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    if character.get("user_id") != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to modify this character")
    
    # Perform level up
    try:
        updated_character = character_service.level_up(character_id, options)
        return updated_character
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))