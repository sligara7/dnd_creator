from enum import Enum
from uuid import UUID
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from llm_service.schemas.common import Theme, ContentMetadata


class ThemeCategory(str, Enum):
    """High-level theme categories."""
    FANTASY = "fantasy"
    HORROR = "horror"
    MYSTERY = "mystery"
    ADVENTURE = "adventure"
    DRAMA = "drama"
    COMEDY = "comedy"
    HEROIC = "heroic"
    DARK = "dark"
    EPIC = "epic"


class ThemeElement(str, Enum):
    """Specific theme elements that can be analyzed."""
    TONE = "tone"
    MOOD = "mood"
    SETTING = "setting"
    CONFLICT = "conflict"
    SYMBOLISM = "symbolism"
    CHARACTER_FOCUS = "character_focus"
    STORY_STRUCTURE = "story_structure"
    WORLD_BUILDING = "world_building"


class TextThemeRequest(BaseModel):
    """Request for text theme application."""
    content: str = Field(description="Text content to process")
    theme: Theme = Field(description="Theme to apply")
    parameters: dict = Field(
        default_factory=lambda: {
            "strength": 0.8,
            "preserve_key_elements": True,
        }
    )


class TextThemeResponse(BaseModel):
    """Response from text theme application."""
    content: str = Field(description="Theme-modified text content")
    theme_id: UUID = Field(description="ID of the theme used")
    original_content: str = Field(description="Original text content")
    similarity_score: float = Field(description="How similar the modified content is")


class VisualThemeRequest(BaseModel):
    """Request for visual theme application."""
    image: str = Field(description="Base64 encoded image")
    theme: Theme = Field(description="Theme to apply")
    parameters: dict = Field(
        default_factory=lambda: {
            "style_strength": 0.8,
            "color_strength": 0.7,
            "lighting_strength": 0.6,
            "preserve_composition": True,
        }
    )


class VisualThemeResponse(BaseModel):
    """Response from visual theme application."""
    image: str = Field(description="Base64 encoded themed image")
    theme_id: UUID = Field(description="ID of the theme used")
    original_image: str = Field(description="Original image")
    parameters_used: dict = Field(description="Final parameters used for theme application")


class ThemePreset(BaseModel):
    """Theme preset for reuse."""
    id: UUID = Field(description="Unique identifier for the theme")
    name: str = Field(description="Name of the theme preset")
    description: str = Field(description="Description of the theme")
    theme: Theme = Field(description="Theme configuration")
    text_parameters: dict = Field(description="Default text parameters")
    visual_parameters: dict = Field(description="Default visual parameters")
    created_by: str = Field(description="Creator of the theme preset")
    is_public: bool = Field(description="Whether the theme is publicly available")


class ThemePresetList(BaseModel):
    """List of theme presets."""
    items: list[ThemePreset]
    total: int = Field(description="Total number of presets")
    page: int = Field(description="Current page number")
    size: int = Field(description="Page size")


class ThemeStatistics(BaseModel):
    """Usage statistics for a theme."""
    theme_id: UUID = Field(description="Theme identifier")
    text_usage_count: int = Field(description="Number of text applications")
    visual_usage_count: int = Field(description="Number of visual applications")
    average_text_score: float = Field(description="Average text similarity score")
    average_visual_score: float = Field(description="Average visual similarity score")
    popular_genres: list[str] = Field(description="Most common genres used with")


class ThemeAnalysisRequest(BaseModel):
    """Request for theme analysis."""
    content: str = Field(description="Content to analyze")
    current_theme: Optional[Dict[str, str]] = Field(
        None,
        description="Current theme parameters if analyzing a theme transition"
    )
    target_theme: Optional[Dict[str, str]] = Field(
        None,
        description="Target theme parameters if analyzing compatibility"
    )
    elements: List[ThemeElement] = Field(
        default_factory=lambda: list(ThemeElement),
        description="Theme elements to analyze"
    )
    category_filter: Optional[List[ThemeCategory]] = Field(
        None,
        description="Filter analysis to specific theme categories"
    )


class ThemeElementAnalysis(BaseModel):
    """Analysis of a single theme element."""
    element: ThemeElement
    score: float = Field(ge=0.0, le=1.0, description="Presence strength of this element")
    description: str = Field(description="Detailed analysis of the element")
    suggestions: List[str] = Field(description="Suggestions for enhancement/improvement")


class ThemeCompatibility(BaseModel):
    """Theme compatibility analysis result."""
    score: float = Field(ge=0.0, le=1.0, description="Overall compatibility score")
    conflicts: List[str] = Field(description="Potential theme conflicts")
    enhancements: List[str] = Field(description="Suggested enhancements")
    transition_steps: Optional[List[str]] = Field(
        None,
        description="Steps needed for theme transition"
    )


class ThemeAnalysisResponse(BaseModel):
    """Response containing theme analysis results."""
    content_id: UUID = Field(description="Unique identifier for this analysis")
    metadata: ContentMetadata = Field(description="Analysis metadata")
    
    # Primary theme categorization
    primary_category: ThemeCategory
    secondary_categories: List[ThemeCategory]
    category_confidence: float = Field(ge=0.0, le=1.0)
    
    # Detailed element analysis
    elements: List[ThemeElementAnalysis]
    
    # Theme compatibility if requested
    compatibility: Optional[ThemeCompatibility] = None
    
    # Generated theme parameters
    suggested_parameters: Dict[str, str] = Field(
        description="Suggested theme parameters based on analysis"
    )
