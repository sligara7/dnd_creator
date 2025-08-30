
# =========================
# BACKEND CONTENT LISTING ENDPOINTS (PROXY)
# =========================

# Place these endpoints after app = FastAPI(...)

import httpx

# ...existing code...

# Place these endpoints after app = FastAPI(...)

# Backend content listing endpoints for DM browsing
def register_backend_content_endpoints(app):
    @app.get("/api/v2/backend/characters", tags=["backend-content"])
    async def list_backend_characters(skip: int = 0, limit: int = 50):
        """List available characters (PCs, NPCs, monsters) from the backend service."""
        backend_url = "http://localhost:8000/api/v2/characters"  # Adjust as needed
        params = {"skip": skip, "limit": limit}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(backend_url, params=params, timeout=30.0)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.get("/api/v2/backend/items", tags=["backend-content"])
    async def list_backend_items(skip: int = 0, limit: int = 50):
        """List available items from the backend service."""
        backend_url = "http://localhost:8000/api/v2/items"  # Adjust as needed
        params = {"skip": skip, "limit": limit}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(backend_url, params=params, timeout=30.0)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.get("/api/v2/backend/monsters", tags=["backend-content"])
    async def list_backend_monsters(skip: int = 0, limit: int = 50):
        """List available monsters from the backend service."""
        backend_url = "http://localhost:8000/api/v2/monsters"  # Adjust as needed
        params = {"skip": skip, "limit": limit}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(backend_url, params=params, timeout=30.0)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.get("/api/v2/backend/spells", tags=["backend-content"])
    async def list_backend_spells(skip: int = 0, limit: int = 50):
        """List available spells from the backend service."""
        backend_url = "http://localhost:8000/api/v2/spells"  # Adjust as needed
        params = {"skip": skip, "limit": limit}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(backend_url, params=params, timeout=30.0)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}

# ...existing code...

# Register backend content endpoints after app is created
# (app is defined after imports, so move this call after app = FastAPI(...))
# ...existing code...
"""
D&D Campaign Creation API
========================
This FastAPI app provides a comprehensive API for D&D campaign creation, management, and collaborative storytelling, as specified in campaign_creation.md.
All endpoints, models, and features are designed for campaign-level operations, not character creation.
"""

import time
import uuid
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query, Path, Depends
from pydantic import BaseModel, Field
import logging
from sqlalchemy.orm import Session

# Database imports
from src.models.database_models import (
    Campaign, Chapter, PlotFork, 
    CampaignDB, init_database, get_db,
    CampaignStatusEnum, ChapterStatusEnum, PlotForkTypeEnum,
    CampaignBackendLinkDB
)

# Import backend service integration
from src.services.backend_integration import (
    BackendIntegrationService, BackendContentRequest, 
    create_backend_integration_service
)

app = FastAPI(title="D&D Campaign Creation API", version="2.0")
logger = logging.getLogger("campaign_api")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_database("sqlite:///campaigns.db")

# =========================
# ENUMS & CONSTANTS (use database enums)
# =========================
# Enums are imported from database_models
CampaignStatus = CampaignStatusEnum
ChapterStatus = ChapterStatusEnum  
PlotForkType = PlotForkTypeEnum

# =========================
# MODELS
# =========================
class CampaignCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    themes: List[str] = []
    gm_notes: Optional[str] = None
    initial_prompt: Optional[str] = None

class CampaignUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    themes: Optional[List[str]] = None
    gm_notes: Optional[str] = None
    status: Optional[CampaignStatus] = None

class CampaignResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    themes: List[str]
    gm_notes: Optional[str]
    status: CampaignStatus
    created_at: str
    updated_at: str
    validation_warnings: Optional[List[str]] = None

class ChapterCreateRequest(BaseModel):
    campaign_id: str
    title: str
    summary: Optional[str] = None
    content_prompt: Optional[str] = None

class ChapterUpdateRequest(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    status: Optional[ChapterStatus] = None

class ChapterResponse(BaseModel):
    id: str
    campaign_id: str
    title: str
    summary: Optional[str]
    content: Optional[str]
    status: ChapterStatus
    created_at: str
    updated_at: str

class PlotForkRequest(BaseModel):
    campaign_id: str
    chapter_id: str
    fork_type: PlotForkType
    description: Optional[str] = None
    options: Optional[List[str]] = None

class PlotForkResponse(BaseModel):
    id: str
    campaign_id: str
    chapter_id: str
    fork_type: PlotForkType
    description: Optional[str]
    options: Optional[List[str]]
    created_at: str

class CampaignRefinementRequest(BaseModel):
    refinement_prompt: str
    user_preferences: Optional[Dict[str, Any]] = None

class CampaignMapRequest(BaseModel):
    campaign_id: str
    map_prompt: Optional[str] = None

class CampaignMapResponse(BaseModel):
    campaign_id: str
    map_url: str
    generated_at: str

class CollaborationInviteRequest(BaseModel):
    campaign_id: str
    collaborator_email: str
    role: str

class CollaborationInviteResponse(BaseModel):
    campaign_id: str
    collaborator_email: str
    invite_status: str

class ExperimentIntegrationRequest(BaseModel):
    campaign_id: str
    experiment_type: str
    parameters: Dict[str, Any]

class ExperimentIntegrationResponse(BaseModel):
    campaign_id: str
    experiment_id: str
    status: str

class CampaignGenerationRequest(BaseModel):
    concept: str = Field(..., min_length=50, max_length=500, description="Campaign concept (50-500 words)")
    genre: Optional[str] = Field("fantasy", description="Campaign genre (fantasy, sci-fi, horror, mystery, etc.)")
    complexity: Optional[str] = Field("medium", description="Campaign complexity (simple, medium, complex)")
    session_count: Optional[int] = Field(10, ge=3, le=20, description="Estimated number of sessions")
    themes: Optional[List[str]] = Field(default=[], description="Campaign themes and focus areas")
    setting_theme: Optional[str] = Field(None, description="Setting theme (western, steampunk, cyberpunk, etc.)")

class CampaignSkeletonRequest(BaseModel):
    campaign_id: str
    detail_level: Optional[str] = Field("standard", description="Detail level (basic, standard, detailed)")

class ChapterContentGenerationRequest(BaseModel):
    include_npcs: bool = Field(True, description="Generate NPCs for this chapter")
    include_monsters: bool = Field(True, description="Generate monsters/encounters")
    include_items: bool = Field(True, description="Generate equipment and items")
    include_locations: bool = Field(True, description="Generate location descriptions")
    theme: Optional[str] = Field(None, description="Specific chapter theme")

# =========================
# HEALTH & SYSTEM ENDPOINTS
# =========================
@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok", "message": "Campaign API is running"}

# =========================
# CAMPAIGN CRUD ENDPOINTS
# =========================
@app.post("/api/v2/campaigns", response_model=CampaignResponse, tags=["campaigns"])
async def create_campaign(request: CampaignCreateRequest, db=Depends(get_db)):
    campaign_data = request.dict()
    db_campaign = CampaignDB.create_campaign(db, campaign_data)
    return CampaignResponse(
        id=db_campaign.id,
        title=db_campaign.title,
        description=db_campaign.description,
        themes=db_campaign.themes or [],
        gm_notes=db_campaign.gm_notes,
        status=db_campaign.status,
        created_at=db_campaign.created_at.isoformat() if db_campaign.created_at else None,
        updated_at=db_campaign.updated_at.isoformat() if db_campaign.updated_at else None
    )

@app.get("/api/v2/campaigns", response_model=List[CampaignResponse], tags=["campaigns"])
async def list_campaigns(db=Depends(get_db)):
    campaigns = CampaignDB.list_campaigns(db)
    return [CampaignResponse(
        id=c.id,
        title=c.title,
        description=c.description,
        themes=c.themes or [],
        gm_notes=c.gm_notes,
        status=c.status,
        created_at=c.created_at.isoformat() if c.created_at else None,
        updated_at=c.updated_at.isoformat() if c.updated_at else None
    ) for c in campaigns]

@app.get("/api/v2/campaigns/{campaign_id}", response_model=CampaignResponse, tags=["campaigns"])
async def get_campaign(campaign_id: str, db=Depends(get_db)):
    db_campaign = CampaignDB.get_campaign(db, campaign_id)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignResponse(
        id=db_campaign.id,
        title=db_campaign.title,
        description=db_campaign.description,
        themes=db_campaign.themes or [],
        gm_notes=db_campaign.gm_notes,
        status=db_campaign.status,
        created_at=db_campaign.created_at.isoformat() if db_campaign.created_at else None,
        updated_at=db_campaign.updated_at.isoformat() if db_campaign.updated_at else None
    )

@app.put("/api/v2/campaigns/{campaign_id}", response_model=CampaignResponse, tags=["campaigns"])
async def update_campaign(campaign_id: str, request: CampaignUpdateRequest, db=Depends(get_db)):
    import httpx
    updates = request.dict(exclude_unset=True)
    # Fetch current campaign to compare themes
    current_campaign = CampaignDB.get_campaign(db, campaign_id)
    if not current_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    old_themes = set(current_campaign.themes or [])
    new_themes = set(updates.get("themes", old_themes))
    themes_changed = ("themes" in updates) and (old_themes != new_themes)

    db_campaign = CampaignDB.update_campaign(db, campaign_id, updates)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    retheme_status = None
    if themes_changed:
        # Fetch all character links for this campaign
        character_links = CampaignBackendLinkDB.list_campaign_characters(db, campaign_id)
        character_ids = [link.character_id for link in character_links]
        if character_ids and new_themes:
            # Call character service retheme endpoint
            character_service_url = "http://localhost:8000/api/v2/characters/retheme"  # Adjust as needed
            payload = {
                "character_ids": character_ids,
                "theme": list(new_themes)[0] if len(new_themes) == 1 else list(new_themes)
            }
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(character_service_url, json=payload, timeout=60.0)
                    response.raise_for_status()
                    retheme_status = response.json()
            except Exception as e:
                logger.error(f"Failed to trigger character retheming: {e}")
                retheme_status = {"success": False, "error": str(e)}
        else:
            retheme_status = {"skipped": True, "reason": "No characters or no new theme"}

    result = CampaignResponse(
        id=db_campaign.id,
        title=db_campaign.title,
        description=db_campaign.description,
        themes=db_campaign.themes or [],
        gm_notes=db_campaign.gm_notes,
        status=db_campaign.status,
        created_at=db_campaign.created_at.isoformat() if db_campaign.created_at else None,
        updated_at=db_campaign.updated_at.isoformat() if db_campaign.updated_at else None
    )
    # Optionally, include retheme_status in the response for tracking
    if themes_changed:
        return {"campaign": result, "retheme_status": retheme_status}
    return result

@app.delete("/api/v2/campaigns/{campaign_id}", tags=["campaigns"])
async def delete_campaign(campaign_id: str, db=Depends(get_db)):
    deleted = CampaignDB.delete_campaign(db, campaign_id)
    if deleted:
        return {"message": "Campaign deleted", "campaign_id": campaign_id}
    raise HTTPException(status_code=404, detail="Campaign not found")

# =========================
# CHAPTER CRUD ENDPOINTS
# =========================
@app.post("/api/v2/campaigns/{campaign_id}/chapters", response_model=ChapterResponse, tags=["chapters"])
async def create_chapter(campaign_id: str, request: ChapterCreateRequest, db=Depends(get_db)):
    if not CampaignDB.get_campaign(db, campaign_id):
        raise HTTPException(status_code=404, detail="Campaign not found")
    chapter_data = request.dict()
    chapter_data["campaign_id"] = campaign_id
    db_chapter = CampaignDB.create_chapter(db, chapter_data)
    return ChapterResponse(
        id=db_chapter.id,
        campaign_id=db_chapter.campaign_id,
        title=db_chapter.title,
        summary=db_chapter.summary,
        content=db_chapter.content,
        status=db_chapter.status,
        created_at=db_chapter.created_at.isoformat() if db_chapter.created_at else None,
        updated_at=db_chapter.updated_at.isoformat() if db_chapter.updated_at else None
    )

@app.get("/api/v2/campaigns/{campaign_id}/chapters", response_model=List[ChapterResponse], tags=["chapters"])
async def list_chapters(campaign_id: str, db=Depends(get_db)):
    chapters = CampaignDB.list_chapters(db, campaign_id)
    return [ChapterResponse(
        id=c.id,
        campaign_id=c.campaign_id,
        title=c.title,
        summary=c.summary,
        content=c.content,
        status=c.status,
        created_at=c.created_at.isoformat() if c.created_at else None,
        updated_at=c.updated_at.isoformat() if c.updated_at else None
    ) for c in chapters]

@app.get("/api/v2/campaigns/{campaign_id}/chapters/{chapter_id}", response_model=ChapterResponse, tags=["chapters"])
async def get_chapter(campaign_id: str, chapter_id: str, db=Depends(get_db)):
    db_chapter = CampaignDB.get_chapter(db, chapter_id)
    if not db_chapter or db_chapter.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return ChapterResponse(
        id=db_chapter.id,
        campaign_id=db_chapter.campaign_id,
        title=db_chapter.title,
        summary=db_chapter.summary,
        content=db_chapter.content,
        status=db_chapter.status,
        created_at=db_chapter.created_at.isoformat() if db_chapter.created_at else None,
        updated_at=db_chapter.updated_at.isoformat() if db_chapter.updated_at else None
    )

@app.put("/api/v2/campaigns/{campaign_id}/chapters/{chapter_id}", response_model=ChapterResponse, tags=["chapters"])
async def update_chapter(campaign_id: str, chapter_id: str, request: ChapterUpdateRequest, db=Depends(get_db)):
    db_chapter = CampaignDB.get_chapter(db, chapter_id)
    if not db_chapter or db_chapter.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Chapter not found")
    updates = request.dict(exclude_unset=True)
    db_chapter = CampaignDB.update_chapter(db, chapter_id, updates)
    return ChapterResponse(
        id=db_chapter.id,
        campaign_id=db_chapter.campaign_id,
        title=db_chapter.title,
        summary=db_chapter.summary,
        content=db_chapter.content,
        status=db_chapter.status,
        created_at=db_chapter.created_at.isoformat() if db_chapter.created_at else None,
        updated_at=db_chapter.updated_at.isoformat() if db_chapter.updated_at else None
    )

@app.delete("/api/v2/campaigns/{campaign_id}/chapters/{chapter_id}", tags=["chapters"])
async def delete_chapter(campaign_id: str, chapter_id: str, db=Depends(get_db)):
    db_chapter = CampaignDB.get_chapter(db, chapter_id)
    if db_chapter and db_chapter.campaign_id == campaign_id:
        CampaignDB.delete_chapter(db, chapter_id)
        return {"message": "Chapter deleted", "chapter_id": chapter_id}
    raise HTTPException(status_code=404, detail="Chapter not found")

# =========================
# PLOT FORK MANAGEMENT
# =========================
@app.post("/api/v2/campaigns/{campaign_id}/chapters/{chapter_id}/plot-forks", response_model=PlotForkResponse, tags=["plot-forks"])
async def create_plot_fork(campaign_id: str, chapter_id: str, request: PlotForkRequest, db=Depends(get_db)):
    if not CampaignDB.get_campaign(db, campaign_id) or not CampaignDB.get_chapter(db, chapter_id):
        raise HTTPException(status_code=404, detail="Campaign or chapter not found")
    fork_data = request.dict()
    fork_data["campaign_id"] = campaign_id
    fork_data["chapter_id"] = chapter_id
    db_fork = CampaignDB.create_plot_fork(db, fork_data)
    return PlotForkResponse(
        id=db_fork.id,
        campaign_id=db_fork.campaign_id,
        chapter_id=db_fork.chapter_id,
        fork_type=db_fork.fork_type,
        description=db_fork.description,
        options=db_fork.options,
        created_at=db_fork.created_at.isoformat() if db_fork.created_at else None
    )

@app.get("/api/v2/campaigns/{campaign_id}/plot-forks", response_model=List[PlotForkResponse], tags=["plot-forks"])
async def list_plot_forks(campaign_id: str, db=Depends(get_db)):
    forks = CampaignDB.list_plot_forks(db, campaign_id)
    return [PlotForkResponse(
        id=f.id,
        campaign_id=f.campaign_id,
        chapter_id=f.chapter_id,
        fork_type=f.fork_type,
        description=f.description,
        options=f.options,
        created_at=f.created_at.isoformat() if f.created_at else None
    ) for f in forks]

# =========================
# LLM-POWERED CONTENT GENERATION & REFINEMENT
# =========================
@app.post("/api/v2/campaigns/{campaign_id}/refine", tags=["refinement"])
async def refine_campaign(campaign_id: str, request: CampaignRefinementRequest, db: Session = Depends(get_db)):
    """Refine campaign using LLM (real integration)."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    try:
        from src.services.llm_service import create_llm_service
        llm_service = create_llm_service()
        llm_prompt = f"Refine the following D&D campaign description based on the user prompt.\n\nCurrent Description:\n{campaign.description}\n\nUser Prompt:\n{request.refinement_prompt}\n\nRefined Description:"
        refined = await llm_service.generate_content(
            llm_prompt,
            max_tokens=512,
            temperature=0.8
        )
        updates = {"description": refined.strip()}
        CampaignDB.update_campaign(db, campaign_id, updates)
        return {"message": "Campaign refined", "campaign_id": campaign_id, "refined": True, "refined_description": refined.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM refinement failed: {str(e)}")

@app.post("/api/v2/campaigns/{campaign_id}/chapters/{chapter_id}/generate", tags=["generation"])
async def generate_chapter_content(campaign_id: str, chapter_id: str, prompt: str = Query(...), db: Session = Depends(get_db)):
    """Generate chapter content using LLM (real integration)."""
    chapter = CampaignDB.get_chapter(db, chapter_id)
    if not chapter or chapter.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Chapter not found")
    try:
        from src.services.llm_service import create_llm_service
        llm_service = create_llm_service()
        
        # Get campaign for context
        campaign = CampaignDB.get_campaign(db, campaign_id)
        llm_prompt = f"Generate a detailed D&D campaign chapter based on the following prompt.\n\nCampaign Title: {campaign.title}\nChapter Title: {chapter.title}\nPrompt: {prompt}\n\nChapter Content:"
        generated_content = await llm_service.generate_content(
            llm_prompt,
            max_tokens=1024,
            temperature=0.85
        )
        updates = {"content": generated_content.strip()}
        CampaignDB.update_chapter(db, chapter_id, updates)
        return {"message": "Chapter content generated", "chapter_id": chapter_id, "generated": True, "content": generated_content.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM chapter generation failed: {str(e)}")

# =========================
# MAP GENERATION ENDPOINTS
# =========================
@app.post("/api/v2/campaigns/{campaign_id}/map", response_model=CampaignMapResponse, tags=["maps"])
async def generate_campaign_map(campaign_id: str, request: CampaignMapRequest, db: Session = Depends(get_db)):
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    # Stub: Replace with map generation logic
    map_url = f"https://maps.example.com/{campaign_id}.png"
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return CampaignMapResponse(campaign_id=campaign_id, map_url=map_url, generated_at=now)

# =========================
# COLLABORATION ENDPOINTS
# =========================
@app.post("/api/v2/campaigns/{campaign_id}/collaborators/invite", response_model=CollaborationInviteResponse, tags=["collaboration"])
async def invite_collaborator(campaign_id: str, request: CollaborationInviteRequest, db: Session = Depends(get_db)):
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    # Stub: Replace with actual invite logic
    return CollaborationInviteResponse(
        campaign_id=campaign_id,
        collaborator_email=request.collaborator_email,
        invite_status="sent"
    )

# =========================
# PSYCHOLOGICAL EXPERIMENT INTEGRATION
# =========================
@app.post("/api/v2/campaigns/{campaign_id}/experiment", response_model=ExperimentIntegrationResponse, tags=["experiments"])
async def integrate_experiment(campaign_id: str, request: ExperimentIntegrationRequest, db: Session = Depends(get_db)):
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    # Stub: Replace with experiment integration logic
    experiment_id = f"exp_{int(time.time() * 1000)}"
    return ExperimentIntegrationResponse(
        campaign_id=campaign_id,
        experiment_id=experiment_id,
        status="integrated"
    )

# =========================
# ENHANCED CAMPAIGN GENERATION ENDPOINTS
# =========================
@app.post("/api/v2/campaigns/generate", response_model=CampaignResponse, tags=["generation"])
async def generate_campaign_from_concept(request: CampaignGenerationRequest, db: Session = Depends(get_db)):
    """
    Generate a complete campaign from a user concept using LLM.
    Implements REQ-CAM-001: AI-Driven Campaign Generation from Scratch
    With comprehensive validation per creation_validation.py requirements
    """
    try:
        from src.services.llm_service import create_llm_service
        from src.services.creation_validation import (
            validate_campaign_concept, validate_campaign_structure, 
            validate_generated_campaign, CampaignCreationType
        )
        from src.models.campaign_creation_models import CampaignFromScratchRequest
        
        # Create validation request object
        validation_request = CampaignFromScratchRequest(
            creation_type=CampaignCreationType.FROM_SCRATCH,
            concept=request.concept,
            genre=request.genre,
            complexity=request.complexity,
            estimated_sessions=request.session_count,
            themes=request.themes,
            setting_theme=request.setting_theme
        )
        
        # VALIDATION PHASE 1: Validate input concept (REQ-CAM-002, REQ-CAM-006)
        concept_validation = validate_campaign_concept(request.concept, CampaignCreationType.FROM_SCRATCH)
        if concept_validation.has_errors():
            raise HTTPException(
                status_code=400, 
                detail={
                    "error": "Campaign concept validation failed",
                    "validation_errors": concept_validation.errors,
                    "validation_warnings": concept_validation.warnings
                }
            )
        
        llm_service = create_llm_service()
        
        # Create campaign generation prompt
        llm_prompt = f"""
Generate a D&D campaign based on the following concept:

Concept: {request.concept}
Genre: {request.genre}
Complexity: {request.complexity}
Sessions: {request.session_count}
Themes: {', '.join(request.themes) if request.themes else 'None specified'}
Setting Theme: {request.setting_theme or 'Standard Fantasy'}

Please generate:
1. Campaign Title (compelling and memorable)
2. Campaign Description (2-3 paragraphs describing the main storyline)
3. Key Themes (3-5 major themes the campaign will explore)
4. GM Notes (guidance for running this campaign)

Format as JSON with keys: title, description, themes (array), gm_notes
"""
        
        generated_content = await llm_service.generate_content(
            llm_prompt,
            max_tokens=1024,
            temperature=0.8
        )
        
        # Parse generated content (simplified - would need proper JSON parsing)
        import json
        try:
            campaign_data = json.loads(generated_content)
        except:
            # Fallback if JSON parsing fails
            campaign_data = {
                "title": f"Generated Campaign from: {request.concept[:50]}...",
                "description": generated_content.strip(),
                "themes": request.themes or ["adventure", "exploration"],
                "gm_notes": "Generated campaign - review and customize as needed."
            }
        
        # VALIDATION PHASE 2: Validate campaign structure (REQ-CAM-013, REQ-CAM-014)
        structure_validation = validate_campaign_structure(campaign_data)
        validation_warnings = []
        if structure_validation.has_warnings():
            validation_warnings.extend(structure_validation.warnings)
        if structure_validation.has_errors():
            logger.warning(f"Campaign structure validation errors: {structure_validation.errors}")
            validation_warnings.extend([f"Structure issue: {err}" for err in structure_validation.errors])
        
        # VALIDATION PHASE 3: Validate generated campaign (REQ-CAM-003, REQ-CAM-005)
        generation_validation = validate_generated_campaign(campaign_data)
        if generation_validation.has_warnings():
            validation_warnings.extend(generation_validation.warnings)
        if generation_validation.has_errors():
            logger.warning(f"Generated campaign validation errors: {generation_validation.errors}")
            validation_warnings.extend([f"Content issue: {err}" for err in generation_validation.errors])
        
        # Create campaign in database
        campaign_data["status"] = CampaignStatus.DRAFT.value
        db_campaign = CampaignDB.create_campaign(db, campaign_data)
        
        # Log validation results
        if validation_warnings:
            logger.info(f"Campaign {db_campaign.id} generated with warnings: {validation_warnings}")
        
        response = CampaignResponse(
            id=db_campaign.id,
            title=db_campaign.title,
            description=db_campaign.description,
            themes=db_campaign.themes or [],
            gm_notes=db_campaign.gm_notes,
            status=db_campaign.status,
            created_at=db_campaign.created_at.isoformat() if db_campaign.created_at else None,
            updated_at=db_campaign.updated_at.isoformat() if db_campaign.updated_at else None
        )
        
        # Add validation warnings to response if any
        if validation_warnings:
            response.validation_warnings = validation_warnings
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign generation failed: {str(e)}")

@app.post("/api/v2/campaigns/{campaign_id}/generate-skeleton", tags=["generation"])
async def generate_campaign_skeleton(campaign_id: str, request: CampaignSkeletonRequest, db: Session = Depends(get_db)):
    """
    Generate campaign skeleton with major plot points and chapter outlines.
    Implements REQ-CAM-023-027: Skeleton Plot and Campaign Generation
    With comprehensive validation per creation_validation.py requirements
    """
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        from src.services.llm_service import create_llm_service
        from src.services.creation_validation import (
            validate_campaign_skeleton_request, validate_campaign_structure,
            validate_performance_requirements, CampaignCreationType
        )
        from src.models.campaign_creation_models import CampaignSkeletonRequest as ValidationSkeletonRequest
        
        # Create validation request object
        validation_request = ValidationSkeletonRequest(
            creation_type=CampaignCreationType.SKELETON,
            campaign_id=campaign_id,
            detail_level=request.detail_level
        )
        
        # VALIDATION PHASE 1: Validate skeleton request (REQ-CAM-023-027)
        request_validation = validate_campaign_skeleton_request(validation_request)
        if request_validation.has_errors():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Campaign skeleton request validation failed",
                    "validation_errors": request_validation.errors,
                    "validation_warnings": request_validation.warnings
                }
            )
        
        llm_service = create_llm_service()
        
        llm_prompt = f"""
Generate a campaign skeleton for the following D&D campaign:

Title: {campaign.title}
Description: {campaign.description}
Themes: {', '.join(campaign.themes) if campaign.themes else 'None'}
Detail Level: {request.detail_level}

Create a campaign skeleton with:
1. 5-8 major plot points/milestones
2. 8-12 chapter outlines with titles and 2-3 sentence summaries
3. Story arc progression (beginning, middle, end phases)
4. Key conflicts and resolution points
5. Character hooks and engagement opportunities

Format as structured text with clear sections.
"""
        
        skeleton_content = await llm_service.generate_content(
            llm_prompt,
            max_tokens=1500,
            temperature=0.75
        )
        
        # VALIDATION PHASE 2: Validate skeleton structure and performance
        skeleton_data = {
            "skeleton_content": skeleton_content,
            "campaign_id": campaign_id,
            "detail_level": request.detail_level
        }
        
        structure_validation = validate_campaign_structure(skeleton_data)
        performance_validation = validate_performance_requirements(skeleton_data, CampaignCreationType.SKELETON)
        
        validation_warnings = []
        if structure_validation.has_warnings():
            validation_warnings.extend(structure_validation.warnings)
        if performance_validation.has_warnings():
            validation_warnings.extend(performance_validation.warnings)
        
        # Log validation errors as warnings since skeleton generation should continue
        if structure_validation.has_errors():
            logger.warning(f"Skeleton structure validation errors for campaign {campaign_id}: {structure_validation.errors}")
            validation_warnings.extend([f"Structure issue: {err}" for err in structure_validation.errors])
        if performance_validation.has_errors():
            logger.warning(f"Skeleton performance validation errors for campaign {campaign_id}: {performance_validation.errors}")
            validation_warnings.extend([f"Performance issue: {err}" for err in performance_validation.errors])
        
        # Create chapters based on skeleton (simplified)
        chapter_titles = [
            "Opening Hook", "Inciting Incident", "First Challenge", 
            "Rising Action", "Major Conflict", "Climactic Battle", 
            "Resolution", "Epilogue"
        ]
        
        chapters_created = []
        for i, title in enumerate(chapter_titles):
            chapter_data = {
                "campaign_id": campaign_id,
                "title": f"Chapter {i+1}: {title}",
                "summary": f"Generated chapter summary for {title}",
                "status": ChapterStatus.DRAFT.value
            }
            db_chapter = CampaignDB.create_chapter(db, chapter_data)
            chapters_created.append(db_chapter.id)
        
        # Log validation results
        if validation_warnings:
            logger.info(f"Campaign skeleton {campaign_id} generated with warnings: {validation_warnings}")
        
        response = {
            "message": "Campaign skeleton generated",
            "campaign_id": campaign_id,
            "skeleton_content": skeleton_content,
            "chapters_created": chapters_created,
            "chapter_count": len(chapters_created)
        }
        
        # Add validation warnings to response if any
        if validation_warnings:
            response["validation_warnings"] = validation_warnings
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skeleton generation failed: {str(e)}")

@app.post("/api/v2/campaigns/{campaign_id}/chapters/{chapter_id}/generate-content", tags=["generation"])
async def generate_comprehensive_chapter_content(
    campaign_id: str, 
    chapter_id: str, 
    request: ChapterContentGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive chapter content including NPCs, monsters, items, and locations.
    Implements REQ-CAM-033-037: Chapter Content Generation
    Implements REQ-CAM-064-078: Auto-generation via /backend integration
    With comprehensive validation per creation_validation.py requirements
    """
    campaign = CampaignDB.get_campaign(db, campaign_id)
    chapter = CampaignDB.get_chapter(db, chapter_id)
    
    if not campaign or not chapter or chapter.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Campaign or chapter not found")
    
    try:
        from src.services.llm_service import create_llm_service
        from src.services.creation_validation import (
            validate_chapter_content_request, validate_chapter_content,
            validate_encounter_balance, validate_narrative_quality,
            CampaignCreationType
        )
        from src.models.campaign_creation_models import ChapterContentRequest as ValidationChapterRequest
        
        # Create validation request object
        validation_request = ValidationChapterRequest(
            creation_type=CampaignCreationType.CHAPTER_CONTENT,
            campaign_id=campaign_id,
            chapter_id=chapter_id,
            include_npcs=request.include_npcs,
            include_monsters=request.include_monsters,
            include_items=getattr(request, 'include_items', False),
            include_locations=getattr(request, 'include_locations', False)
        )
        
        # VALIDATION PHASE 1: Validate chapter content request (REQ-CAM-033-037)
        request_validation = validate_chapter_content_request(validation_request)
        if request_validation.has_errors():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Chapter content request validation failed",
                    "validation_errors": request_validation.errors,
                    "validation_warnings": request_validation.warnings
                }
            )
        
        llm_service = create_llm_service()
        
        generated_content = {
            "chapter_content": "",
            "npcs": [],
            "monsters": [],
            "items": [],
            "locations": []
        }
        
        # Generate main chapter content
        chapter_prompt = f"""
Generate detailed content for this D&D campaign chapter:

Campaign: {campaign.title}
Chapter: {chapter.title}
Chapter Summary: {chapter.summary or 'To be determined'}
Campaign Themes: {', '.join(campaign.themes) if campaign.themes else 'Adventure'}
Chapter Theme: {getattr(request, 'theme', 'General adventure')}

Include:
- Detailed scene descriptions
- Key events and encounters
- Dialogue suggestions
- Atmosphere and mood
- Treasure/reward opportunities
- Connection to overall campaign story

Length: 500-800 words
"""
        
        chapter_content = await llm_service.generate_content(
            chapter_prompt,
            max_tokens=1200,
            temperature=0.8
        )
        
        generated_content["chapter_content"] = chapter_content
        
        # Generate NPCs using /backend integration (stubbed for now)
        if request.include_npcs:
            # TODO: Integrate with /backend/api/v2/factory/create endpoint
            # For now, generate using LLM
            npc_prompt = f"Generate 2-3 NPCs for this chapter with names, descriptions, and motivations: {chapter.title}"
            npcs_text = await llm_service.generate_content(npc_prompt, max_tokens=400, temperature=0.9)
            generated_content["npcs"] = [{"generated_text": npcs_text}]
        
        # Generate monsters/encounters
        if request.include_monsters:
            encounter_prompt = f"Generate 1-2 encounters (combat or non-combat) for this chapter: {chapter.title}"
            encounters_text = await llm_service.generate_content(encounter_prompt, max_tokens=400, temperature=0.8)
            generated_content["monsters"] = [{"generated_text": encounters_text}]
        
        # Generate items/equipment
        if getattr(request, 'include_items', False):
            items_prompt = f"Generate appropriate treasure/items for this chapter: {chapter.title}"
            items_text = await llm_service.generate_content(items_prompt, max_tokens=300, temperature=0.8)
            generated_content["items"] = [{"generated_text": items_text}]
        
        # Generate locations
        if getattr(request, 'include_locations', False):
            location_prompt = f"Generate detailed location descriptions for this chapter: {chapter.title}"
            locations_text = await llm_service.generate_content(location_prompt, max_tokens=400, temperature=0.8)
            generated_content["locations"] = [{"generated_text": locations_text}]
        
        # VALIDATION PHASE 2: Validate generated chapter content (REQ-CAM-035, REQ-CAM-036)
        # Estimate party level/size for validation (would come from campaign settings in production)
        estimated_party_level = 3  # Default for mid-level campaigns
        estimated_party_size = 4   # Standard party size
        
        content_validation = validate_chapter_content(generated_content, estimated_party_level, estimated_party_size)
        narrative_validation = validate_narrative_quality(generated_content)
        
        validation_warnings = []
        if content_validation.has_warnings():
            validation_warnings.extend(content_validation.warnings)
        if narrative_validation.has_warnings():
            validation_warnings.extend(narrative_validation.warnings)
        
        # Log validation errors as warnings since content generation should continue
        if content_validation.has_errors():
            logger.warning(f"Chapter content validation errors for {campaign_id}/{chapter_id}: {content_validation.errors}")
            validation_warnings.extend([f"Content issue: {err}" for err in content_validation.errors])
        if narrative_validation.has_errors():
            logger.warning(f"Chapter narrative validation errors for {campaign_id}/{chapter_id}: {narrative_validation.errors}")
            validation_warnings.extend([f"Narrative issue: {err}" for err in narrative_validation.errors])
        
        # VALIDATION PHASE 3: Validate encounter balance if monsters included
        if request.include_monsters and generated_content.get("monsters"):
            encounter_validation = validate_encounter_balance(
                generated_content["monsters"], estimated_party_level, estimated_party_size
            )
            if encounter_validation.has_warnings():
                validation_warnings.extend(encounter_validation.warnings)
            if encounter_validation.has_errors():
                logger.warning(f"Encounter balance validation errors for {campaign_id}/{chapter_id}: {encounter_validation.errors}")
                validation_warnings.extend([f"Encounter issue: {err}" for err in encounter_validation.errors])
        
        # Update chapter with generated content
        updates = {"content": chapter_content}
        CampaignDB.update_chapter(db, chapter_id, updates)
        
        # Log validation results
        if validation_warnings:
            logger.info(f"Chapter content {campaign_id}/{chapter_id} generated with warnings: {validation_warnings}")
        
        response = {
            "message": "Chapter content generated successfully",
            "campaign_id": campaign_id,
            "chapter_id": chapter_id,
            "generated_content": generated_content,
            "content_summary": {
                "chapter_content_length": len(chapter_content),
                "npcs_generated": len(generated_content["npcs"]),
                "monsters_generated": len(generated_content["monsters"]),
                "items_generated": len(generated_content["items"]),
                "locations_generated": len(generated_content["locations"])
            }
        }
        
        # Add validation warnings to response if any
        if validation_warnings:
            response["validation_warnings"] = validation_warnings
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chapter content generation failed: {str(e)}")

# =========================
# BACKEND INTEGRATION FOR CONTENT GENERATION  
# =========================

import httpx
from typing import Union

class BackendIntegrationRequest(BaseModel):
    creation_type: str = Field(..., description="Type to create (npc, monster, character, weapon, armor, spell, other_item)")
    parameters: Optional[Dict[str, Any]] = Field(default={}, description="Creation parameters")
    campaign_context: Optional[str] = Field(None, description="Campaign context for thematic consistency")

class ContentGenerationBatchRequest(BaseModel):
    campaign_id: str
    chapter_id: Optional[str] = None
    content_types: List[str] = Field(..., description="Types of content to generate (npcs, monsters, items, spells)")
    quantity: Optional[Dict[str, int]] = Field(default={}, description="Quantity of each content type")

async def call_backend_factory_endpoint(creation_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call the /backend/api/v2/factory/create endpoint for content generation.
    Implements REQ-CAM-153-157: Content Generation Service Utilization
    """
    # This would be the actual backend URL in production
    backend_url = "http://localhost:8000"  # Adjust as needed
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{backend_url}/api/v2/factory/create",
                json={
                    "creation_type": creation_type,
                    "parameters": parameters
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError:
        # Fallback to LLM generation if backend is unavailable
        return {"error": "Backend unavailable", "fallback": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backend integration failed: {str(e)}")

@app.post("/api/v2/campaigns/{campaign_id}/generate-via-backend", tags=["backend-integration"])
async def generate_content_via_backend(
    campaign_id: str,
    request: BackendIntegrationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate campaign content using the existing /backend factory endpoints.
    Implements REQ-CAM-148-162: Backend Service Integration
    """
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Add campaign context to parameters for thematic consistency
    enhanced_parameters = request.parameters.copy()
    enhanced_parameters.update({
        "campaign_title": campaign.title,
        "campaign_themes": campaign.themes or [],
        "campaign_context": request.campaign_context or campaign.description,
    })
    
    try:
        # Call backend factory endpoint
        backend_result = await call_backend_factory_endpoint(
            request.creation_type,
            enhanced_parameters
        )
        
        if backend_result.get("fallback"):
            # Use LLM fallback if backend unavailable
            from src.services.llm_service import create_llm_service
            llm_service = create_llm_service()
            
            fallback_prompt = f"""
Generate a D&D {request.creation_type} for this campaign:

Campaign: {campaign.title}
Context: {request.campaign_context or campaign.description}
Parameters: {enhanced_parameters}

Create detailed {request.creation_type} content that fits the campaign theme and context.
"""
            
            fallback_content = await llm_service.generate_content(
                fallback_prompt,
                max_tokens=600,
                temperature=0.8
            )
            
            backend_result = {
                "type": request.creation_type,
                "content": fallback_content.strip(),
                "source": "llm_fallback",
                "campaign_integrated": True
            }
        
        return {
            "message": f"Generated {request.creation_type} via backend integration",
            "campaign_id": campaign_id,
            "creation_type": request.creation_type,
            "generated_content": backend_result,
            "parameters_used": enhanced_parameters
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

@app.post("/api/v2/campaigns/{campaign_id}/batch-generate-content", tags=["backend-integration"])
async def batch_generate_campaign_content(
    campaign_id: str,
    request: ContentGenerationBatchRequest,
    db: Session = Depends(get_db)
):
    """
    Batch generate multiple types of content for a campaign using /backend integration.
    Implements REQ-CAM-064-078: Auto-Generation of Campaign Content via /backend Integration
    """
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    chapter = None
    if request.chapter_id:
        chapter = CampaignDB.get_chapter(db, request.chapter_id)
        if not chapter or chapter.campaign_id != campaign_id:
            raise HTTPException(status_code=404, detail="Chapter not found")
    
    generated_content = {}
    
    # Define content type mappings to backend creation types
    content_type_mapping = {
        "npcs": "npc",
        "monsters": "monster", 
        "weapons": "weapon",
        "armor": "armor",
        "spells": "spell",
        "items": "other_item"
    }
    
    # Default quantities if not specified
    default_quantities = {
        "npcs": 3,
        "monsters": 2,
        "weapons": 2,
        "armor": 1,
        "spells": 2,
        "items": 3
    }
    
    try:
        for content_type in request.content_types:
            if content_type not in content_type_mapping:
                continue
                
            backend_creation_type = content_type_mapping[content_type]
            quantity = request.quantity.get(content_type, default_quantities.get(content_type, 1))
            
            generated_items = []
            
            for i in range(quantity):
                # Prepare context-specific parameters
                context_parameters = {
                    "campaign_title": campaign.title,
                    "campaign_themes": campaign.themes or [],
                    "index": i + 1,
                    "total_quantity": quantity
                }
                
                if chapter:
                    context_parameters.update({
                        "chapter_title": chapter.title,
                        "chapter_summary": chapter.summary,
                        "chapter_context": chapter.content
                    })
                
                # Add content-specific parameters
                if content_type == "npcs":
                    context_parameters.update({
                        "role_variety": True,
                        "personality_depth": "detailed",
                        "motivation_complexity": "high"
                    })
                elif content_type == "monsters":
                    context_parameters.update({
                        "encounter_type": "varied",
                        "challenge_appropriate": True,
                        "thematic_consistency": True
                    })
                elif content_type in ["weapons", "armor", "items"]:
                    context_parameters.update({
                        "power_level": "campaign_appropriate",
                        "thematic_design": True,
                        "unique_properties": True
                    })
                elif content_type == "spells":
                    context_parameters.update({
                        "spell_level_variety": True,
                        "thematic_flavoring": True,
                        "campaign_integration": True
                    })
                
                # Generate via backend
                backend_result = await call_backend_factory_endpoint(
                    backend_creation_type,
                    context_parameters
                )
                
                # Handle fallback if needed
                if backend_result.get("fallback"):
                    from src.services.llm_service import create_llm_service
                    llm_service = create_llm_service()
                    
                    fallback_prompt = f"""
Generate a D&D {backend_creation_type} for this campaign:

Campaign: {campaign.title}
Chapter: {chapter.title if chapter else 'General campaign use'}
Context: {context_parameters}

Create a detailed, unique {backend_creation_type} that fits the campaign setting and themes.
Include stats, description, and any special properties.
"""
                    
                    fallback_content = await llm_service.generate_content(
                        fallback_prompt,
                        max_tokens=400,
                        temperature=0.85
                    )
                    
                    backend_result = {
                        "name": f"Generated {backend_creation_type.title()} {i+1}",
                        "content": fallback_content.strip(),
                        "source": "llm_fallback"
                    }
                
                generated_items.append(backend_result)
            
            generated_content[content_type] = generated_items
        
        return {
            "message": "Batch content generation completed",
            "campaign_id": campaign_id,
            "chapter_id": request.chapter_id,
            "content_types_generated": request.content_types,
            "generated_content": generated_content,
            "total_items_generated": sum(len(items) for items in generated_content.values())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch content generation failed: {str(e)}")

@app.post("/api/v2/campaigns/{campaign_id}/chapters/{chapter_id}/populate-via-backend", tags=["backend-integration"])
async def populate_chapter_via_backend(
    campaign_id: str,
    chapter_id: str,
    db: Session = Depends(get_db)
):
    """
    Fully populate a chapter with NPCs, monsters, items, and spells using /backend integration.
    Implements comprehensive chapter population per campaign_creation.md requirements.
    """
    campaign = CampaignDB.get_campaign(db, campaign_id)
    chapter = CampaignDB.get_chapter(db, chapter_id)
    
    if not campaign or not chapter or chapter.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Campaign or chapter not found")
    
    # Generate comprehensive chapter content using batch generation
    batch_request = ContentGenerationBatchRequest(
        campaign_id=campaign_id,
        chapter_id=chapter_id,
        content_types=["npcs", "monsters", "weapons", "armor", "spells", "items"],
        quantity={
            "npcs": 4,      # Major NPCs for the chapter
            "monsters": 3,   # Encounters for the chapter  
            "weapons": 2,    # Treasure weapons
            "armor": 1,      # Treasure armor
            "spells": 3,     # Chapter-specific spells
            "items": 4       # Miscellaneous magical/useful items
        }
    )
    
    batch_result = await batch_generate_campaign_content(campaign_id, batch_request, db)
    
    # Update chapter with generated content summary
    content_summary = f"""
Chapter Content Generated via Backend Integration:

NPCs: {len(batch_result['generated_content'].get('npcs', []))} characters
Monsters/Encounters: {len(batch_result['generated_content'].get('monsters', []))} encounters  
Weapons: {len(batch_result['generated_content'].get('weapons', []))} items
Armor: {len(batch_result['generated_content'].get('armor', []))} items
Spells: {len(batch_result['generated_content'].get('spells', []))} spells
Items: {len(batch_result['generated_content'].get('items', []))} items

Total Generated Items: {batch_result['total_items_generated']}

{chapter.content or 'Original chapter content'}
"""
    
    updates = {"content": content_summary}
    CampaignDB.update_chapter(db, chapter_id, updates)
    
    return {
        "message": "Chapter fully populated via backend integration",
        "campaign_id": campaign_id,
        "chapter_id": chapter_id,
        "population_results": batch_result,
        "chapter_updated": True
    }

# =========================
# BACKEND-INTEGRATED CAMPAIGN CONTENT MODELS
# =========================

class CampaignCharacterLinkRequest(BaseModel):
    """Request to link a character to a campaign via backend service."""
    # Option 1: Create new character via backend
    create_new: Optional[bool] = Field(False, description="Create new character via backend service")
    creation_prompt: Optional[str] = Field(None, min_length=20, max_length=500, description="Prompt for character creation")
    character_type: Optional[str] = Field("character", description="character, npc, monster")
    
    # Option 2: Link existing character by ID
    existing_character_id: Optional[str] = Field(None, description="ID of existing character from backend")
    
    # Campaign-specific metadata
    role_in_campaign: Optional[str] = Field(None, max_length=100, description="Role in this specific campaign")
    campaign_notes: Optional[str] = Field(None, max_length=1000, description="Campaign-specific notes")
    apply_campaign_themes: Optional[bool] = Field(True, description="Apply campaign themes to character creation (optional)")

class CampaignCharacterUpdateRequest(BaseModel):
    """Request to update campaign-specific character information."""
    role_in_campaign: Optional[str] = Field(None, max_length=100)
    campaign_notes: Optional[str] = Field(None, max_length=1000)
    # Note: Core character updates should go through backend service directly

class CampaignCharacterResponse(BaseModel):
    """Response containing character information from backend plus campaign data."""
    # Campaign-specific data
    campaign_id: str
    character_id: str  # ID from backend service
    role_in_campaign: Optional[str]
    campaign_notes: Optional[str]
    added_to_campaign_at: str
    
    # Character data from backend service
    backend_character_data: Dict[str, Any]  # Full character data from backend

class CampaignItemLinkRequest(BaseModel):
    """Request to add an item to a campaign via backend service."""
    # Option 1: Create new item via backend
    create_new: Optional[bool] = Field(False, description="Create new item via backend service")
    creation_prompt: Optional[str] = Field(None, min_length=20, max_length=500, description="Prompt for item creation")
    item_type: Optional[str] = Field("other_item", description="weapon, armor, spell, other_item")
    
    # Option 2: Link existing item by ID
    existing_item_id: Optional[str] = Field(None, description="ID of existing item from backend")
    
    # Campaign-specific metadata
    location_found: Optional[str] = Field(None, max_length=200, description="Where item was found/acquired")
    owner_character_id: Optional[str] = Field(None, description="Character who owns this item")
    campaign_notes: Optional[str] = Field(None, max_length=1000, description="Campaign-specific notes")
    apply_campaign_themes: Optional[bool] = Field(True, description="Apply campaign themes to item creation (optional)")

class CampaignItemResponse(BaseModel):
    """Response containing item information from backend plus campaign data."""
    # Campaign-specific data
    campaign_id: str
    item_id: str  # ID from backend service
    location_found: Optional[str]
    owner_character_id: Optional[str]
    campaign_notes: Optional[str]
    added_to_campaign_at: str
    
    # Item data from backend service
    backend_item_data: Dict[str, Any]  # Full item data from backend

class CampaignItemUpdateRequest(BaseModel):
    """Request to update campaign-specific item information."""
    location_found: Optional[str] = Field(None, max_length=200)
    owner_character_id: Optional[str] = Field(None)
    campaign_notes: Optional[str] = Field(None, max_length=1000)
    # Note: Core item updates should go through backend service directly

# Dependency injection for backend service
async def get_backend_service() -> BackendIntegrationService:
    """Get backend integration service instance."""
    return create_backend_integration_service()

# =========================
# BACKEND-INTEGRATED CHARACTER MANAGEMENT ENDPOINTS
# =========================

@app.post("/api/v2/campaigns/{campaign_id}/characters", response_model=CampaignCharacterResponse, tags=["campaign-characters"])
async def add_character_to_campaign(
    campaign_id: str, 
    request: CampaignCharacterLinkRequest, 
    db: Session = Depends(get_db),
    backend_service: BackendIntegrationService = Depends(get_backend_service)
):
    """Add or link a character to a campaign via backend service."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        character_id = None
        backend_character_data = None
        
        if request.create_new and request.creation_prompt:
            # Create new character via backend service
            creation_request = BackendContentRequest(
                creation_type=request.character_type or "character",
                prompt=request.creation_prompt,
                user_preferences={},
                extra_fields={},
                save_to_database=True
            )
            
            # Apply campaign themes if requested
            if request.apply_campaign_themes and campaign.themes:
                creation_request.user_preferences["campaign_themes"] = campaign.themes
                creation_request.user_preferences["campaign_context"] = campaign.description
                
                # Enhance prompt with campaign context
                enhanced_prompt = f"""
Campaign Context: {campaign.title} - {campaign.description}
Campaign Themes: {', '.join(campaign.themes)}

Character Creation Request: {request.creation_prompt}

Create a character that fits the campaign themes while respecting any specific character requirements in the request.
"""
                creation_request.prompt = enhanced_prompt
            
            # Call backend service
            backend_result = await backend_service.create_content(creation_request)
            if not backend_result.get("success"):
                raise HTTPException(status_code=500, detail="Backend character creation failed")
            
            character_id = backend_result.get("object_id")
            backend_character_data = backend_result.get("result", {})
            
        elif request.existing_character_id:
            # Link existing character
            character_id = request.existing_character_id
            backend_character_data = await backend_service.get_character(character_id)
            if not backend_character_data:
                raise HTTPException(status_code=404, detail="Character not found in backend service")
        
        else:
            raise HTTPException(status_code=400, detail="Must specify either create_new=true with creation_prompt or existing_character_id")
        
        # Check if character is already linked to this campaign
        existing_link = CampaignBackendLinkDB.get_character_link(db, campaign_id, character_id)
        if existing_link:
            raise HTTPException(status_code=409, detail="Character already linked to this campaign")
        
        # Create campaign-character link
        character_link = CampaignBackendLinkDB.link_character(
            db, campaign_id, character_id, 
            request.role_in_campaign, request.campaign_notes
        )
        
        return CampaignCharacterResponse(
            campaign_id=campaign_id,
            character_id=character_id,
            role_in_campaign=character_link.role_in_campaign,
            campaign_notes=character_link.campaign_notes,
            added_to_campaign_at=character_link.added_to_campaign_at.isoformat(),
            backend_character_data=backend_character_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add character: {str(e)}")

@app.get("/api/v2/campaigns/{campaign_id}/characters", response_model=List[CampaignCharacterResponse], tags=["campaign-characters"])
async def list_campaign_characters(
    campaign_id: str,
    db: Session = Depends(get_db),
    backend_service: BackendIntegrationService = Depends(get_backend_service)
):
    """List all characters linked to a campaign."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        character_links = CampaignBackendLinkDB.list_campaign_characters(db, campaign_id)
        
        characters = []
        for link in character_links:
            # Get character data from backend service
            backend_character_data = await backend_service.get_character(link.character_id)
            if backend_character_data:  # Only include characters that still exist in backend
                characters.append(CampaignCharacterResponse(
                    campaign_id=campaign_id,
                    character_id=link.character_id,
                    role_in_campaign=link.role_in_campaign,
                    campaign_notes=link.campaign_notes,
                    added_to_campaign_at=link.added_to_campaign_at.isoformat(),
                    backend_character_data=backend_character_data
                ))
        
        return characters
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list characters: {str(e)}")

@app.get("/api/v2/campaigns/{campaign_id}/characters/{character_id}", response_model=CampaignCharacterResponse, tags=["campaign-characters"])
async def get_campaign_character(
    campaign_id: str, 
    character_id: str, 
    db: Session = Depends(get_db),
    backend_service: BackendIntegrationService = Depends(get_backend_service)
):
    """Get a specific character from a campaign."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        character_link = CampaignBackendLinkDB.get_character_link(db, campaign_id, character_id)
        if not character_link:
            raise HTTPException(status_code=404, detail="Character not linked to this campaign")
        
        # Get character data from backend service
        backend_character_data = await backend_service.get_character(character_id)
        if not backend_character_data:
            raise HTTPException(status_code=404, detail="Character not found in backend service")
        
        return CampaignCharacterResponse(
            campaign_id=campaign_id,
            character_id=character_id,
            role_in_campaign=character_link.role_in_campaign,
            campaign_notes=character_link.campaign_notes,
            added_to_campaign_at=character_link.added_to_campaign_at.isoformat(),
            backend_character_data=backend_character_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get character: {str(e)}")

@app.put("/api/v2/campaigns/{campaign_id}/characters/{character_id}", response_model=CampaignCharacterResponse, tags=["campaign-characters"])
async def update_campaign_character(
    campaign_id: str, 
    character_id: str, 
    request: CampaignCharacterUpdateRequest, 
    db: Session = Depends(get_db),
    backend_service: BackendIntegrationService = Depends(get_backend_service)
):
    """Update campaign-specific character information."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        character_link = CampaignBackendLinkDB.get_character_link(db, campaign_id, character_id)
        if not character_link:
            raise HTTPException(status_code=404, detail="Character not linked to this campaign")
        
        # Update campaign-specific data
        if request.role_in_campaign is not None:
            character_link.role_in_campaign = request.role_in_campaign
        if request.campaign_notes is not None:
            character_link.campaign_notes = request.campaign_notes
        
        db.commit()
        db.refresh(character_link)
        
        # Get updated character data from backend service
        backend_character_data = await backend_service.get_character(character_id)
        if not backend_character_data:
            raise HTTPException(status_code=404, detail="Character not found in backend service")
        
        return CampaignCharacterResponse(
            campaign_id=campaign_id,
            character_id=character_id,
            role_in_campaign=character_link.role_in_campaign,
            campaign_notes=character_link.campaign_notes,
            added_to_campaign_at=character_link.added_to_campaign_at.isoformat(),
            backend_character_data=backend_character_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update character: {str(e)}")

@app.delete("/api/v2/campaigns/{campaign_id}/characters/{character_id}", tags=["campaign-characters"])
async def remove_character_from_campaign(
    campaign_id: str, 
    character_id: str, 
    db: Session = Depends(get_db),
    backend_service: BackendIntegrationService = Depends(get_backend_service)
):
    """Remove a character link from a campaign (does not delete the character from backend)."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        character_link = CampaignBackendLinkDB.get_character_link(db, campaign_id, character_id)
        if not character_link:
            raise HTTPException(status_code=404, detail="Character not linked to this campaign")
        
        # Get character name for response
        backend_character_data = await backend_service.get_character(character_id)
        character_name = backend_character_data.get("name", "Unknown") if backend_character_data else "Unknown"
        
        # Remove link (character remains in backend service)
        CampaignBackendLinkDB.unlink_character(db, campaign_id, character_id)
        
        return {
            "message": "Character unlinked from campaign",
            "character_id": character_id,
            "character_name": character_name,
            "note": "Character still exists in backend service"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove character: {str(e)}")

# =========================
# BACKEND-INTEGRATED ITEM MANAGEMENT ENDPOINTS
# =========================

@app.post("/api/v2/campaigns/{campaign_id}/items", response_model=CampaignItemResponse, tags=["campaign-items"])
async def add_item_to_campaign(
    campaign_id: str, 
    request: CampaignItemLinkRequest, 
    db: Session = Depends(get_db),
    backend_service: BackendIntegrationService = Depends(get_backend_service)
):
    """Add or link an item to a campaign via backend service with graceful fallback."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        item_id = None
        backend_item_data = None
        created_via_backend = False
        
        # Check if backend service is available
        backend_available = await backend_service.health_check()
        
        if request.create_new and request.creation_prompt:
            if backend_available:
                try:
                    # Create new item via backend service
                    creation_context = None
                    if request.apply_campaign_themes and campaign.themes:
                        creation_context = f"{campaign.title} - {campaign.description}"
                        creation_context += f"\nThemes: {', '.join(campaign.themes)}"
                    
                    backend_result = await backend_service.create_item(
                        request.creation_prompt,
                        request.item_type or "other_item",
                        creation_context
                    )
                    
                    if backend_result.get("success"):
                        # Backend created successfully, but we still need to track locally
                        # since backend doesn't have persistent item storage
                        backend_item_data = backend_result.get("result", {})
                        created_via_backend = True
                        
                        # Generate a local ID for tracking
                        item_id = str(uuid.uuid4())
                    else:
                        logger.warning(f"Backend item creation failed, falling back to local: {backend_result}")
                        backend_available = False
                        
                except Exception as e:
                    logger.warning(f"Backend item creation failed, falling back to local: {e}")
                    backend_available = False
            
            if not backend_available:
                # Fallback: Create item locally using LLM service
                try:
                    from src.services.llm_service import create_llm_service
                    llm_service = create_llm_service()
                    
                    # Build enhanced prompt with campaign context
                    enhanced_prompt = request.creation_prompt
                    if request.apply_campaign_themes and campaign.themes:
                        enhanced_prompt = f"""
Campaign: {campaign.title}
Description: {campaign.description}
Themes: {', '.join(campaign.themes)}

Item Request: {request.creation_prompt}

Create an item that fits the campaign setting and themes.
"""
                    
                    # Generate item using LLM
                    item_content = await llm_service.generate_content(
                        enhanced_prompt,
                        max_tokens=400,
                        temperature=0.8
                    )
                    
                    # Structure the generated content
                    backend_item_data = {
                        "name": f"Generated {request.item_type or 'Item'}",
                        "description": item_content.strip(),
                        "item_type": request.item_type or "other_item",
                        "source": "campaign_service_llm",
                        "campaign_integrated": True
                    }
                    
                    # Generate a local ID
                    item_id = str(uuid.uuid4())
                    
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to create item via fallback: {str(e)}")
                        
        elif request.existing_item_id:
            # Link existing item - this would only work if backend service tracks items by ID
            item_id = request.existing_item_id
            if backend_available:
                backend_item_data = await backend_service.get_item_by_id(item_id)
                if not backend_item_data:
                    logger.warning(f"Item {item_id} not found in backend, creating placeholder")
                    backend_item_data = {
                        "id": item_id,
                        "name": "External Item",
                        "description": "Item linked from external source",
                        "source": "external_reference"
                    }
            else:
                # Create a placeholder when backend is unavailable
                backend_item_data = {
                    "id": item_id,
                    "name": "External Item", 
                    "description": "Item reference (backend unavailable)",
                    "source": "external_reference"
                }
        else:
            raise HTTPException(status_code=400, detail="Must specify either create_new=true with creation_prompt or existing_item_id")
        
        # Check if item is already linked to this campaign
        existing_link = CampaignBackendLinkDB.get_item_link(db, campaign_id, item_id)
        if existing_link:
            raise HTTPException(status_code=409, detail="Item already linked to this campaign")
        
        # Create campaign-item link
        item_link = CampaignBackendLinkDB.link_item(
            db, campaign_id, item_id,
            request.location_found, request.owner_character_id, request.campaign_notes
        )
        
        return CampaignItemResponse(
            campaign_id=campaign_id,
            item_id=item_id,
            location_found=item_link.location_found,
            owner_character_id=item_link.owner_character_id,
            campaign_notes=item_link.campaign_notes,
            added_to_campaign_at=item_link.added_to_campaign_at.isoformat(),
            backend_item_data=backend_item_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add item: {str(e)}")

@app.get("/api/v2/campaigns/{campaign_id}/items", response_model=List[CampaignItemResponse], tags=["campaign-items"])
async def list_campaign_items(
    campaign_id: str,
    item_type: Optional[str] = Query(None, description="Filter by item type"),
    owner_character_id: Optional[str] = Query(None, description="Filter by owner character"),
    db: Session = Depends(get_db),
    backend_service: BackendIntegrationService = Depends(get_backend_service)
):
    """List all items linked to a campaign."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        item_links = CampaignBackendLinkDB.list_campaign_items(db, campaign_id)
        
        # Check backend availability for enhanced data
        backend_available = await backend_service.health_check()
        
        items = []
        for link in item_links:
            # Filter by type if specified (would need to check backend data)
            if item_type and backend_available:
                # Skip if filtering and we can't check the item type
                pass
            
            # Filter by owner if specified
            if owner_character_id and link.owner_character_id != owner_character_id:
                continue
            
            # Try to get enhanced item data from backend if available
            backend_item_data = {"id": link.item_id, "name": "Unknown Item", "source": "local_reference"}
            if backend_available:
                try:
                    enhanced_data = await backend_service.get_item_by_id(link.item_id)
                    if enhanced_data:
                        backend_item_data = enhanced_data
                except Exception as e:
                    logger.warning(f"Failed to get item data from backend for {link.item_id}: {e}")
            
            # Apply item type filter if we have the data
            if item_type and backend_item_data.get("item_type") != item_type:
                continue
            
            items.append(CampaignItemResponse(
                campaign_id=campaign_id,
                item_id=link.item_id,
                location_found=link.location_found,
                owner_character_id=link.owner_character_id,
                campaign_notes=link.campaign_notes,
                added_to_campaign_at=link.added_to_campaign_at.isoformat(),
                backend_item_data=backend_item_data
            ))
        
        return items
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list items: {str(e)}")

@app.get("/api/v2/campaigns/{campaign_id}/items/{item_id}", response_model=CampaignItemResponse, tags=["campaign-items"])
async def get_campaign_item(
    campaign_id: str, 
    item_id: str, 
    db: Session = Depends(get_db),
    backend_service: BackendIntegrationService = Depends(get_backend_service)
):
    """Get a specific item from a campaign."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        item_link = CampaignBackendLinkDB.get_item_link(db, campaign_id, item_id)
        if not item_link:
            raise HTTPException(status_code=404, detail="Item not linked to this campaign")
        
        # Try to get item data from backend service
        backend_item_data = {"id": item_id, "name": "Unknown Item", "source": "local_reference"}
        backend_available = await backend_service.health_check()
        
        if backend_available:
            try:
                enhanced_data = await backend_service.get_item_by_id(item_id)
                if enhanced_data:
                    backend_item_data = enhanced_data
            except Exception as e:
                logger.warning(f"Failed to get item data from backend for {item_id}: {e}")
        
        return CampaignItemResponse(
            campaign_id=campaign_id,
            item_id=item_id,
            location_found=item_link.location_found,
            owner_character_id=item_link.owner_character_id,
            campaign_notes=item_link.campaign_notes,
            added_to_campaign_at=item_link.added_to_campaign_at.isoformat(),
            backend_item_data=backend_item_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get item: {str(e)}")

@app.put("/api/v2/campaigns/{campaign_id}/items/{item_id}", response_model=CampaignItemResponse, tags=["campaign-items"])
async def update_campaign_item(
    campaign_id: str, 
    item_id: str, 
    request: CampaignItemUpdateRequest, 
    db: Session = Depends(get_db),
    backend_service: BackendIntegrationService = Depends(get_backend_service)
):
    """Update campaign-specific item information."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        item_link = CampaignBackendLinkDB.get_item_link(db, campaign_id, item_id)
        if not item_link:
            raise HTTPException(status_code=404, detail="Item not linked to this campaign")
        
        # Update campaign-specific data (not the core item data)
        if request.location_found is not None:
            item_link.location_found = request.location_found
        if request.owner_character_id is not None:
            item_link.owner_character_id = request.owner_character_id
        if request.campaign_notes is not None:
            item_link.campaign_notes = request.campaign_notes
        
        db.commit()
        db.refresh(item_link)
        
        # Try to get updated item data from backend service
        backend_item_data = {"id": item_id, "name": "Unknown Item", "source": "local_reference"}
        backend_available = await backend_service.health_check()
        
        if backend_available:
            try:
                enhanced_data = await backend_service.get_item_by_id(item_id)
                if enhanced_data:
                    backend_item_data = enhanced_data
            except Exception as e:
                logger.warning(f"Failed to get item data from backend for {item_id}: {e}")
        
        return CampaignItemResponse(
            campaign_id=campaign_id,
            item_id=item_id,
            location_found=item_link.location_found,
            owner_character_id=item_link.owner_character_id,
            campaign_notes=item_link.campaign_notes,
            added_to_campaign_at=item_link.added_to_campaign_at.isoformat(),
            backend_item_data=backend_item_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update item: {str(e)}")

@app.delete("/api/v2/campaigns/{campaign_id}/items/{item_id}", tags=["campaign-items"])
async def remove_item_from_campaign(
    campaign_id: str, 
    item_id: str, 
    db: Session = Depends(get_db),
    backend_service: BackendIntegrationService = Depends(get_backend_service)
):
    """Remove an item link from a campaign (does not delete the item from backend)."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        item_link = CampaignBackendLinkDB.get_item_link(db, campaign_id, item_id)
        if not item_link:
            raise HTTPException(status_code=404, detail="Item not linked to this campaign")
        
        # Get item name for response if possible
        item_name = "Unknown Item"
        backend_available = await backend_service.health_check()
        
        if backend_available:
            try:
                backend_item_data = await backend_service.get_item_by_id(item_id)
                if backend_item_data:
                    item_name = backend_item_data.get("name", item_name)
            except Exception as e:
                logger.warning(f"Failed to get item name from backend for {item_id}: {e}")
        
        # Remove link (item may remain in backend service if it was created there)
        CampaignBackendLinkDB.unlink_item(db, campaign_id, item_id)
        
        return {
            "message": "Item unlinked from campaign",
            "item_id": item_id,
            "item_name": item_name,
            "note": "Item may still exist in backend service if created there"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove item: {str(e)}")

@app.post("/api/v2/campaigns/{campaign_id}/items/{item_id}/transfer", response_model=CampaignItemResponse, tags=["campaign-items"])
async def transfer_item_to_character(
    campaign_id: str,
    item_id: str,
    new_owner_id: Optional[str] = Query(None, description="Character ID to transfer to (null to unassign)"),
    db: Session = Depends(get_db),
    backend_service: BackendIntegrationService = Depends(get_backend_service)
):
    """Transfer an item to a different character or unassign it."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        item_link = CampaignBackendLinkDB.get_item_link(db, campaign_id, item_id)
        if not item_link:
            raise HTTPException(status_code=404, detail="Item not linked to this campaign")
        
        # Validate new owner if specified
        if new_owner_id:
            new_owner_link = CampaignBackendLinkDB.get_character_link(db, campaign_id, new_owner_id)
            if not new_owner_link:
                raise HTTPException(status_code=400, detail="New owner character not found in this campaign")
        
        # Update item ownership
        item_link.owner_character_id = new_owner_id
        db.commit()
        db.refresh(item_link)
        
        # Try to get item data from backend service
        backend_item_data = {"id": item_id, "name": "Unknown Item", "source": "local_reference"}
        backend_available = await backend_service.health_check()
        
        if backend_available:
            try:
                enhanced_data = await backend_service.get_item_by_id(item_id)
                if enhanced_data:
                    backend_item_data = enhanced_data
            except Exception as e:
                logger.warning(f"Failed to get item data from backend for {item_id}: {e}")
        
        return CampaignItemResponse(
            campaign_id=campaign_id,
            item_id=item_id,
            location_found=item_link.location_found,
            owner_character_id=item_link.owner_character_id,
            campaign_notes=item_link.campaign_notes,
            added_to_campaign_at=item_link.added_to_campaign_at.isoformat(),
            backend_item_data=backend_item_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transfer item: {str(e)}")
