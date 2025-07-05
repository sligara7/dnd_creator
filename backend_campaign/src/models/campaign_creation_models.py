"""
Campaign Creation Models

Pydantic models for campaign creation API requests and responses.
Based on requirements from campaign_creation.md
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime

# Import from existing generators for consistency
from src.services.generators import (
    CampaignGenre, 
    CampaignComplexity, 
    SettingTheme, 
    PsychologicalExperimentType
)

# ============================================================================
# CAMPAIGN CREATION REQUEST MODELS
# ============================================================================

class CampaignCreationType(str, Enum):
    """Types of campaign creation supported by the API."""
    CAMPAIGN_FROM_SCRATCH = "campaign_from_scratch"
    CAMPAIGN_SKELETON = "campaign_skeleton" 
    CHAPTER_CONTENT = "chapter_content"
    ITERATIVE_REFINEMENT = "iterative_refinement"
    ADAPTIVE_CONTENT = "adaptive_content"
    PSYCHOLOGICAL_EXPERIMENT = "psychological_experiment"
    SETTING_THEME = "setting_theme"
    NPC_FOR_CAMPAIGN = "npc_for_campaign"
    MONSTER_FOR_CAMPAIGN = "monster_for_campaign"
    EQUIPMENT_FOR_CAMPAIGN = "equipment_for_campaign"

class BaseCampaignRequest(BaseModel):
    """Base model for all campaign creation requests."""
    creation_type: CampaignCreationType
    concept: str = Field(..., min_length=50, max_length=500, 
                        description="Campaign concept (50-500 words)")
    
    @validator('concept')
    def validate_concept_length(cls, v):
        word_count = len(v.split())
        if not (50 <= word_count <= 500):
            raise ValueError(f"Concept must be 50-500 words, got {word_count}")
        return v

class CampaignFromScratchRequest(BaseCampaignRequest):
    """Request model for creating a complete campaign from scratch."""
    creation_type: CampaignCreationType = CampaignCreationType.CAMPAIGN_FROM_SCRATCH
    
    # Core campaign parameters
    genre: CampaignGenre = CampaignGenre.FANTASY
    complexity: CampaignComplexity = CampaignComplexity.MEDIUM
    session_count: int = Field(default=10, ge=3, le=20, 
                              description="Number of planned sessions (3-20)")
    themes: List[str] = Field(default_factory=list, 
                             description="Campaign themes and focus areas")
    setting_theme: Optional[SettingTheme] = SettingTheme.STANDARD_FANTASY
    
    # Character integration parameters
    party_level: int = Field(default=1, ge=1, le=20, 
                            description="Starting party level")
    party_size: int = Field(default=4, ge=2, le=8, 
                           description="Expected party size")
    use_character_service: bool = Field(default=True, 
                                       description="Use backend character service for NPCs/monsters")
    
    # Advanced options
    include_psychological_experiments: bool = False
    experiment_types: List[PsychologicalExperimentType] = Field(default_factory=list)
    custom_requirements: Dict[str, Any] = Field(default_factory=dict, 
                                               description="Additional custom requirements")

class CampaignSkeletonRequest(BaseCampaignRequest):
    """Request model for creating a campaign skeleton."""
    creation_type: CampaignCreationType = CampaignCreationType.CAMPAIGN_SKELETON
    
    campaign_title: str = Field(..., min_length=5, max_length=100)
    campaign_description: str = Field(..., min_length=50, max_length=1000)
    themes: List[str] = Field(default_factory=list)
    session_count: int = Field(default=10, ge=3, le=20)
    detail_level: str = Field(default="standard", pattern="^(basic|standard|detailed)$")

class ChapterContentRequest(BaseCampaignRequest):
    """Request model for creating chapter content."""
    creation_type: CampaignCreationType = CampaignCreationType.CHAPTER_CONTENT
    
    # Chapter identification
    campaign_title: str = Field(..., min_length=5, max_length=100)
    campaign_description: str = Field(default="", max_length=1000)
    chapter_title: str = Field(..., min_length=5, max_length=100)
    chapter_summary: str = Field(..., min_length=20, max_length=500)
    
    # Campaign context for character service integration
    genre: CampaignGenre = CampaignGenre.FANTASY
    setting_theme: SettingTheme = SettingTheme.STANDARD_FANTASY
    complexity: CampaignComplexity = CampaignComplexity.MEDIUM
    party_level: int = Field(default=1, ge=1, le=20)
    party_size: int = Field(default=4, ge=2, le=8)
    
    # Content generation flags
    themes: List[str] = Field(default_factory=list)
    chapter_theme: Optional[str] = None
    include_npcs: bool = True
    include_encounters: bool = True
    include_locations: bool = True
    include_items: bool = True
    use_character_service: bool = True

class CampaignRefinementRequest(BaseModel):
    """Request model for refining existing campaigns."""
    creation_type: CampaignCreationType = CampaignCreationType.ITERATIVE_REFINEMENT
    
    # Existing campaign data
    campaign_id: Optional[str] = None
    existing_data: Dict[str, Any] = Field(..., 
                                         description="Current campaign content to refine")
    
    # Refinement parameters
    refinement_prompt: str = Field(..., min_length=20, max_length=1000,
                                  description="Guidance for how to refine the campaign")
    refinement_type: str = Field(default="enhance", pattern="^(enhance|modify|player_driven)$")
    preserve_elements: List[str] = Field(default_factory=lambda: ['title', 'core_concept', 'main_characters'],
                                        description="Elements to preserve during refinement")
    player_feedback: List[str] = Field(default_factory=list,
                                      description="Player feedback to incorporate")
    refinement_cycles: int = Field(default=1, ge=1, le=5,
                                  description="Number of refinement iterations")

class PsychologicalExperimentRequest(BaseCampaignRequest):
    """Request model for psychological experiment integration."""
    creation_type: CampaignCreationType = CampaignCreationType.PSYCHOLOGICAL_EXPERIMENT
    
    experiment_type: PsychologicalExperimentType = PsychologicalExperimentType.CUSTOM
    campaign_context: str = Field(default="", max_length=1000,
                                 description="Existing campaign context for integration")
    custom_concept: str = Field(default="", max_length=500,
                               description="Custom experiment concept if type is CUSTOM")

class SettingThemeRequest(BaseCampaignRequest):
    """Request model for custom setting theme creation."""
    creation_type: CampaignCreationType = CampaignCreationType.SETTING_THEME
    
    base_genre: CampaignGenre = CampaignGenre.FANTASY
    enhance_existing: Optional[SettingTheme] = None

class CharacterForCampaignRequest(BaseModel):
    """Request model for generating characters for campaigns."""
    creation_type: CampaignCreationType
    concept: str = Field(..., min_length=10, max_length=200)
    
    # Campaign context for character generation
    campaign_context: Dict[str, Any] = Field(..., 
                                            description="Campaign context for character integration")
    
    # Character requirements
    character_count: int = Field(default=1, ge=1, le=10)
    narrative_roles: List[str] = Field(default_factory=list,
                                      description="Required narrative roles (ally, antagonist, etc.)")
    challenge_ratings: List[int] = Field(default_factory=list,
                                        description="Challenge ratings for monsters")

# ============================================================================
# CAMPAIGN CREATION RESPONSE MODELS
# ============================================================================

class CampaignMetadata(BaseModel):
    """Metadata about campaign creation process."""
    source: str = Field(..., description="Generation source (llm, fallback, character_service)")
    attempts: int = Field(..., description="Number of generation attempts")
    generated_at: datetime = Field(..., description="Timestamp of generation")
    generation_time: float = Field(..., description="Time taken in seconds")
    within_timeout: bool = Field(..., description="Whether generation completed within timeout")
    timeout_limit: int = Field(..., description="Timeout limit used")

class CampaignCharacterData(BaseModel):
    """Data for characters generated for campaigns."""
    npcs: List[Dict[str, Any]] = Field(default_factory=list)
    monsters: List[Dict[str, Any]] = Field(default_factory=list)
    requirements_analysis: Dict[str, Any] = Field(default_factory=dict)
    generation_method: str = Field(default="llm_only")

class CampaignChapterData(BaseModel):
    """Data for a campaign chapter."""
    narrative: Dict[str, Any] = Field(default_factory=dict)
    npcs: Dict[str, Any] = Field(default_factory=dict)
    encounters: Dict[str, Any] = Field(default_factory=dict)
    locations: Dict[str, Any] = Field(default_factory=dict)
    items: Dict[str, Any] = Field(default_factory=dict)
    hooks: Dict[str, Any] = Field(default_factory=dict)
    generation_metadata: Dict[str, Any] = Field(default_factory=dict)

class CampaignSkeletonData(BaseModel):
    """Data for a campaign skeleton."""
    major_plot_points: List[Dict[str, Any]] = Field(default_factory=list)
    story_phases: Dict[str, Any] = Field(default_factory=dict)
    chapter_outlines: List[Dict[str, Any]] = Field(default_factory=list)
    narrative_threads: List[Dict[str, Any]] = Field(default_factory=list)
    campaign_progression: str = ""

class CampaignData(BaseModel):
    """Data for a complete campaign."""
    title: str = Field(..., description="Campaign title")
    description: str = Field(..., description="Campaign description")
    main_storyline: str = Field(default="")
    major_plot_points: List[str] = Field(default_factory=list)
    antagonists: List[Dict[str, Any]] = Field(default_factory=list)
    themes: List[str] = Field(default_factory=list)
    plot_hooks: List[str] = Field(default_factory=list)
    moral_dilemmas: List[str] = Field(default_factory=list)
    subplots: List[str] = Field(default_factory=list)
    world_stakes: str = Field(default="")
    gm_notes: str = Field(default="")
    
    # Campaign settings
    status: str = Field(default="draft")
    session_count: int = Field(default=10)
    complexity: str = Field(default="medium")
    genre: str = Field(default="fantasy")
    estimated_duration: str = Field(default="")

class CampaignCreationResponse(BaseModel):
    """Standard response for campaign creation requests."""
    success: bool = Field(..., description="Whether creation was successful")
    creation_type: str = Field(..., description="Type of content created")
    
    # Response data (one of these will be populated based on creation_type)
    campaign: Optional[CampaignData] = None
    skeleton: Optional[CampaignSkeletonData] = None
    chapter: Optional[CampaignChapterData] = None
    characters: Optional[CampaignCharacterData] = None
    experiment: Optional[Dict[str, Any]] = None
    theme: Optional[Dict[str, Any]] = None
    
    # Metadata and performance info
    performance: CampaignMetadata = Field(..., description="Generation performance data")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings")
    error: Optional[str] = None

class CampaignRefinementResponse(BaseModel):
    """Response for campaign refinement requests."""
    success: bool = Field(..., description="Whether refinement was successful")
    evolution_type: str = Field(..., description="Type of evolution performed")
    
    # Refined content
    campaign: Optional[CampaignData] = None
    skeleton: Optional[CampaignSkeletonData] = None
    chapter: Optional[CampaignChapterData] = None
    
    # Refinement tracking
    cycles_completed: int = Field(default=1)
    refinement_log: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    performance: CampaignMetadata = Field(..., description="Refinement performance data")
    warnings: List[str] = Field(default_factory=list)
    error: Optional[str] = None

# ============================================================================
# VALIDATION HELPERS
# ============================================================================

class CampaignRequestValidator:
    """Validator for campaign creation requests."""
    
    @staticmethod
    def validate_campaign_request(request: BaseCampaignRequest) -> List[str]:
        """Validate a campaign creation request and return any errors."""
        errors = []
        
        # Validate concept word count
        word_count = len(request.concept.split())
        if not (50 <= word_count <= 500):
            errors.append(f"Concept must be 50-500 words, got {word_count}")
        
        return errors
    
    @staticmethod
    def validate_character_context(context: Dict[str, Any]) -> List[str]:
        """Validate campaign context for character integration."""
        errors = []
        required_fields = ['genre', 'party_level', 'party_size']
        
        for field in required_fields:
            if field not in context:
                errors.append(f"Missing required context field: {field}")
        
        if 'party_level' in context:
            if not (1 <= context['party_level'] <= 20):
                errors.append("Party level must be between 1 and 20")
        
        if 'party_size' in context:
            if not (2 <= context['party_size'] <= 8):
                errors.append("Party size must be between 2 and 8")
        
        return errors

# ============================================================================
# REQUEST FACTORY
# ============================================================================

class CampaignRequestFactory:
    """Factory for creating campaign request objects from API data."""
    
    REQUEST_TYPE_MAP = {
        CampaignCreationType.CAMPAIGN_FROM_SCRATCH: CampaignFromScratchRequest,
        CampaignCreationType.CAMPAIGN_SKELETON: CampaignSkeletonRequest,
        CampaignCreationType.CHAPTER_CONTENT: ChapterContentRequest,
        CampaignCreationType.ITERATIVE_REFINEMENT: CampaignRefinementRequest,
        CampaignCreationType.PSYCHOLOGICAL_EXPERIMENT: PsychologicalExperimentRequest,
        CampaignCreationType.SETTING_THEME: SettingThemeRequest,
        CampaignCreationType.NPC_FOR_CAMPAIGN: CharacterForCampaignRequest,
        CampaignCreationType.MONSTER_FOR_CAMPAIGN: CharacterForCampaignRequest,
        CampaignCreationType.EQUIPMENT_FOR_CAMPAIGN: CharacterForCampaignRequest,
    }
    
    @classmethod
    def create_request(cls, creation_type: CampaignCreationType, 
                      data: Dict[str, Any]) -> BaseCampaignRequest:
        """Create the appropriate request object based on creation type."""
        request_class = cls.REQUEST_TYPE_MAP.get(creation_type)
        if not request_class:
            raise ValueError(f"Unsupported creation type: {creation_type}")
        
        # Ensure creation_type is set
        data['creation_type'] = creation_type
        
        return request_class(**data)
