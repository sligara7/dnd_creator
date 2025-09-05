"""Theme-related domain models."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ThemeCategory(str, Enum):
    """Theme categories."""
    BACKGROUND = "background"
    ARCHETYPE = "archetype"
    PRESTIGE = "prestige"
    EPIC = "epic"
    ANTITHETICON = "antitheticon"
    CUSTOM = "custom"


class ThemeTransitionType(str, Enum):
    """Theme transition types."""
    INITIAL = "initial"
    PROGRESSION = "progression"
    STORY = "story"
    MILESTONE = "milestone"
    ANTITHETICON = "antitheticon"
    CUSTOM = "custom"


class ThemeTriggerType(str, Enum):
    """Theme progression trigger types."""
    LEVEL = "level"
    STORY = "story"
    ACHIEVEMENT = "achievement"
    MILESTONE = "milestone"
    CONDITION = "condition"
    CUSTOM = "custom"


class ThemeFeature(BaseModel):
    """Domain model for theme features."""
    id: Optional[UUID] = None
    theme_id: UUID
    name: str
    description: str
    level_granted: int = Field(default=1, ge=1, le=20)
    mechanics: Dict[str, Any]
    is_optional: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ThemeEquipment(BaseModel):
    """Domain model for theme equipment changes."""
    id: Optional[UUID] = None
    theme_id: UUID
    item_id: UUID
    operation: str = Field(regex="^(add|remove|replace)$")
    quantity: int = Field(default=1, ge=1)
    requirements: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProgressionRule(BaseModel):
    """Domain model for theme progression rules."""
    id: Optional[UUID] = None
    theme_id: UUID
    name: str
    description: str
    trigger_type: ThemeTriggerType
    trigger_conditions: Dict[str, Any]
    effects: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Theme(BaseModel):
    """Domain model for character themes."""
    id: Optional[UUID] = None
    name: str
    description: str
    category: ThemeCategory
    is_active: bool = True
    base_modifiers: Dict[str, Any]
    ability_adjustments: Dict[str, int]
    level_requirement: int = Field(default=1, ge=1, le=20)
    class_restrictions: List[str] = Field(default_factory=list)
    race_restrictions: List[str] = Field(default_factory=list)
    version: int = 1
    parent_theme_id: Optional[UUID] = None
    features: List[ThemeFeature] = Field(default_factory=list)
    equipment_changes: List[ThemeEquipment] = Field(default_factory=list)
    progression_rules: List[ProgressionRule] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        validate_assignment = True


class ThemeState(BaseModel):
    """Domain model for character theme state."""
    id: Optional[UUID] = None
    character_id: UUID
    theme_id: UUID
    is_active: bool = True
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    deactivated_at: Optional[datetime] = None
    applied_features: List[str] = Field(default_factory=list)
    applied_modifiers: Dict[str, Any] = Field(default_factory=dict)
    progress_state: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ThemeTransition(BaseModel):
    """Domain model for theme transitions."""
    id: Optional[UUID] = None
    character_id: UUID
    from_theme_id: Optional[UUID] = None
    to_theme_id: UUID
    transition_type: ThemeTransitionType
    triggered_by: str  # user_id, system, event_id, etc.
    campaign_event_id: Optional[UUID] = None
    changes: Dict[str, Any] = Field(default_factory=dict)
    rolled_back: bool = False
    rollback_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class ThemeValidationError(BaseModel):
    """Domain model for theme validation errors."""
    error_type: str
    message: str
    context: Dict[str, Any] = Field(default_factory=dict)
    fix_suggestion: Optional[str] = None


class ThemeValidationResult(BaseModel):
    """Domain model for theme validation results."""
    is_valid: bool
    errors: List[ThemeValidationError] = Field(default_factory=list)
    warnings: List[ThemeValidationError] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class ThemeTransitionResult(BaseModel):
    """Domain model for theme transition results."""
    success: bool
    transition_id: Optional[UUID] = None
    old_state: Optional[ThemeState] = None
    new_state: Optional[ThemeState] = None
    applied_changes: Dict[str, Any] = Field(default_factory=dict)
    validation_result: ThemeValidationResult
    error_details: Optional[Dict[str, Any]] = None
