from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field


class ImageType(str, Enum):
    MAP = "map"
    CHARACTER = "character"
    ITEM = "item"


class ImageSubtype(str, Enum):
    TACTICAL = "tactical"
    CAMPAIGN = "campaign"
    PORTRAIT = "portrait"
    WEAPON = "weapon"
    ARMOR = "armor"
    MISC = "misc"


class OverlayType(str, Enum):
    POSITION = "position"
    RANGE = "range"
    EFFECT = "effect"
    PARTY = "party"
    TERRITORY = "territory"
    ROUTE = "route"


class ImageSize(BaseModel):
    """Image dimensions"""
    width: int
    height: int


class GridSettings(BaseModel):
    """Grid configuration for maps"""
    enabled: bool
    size: int
    color: str = "#000000"


class Point(BaseModel):
    """2D coordinate"""
    x: int
    y: int


class OverlayProperties(BaseModel):
    """Visual properties for overlays"""
    color: str = "#FF0000"
    opacity: float = 0.5
    radius: Optional[int] = None
    style: Optional[str] = None
    label: Optional[str] = None


class OverlayElement(BaseModel):
    """Individual overlay element"""
    id: UUID
    position: Optional[Point] = None
    coordinates: Optional[List[Point]] = None
    properties: OverlayProperties


class ImageContent(BaseModel):
    """Image content details"""
    url: str
    format: str
    size: ImageSize


class ImageMetadata(BaseModel):
    """Image metadata"""
    theme: Optional[str] = None
    source_id: Optional[UUID] = None
    service: str
    generation_params: Dict
    created_at: datetime
    updated_at: datetime


class MapFeatures(BaseModel):
    """Map feature configuration"""
    grid: GridSettings
    terrain: Dict
    features: List[str]


class PortraitStyle(BaseModel):
    """Portrait style configuration"""
    pose: str
    background: str
    lighting: str


class ItemStyle(BaseModel):
    """Item visualization style"""
    angle: str
    lighting: str
    detail_level: str


class ItemProperties(BaseModel):
    """Item visual properties"""
    material: str
    magical_effects: List[str] = Field(default_factory=list)
    wear_state: str = "new"


class ThemeStyle(BaseModel):
    """Theme style configuration"""
    color_scheme: str
    lighting: str
    atmosphere: str


class Image(BaseModel):
    """Base image model"""
    id: UUID
    type: ImageType
    subtype: ImageSubtype
    content: ImageContent
    metadata: ImageMetadata
    overlays: List[Dict] = Field(default_factory=list)
    references: List[Dict] = Field(default_factory=list)


class Overlay(BaseModel):
    """Overlay model"""
    id: UUID
    image_id: UUID
    type: OverlayType
    elements: List[OverlayElement]
    created_at: datetime
    updated_at: datetime


class TacticalMapRequest(BaseModel):
    """Request model for tactical map generation"""
    size: ImageSize
    grid: GridSettings
    theme: str
    features: List[str]
    terrain: Dict


class CampaignMapRequest(BaseModel):
    """Request model for campaign map generation"""
    size: ImageSize
    scale: Dict[str, Union[str, int]]
    theme: str
    features: List[str]
    points_of_interest: List[Dict]


class PortraitRequest(BaseModel):
    """Request model for portrait generation"""
    character_id: UUID
    theme: str
    style: PortraitStyle
    equipment: Dict[str, Union[bool, List[UUID]]]


class ItemImageRequest(BaseModel):
    """Request model for item image generation"""
    item_id: UUID
    type: str
    theme: str
    style: ItemStyle
    properties: ItemProperties


class ThemeRequest(BaseModel):
    """Request model for theme application"""
    theme: str
    strength: float = 1.0
    elements: List[str] = Field(default_factory=list)
    style: Optional[ThemeStyle] = None


class OverlayRequest(BaseModel):
    """Request model for overlay application"""
    type: OverlayType
    elements: List[OverlayElement]
