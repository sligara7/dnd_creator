from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List, Optional
import httpx
import os
import logging
from pydantic import BaseModel

from backend.core.services.ollama_service import OllamaService
from backend.core.character.character import Character
from backend.core.character.llm_character_advisor import LLMCharacterAdvisor
from backend.core.npc.llm_npc_advisor import LLMNPCAdvisor
from backend.core.personality_and_backstory.abstract_personality import AbstractPersonality

# Set up router
router = APIRouter(
    prefix="/api/ai",
    tags=["ai"],
    responses={404: {"description": "Not found"}},
)

# Models for request/response
class CharacterPromptRequest(BaseModel):
    prompt_type: str  # description, background, abilities, etc.
    prompt_text: str
    character_context: Optional[Dict[str, Any]] = None

class PortraitGenerationRequest(BaseModel):
    character_data: Dict[str, Any]
    style: Optional[str] = "fantasy"
    count: int = 1

class JournalSummaryRequest(BaseModel):
    journal_entries: List[Dict[str, Any]]
    focus: Optional[str] = "all"  # could be "combat", "character-development", etc.

# Service instances
ollama_service = OllamaService()
character_advisor = LLMCharacterAdvisor()
npc_advisor = LLMNPCAdvisor()

# Endpoints
@router.post("/character-prompt", response_model=Dict[str, Any])
async def process_character_prompt(request: CharacterPromptRequest):
    """
    Process character creation prompts and return AI suggestions
    based on the prompt type and text.
    """
    try:
        if request.prompt_type == "description":
            # Initial character concept
            system_message = "You are a D&D character creation assistant. Help create a balanced character concept based on the player's description."
            results = character_advisor.generate_character_concept(request.prompt_text)
            
        elif request.prompt_type == "background":
            # Personality and backstory
            system_message = "You are a D&D character creation assistant. Create a compelling backstory and personality traits."
            results = character_advisor.generate_personality_and_backstory(
                request.prompt_text,
                request.character_context
            )
            
        elif request.prompt_type == "abilities":
            # Powers and abilities
            system_message = "You are a D&D character creation assistant. Suggest balanced abilities and class options."
            results = character_advisor.suggest_class_and_abilities(
                request.prompt_text,
                request.character_context
            )
            
        elif request.prompt_type == "final":
            # Final review and enhancement
            system_message = "You are a D&D character creation assistant. Review this character for balance and rules compliance."
            results = character_advisor.finalize_character_concept(request.character_context)
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported prompt_type: {request.prompt_type}")
            
        return results
        
    except Exception as e:
        logging.error(f"Error processing character prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing prompt: {str(e)}")

@router.post("/generate-portraits")
async def generate_character_portraits(request: PortraitGenerationRequest, background_tasks: BackgroundTasks):
    """
    Generate character portraits using stable diffusion service.
    This is an asynchronous operation that returns a job ID.
    """
    try:
        # Build a character description for the image generation
        character = request.character_data
        species = character.get("species", "human")
        character_class = character.get("class", "adventurer")
        description = character.get("description", "")
        
        # Generate a detailed prompt for stable diffusion
        prompt = character_advisor.generate_portrait_prompt(character)
        
        # Call the stable diffusion service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{os.environ.get('STABLE_DIFFUSION_URL', 'http://stable-diffusion:7860')}/sdapi/v1/txt2img",
                json={
                    "prompt": prompt,
                    "negative_prompt": "deformed, ugly, bad anatomy",
                    "steps": 30,
                    "width": 512,
                    "height": 768,
                    "cfg_scale": 7.5,
                    "batch_size": request.count
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Error generating portrait")
                
            return response.json()
            
    except Exception as e:
        logging.error(f"Error generating portraits: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating portraits: {str(e)}")

@router.post("/journal-summary")
async def generate_journal_summary(request: JournalSummaryRequest):
    """
    Analyze journal entries and create a summarized narrative for the DM.
    """
    try:
        system_message = "You are a D&D campaign chronicler. Summarize these journal entries into a cohesive narrative."
        
        # Prepare content for the LLM
        journal_text = "\n\n".join([
            f"Date: {entry.get('date', 'Unknown')}\n"
            f"Character: {entry.get('character_name', 'Unknown')}\n"
            f"Entry: {entry.get('content', '')}"
            for entry in request.journal_entries
        ])
        
        prompt = f"Summarize the following journal entries focusing on {request.focus} aspects:\n\n{journal_text}"
        
        response = ollama_service.generate_text(
            prompt=prompt,
            system_message=system_message,
            max_tokens=2000,
            temperature=0.7
        )
        
        return {"summary": response}
        
    except Exception as e:
        logging.error(f"Error generating journal summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

@router.post("/npc-generator")
async def generate_npc(npc_type: str, importance: str = "minor", context: Optional[Dict[str, Any]] = None):
    """
    Generate an NPC with the given type and importance level
    """
    try:
        npc_data = npc_advisor.generate_quick_npc(npc_type, importance)
        
        # If context is provided, adapt the NPC to fit the campaign context
        if context:
            npc_data = npc_advisor.adapt_to_campaign_context(npc_data, context)
            
        return npc_data
        
    except Exception as e:
        logging.error(f"Error generating NPC: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating NPC: {str(e)}")

@router.post("/rules-validation")
async def validate_rules(character_data: Dict[str, Any], aspect: str):
    """
    Validate if a character's aspect (abilities, spells, etc) follows D&D 5e rules
    """
    try:
        system_message = "You are a D&D rules expert. Validate if this character aspect follows the official 5e rules."
        
        # Build prompt based on what aspect we're validating
        if aspect == "abilities":
            validation_response = character_advisor.validate_ability_scores(character_data)
        elif aspect == "class_features":
            validation_response = character_advisor.validate_class_features(character_data)
        elif aspect == "spells":
            validation_response = character_advisor.validate_spell_selection(character_data)
        else:
            validation_response = character_advisor.validate_general_rules(character_data, aspect)
            
        return validation_response
        
    except Exception as e:
        logging.error(f"Error validating rules: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error validating rules: {str(e)}")