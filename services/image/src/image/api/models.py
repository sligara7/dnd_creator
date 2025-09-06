"""API models for image generation endpoints."""
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from image.core.cdn_config import CdnRegion


# Common Models
class Point(BaseModel):
    """2D point coordinates."""

    x: int = Field(..., description="X coordinate")
    y: int = Field(..., description="Y coordinate")


class Size(BaseModel):
    """Image size dimensions."""

    width: int = Field(..., gt=0, description="Width in pixels")
    height: int = Field(..., gt=0, description="Height in pixels")


class Scale(BaseModel):
    """Map scale information."""

    unit: str = Field(..., description="Scale unit")
    value: int = Field(..., gt=0, description="Scale value")


# Map Generation Models
class GridConfig(BaseModel):
    """Grid configuration for tactical maps."""

    enabled: bool = Field(True, description="Whether grid is enabled")
    size: int = Field(32, gt=0, description="Grid cell size in pixels")
    color: str = Field("#000000", description="Grid line color")


class TerrainConfig(BaseModel):
    """Terrain configuration for maps."""

    type: str = Field(..., description="Terrain type")
    properties: Dict = Field(
        default_factory=dict,
        description="Additional terrain properties"
    )


class PointOfInterest(BaseModel):
    """Point of interest on a map."""

    type: str = Field(..., description="POI type")
    location: Point
    name: str = Field(..., description="POI name")
    icon: str = Field(..., description="Icon identifier")


class TacticalMapRequest(BaseModel):
    """Request model for tactical map generation."""

    size: Size
    grid: Optional[GridConfig] = None
    theme: Optional[str] = None
    features: List[str] = Field(default_factory=list)
    terrain: Optional[TerrainConfig] = None


class CampaignMapRequest(BaseModel):
    """Request model for campaign map generation."""

    size: Size
    scale: Scale
    theme: Optional[str] = None
    features: List[str] = Field(default_factory=list)
    points_of_interest: List[PointOfInterest] = Field(default_factory=list)


# Portrait Generation Models
class PortraitStyle(BaseModel):
    """Portrait style configuration."""

    pose: str = Field(..., description="Portrait pose")
    background: str = Field(..., description="Background style")
    lighting: str = Field(..., description="Lighting style")


class EquipmentConfig(BaseModel):
    """Equipment configuration for portraits."""

    visible: bool = Field(True, description="Show equipment")
    items: List[UUID] = Field(default_factory=list)


class PortraitRequest(BaseModel):
    """Request model for portrait generation."""

    character_id: UUID
    theme: Optional[str] = None
    style: PortraitStyle
    equipment: Optional[EquipmentConfig] = None


# Item Illustration Models
class ItemType(str, Enum):
    """Types of items that can be illustrated."""

    WEAPON = "weapon"
    ARMOR = "armor"
    OTHER = "other"


class ItemStyle(BaseModel):
    """Item illustration style."""

    angle: str = Field(..., description="Viewing angle")
    lighting: str = Field(..., description="Lighting style")
    detail_level: str = Field(..., description="Level of detail")


class ItemProperties(BaseModel):
    """Physical properties of an item."""

    material: str = Field(..., description="Material type")
    magical_effects: List[str] = Field(default_factory=list)
    wear_state: Optional[str] = None


class ItemRequest(BaseModel):
    """Request model for item illustration."""

    item_id: UUID
    type: ItemType
    theme: Optional[str] = None
    style: ItemStyle
    properties: ItemProperties


# Overlay Models
class OverlayType(str, Enum):
    """Types of tactical overlays."""

    POSITION = "position"
    RANGE = "range"
    EFFECT = "effect"


class OverlayElement(BaseModel):
    """Single element in an overlay."""

    id: UUID
    position: Point
    properties: Dict = Field(
        default_factory=dict,
        description="Element properties"
    )


class CampaignOverlayType(str, Enum):
    """Types of campaign overlays."""

    PARTY = "party"
    TERRITORY = "territory"
    ROUTE = "route"


class CampaignOverlayElement(BaseModel):
    """Campaign map overlay element."""

    id: UUID
    coordinates: List[Point]
    properties: Dict = Field(
        default_factory=dict,
        description="Element properties"
    )


class TacticalOverlayRequest(BaseModel):
    """Request model for tactical overlay."""

    type: OverlayType
    elements: List[OverlayElement]


class CampaignOverlayRequest(BaseModel):
    """Request model for campaign overlay."""

    type: CampaignOverlayType
    elements: List[CampaignOverlayElement]


# Theme Models
class ThemeStyle(BaseModel):
    """Theme style configuration."""

    color_scheme: str = Field(..., description="Color scheme name")
    lighting: str = Field(..., description="Lighting style")
    atmosphere: str = Field(..., description="Atmospheric style")


class ThemeApplication(BaseModel):
    """Request model for theme application."""

    theme: str = Field(..., description="Theme name")
    strength: float = Field(
        1.0,
        ge=0.0,
        le=1.0,
        description="Theme application strength"
    )
    elements: List[str] = Field(default_factory=list)
    style: ThemeStyle


class ThemeResponse(BaseModel):
    """Response model for available themes."""

    visual_themes: List[str]
    style_elements: Dict[str, List[str]]


# Common Response Models
class ImageResponse(BaseModel):
    """Common image operation response."""

    id: UUID
    type: str
    url: str
    size: Size
    theme: Optional[str] = None
    cdn_url: Optional[str] = None
    metadata: Dict = Field(default_factory=dict)


class BatchResponse(BaseModel):
    """Response for batch operations."""

    successful: List[UUID]
    failed: List[UUID]
    error_details: Optional[Dict[str, str]] = None


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: Dict[str, str]
    details: Optional[Dict] = None


# Integration Models
class CharacterGallery(BaseModel):
    """Response for character image gallery."""

    portraits: List[ImageResponse]
    equipment: List[ImageResponse]


class CampaignAssets(BaseModel):
    """Response for campaign assets."""

    maps: List[ImageResponse]
    overlays: List[Dict]
    themes: List[str]
