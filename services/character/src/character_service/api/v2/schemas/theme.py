"""Theme API schemas."""
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from character_service.domain.theme import (
    Theme as ThemeDomain,
    ThemeState as ThemeStateDomain,
    ThemeTransition as ThemeTransitionDomain,
    ThemeTransitionType,
    ThemeCategory,
    ThemeValidationError,
    ThemeValidationResult,
)


class ThemeTransitionRequest(BaseModel):
    """Request model for theme transitions."""
    from_theme_id: Optional[UUID] = None
    to_theme_id: UUID
    transition_type: ThemeTransitionType = Field(default=ThemeTransitionType.STORY)
    triggered_by: str = Field(description="User ID or system identifier that triggered the transition")
    campaign_event_id: Optional[UUID] = None
    context: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional context for the transition",
    )


class ThemeListResponse(BaseModel):
    """Response model for theme list."""
    themes: List[ThemeDomain]
    total: int
    page: int
    page_size: int


class ThemeListQuery(BaseModel):
    """Query parameters for theme list."""
    category: Optional[ThemeCategory] = None
    level_min: Optional[int] = Field(default=None, ge=1, le=20)
    level_max: Optional[int] = Field(default=None, ge=1, le=20)
    class_name: Optional[str] = None
    race: Optional[str] = None
    search: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class ThemeHistoryResponse(BaseModel):
    """Response model for theme history."""
    transitions: List[ThemeTransitionDomain]
    current_theme: Optional[ThemeDomain] = None
    current_state: Optional[ThemeStateDomain] = None


class ThemeValidationRequest(BaseModel):
    """Request model for theme validation."""
    theme_id: UUID
    character_id: UUID
    transition_type: Optional[ThemeTransitionType] = None
    campaign_event_id: Optional[UUID] = None
    context: Optional[Dict[str, str]] = None


class ThemeValidationResponse(BaseModel):
    """Response model for theme validation."""
    is_valid: bool
    errors: List[ThemeValidationError] = Field(default_factory=list)
    warnings: List[ThemeValidationError] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class ThemeSuggestionRequest(BaseModel):
    """Request model for theme suggestions."""
    character_id: UUID
    event_context: Optional[Dict[str, str]] = Field(
        default=None,
        description="Campaign event context for suggestions",
    )
    preferences: Optional[Dict[str, str]] = Field(
        default=None,
        description="Theme preferences",
    )


class ThemeSuggestionResponse(BaseModel):
    """Response model for theme suggestions."""
    suggestions: List[ThemeDomain]
    reason: Optional[str] = None
