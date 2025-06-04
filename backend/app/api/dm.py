from fastapi import APIRouter, HTTPException, Body, Query, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional
import httpx
import os
import logging
from pydantic import BaseModel

from backend.core.npc.npc import NPC
from backend.core.npc.llm_npc_advisor import LLMNPCAdvisor
from backend.core.character.character import Character
from backend.core.services.ollama_service import OllamaService
from backend.app.dependencies.auth import get_current_user, get_dm_user
from backend.app.models.campaign import (
    CampaignCreate, CampaignResponse, CampaignUpdate,
    SessionCreate, SessionResponse, WaypointCreate, WaypointResponse
)
from backend.app.models.character import CharacterApproval, CharacterResponse
from backend.app.models.journal import JournalCreate, JournalResponse
from backend.app.models.user import User

# Create router with appropriate prefix and tags
router = APIRouter(
    prefix="/api/dm",
    tags=["dm"],
    responses={404: {"description": "Resource not found"}}
)

# Initialize services
ollama_service = OllamaService()
npc_service = NPC()
npc_advisor = LLMNPCAdvisor()
character_service = Character()

# Pydantic models for requests
class MapGenerationRequest(BaseModel):
    map_type: str  # "dungeon", "town", "wilderness", "battle"
    description: str
    style: Optional[str] = "fantasy"
    
class NPCGenerationRequest(BaseModel):
    npc_type: str
    importance: str = "minor"
    campaign_context: Optional[Dict[str, Any]] = None
    count: int = 1

class JournalSummaryRequest(BaseModel):
    campaign_id: str
    session_ids: Optional[List[str]] = None
    focus_areas: Optional[List[str]] = None

# Campaign Management Endpoints
@router.post("/campaigns", response_model=CampaignResponse)
async def create_campaign(
    campaign: CampaignCreate,
    current_user: User = Depends(get_dm_user)
):
    """Create a new campaign"""
    # Add DM reference
    campaign_dict = campaign.dict()
    campaign_dict["dm_id"] = current_user.id
    
    # Create the campaign (implementation depends on your data layer)
    campaign_id = await campaign_service.create_campaign(campaign_dict)
    return await campaign_service.get_campaign(campaign_id)

@router.get("/campaigns", response_model=List[CampaignResponse])
async def list_campaigns(
    current_user: User = Depends(get_dm_user)
):
    """List all campaigns for the current DM"""
    return await campaign_service.list_campaigns(dm_id=current_user.id)

@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_user: User = Depends(get_dm_user)
):
    """Get campaign details by ID"""
    campaign = await campaign_service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    # Verify ownership
    if campaign.get("dm_id") != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this campaign")
        
    return campaign

@router.put("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    campaign_update: CampaignUpdate,
    current_user: User = Depends(get_dm_user)
):
    """Update campaign details"""
    # Check if campaign exists and user is DM
    campaign = await campaign_service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    if campaign.get("dm_id") != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to modify this campaign")
    
    # Apply the update
    update_data = campaign_update.dict(exclude_unset=True)
    await campaign_service.update_campaign(campaign_id, update_data)
    return await campaign_service.get_campaign(campaign_id)

@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    current_user: User = Depends(get_dm_user)
):
    """Delete a campaign"""
    # Check if campaign exists and user is DM
    campaign = await campaign_service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    if campaign.get("dm_id") != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this campaign")
    
    await campaign_service.delete_campaign(campaign_id)
    return {"message": "Campaign deleted successfully"}

# Character Approval Workflow
@router.get("/campaigns/{campaign_id}/pending-characters", response_model=List[CharacterResponse])
async def list_pending_characters(
    campaign_id: str,
    current_user: User = Depends(get_dm_user)
):
    """List characters pending approval for a campaign"""
    # Check campaign exists and user is DM
    campaign = await campaign_service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    if campaign.get("dm_id") != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this campaign")
    
    # Get pending characters
    pending_characters = await character_service.list_characters(
        campaign_id=campaign_id, status="pending_approval"
    )
    return pending_characters

@router.post("/characters/{character_id}/approval", response_model=CharacterResponse)
async def approve_character(
    character_id: str,
    approval: CharacterApproval,
    current_user: User = Depends(get_dm_user)
):
    """Approve or reject a character"""
    # Get character
    character = await character_service.get_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Get campaign and verify DM permissions
    campaign = await campaign_service.get_campaign(character.get("campaign_id"))
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    if campaign.get("dm_id") != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to approve characters for this campaign")
    
    # Apply approval or rejection
    update_data = {
        "status": "approved" if approval.approved else "rejected",
        "dm_notes": approval.notes,
        "revision_requested": approval.revision_requested
    }
    
    await character_service.update_character(character_id, update_data)
    return await character_service.get_character(character_id)

# NPC Generation
@router.post("/npcs", response_model=Dict[str, Any])
async def generate_npcs(
    request: NPCGenerationRequest,
    current_user: User = Depends(get_dm_user)
):
    """Generate NPCs based on DM requirements"""
    try:
        npcs = []
        
        for _ in range(request.count):
            # Generate NPC
            npc_data = npc_service.generate_quick_npc(
                role=request.npc_type, 
                importance_level=request.importance
            )
            
            # If context is provided, adapt the NPC to the campaign
            if request.campaign_context:
                npc_data = npc_advisor.adapt_to_campaign_context(
                    npc_data, request.campaign_context
                )
                
            npcs.append(npc_data)
            
        return {
            "success": True,
            "npcs": npcs,
            "count": len(npcs)
        }
        
    except Exception as e:
        logging.error(f"Error generating NPCs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating NPCs: {str(e)}")

# Map Generation with Stable Diffusion
@router.post("/generate-map")
async def generate_map(
    request: MapGenerationRequest,
    current_user: User = Depends(get_dm_user)
):
    """Generate a map using Stable Diffusion"""
    try:
        # Enhance the map description with D&D specific elements
        enhanced_prompt = f"Fantasy map, top-down view, {request.map_type} setting, {request.description}, detailed, D&D style"
        
        # Call Stable Diffusion service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{os.environ.get('STABLE_DIFFUSION_URL', 'http://stable-diffusion:7860')}/sdapi/v1/txt2img",
                json={
                    "prompt": enhanced_prompt,
                    "negative_prompt": "blurry, distorted, text, words, labels",
                    "steps": 40,
                    "width": 896,
                    "height": 640,
                    "cfg_scale": 8.0
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Error generating map")
                
            return response.json()
            
    except Exception as e:
        logging.error(f"Error generating map: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating map: {str(e)}")

# Session & Waypoint Management
@router.post("/campaigns/{campaign_id}/sessions", response_model=SessionResponse)
async def create_session(
    campaign_id: str,
    session: SessionCreate,
    current_user: User = Depends(get_dm_user)
):
    """Create a new game session for a campaign"""
    # Check campaign exists and user is DM
    campaign = await campaign_service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    if campaign.get("dm_id") != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to manage sessions for this campaign")
    
    # Create the session
    session_dict = session.dict()
    session_dict["campaign_id"] = campaign_id
    
    session_id = await campaign_service.create_session(session_dict)
    return await campaign_service.get_session(session_id)

@router.post("/campaigns/{campaign_id}/waypoints", response_model=WaypointResponse)
async def create_waypoint(
    campaign_id: str,
    waypoint: WaypointCreate,
    current_user: User = Depends(get_dm_user)
):
    """
    Create a waypoint (character evolution milestone)
    Waypoints track character development at key points in the campaign
    """
    # Check campaign exists and user is DM
    campaign = await campaign_service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    if campaign.get("dm_id") != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to manage waypoints for this campaign")
    
    # Create the waypoint
    waypoint_dict = waypoint.dict()
    waypoint_dict["campaign_id"] = campaign_id
    
    waypoint_id = await campaign_service.create_waypoint(waypoint_dict)
    return await campaign_service.get_waypoint(waypoint_id)

# Journal Summaries
@router.post("/journal-summary")
async def generate_journal_summary(
    request: JournalSummaryRequest,
    current_user: User = Depends(get_dm_user)
):
    """
    Generate a summary of journal entries for campaign sessions
    """
    try:
        # Check campaign exists and user is DM
        campaign = await campaign_service.get_campaign(request.campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
            
        if campaign.get("dm_id") != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Not authorized to access this campaign")
        
        # Get journal entries
        journal_entries = await journal_service.get_journal_entries(
            campaign_id=request.campaign_id,
            session_ids=request.session_ids
        )
        
        if not journal_entries:
            return {"summary": "No journal entries found for the selected sessions."}
        
        # Format entries for the LLM
        entries_text = "\n\n".join([
            f"Date: {entry.get('date', 'Unknown')}\n"
            f"Character: {entry.get('character_name', 'Unknown')}\n"
            f"Session: {entry.get('session_name', 'Unknown')}\n"
            f"Entry: {entry.get('content', '')}"
            for entry in journal_entries
        ])
        
        # Create focus area instruction
        focus_instruction = ""
        if request.focus_areas:
            focus_instruction = f"Focus on these aspects: {', '.join(request.focus_areas)}. "
            
        # Create prompt
        system_message = "You are a D&D campaign chronicler. Create a cohesive narrative summary of these journal entries."
        prompt = f"{focus_instruction}Summarize these journal entries into a compelling narrative that captures the key developments, character growth, and important plot points:\n\n{entries_text}"
        
        # Generate summary
        summary = ollama_service.generate_text(
            prompt=prompt,
            system_message=system_message,
            max_tokens=2000,
            temperature=0.7
        )
        
        return {"summary": summary}
        
    except Exception as e:
        logging.error(f"Error generating journal summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating journal summary: {str(e)}")