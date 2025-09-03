"""API schemas for campaign operations."""
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CampaignComplexity(str, Enum):
    """Campaign complexity levels."""
    SIMPLE = "simple"       # Linear story, few branches
    MODERATE = "moderate"   # Multiple branches, moderate complexity
    COMPLEX = "complex"     # Many branches, high complexity
    EPIC = "epic"          # Multiple interweaving plots


class CampaignMoralTone(str, Enum):
    """Campaign moral tone settings."""
    BLACK_AND_WHITE = "black_and_white"  # Clear good vs evil
    GRAY = "gray"                        # Morally ambiguous
    MIXED = "mixed"                      # Mix of clear and ambiguous
    SHIFTING = "shifting"                # Morality changes based on perspective


class CampaignViolenceLevel(str, Enum):
    """Campaign violence level settings."""
    LOW = "low"           # Minimal violence, focus on roleplay
    MODERATE = "moderate" # Standard D&D combat level
    HIGH = "high"         # Dark themes, graphic descriptions
    EXTREME = "extreme"   # Grimdark, horror elements


class CampaignTheme(BaseModel):
    """Campaign theme configuration."""
    primary: str = Field(..., description="Primary theme of the campaign")
    secondary: Optional[str] = Field(None, description="Secondary theme")
    elements: List[str] = Field(default_factory=list, description="Theme elements to include")
    exclusions: List[str] = Field(default_factory=list, description="Elements to exclude")


class CampaignLength(BaseModel):
    """Campaign length configuration."""
    min_sessions: int = Field(ge=1, description="Minimum number of sessions")
    max_sessions: int = Field(ge=1, description="Maximum number of sessions")

    def __init__(self, **data):
        super().__init__(**data)
        if self.max_sessions < self.min_sessions:
            self.max_sessions = self.min_sessions


class CampaignPreferences(BaseModel):
    """Campaign creation preferences."""
    complexity: CampaignComplexity = Field(
        CampaignComplexity.MODERATE,
        description="Campaign complexity level"
    )
    moral_tone: CampaignMoralTone = Field(
        CampaignMoralTone.MIXED,
        description="Campaign moral tone"
    )
    violence_level: CampaignViolenceLevel = Field(
        CampaignViolenceLevel.MODERATE,
        description="Campaign violence level"
    )


class CreateCampaignRequest(BaseModel):
    """Request model for campaign creation."""
    name: str = Field(..., min_length=1, max_length=100)
    concept: str = Field(..., min_length=50, max_length=5000)
    theme: CampaignTheme = Field(..., description="Campaign theme settings")
    length: CampaignLength = Field(..., description="Campaign length settings")
    preferences: CampaignPreferences = Field(
        default_factory=CampaignPreferences,
        description="Campaign preferences"
    )
    generation_flags: Dict[str, bool] = Field(
        default_factory=lambda: {"generate_first_chapter": True},
        description="Optional generation flags"
    )


class CampaignRefinement(BaseModel):
    """Campaign refinement request."""
    aspect: str = Field(..., description="Aspect to refine")
    change: str = Field(..., description="Desired change")
    reason: str = Field(..., description="Reason for change")


class RefineCampaignRequest(BaseModel):
    """Request model for campaign refinement."""
    refinements: List[CampaignRefinement] = Field(..., min_items=1)
    preserve: List[str] = Field(default_factory=list)


class NPCSummary(BaseModel):
    """Summary of an NPC."""
    id: UUID
    name: str
    role: str
    description: str
    chapters: List[str] = Field(default_factory=list)


class LocationSummary(BaseModel):
    """Summary of a location."""
    id: UUID
    name: str
    type: str
    description: str
    chapters: List[str] = Field(default_factory=list)


class ChapterSummary(BaseModel):
    """Summary of a chapter."""
    id: UUID
    title: str
    summary: str
    status: str
    dependencies: List[UUID] = Field(default_factory=list)


class PlotBranch(BaseModel):
    """Plot branch information."""
    id: UUID
    trigger_condition: str
    choices: List[Dict[str, str]]
    consequences: List[str]
    explored: bool = False


class Campaign(BaseModel):
    """Complete campaign model."""
    name: str
    concept: str
    theme: CampaignTheme
    chapters: List[ChapterSummary] = Field(default_factory=list)
    npcs: List[NPCSummary] = Field(default_factory=list)
    locations: List[LocationSummary] = Field(default_factory=list)
    plot_branches: List[PlotBranch] = Field(default_factory=list)


class CreateCampaignResponse(BaseModel):
    """Response model for campaign creation."""
    id: UUID
    campaign: Campaign
    generation_notes: Optional[str] = None
