"""API models for theme management endpoints."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ..theme import ThemeIntensity, ThemeTone, ThemeType, WorldEffectType


class ThemeBase(BaseModel):
    """Base model for theme data."""
    name: str
    description: str
    type: ThemeType
    tone: ThemeTone
    intensity: ThemeIntensity
    attributes: Dict = Field(default_factory=dict)
    validation_rules: Dict = Field(default_factory=dict)
    generation_prompts: Dict = Field(default_factory=dict)
    style_guide: Dict = Field(default_factory=dict)


class ThemeCreate(ThemeBase):
    """Data required to create a new theme."""
    pass


class ThemeUpdate(ThemeBase):
    """Data that can be updated on a theme."""
    pass


class ThemeResponse(ThemeBase):
    """Full theme data including system fields."""
    id: UUID
    created_at: datetime
    updated_at: datetime


class ThemeCombinationBase(BaseModel):
    """Base model for theme combination data."""
    primary_theme_id: UUID
    secondary_theme_id: UUID
    weight: float = Field(ge=0.0, le=1.0, default=1.0)


class ThemeCombinationCreate(ThemeCombinationBase):
    """Data required to create a new theme combination."""
    pass


class ThemeCombinationResponse(ThemeCombinationBase):
    """Full theme combination data including system fields."""
    created_at: datetime


class WorldEffectBase(BaseModel):
    """Base model for world effect data."""
    theme_id: UUID
    name: str
    description: str
    effect_type: WorldEffectType
    parameters: Dict = Field(default_factory=dict)
    conditions: Dict = Field(default_factory=dict)
    impact_scale: float = Field(ge=0.0, le=1.0)
    duration: int = Field(gt=0)  # In days


class WorldEffectCreate(WorldEffectBase):
    """Data required to create a new world effect."""
    pass


class WorldEffectUpdate(WorldEffectBase):
    """Data that can be updated on a world effect."""
    pass


class WorldEffectResponse(WorldEffectBase):
    """Full world effect data including system fields."""
    id: UUID
    created_at: datetime
    updated_at: datetime


class LocationBase(BaseModel):
    """Base model for location data."""
    campaign_id: UUID
    name: str
    description: str
    location_type: str
    attributes: Dict = Field(default_factory=dict)
    state: Dict = Field(default_factory=dict)


class LocationCreate(LocationBase):
    """Data required to create a new location."""
    pass


class LocationUpdate(LocationBase):
    """Data that can be updated on a location."""
    pass


class LocationResponse(LocationBase):
    """Full location data including system fields."""
    id: UUID
    created_at: datetime
    updated_at: datetime


class FactionBase(BaseModel):
    """Base model for faction data."""
    campaign_id: UUID
    name: str
    description: str
    faction_type: str
    attributes: Dict = Field(default_factory=dict)
    state: Dict = Field(default_factory=dict)
    relationships: Dict = Field(default_factory=dict)


class FactionCreate(FactionBase):
    """Data required to create a new faction."""
    pass


class FactionUpdate(FactionBase):
    """Data that can be updated on a faction."""
    pass


class FactionResponse(FactionBase):
    """Full faction data including system fields."""
    id: UUID
    created_at: datetime
    updated_at: datetime


class ThemeValidationRequest(BaseModel):
    """Request model for theme validation."""
    theme_id: UUID
    content: Dict
    context: Optional[Dict] = None


class ThemeValidationResponse(BaseModel):
    """Response model for theme validation results."""
    is_valid: bool
    score: float = Field(ge=0.0, le=1.0)
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class ThemeApplicationRequest(BaseModel):
    """Request model for applying a theme to content."""
    theme_id: UUID
    content: Dict
    parameters: Optional[Dict] = None


class ThemeApplicationResponse(BaseModel):
    """Response model for theme application results."""
    modified_content: Dict
    changes: List[str]
    theme_elements: List[str]
    confidence_score: float = Field(ge=0.0, le=1.0)
