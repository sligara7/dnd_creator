"""
D&D Campaign Creation API
========================
This FastAPI app provides a comprehensive API for D&D campaign creation, management, and collaborative storytelling, as specified in campaign_creation.md.
All endpoints, models, and features are designed for campaign-level operations, not character creation.
"""

import time
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query, Path, Depends
from pydantic import BaseModel, Field
import logging
from sqlalchemy.orm import Session

# Database imports
from src.models.database_models import (
    Campaign, Chapter, PlotFork, 
    CampaignDB, init_database, get_db,
    CampaignStatusEnum, ChapterStatusEnum, PlotForkTypeEnum
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
    updates = request.dict(exclude_unset=True)
    db_campaign = CampaignDB.update_campaign(db, campaign_id, updates)
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
# CAMPAIGN CONTENT MANAGEMENT ENDPOINTS
# =========================

class CampaignCharacterRequest(BaseModel):
    """Request to add/update a character in a campaign."""
    name: str = Field(..., min_length=2, max_length=100)
    player_name: Optional[str] = Field(None, max_length=100)
    character_class: str = Field(..., max_length=50)
    level: int = Field(default=1, ge=1, le=20)
    race: str = Field(..., max_length=50)
    background: str = Field(default="", max_length=100)
    alignment: str = Field(default="Neutral", max_length=50)
    abilities: Dict[str, int] = Field(default_factory=dict)
    hit_points: int = Field(default=1, ge=1)
    armor_class: int = Field(default=10, ge=1)
    backstory: Optional[str] = Field(None, max_length=2000)
    notes: Optional[str] = Field(None, max_length=1000)
    is_active: bool = Field(default=True)

class CampaignNPCRequest(BaseModel):
    """Request to add/update an NPC in a campaign."""
    name: str = Field(..., min_length=2, max_length=100)
    npc_type: str = Field(..., max_length=50)  # "friendly", "neutral", "hostile", "merchant", "quest_giver"
    description: str = Field(..., min_length=10, max_length=500)
    location: Optional[str] = Field(None, max_length=100)
    role: str = Field(default="background", max_length=50)  # "major", "minor", "background"
    stats: Optional[Dict[str, Any]] = Field(default_factory=dict)
    personality: Optional[str] = Field(None, max_length=500)
    motivations: Optional[str] = Field(None, max_length=500)
    relationships: Optional[Dict[str, str]] = Field(default_factory=dict)
    dialogue_notes: Optional[str] = Field(None, max_length=1000)
    is_active: bool = Field(default=True)

class CampaignMonsterRequest(BaseModel):
    """Request to add/update a monster in a campaign."""
    name: str = Field(..., min_length=2, max_length=100)
    monster_type: str = Field(..., max_length=50)
    challenge_rating: float = Field(..., ge=0, le=30)
    stat_block: Dict[str, Any] = Field(..., description="Complete monster stat block")
    description: str = Field(..., min_length=10, max_length=500)
    habitat: Optional[str] = Field(None, max_length=100)
    behavior: Optional[str] = Field(None, max_length=500)
    tactics: Optional[str] = Field(None, max_length=500)
    loot_table: Optional[List[str]] = Field(default_factory=list)
    encounter_notes: Optional[str] = Field(None, max_length=1000)
    is_active: bool = Field(default=True)

class CampaignItemRequest(BaseModel):
    """Request to add/update an item in a campaign."""
    name: str = Field(..., min_length=2, max_length=100)
    item_type: str = Field(..., max_length=50)  # "weapon", "armor", "potion", "scroll", "wondrous", "treasure"
    rarity: str = Field(default="common", max_length=20)  # "common", "uncommon", "rare", "very_rare", "legendary"
    description: str = Field(..., min_length=10, max_length=500)
    properties: Dict[str, Any] = Field(default_factory=dict)
    value_gp: Optional[int] = Field(None, ge=0)
    weight_lbs: Optional[float] = Field(None, ge=0)
    requires_attunement: bool = Field(default=False)
    magic_properties: Optional[str] = Field(None, max_length=500)
    location_found: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    is_active: bool = Field(default=True)

class ChapterMapRequest(BaseModel):
    """Request to add/update a map for a chapter."""
    map_name: str = Field(..., min_length=2, max_length=100)
    map_type: str = Field(..., max_length=50)  # "battle", "exploration", "town", "dungeon", "region"
    description: str = Field(..., min_length=10, max_length=500)
    grid_size: Optional[str] = Field(None, max_length=20)  # "5ft", "10ft", "1mile", etc.
    dimensions: Optional[str] = Field(None, max_length=50)  # "30x40", "large", etc.
    map_url: Optional[str] = Field(None, max_length=500)
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    map_features: Optional[List[str]] = Field(default_factory=list)
    encounter_areas: Optional[Dict[str, str]] = Field(default_factory=dict)
    dm_notes: Optional[str] = Field(None, max_length=1000)
    is_active: bool = Field(default=True)

class ContentResponse(BaseModel):
    """Generic response for campaign content."""
    id: str
    campaign_id: str
    content_type: str
    name: str
    created_at: str
    updated_at: str
    is_active: bool

class ChapterMapResponse(BaseModel):
    """Response for chapter map."""
    id: str
    campaign_id: str
    chapter_id: str
    map_name: str
    map_type: str
    description: str
    map_url: Optional[str]
    created_at: str
    updated_at: str
    is_active: bool

# =========================
# CHARACTER MANAGEMENT ENDPOINTS
# =========================

@app.post("/api/v2/campaigns/{campaign_id}/characters", response_model=ContentResponse, tags=["campaign-content"])
async def add_character_to_campaign(
    campaign_id: str, 
    request: CampaignCharacterRequest, 
    db: Session = Depends(get_db)
):
    """Add a character to a campaign for in-game play."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        # Import the new models
        from src.models.database_models import CampaignCharacterDB, CampaignCharacter
        
        character_data = {
            "campaign_id": campaign_id,
            "name": request.name,
            "player_name": request.player_name,
            "character_class": request.character_class,
            "level": request.level,
            "race": request.race,
            "background": request.background,
            "alignment": request.alignment,
            "abilities": request.abilities,
            "hit_points": request.hit_points,
            "armor_class": request.armor_class,
            "backstory": request.backstory,
            "notes": request.notes,
            "is_active": request.is_active
        }
        
        db_character = CampaignCharacterDB.create_character(db, character_data)
        
        return ContentResponse(
            id=db_character.id,
            campaign_id=campaign_id,
            content_type="character",
            name=db_character.name,
            created_at=db_character.created_at.isoformat(),
            updated_at=db_character.updated_at.isoformat(),
            is_active=db_character.is_active
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add character: {str(e)}")

@app.get("/api/v2/campaigns/{campaign_id}/characters", response_model=List[ContentResponse], tags=["campaign-content"])
async def list_campaign_characters(campaign_id: str, include_inactive: bool = Query(False), db: Session = Depends(get_db)):
    """List all characters in a campaign."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        from src.models.database_models import CampaignCharacterDB
        
        characters = CampaignCharacterDB.list_characters(db, campaign_id, include_inactive)
        
        return [
            ContentResponse(
                id=char.id,
                campaign_id=campaign_id,
                content_type="character",
                name=char.name,
                created_at=char.created_at.isoformat(),
                updated_at=char.updated_at.isoformat(),
                is_active=char.is_active
            )
            for char in characters
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list characters: {str(e)}")

@app.get("/api/v2/campaigns/{campaign_id}/characters/{character_id}", tags=["campaign-content"])
async def get_campaign_character(campaign_id: str, character_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific character in a campaign."""
    try:
        from src.models.database_models import CampaignCharacterDB
        
        character = CampaignCharacterDB.get_character(db, character_id)
        if not character or character.campaign_id != campaign_id:
            raise HTTPException(status_code=404, detail="Character not found")
        
        return character.to_dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get character: {str(e)}")

@app.put("/api/v2/campaigns/{campaign_id}/characters/{character_id}", response_model=ContentResponse, tags=["campaign-content"])
async def update_campaign_character(
    campaign_id: str, 
    character_id: str, 
    request: CampaignCharacterRequest, 
    db: Session = Depends(get_db)
):
    """Update a character in a campaign."""
    try:
        from src.models.database_models import CampaignCharacterDB
        
        character = CampaignCharacterDB.get_character(db, character_id)
        if not character or character.campaign_id != campaign_id:
            raise HTTPException(status_code=404, detail="Character not found")
        
        updates = request.dict(exclude_unset=True)
        updated_character = CampaignCharacterDB.update_character(db, character_id, updates)
        
        return ContentResponse(
            id=updated_character.id,
            campaign_id=campaign_id,
            content_type="character",
            name=updated_character.name,
            created_at=updated_character.created_at.isoformat(),
            updated_at=updated_character.updated_at.isoformat(),
            is_active=updated_character.is_active
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update character: {str(e)}")

@app.delete("/api/v2/campaigns/{campaign_id}/characters/{character_id}", tags=["campaign-content"])
async def remove_character_from_campaign(campaign_id: str, character_id: str, db: Session = Depends(get_db)):
    """Remove (deactivate) a character from a campaign."""
    try:
        from src.models.database_models import CampaignCharacterDB
        
        character = CampaignCharacterDB.get_character(db, character_id)
        if not character or character.campaign_id != campaign_id:
            raise HTTPException(status_code=404, detail="Character not found")
        
        success = CampaignCharacterDB.deactivate_character(db, character_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to remove character")
        
        return {"message": "Character removed from campaign", "character_id": character_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove character: {str(e)}")

# =========================
# NPC MANAGEMENT ENDPOINTS
# =========================

@app.post("/api/v2/campaigns/{campaign_id}/npcs", response_model=ContentResponse, tags=["campaign-content"])
async def add_npc_to_campaign(
    campaign_id: str, 
    request: CampaignNPCRequest, 
    db: Session = Depends(get_db)
):
    """Add an NPC to a campaign."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        from src.models.database_models import CampaignNPCDB
        
        npc_data = request.dict()
        npc_data["campaign_id"] = campaign_id
        
        db_npc = CampaignNPCDB.create_npc(db, npc_data)
        
        return ContentResponse(
            id=db_npc.id,
            campaign_id=campaign_id,
            content_type="npc",
            name=db_npc.name,
            created_at=db_npc.created_at.isoformat(),
            updated_at=db_npc.updated_at.isoformat(),
            is_active=db_npc.is_active
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add NPC: {str(e)}")

@app.get("/api/v2/campaigns/{campaign_id}/npcs", response_model=List[ContentResponse], tags=["campaign-content"])
async def list_campaign_npcs(
    campaign_id: str, 
    npc_type: Optional[str] = Query(None), 
    role: Optional[str] = Query(None),
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db)
):
    """List NPCs in a campaign with optional filtering."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        from src.models.database_models import CampaignNPCDB
        
        npcs = CampaignNPCDB.list_npcs(db, campaign_id, npc_type, role, include_inactive)
        
        return [
            ContentResponse(
                id=npc.id,
                campaign_id=campaign_id,
                content_type="npc",
                name=npc.name,
                created_at=npc.created_at.isoformat(),
                updated_at=npc.updated_at.isoformat(),
                is_active=npc.is_active
            )
            for npc in npcs
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list NPCs: {str(e)}")

@app.get("/api/v2/campaigns/{campaign_id}/npcs/{npc_id}", tags=["campaign-content"])
async def get_campaign_npc(campaign_id: str, npc_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific NPC."""
    try:
        from src.models.database_models import CampaignNPCDB
        
        npc = CampaignNPCDB.get_npc(db, npc_id)
        if not npc or npc.campaign_id != campaign_id:
            raise HTTPException(status_code=404, detail="NPC not found")
        
        return npc.to_dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get NPC: {str(e)}")

@app.put("/api/v2/campaigns/{campaign_id}/npcs/{npc_id}", response_model=ContentResponse, tags=["campaign-content"])
async def update_campaign_npc(
    campaign_id: str, 
    npc_id: str, 
    request: CampaignNPCRequest, 
    db: Session = Depends(get_db)
):
    """Update an NPC in a campaign."""
    try:
        from src.models.database_models import CampaignNPCDB
        
        npc = CampaignNPCDB.get_npc(db, npc_id)
        if not npc or npc.campaign_id != campaign_id:
            raise HTTPException(status_code=404, detail="NPC not found")
        
        updates = request.dict(exclude_unset=True)
        updated_npc = CampaignNPCDB.update_npc(db, npc_id, updates)
        
        return ContentResponse(
            id=updated_npc.id,
            campaign_id=campaign_id,
            content_type="npc",
            name=updated_npc.name,
            created_at=updated_npc.created_at.isoformat(),
            updated_at=updated_npc.updated_at.isoformat(),
            is_active=updated_npc.is_active
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update NPC: {str(e)}")

@app.delete("/api/v2/campaigns/{campaign_id}/npcs/{npc_id}", tags=["campaign-content"])
async def remove_npc_from_campaign(campaign_id: str, npc_id: str, db: Session = Depends(get_db)):
    """Remove (deactivate) an NPC from a campaign."""
    try:
        from src.models.database_models import CampaignNPCDB
        
        npc = CampaignNPCDB.get_npc(db, npc_id)
        if not npc or npc.campaign_id != campaign_id:
            raise HTTPException(status_code=404, detail="NPC not found")
        
        success = CampaignNPCDB.deactivate_npc(db, npc_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to remove NPC")
        
        return {"message": "NPC removed from campaign", "npc_id": npc_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove NPC: {str(e)}")

# =========================
# MONSTER MANAGEMENT ENDPOINTS
# =========================

@app.post("/api/v2/campaigns/{campaign_id}/monsters", response_model=ContentResponse, tags=["campaign-content"])
async def add_monster_to_campaign(
    campaign_id: str, 
    request: CampaignMonsterRequest, 
    db: Session = Depends(get_db)
):
    """Add a monster to a campaign."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        from src.models.database_models import CampaignMonsterDB
        
        monster_data = request.dict()
        monster_data["campaign_id"] = campaign_id
        
        db_monster = CampaignMonsterDB.create_monster(db, monster_data)
        
        return ContentResponse(
            id=db_monster.id,
            campaign_id=campaign_id,
            content_type="monster",
            name=db_monster.name,
            created_at=db_monster.created_at.isoformat(),
            updated_at=db_monster.updated_at.isoformat(),
            is_active=db_monster.is_active
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add monster: {str(e)}")

@app.get("/api/v2/campaigns/{campaign_id}/monsters", response_model=List[ContentResponse], tags=["campaign-content"])
async def list_campaign_monsters(
    campaign_id: str, 
    monster_type: Optional[str] = Query(None),
    cr_min: Optional[float] = Query(None),
    cr_max: Optional[float] = Query(None),
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db)
):
    """List monsters in a campaign with optional filtering."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        from src.models.database_models import CampaignMonsterDB
        
        monsters = CampaignMonsterDB.list_monsters(db, campaign_id, monster_type, cr_min, cr_max, include_inactive)
        
        return [
            ContentResponse(
                id=monster.id,
                campaign_id=campaign_id,
                content_type="monster",
                name=monster.name,
                created_at=monster.created_at.isoformat(),
                updated_at=monster.updated_at.isoformat(),
                is_active=monster.is_active
            )
            for monster in monsters
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list monsters: {str(e)}")

@app.get("/api/v2/campaigns/{campaign_id}/monsters/{monster_id}", tags=["campaign-content"])
async def get_campaign_monster(campaign_id: str, monster_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific monster."""
    try:
        from src.models.database_models import CampaignMonsterDB
        
        monster = CampaignMonsterDB.get_monster(db, monster_id)
        if not monster or monster.campaign_id != campaign_id:
            raise HTTPException(status_code=404, detail="Monster not found")
        
        return monster.to_dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get monster: {str(e)}")

@app.put("/api/v2/campaigns/{campaign_id}/monsters/{monster_id}", response_model=ContentResponse, tags=["campaign-content"])
async def update_campaign_monster(
    campaign_id: str, 
    monster_id: str, 
    request: CampaignMonsterRequest, 
    db: Session = Depends(get_db)
):
    """Update a monster in a campaign."""
    try:
        from src.models.database_models import CampaignMonsterDB
        
        monster = CampaignMonsterDB.get_monster(db, monster_id)
        if not monster or monster.campaign_id != campaign_id:
            raise HTTPException(status_code=404, detail="Monster not found")
        
        updates = request.dict(exclude_unset=True)
        updated_monster = CampaignMonsterDB.update_monster(db, monster_id, updates)
        
        return ContentResponse(
            id=updated_monster.id,
            campaign_id=campaign_id,
            content_type="monster",
            name=updated_monster.name,
            created_at=updated_monster.created_at.isoformat(),
            updated_at=updated_monster.updated_at.isoformat(),
            is_active=updated_monster.is_active
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update monster: {str(e)}")

@app.delete("/api/v2/campaigns/{campaign_id}/monsters/{monster_id}", tags=["campaign-content"])
async def remove_monster_from_campaign(campaign_id: str, monster_id: str, db: Session = Depends(get_db)):
    """Remove (deactivate) a monster from a campaign."""
    try:
        from src.models.database_models import CampaignMonsterDB
        
        monster = CampaignMonsterDB.get_monster(db, monster_id)
        if not monster or monster.campaign_id != campaign_id:
            raise HTTPException(status_code=404, detail="Monster not found")
        
        success = CampaignMonsterDB.deactivate_monster(db, monster_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to remove monster")
        
        return {"message": "Monster removed from campaign", "monster_id": monster_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove monster: {str(e)}")

# =========================
# ITEM MANAGEMENT ENDPOINTS
# =========================

@app.post("/api/v2/campaigns/{campaign_id}/items", response_model=ContentResponse, tags=["campaign-content"])
async def add_item_to_campaign(
    campaign_id: str, 
    request: CampaignItemRequest, 
    db: Session = Depends(get_db)
):
    """Add an item to a campaign."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        from src.models.database_models import CampaignItemDB
        
        item_data = request.dict()
        item_data["campaign_id"] = campaign_id
        
        db_item = CampaignItemDB.create_item(db, item_data)
        
        return ContentResponse(
            id=db_item.id,
            campaign_id=campaign_id,
            content_type="item",
            name=db_item.name,
            created_at=db_item.created_at.isoformat(),
            updated_at=db_item.updated_at.isoformat(),
            is_active=db_item.is_active
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add item: {str(e)}")

@app.get("/api/v2/campaigns/{campaign_id}/items", response_model=List[ContentResponse], tags=["campaign-content"])
async def list_campaign_items(
    campaign_id: str, 
    item_type: Optional[str] = Query(None),
    rarity: Optional[str] = Query(None),
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db)
):
    """List items in a campaign with optional filtering."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        from src.models.database_models import CampaignItemDB
        
        items = CampaignItemDB.list_items(db, campaign_id, item_type, rarity, include_inactive)
        
        return [
            ContentResponse(
                id=item.id,
                campaign_id=campaign_id,
                content_type="item",
                name=item.name,
                created_at=item.created_at.isoformat(),
                updated_at=item.updated_at.isoformat(),
                is_active=item.is_active
            )
            for item in items
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list items: {str(e)}")

@app.get("/api/v2/campaigns/{campaign_id}/items/{item_id}", tags=["campaign-content"])
async def get_campaign_item(campaign_id: str, item_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific item."""
    try:
        from src.models.database_models import CampaignItemDB
        
        item = CampaignItemDB.get_item(db, item_id)
        if not item or item.campaign_id != campaign_id:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return item.to_dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get item: {str(e)}")

@app.put("/api/v2/campaigns/{campaign_id}/items/{item_id}", response_model=ContentResponse, tags=["campaign-content"])
async def update_campaign_item(
    campaign_id: str, 
    item_id: str, 
    request: CampaignItemRequest, 
    db: Session = Depends(get_db)
):
    """Update an item in a campaign."""
    try:
        from src.models.database_models import CampaignItemDB
        
        item = CampaignItemDB.get_item(db, item_id)
        if not item or item.campaign_id != campaign_id:
            raise HTTPException(status_code=404, detail="Item not found")
        
        updates = request.dict(exclude_unset=True)
        updated_item = CampaignItemDB.update_item(db, item_id, updates)
        
        return ContentResponse(
            id=updated_item.id,
            campaign_id=campaign_id,
            content_type="item",
            name=updated_item.name,
            created_at=updated_item.created_at.isoformat(),
            updated_at=updated_item.updated_at.isoformat(),
            is_active=updated_item.is_active
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update item: {str(e)}")

@app.delete("/api/v2/campaigns/{campaign_id}/items/{item_id}", tags=["campaign-content"])
async def remove_item_from_campaign(campaign_id: str, item_id: str, db: Session = Depends(get_db)):
    """Remove (deactivate) an item from a campaign."""
    try:
        from src.models.database_models import CampaignItemDB
        
        item = CampaignItemDB.get_item(db, item_id)
        if not item or item.campaign_id != campaign_id:
            raise HTTPException(status_code=404, detail="Item not found")
        
        success = CampaignItemDB.deactivate_item(db, item_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to remove item")
        
        return {"message": "Item removed from campaign", "item_id": item_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove item: {str(e)}")

# =========================
# CHAPTER MAP MANAGEMENT ENDPOINTS
# =========================

@app.post("/api/v2/campaigns/{campaign_id}/chapters/{chapter_id}/maps", response_model=ChapterMapResponse, tags=["campaign-content"])
async def add_map_to_chapter(
    campaign_id: str, 
    chapter_id: str, 
    request: ChapterMapRequest, 
    db: Session = Depends(get_db)
):
    """Add an encounter map to a chapter."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    chapter = CampaignDB.get_chapter(db, chapter_id)
    
    if not campaign or not chapter or chapter.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Campaign or chapter not found")
    
    try:
        from src.models.database_models import ChapterMapDB
        
        map_data = request.dict()
        map_data["campaign_id"] = campaign_id
        map_data["chapter_id"] = chapter_id
        
        db_map = ChapterMapDB.create_map(db, map_data)
        
        return ChapterMapResponse(
            id=db_map.id,
            campaign_id=campaign_id,
            chapter_id=chapter_id,
            map_name=db_map.map_name,
            map_type=db_map.map_type,
            description=db_map.description,
            map_url=db_map.map_url,
            created_at=db_map.created_at.isoformat(),
            updated_at=db_map.updated_at.isoformat(),
            is_active=db_map.is_active
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add map: {str(e)}")

@app.get("/api/v2/campaigns/{campaign_id}/chapters/{chapter_id}/maps", response_model=List[ChapterMapResponse], tags=["campaign-content"])
async def list_chapter_maps(
    campaign_id: str, 
    chapter_id: str, 
    map_type: Optional[str] = Query(None),
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db)
):
    """List maps for a chapter."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    chapter = CampaignDB.get_chapter(db, chapter_id)
    
    if not campaign or not chapter or chapter.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Campaign or chapter not found")
    
    try:
        from src.models.database_models import ChapterMapDB
        
        maps = ChapterMapDB.list_maps(db, chapter_id, map_type, include_inactive)
        
        return [
            ChapterMapResponse(
                id=map_obj.id,
                campaign_id=campaign_id,
                chapter_id=chapter_id,
                map_name=map_obj.map_name,
                map_type=map_obj.map_type,
                description=map_obj.description,
                map_url=map_obj.map_url,
                created_at=map_obj.created_at.isoformat(),
                updated_at=map_obj.updated_at.isoformat(),
                is_active=map_obj.is_active
            )
            for map_obj in maps
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list maps: {str(e)}")

@app.get("/api/v2/campaigns/{campaign_id}/chapters/{chapter_id}/maps/{map_id}", tags=["campaign-content"])
async def get_chapter_map(campaign_id: str, chapter_id: str, map_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific chapter map."""
    try:
        from src.models.database_models import ChapterMapDB
        
        map_obj = ChapterMapDB.get_map(db, map_id)
        if not map_obj or map_obj.campaign_id != campaign_id or map_obj.chapter_id != chapter_id:
            raise HTTPException(status_code=404, detail="Map not found")
        
        return map_obj.to_dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get map: {str(e)}")

@app.put("/api/v2/campaigns/{campaign_id}/chapters/{chapter_id}/maps/{map_id}", response_model=ChapterMapResponse, tags=["campaign-content"])
async def update_chapter_map(
    campaign_id: str, 
    chapter_id: str, 
    map_id: str, 
    request: ChapterMapRequest, 
    db: Session = Depends(get_db)
):
    """Update a chapter map."""
    try:
        from src.models.database_models import ChapterMapDB
        
        map_obj = ChapterMapDB.get_map(db, map_id)
        if not map_obj or map_obj.campaign_id != campaign_id or map_obj.chapter_id != chapter_id:
            raise HTTPException(status_code=404, detail="Map not found")
        
        updates = request.dict(exclude_unset=True)
        updated_map = ChapterMapDB.update_map(db, map_id, updates)
        
        return ChapterMapResponse(
            id=updated_map.id,
            campaign_id=campaign_id,
            chapter_id=chapter_id,
            map_name=updated_map.map_name,
            map_type=updated_map.map_type,
            description=updated_map.description,
            map_url=updated_map.map_url,
            created_at=updated_map.created_at.isoformat(),
            updated_at=updated_map.updated_at.isoformat(),
            is_active=updated_map.is_active
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update map: {str(e)}")

@app.delete("/api/v2/campaigns/{campaign_id}/chapters/{chapter_id}/maps/{map_id}", tags=["campaign-content"])
async def remove_map_from_chapter(campaign_id: str, chapter_id: str, map_id: str, db: Session = Depends(get_db)):
    """Remove (deactivate) a map from a chapter."""
    try:
        from src.models.database_models import ChapterMapDB
        
        map_obj = ChapterMapDB.get_map(db, map_id)
        if not map_obj or map_obj.campaign_id != campaign_id or map_obj.chapter_id != chapter_id:
            raise HTTPException(status_code=404, detail="Map not found")
        
        success = ChapterMapDB.deactivate_map(db, map_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to remove map")
        
        return {"message": "Map removed from chapter", "map_id": map_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove map: {str(e)}")

# =========================
# BATCH CONTENT MANAGEMENT
# =========================

@app.get("/api/v2/campaigns/{campaign_id}/content-summary", tags=["campaign-content"])
async def get_campaign_content_summary(campaign_id: str, db: Session = Depends(get_db)):
    """Get a summary of all content in a campaign."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        from src.models.database_models import (
            CampaignCharacterDB, CampaignNPCDB, CampaignMonsterDB, 
            CampaignItemDB, ChapterMapDB
        )
        
        summary = {
            "campaign_id": campaign_id,
            "campaign_title": campaign.title,
            "content_counts": {
                "characters": len(CampaignCharacterDB.list_characters(db, campaign_id)),
                "npcs": len(CampaignNPCDB.list_npcs(db, campaign_id)),
                "monsters": len(CampaignMonsterDB.list_monsters(db, campaign_id)),
                "items": len(CampaignItemDB.list_items(db, campaign_id)),
                "chapters": len(CampaignDB.list_chapters(db, campaign_id)),
                "maps": len(ChapterMapDB.list_all_campaign_maps(db, campaign_id))
            },
            "content_by_type": {
                "active_characters": len(CampaignCharacterDB.list_characters(db, campaign_id, include_inactive=False)),
                "active_npcs": len(CampaignNPCDB.list_npcs(db, campaign_id, include_inactive=False)),
                "active_monsters": len(CampaignMonsterDB.list_monsters(db, campaign_id, include_inactive=False)),
                "active_items": len(CampaignItemDB.list_items(db, campaign_id, include_inactive=False)),
                "active_maps": len(ChapterMapDB.list_all_campaign_maps(db, campaign_id, include_inactive=False))
            }
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get content summary: {str(e)}")

@app.post("/api/v2/campaigns/{campaign_id}/content/bulk-deactivate", tags=["campaign-content"])
async def bulk_deactivate_content(
    campaign_id: str,
    content_ids: List[str] = Query(..., description="List of content IDs to deactivate"),
    content_type: str = Query(..., description="Type of content (character, npc, monster, item, map)"),
    db: Session = Depends(get_db)
):
    """Bulk deactivate multiple pieces of content."""
    campaign = CampaignDB.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    try:
        deactivated_count = 0
        failed_ids = []
        
        for content_id in content_ids:
            try:
                if content_type == "character":
                    from src.models.database_models import CampaignCharacterDB
                    success = CampaignCharacterDB.deactivate_character(db, content_id)
                elif content_type == "npc":
                    from src.models.database_models import CampaignNPCDB
                    success = CampaignNPCDB.deactivate_npc(db, content_id)
                elif content_type == "monster":
                    from src.models.database_models import CampaignMonsterDB
                    success = CampaignMonsterDB.deactivate_monster(db, content_id)
                elif content_type == "item":
                    from src.models.database_models import CampaignItemDB
                    success = CampaignItemDB.deactivate_item(db, content_id)
                elif content_type == "map":
                    from src.models.database_models import ChapterMapDB
                    success = ChapterMapDB.deactivate_map(db, content_id)
                else:
                    failed_ids.append(content_id)
                    continue
                
                if success:
                    deactivated_count += 1
                else:
                    failed_ids.append(content_id)
                    
            except Exception:
                failed_ids.append(content_id)
        
        return {
            "message": f"Bulk deactivation completed",
            "campaign_id": campaign_id,
            "content_type": content_type,
            "requested_count": len(content_ids),
            "deactivated_count": deactivated_count,
            "failed_count": len(failed_ids),
            "failed_ids": failed_ids
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk deactivation failed: {str(e)}")

# Import required libraries at the top
import logging
import time
import json
import httpx
