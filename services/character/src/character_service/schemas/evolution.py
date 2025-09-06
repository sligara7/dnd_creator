"""Evolution schemas."""
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, UUID4

from character_service.domain.evolution import (
    EventType,
    MilestoneType,
    AchievementCategory,
    Difficulty,
)


class BaseEvent(BaseModel):
    """Base event schema."""

    event_type: EventType
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    impact: Optional[Dict] = None
    campaign_event_id: Optional[UUID4] = None
    metadata: Optional[Dict] = None


class CharacterEventCreate(BaseEvent):
    """Create character event schema."""

    pass


class CharacterEventResponse(BaseEvent):
    """Response character event schema."""

    id: UUID4
    character_id: UUID4
    is_processed: bool
    processed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        """Pydantic config."""

        orm_mode = True


class BaseMilestone(BaseModel):
    """Base milestone schema."""

    milestone_type: MilestoneType
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    requirements: Optional[Dict] = None
    rewards: Optional[Dict] = None
    campaign_milestone_id: Optional[UUID4] = None
    metadata: Optional[Dict] = None


class MilestoneCreate(BaseMilestone):
    """Create milestone schema."""

    pass


class MilestoneResponse(BaseMilestone):
    """Response milestone schema."""

    id: UUID4
    character_id: UUID4
    completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        """Pydantic config."""

        orm_mode = True


class BaseAchievement(BaseModel):
    """Base achievement schema."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    category: AchievementCategory
    difficulty: Difficulty
    requirements: Dict
    rewards: Optional[Dict] = None
    points: int = Field(0, ge=0)
    campaign_achievement_id: Optional[UUID4] = None
    metadata: Optional[Dict] = None


class AchievementCreate(BaseAchievement):
    """Create achievement schema."""

    pass


class AchievementResponse(BaseAchievement):
    """Response achievement schema."""

    id: UUID4
    character_id: UUID4
    completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        orm_mode = True


class ProgressResponse(BaseModel):
    """Character progress response schema."""

    id: UUID4
    character_id: UUID4
    current_xp: int
    total_xp: int
    current_level: int
    milestones_completed: int
    level_progression: Dict
    requirements: Optional[Dict] = None
    metadata: Optional[Dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        orm_mode = True


class SnapshotResponse(BaseModel):
    """Progress snapshot response schema."""

    id: UUID4
    character_id: UUID4
    event_id: UUID4
    snapshot_type: str
    state_before: Dict
    state_after: Optional[Dict] = None
    diff: Optional[Dict] = None
    metadata: Optional[Dict] = None
    created_at: datetime

    class Config:
        """Pydantic config."""

        orm_mode = True
