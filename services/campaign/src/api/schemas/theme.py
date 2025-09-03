"""API schemas for theme operations."""
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CoreTheme(str, Enum):
    """Core themes for campaigns."""
    PUZZLE_SOLVING = "puzzle_solving"
    MYSTERY = "mystery"
    TACTICAL_COMBAT = "tactical_combat"
    CHARACTER_INTERACTION = "character_interaction"
    POLITICAL_INTRIGUE = "political_intrigue"
    EXPLORATION = "exploration"
    HORROR_SURVIVAL = "horror_survival"
    PSYCHOLOGICAL_DRAMA = "psychological_drama"
    HEIST_INFILTRATION = "heist_infiltration"
    RESOURCE_MANAGEMENT = "resource_management"
    TIME_TRAVEL = "time_travel"
    MORAL_PHILOSOPHY = "moral_philosophy"
    EDUCATIONAL_HISTORICAL = "educational_historical"


class SettingTheme(str, Enum):
    """Setting themes for campaigns."""
    WESTERN = "western"
    STEAMPUNK = "steampunk"
    CYBERPUNK = "cyberpunk"
    HORROR = "horror"
    SPACE_FANTASY = "space_fantasy"
    POST_APOCALYPTIC = "post_apocalyptic"
    NOIR_DETECTIVE = "noir_detective"
    HIGH_FANTASY = "high_fantasy"
    LOW_FANTASY = "low_fantasy"
    HISTORICAL = "historical"


class ThemeElement(BaseModel):
    """Theme element with rules."""
    name: str
    description: str
    rules: List[str]
    examples: List[str]
    incompatible_with: List[str] = Field(default_factory=list)


class ThemePreset(BaseModel):
    """Preset theme configuration."""
    id: UUID
    name: str
    description: str
    core_theme: CoreTheme
    setting_theme: Optional[SettingTheme] = None
    elements: List[ThemeElement]
    style_guide: Dict[str, List[str]]
    naming_conventions: Dict[str, List[str]]


class ThemeCatalog(BaseModel):
    """Available themes and elements."""
    core_themes: List[str]
    setting_themes: List[str]
    elements: Dict[str, ThemeElement]
    presets: List[ThemePreset]


class ThemeStrength(str, Enum):
    """Theme application strength levels."""
    SUBTLE = "subtle"      # Light touch
    MODERATE = "moderate"  # Clear but not overwhelming
    STRONG = "strong"      # Heavily themed
    DOMINANT = "dominant"  # Theme takes precedence


class ThemeRequest(BaseModel):
    """Request model for theme application."""
    theme: str = Field(..., description="Theme to apply")
    strength: float = Field(
        0.8,
        ge=0.0,
        le=1.0,
        description="Theme application strength"
    )
    elements: List[str] = Field(default_factory=list)
    exclusions: List[str] = Field(default_factory=list)


class ContentNaming(BaseModel):
    """Naming patterns for themed content."""
    locations: List[str]
    npcs: List[str]
    items: List[str]
    events: List[str]


class ThemeStyleGuide(BaseModel):
    """Theme style guide for content."""
    tone: List[str]
    descriptors: List[str]
    colors: List[str]
    architecture: List[str]
    clothing: List[str]
    technology: List[str]
    magic: List[str]
    naming: ContentNaming


class ThemeRules(BaseModel):
    """Theme rules and constraints."""
    required_elements: List[str]
    forbidden_elements: List[str]
    balancing_rules: Dict[str, str]
    adaptation_rules: Dict[str, str]


class ThemeProfile(BaseModel):
    """Complete theme profile."""
    name: str
    description: str
    core_theme: CoreTheme
    setting_theme: Optional[SettingTheme]
    style_guide: ThemeStyleGuide
    rules: ThemeRules
    elements: List[ThemeElement]


class ApplyThemeRequest(BaseModel):
    """Request model for theme application."""
    theme: str
    strength: float = Field(0.8, ge=0.0, le=1.0)
    elements: List[str] = Field(default_factory=list)
    exclusions: List[str] = Field(default_factory=list)


class ApplyThemeResponse(BaseModel):
    """Response model for theme application."""
    theme_id: UUID
    theme_profile: ThemeProfile
    generation_notes: Optional[str] = None


class ThemeUpdateEvent(BaseModel):
    """Event for theme updates."""
    campaign_id: UUID
    old_theme: str
    new_theme: str
    changes: List[Dict[str, str]]
    reason: str
