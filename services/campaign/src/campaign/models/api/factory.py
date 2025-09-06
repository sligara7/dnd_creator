"""API models for campaign factory and generation."""

from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CampaignType(str, Enum):
    """Campaign types."""
    TRADITIONAL = "traditional"
    ANTITHETICON = "antitheticon"


class CampaignComplexity(str, Enum):
    """Campaign complexity levels."""
    SIMPLE = "simple"  # Linear storyline, few subplots
    MODERATE = "moderate"  # Main plot with some subplots
    COMPLEX = "complex"  # Multiple interweaving plots
    INTRICATE = "intricate"  # Complex narrative with many subplots


class CampaignLength(str, Enum):
    """Campaign length types."""
    ONE_SHOT = "one_shot"  # Single session (1-2 chapters)
    SHORT = "short"  # 2-5 sessions (3-5 chapters)
    MEDIUM = "medium"  # 6-12 sessions (6-10 chapters)
    LONG = "long"  # 13-24 sessions (11-20 chapters)
    EPIC = "epic"  # 25+ sessions (21+ chapters)


class LevelRange(BaseModel):
    """Character level range for a campaign."""
    min: int = Field(ge=1, le=20)
    max: int = Field(ge=1, le=20)

    def __init__(self, **data):
        super().__init__(**data)
        if self.min > self.max:
            self.min, self.max = self.max, self.min


class PlayerCount(BaseModel):
    """Player count range for a campaign."""
    min: int = Field(ge=1, le=8)
    max: int = Field(ge=1, le=8)

    def __init__(self, **data):
        super().__init__(**data)
        if self.min > self.max:
            self.min, self.max = self.max, self.min


class CampaignGenerationRequest(BaseModel):
    """Request model for campaign generation."""
    title: Optional[str] = None
    description: Optional[str] = None
    campaign_type: CampaignType
    complexity: CampaignComplexity = CampaignComplexity.MODERATE
    length: CampaignLength = CampaignLength.MEDIUM
    level_range: LevelRange = Field(default_factory=lambda: LevelRange(min=1, max=20))
    player_count: PlayerCount = Field(default_factory=lambda: PlayerCount(min=3, max=6))
    theme_ids: Optional[List[UUID]] = None  # Optional themes to apply
    parameters: Optional[Dict] = None  # Additional generation parameters


class CampaignGenerationResponse(BaseModel):
    """Response model for campaign generation."""
    campaign_id: UUID
    status: str  # 'success' or 'error'
    message: str
    details: Optional[Dict] = None
    generated_content: Optional[Dict] = None


class CampaignRefinementRequest(BaseModel):
    """Request model for campaign refinement."""
    campaign_id: UUID
    refinement_type: str  # 'theme', 'content', 'structure'
    adjustments: Dict  # Specific adjustments to make
    preserve: Optional[List[str]] = None  # Elements to preserve
    parameters: Optional[Dict] = None  # Additional refinement parameters


class CampaignRefinementResponse(BaseModel):
    """Response model for campaign refinement."""
    campaign_id: UUID
    status: str  # 'success' or 'error'
    message: str
    changes: List[Dict]  # List of changes made
    preserved: List[str]  # List of preserved elements


class NPCGenerationRequest(BaseModel):
    """Request model for NPC generation."""
    campaign_id: UUID
    npc_type: str  # 'major', 'minor', 'background'
    role: Optional[str] = None  # NPC's role in the campaign
    relationships: Optional[List[Dict]] = None  # Relationships to other characters/NPCs
    theme_id: Optional[UUID] = None  # Optional theme to apply
    parameters: Optional[Dict] = None  # Additional generation parameters


class NPCGenerationResponse(BaseModel):
    """Response model for NPC generation."""
    npc_id: UUID
    status: str
    message: str
    npc_data: Dict  # Generated NPC data
    relationships: List[Dict]  # Generated relationships
    theme_elements: Optional[List[str]] = None  # Theme elements incorporated


class LocationGenerationRequest(BaseModel):
    """Request model for location generation."""
    campaign_id: UUID
    location_type: str  # 'settlement', 'dungeon', 'wilderness', etc.
    importance: str = "minor"  # 'major', 'minor', 'background'
    theme_id: Optional[UUID] = None  # Optional theme to apply
    connections: Optional[List[Dict]] = None  # Connections to other locations
    parameters: Optional[Dict] = None  # Additional generation parameters


class LocationGenerationResponse(BaseModel):
    """Response model for location generation."""
    location_id: UUID
    status: str
    message: str
    location_data: Dict  # Generated location data
    connections: List[Dict]  # Generated connections
    theme_elements: Optional[List[str]] = None  # Theme elements incorporated


class MapGenerationRequest(BaseModel):
    """Request model for map generation."""
    campaign_id: UUID
    location_id: Optional[UUID] = None  # Optional location to map
    map_type: str  # 'world', 'region', 'settlement', 'dungeon', etc.
    scale: str  # 'overview', 'detailed'
    theme_id: Optional[UUID] = None  # Optional theme to apply
    parameters: Optional[Dict] = None  # Additional generation parameters


class MapGenerationResponse(BaseModel):
    """Response model for map generation."""
    map_id: UUID
    status: str
    message: str
    map_data: Dict  # Generated map data
    image_url: str  # URL to generated map image
    features: List[Dict]  # Map features and points of interest
    theme_elements: Optional[List[str]] = None  # Theme elements incorporated
