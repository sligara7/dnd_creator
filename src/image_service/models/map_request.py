"""
Map generation request models.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from uuid import UUID

class GridPoint(BaseModel):
    """Represents a point on the grid."""
    x: int = Field(..., description="X coordinate")
    y: int = Field(..., description="Y coordinate")

class GridSize(BaseModel):
    """Represents the size of a grid."""
    width: int = Field(..., description="Grid width in cells")
    height: int = Field(..., description="Grid height in cells")
    scale: Optional[float] = Field(1.0, description="Grid scale (1 cell = scale feet)")

class TerrainFeature(BaseModel):
    """Represents a terrain feature."""
    type: str = Field(..., description="Type of terrain feature (e.g., forest, mountain, river)")
    position: GridPoint = Field(..., description="Position of the feature")
    size: Optional[GridSize] = None
    properties: Optional[Dict[str, str]] = Field(default_factory=dict)

class SpellEffect(BaseModel):
    """Represents a spell effect overlay."""
    type: str = Field(..., description="Type of spell effect (e.g., circle, cone, line)")
    origin: GridPoint = Field(..., description="Origin point of the effect")
    size: int = Field(..., description="Size/range of the effect in feet")
    properties: Optional[Dict[str, str]] = Field(default_factory=dict)

class CharacterPosition(BaseModel):
    """Represents a character's position on the map."""
    character_id: UUID = Field(..., description="ID of the character")
    position: GridPoint = Field(..., description="Position on the grid")
    size: str = Field("medium", description="Size category of the character")
    status_effects: Optional[List[str]] = Field(default_factory=list)
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

class MapRequest(BaseModel):
    """Base class for map generation requests."""
    campaign_id: Optional[UUID] = None
    theme: str = Field(..., description="Visual theme for the map")
    grid_size: GridSize = Field(..., description="Size of the map grid")
    terrain_features: List[TerrainFeature] = Field(default_factory=list)
    characters: List[CharacterPosition] = Field(default_factory=list)
    spell_effects: List[SpellEffect] = Field(default_factory=list)

class TacticalMapRequest(MapRequest):
    """Request for tactical battle map generation."""
    encounter_id: Optional[UUID] = None
    battle_theme: Optional[str] = None
    lighting_conditions: str = Field("bright", description="Lighting conditions")
    weather_effects: Optional[List[str]] = Field(default_factory=list)

class CampaignMapRequest(MapRequest):
    """Request for campaign/world map generation."""
    region_name: str = Field(..., description="Name of the region")
    map_style: str = Field("fantasy", description="Style of the map")
    points_of_interest: List[Dict[str, str]] = Field(default_factory=list)
    region_type: str = Field(..., description="Type of region (e.g., kingdom, wilderness)")
    show_scale: bool = Field(True, description="Whether to show map scale")
