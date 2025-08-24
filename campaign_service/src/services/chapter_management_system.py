"""
Chapter Management System

Provides comprehensive chapter management with git-like versioning:
- Chapter generation endpoints
- Chapter content creation
- Chapter dependency management
- Branching and version control
- Visual campaign graph generation
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# Import git-like versioning components
from src.services.chapter_version_manager import (
    ChapterVersionManager, ChapterGitOperations, ChapterVersionType,
    BranchType, ChapterCommit, ChapterBranch
)
from src.models.chapter_version_models import (
    ChapterVersionTypeEnum, BranchTypeEnum, ChapterVersionDB
)

# Import existing services
from src.services.creation import CampaignCreationService, CampaignCreationConfig
from src.services.creation_validation import validate_chapter_content_request
from src.models.campaign_creation_models import ChapterContentRequest, CampaignCreationType
from src.models.database_models import get_db
from src.services.llm_service import create_llm_service

logger = logging.getLogger(__name__)

# ============================================================================
# CHAPTER MANAGEMENT API MODELS
# ============================================================================

class ChapterCreateRequest(BaseModel):
    """Request to create a new chapter."""
    title: str = Field(..., min_length=5, max_length=200)
    summary: str = Field(..., min_length=20, max_length=500)
    content: Optional[Dict[str, Any]] = None
    chapter_order: int = Field(default=0, ge=0)
    branch_name: str = Field(default="main", max_length=100)
    parent_hashes: List[str] = Field(default_factory=list)
    commit_message: str = Field(default="", max_length=500)
    version_type: ChapterVersionTypeEnum = ChapterVersionTypeEnum.DRAFT
    author: str = Field(default="system", max_length=100)

class ChapterGenerateRequest(BaseModel):
    """Request to generate chapter content using LLM."""
    concept: str = Field(..., min_length=50, max_length=500)
    campaign_title: str = Field(..., min_length=5, max_length=100)
    campaign_description: str = Field(default="", max_length=1000)
    chapter_title: str = Field(..., min_length=5, max_length=100)
    chapter_summary: str = Field(..., min_length=20, max_length=500)
    party_level: int = Field(default=1, ge=1, le=20)
    party_size: int = Field(default=4, ge=2, le=8)
    themes: List[str] = Field(default_factory=list)
    include_npcs: bool = True
    include_encounters: bool = True
    include_locations: bool = True
    include_items: bool = True
    branch_name: str = Field(default="main", max_length=100)
    commit_message: str = Field(default="Generated chapter content")

class ChapterBranchRequest(BaseModel):
    """Request to create a new story branch."""
    branch_name: str = Field(..., min_length=3, max_length=100)
    from_chapter_hash: str = Field(..., min_length=12, max_length=12)
    branch_type: BranchTypeEnum = BranchTypeEnum.ALTERNATE
    description: str = Field(default="", max_length=500)
    parent_branch: str = Field(default="main", max_length=100)

class PlayerChoiceRequest(BaseModel):
    """Request to record a player choice and create branch."""
    current_chapter_hash: str = Field(..., min_length=12, max_length=12)
    choice_description: str = Field(..., min_length=10, max_length=1000)
    choice_context: Dict[str, Any] = Field(default_factory=dict)
    options_presented: List[str] = Field(default_factory=list)
    choice_made: Dict[str, Any] = Field(default_factory=dict)
    players_involved: List[str] = Field(default_factory=list)
    new_chapter_content: Dict[str, Any] = Field(default_factory=dict)

class ChapterResponse(BaseModel):
    """Response containing chapter information."""
    id: str
    campaign_id: str
    version_hash: str
    branch_name: str
    title: str
    summary: Optional[str]
    content: Optional[Dict[str, Any]]
    version_type: str
    commit_message: str
    author: str
    commit_timestamp: str
    parent_hashes: List[str]
    is_head: bool

class BranchResponse(BaseModel):
    """Response containing branch information."""
    id: str
    campaign_id: str
    name: str
    branch_type: str
    description: str
    head_commit: str
    parent_branch: Optional[str]
    is_active: bool
    created_at: str

class CampaignGraphResponse(BaseModel):
    """Response containing visual campaign graph."""
    campaign_id: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    branches: List[Dict[str, Any]]
    graph_metadata: Dict[str, Any]

# ============================================================================
# CHAPTER MANAGEMENT SERVICE
# ============================================================================

class ChapterManagementService:
    """
    High-level service for chapter management operations.
    
    Combines LLM generation, git-like versioning, and validation.
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.llm_service = create_llm_service()
        self.campaign_service = CampaignCreationService(
            self.llm_service, 
            CampaignCreationConfig()
        )
        self.version_manager = ChapterVersionManager(db_session)
        self.git_ops = ChapterGitOperations(self.version_manager)
    
    async def generate_chapter_content(self, 
                                     campaign_id: str,
                                     request: ChapterGenerateRequest) -> ChapterResponse:
        """
        Generate chapter content using LLM and create version commit.
        
        This combines content generation with git-like versioning.
        """
        logger.info(f"Generating chapter content: {request.chapter_title}")
        
        # Create LLM generation request
        chapter_request = ChapterContentRequest(
            creation_type=CampaignCreationType.CHAPTER_CONTENT,
            concept=request.concept,
            campaign_title=request.campaign_title,
            campaign_description=request.campaign_description,
            chapter_title=request.chapter_title,
            chapter_summary=request.chapter_summary,
            party_level=request.party_level,
            party_size=request.party_size,
            themes=request.themes,
            include_npcs=request.include_npcs,
            include_encounters=request.include_encounters,
            include_locations=request.include_locations,
            include_items=request.include_items
        )
        
        # Validate request
        validation_result = validate_chapter_content_request(chapter_request)
        if validation_result.has_errors():
            raise HTTPException(
                status_code=400,
                detail=f"Chapter generation validation failed: {'; '.join(validation_result.errors)}"
            )
        
        # Generate content using campaign service
        generation_response = await self.campaign_service.create_content(chapter_request)
        
        if not generation_response.success:
            raise HTTPException(
                status_code=500,
                detail=f"Chapter generation failed: {generation_response.error}"
            )
        
        # Get parent commit hash for current branch
        current_head = self.version_manager._get_current_branch_head(campaign_id, request.branch_name)
        
        # Create chapter version commit
        commit = self.version_manager.commit_chapter(
            campaign_id=campaign_id,
            chapter_content=generation_response.chapter,
            branch_name=request.branch_name,
            commit_message=request.commit_message,
            author="llm_generation",
            version_type=ChapterVersionType.DRAFT,
            parent_hashes=current_head
        )
        
        return self._commit_to_response(campaign_id, commit)
    
    def create_chapter_manually(self, 
                               campaign_id: str,
                               request: ChapterCreateRequest) -> ChapterResponse:
        """
        Create a chapter manually (without LLM generation).
        
        This allows manual chapter creation with git-like versioning.
        """
        logger.info(f"Creating manual chapter: {request.title}")
        
        commit = self.version_manager.commit_chapter(
            campaign_id=campaign_id,
            chapter_content={
                "title": request.title,
                "summary": request.summary,
                "content": request.content or {},
                "chapter_order": request.chapter_order
            },
            branch_name=request.branch_name,
            commit_message=request.commit_message,
            author=request.author,
            version_type=request.version_type,
            parent_hashes=request.parent_hashes
        )
        
        return self._commit_to_response(campaign_id, commit)
    
    def create_story_branch(self,
                           campaign_id: str,
                           request: ChapterBranchRequest) -> BranchResponse:
        """Create a new story branch from existing chapter."""
        logger.info(f"Creating story branch: {request.branch_name}")
        
        branch = self.version_manager.create_branch(
            campaign_id=campaign_id,
            branch_name=request.branch_name,
            from_hash=request.from_chapter_hash,
            branch_type=BranchType(request.branch_type.value),
            description=request.description,
            parent_branch=request.parent_branch
        )
        
        return self._branch_to_response(campaign_id, branch)
    
    async def handle_player_choice(self,
                                 campaign_id: str,
                                 request: PlayerChoiceRequest) -> Tuple[BranchResponse, ChapterResponse]:
        """
        Handle player choice that creates new story branch.
        
        This is the core of dynamic campaign evolution.
        """
        logger.info(f"Handling player choice: {request.choice_description[:50]}...")
        
        # Create branch and new chapter from player choice
        branch, commit = self.version_manager.branch_from_player_choice(
            campaign_id=campaign_id,
            current_chapter_hash=request.current_chapter_hash,
            player_choice={
                "description": request.choice_description,
                "context": request.choice_context,
                "options": request.options_presented,
                "choice": request.choice_made,
                "players": request.players_involved
            },
            new_content=request.new_chapter_content,
            author="player_choice"
        )
        
        branch_response = self._branch_to_response(campaign_id, branch)
        chapter_response = self._commit_to_response(campaign_id, commit)
        
        return branch_response, chapter_response
    
    def get_campaign_visual_graph(self, campaign_id: str) -> CampaignGraphResponse:
        """Get visual git-like graph of campaign structure."""
        graph_data = self.version_manager.generate_campaign_graph(campaign_id)
        
        return CampaignGraphResponse(
            campaign_id=graph_data["campaign_id"],
            nodes=graph_data["nodes"],
            edges=graph_data["edges"],
            branches=graph_data["branches"],
            graph_metadata=graph_data["graph_metadata"]
        )
    
    def get_chapter_history(self, campaign_id: str, chapter_hash: str) -> List[ChapterResponse]:
        """Get full history leading to a chapter."""
        history = self.version_manager.get_chapter_history(campaign_id, chapter_hash)
        return [self._commit_to_response(campaign_id, commit) for commit in history]
    
    def get_campaign_branches(self, campaign_id: str) -> List[BranchResponse]:
        """Get all story branches in campaign."""
        branches = self.version_manager.get_campaign_branches(campaign_id)
        return [self._branch_to_response(campaign_id, branch) for branch in branches]
    
    def checkout_branch(self, campaign_id: str, branch_name: str) -> List[ChapterResponse]:
        """Get all chapters in a specific branch."""
        commits = self.git_ops.checkout_branch(campaign_id, branch_name)
        return [self._commit_to_response(campaign_id, commit) for commit in commits]
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _commit_to_response(self, campaign_id: str, commit: ChapterCommit) -> ChapterResponse:
        """Convert ChapterCommit to API response."""
        return ChapterResponse(
            id=f"{campaign_id}_{commit.hash}",
            campaign_id=campaign_id,
            version_hash=commit.hash,
            branch_name=commit.branch_name,
            title=commit.content.get("title", "Untitled"),
            summary=commit.content.get("summary"),
            content=commit.content,
            version_type=commit.version_type.value,
            commit_message=commit.message,
            author=commit.author,
            commit_timestamp=commit.timestamp.isoformat(),
            parent_hashes=commit.parent_hashes,
            is_head=True  # Simplified for now
        )
    
    def _branch_to_response(self, campaign_id: str, branch: ChapterBranch) -> BranchResponse:
        """Convert ChapterBranch to API response."""
        return BranchResponse(
            id=f"{campaign_id}_{branch.name}",
            campaign_id=campaign_id,
            name=branch.name,
            branch_type=branch.branch_type.value,
            description=branch.description,
            head_commit=branch.head_commit,
            parent_branch=branch.parent_branch,
            is_active=True,  # Simplified for now
            created_at=branch.created_at.isoformat()
        )

# ============================================================================
# CHAPTER MANAGEMENT API ENDPOINTS
# ============================================================================

router = APIRouter(prefix="/api/v2/campaigns", tags=["chapter-management"])

@router.post("/{campaign_id}/chapters/generate", response_model=ChapterResponse)
async def generate_chapter_content(
    campaign_id: str = Path(..., description="Campaign ID"),
    request: ChapterGenerateRequest = ...,
    db: Session = Depends(get_db)
):
    """
    Generate chapter content using LLM with git-like versioning.
    
    Creates a new chapter version commit with AI-generated content.
    """
    service = ChapterManagementService(db)
    return await service.generate_chapter_content(campaign_id, request)

@router.post("/{campaign_id}/chapters/create", response_model=ChapterResponse)
async def create_chapter_manually(
    campaign_id: str = Path(..., description="Campaign ID"),
    request: ChapterCreateRequest = ...,
    db: Session = Depends(get_db)
):
    """
    Create a chapter manually with git-like versioning.
    
    Creates a new chapter version commit with user-provided content.
    """
    service = ChapterManagementService(db)
    return service.create_chapter_manually(campaign_id, request)

@router.post("/{campaign_id}/branches/create", response_model=BranchResponse)
async def create_story_branch(
    campaign_id: str = Path(..., description="Campaign ID"),
    request: ChapterBranchRequest = ...,
    db: Session = Depends(get_db)
):
    """
    Create a new story branch from existing chapter.
    
    Enables alternate storylines and experimental paths.
    """
    service = ChapterManagementService(db)
    return service.create_story_branch(campaign_id, request)

@router.post("/{campaign_id}/player-choice")
async def handle_player_choice(
    campaign_id: str = Path(..., description="Campaign ID"),
    request: PlayerChoiceRequest = ...,
    db: Session = Depends(get_db)
):
    """
    Handle player choice that creates new story branch.
    
    Core functionality for dynamic campaign evolution based on player decisions.
    """
    service = ChapterManagementService(db)
    branch, chapter = await service.handle_player_choice(campaign_id, request)
    
    return {
        "success": True,
        "message": "Player choice processed successfully",
        "new_branch": branch,
        "new_chapter": chapter,
        "choice_summary": request.choice_description
    }

@router.get("/{campaign_id}/graph", response_model=CampaignGraphResponse)
async def get_campaign_visual_graph(
    campaign_id: str = Path(..., description="Campaign ID"),
    db: Session = Depends(get_db)
):
    """
    Get visual git-like graph of campaign structure.
    
    Returns nodes, edges, and branch information for visualization.
    """
    service = ChapterManagementService(db)
    return service.get_campaign_visual_graph(campaign_id)

@router.get("/{campaign_id}/chapters/{chapter_hash}/history", response_model=List[ChapterResponse])
async def get_chapter_history(
    campaign_id: str = Path(..., description="Campaign ID"),
    chapter_hash: str = Path(..., description="Chapter version hash"),
    db: Session = Depends(get_db)
):
    """
    Get full history leading to a chapter version.
    
    Shows the lineage of how the chapter evolved.
    """
    service = ChapterManagementService(db)
    return service.get_chapter_history(campaign_id, chapter_hash)

@router.get("/{campaign_id}/branches", response_model=List[BranchResponse])
async def get_campaign_branches(
    campaign_id: str = Path(..., description="Campaign ID"),
    db: Session = Depends(get_db)
):
    """
    Get all story branches in campaign.
    
    Lists all alternate storylines and experimental paths.
    """
    service = ChapterManagementService(db)
    return service.get_campaign_branches(campaign_id)

@router.get("/{campaign_id}/branches/{branch_name}/chapters", response_model=List[ChapterResponse])
async def checkout_branch(
    campaign_id: str = Path(..., description="Campaign ID"),
    branch_name: str = Path(..., description="Branch name"),
    db: Session = Depends(get_db)
):
    """
    Get all chapters in a specific branch (git checkout).
    
    Shows the complete storyline for a particular branch.
    """
    service = ChapterManagementService(db)
    return service.checkout_branch(campaign_id, branch_name)

@router.get("/{campaign_id}/ascii-graph")
async def get_ascii_campaign_graph(
    campaign_id: str = Path(..., description="Campaign ID"),
    db: Session = Depends(get_db)
):
    """
    Get ASCII art representation of campaign git graph.
    
    Returns text-based visualization similar to 'git log --graph'.
    """
    service = ChapterManagementService(db)
    ascii_graph = service.version_manager.generate_ascii_git_graph(campaign_id)
    
    return {
        "campaign_id": campaign_id,
        "ascii_graph": ascii_graph,
        "generated_at": datetime.utcnow().isoformat()
    }

# ============================================================================
# SKELETON INITIALIZATION ENDPOINTS
# ============================================================================

@router.post("/{campaign_id}/initialize-skeleton")
async def initialize_campaign_skeleton(
    campaign_id: str = Path(..., description="Campaign ID"),
    chapter_count: int = Query(default=8, ge=3, le=20, description="Number of skeleton chapters"),
    db: Session = Depends(get_db)
):
    """
    Initialize campaign with skeleton chapter structure.
    
    Creates the initial "git repository" with bare-bones chapter outlines.
    """
    service = ChapterManagementService(db)
    
    # Generate basic skeleton chapters
    skeleton_chapters = []
    for i in range(chapter_count):
        skeleton_chapters.append({
            "title": f"Chapter {i+1}",
            "summary": f"Skeleton outline for chapter {i+1}",
            "content": {
                "chapter_type": "skeleton",
                "estimated_sessions": 1,
                "party_level_range": [max(1, i), max(1, i+2)]
            },
            "chapter_order": i
        })
    
    # Create skeleton commits
    commits = service.version_manager.create_skeleton_commits(
        campaign_id=campaign_id,
        skeleton_chapters=skeleton_chapters,
        author="skeleton_generator"
    )
    
    # Convert to responses
    chapter_responses = [service._commit_to_response(campaign_id, commit) for commit in commits]
    
    return {
        "success": True,
        "message": f"Campaign skeleton initialized with {len(commits)} chapters",
        "skeleton_chapters": chapter_responses,
        "main_branch_head": commits[-1].hash if commits else None
    }

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'ChapterManagementService',
    'router',
    'ChapterCreateRequest',
    'ChapterGenerateRequest',
    'ChapterBranchRequest',
    'PlayerChoiceRequest',
    'ChapterResponse',
    'BranchResponse',
    'CampaignGraphResponse'
]
