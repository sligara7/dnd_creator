"""Progress and event schema models."""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CreateEventRequest(BaseModel):
    """Request model for creating a campaign event."""

    event_type: str = Field(..., description="Type of campaign event")
    event_data: Dict = Field(default_factory=dict, description="Event-specific data")
    impact_type: str = Field(..., description="Type of impact this event has")
    impact_magnitude: int = Field(..., description="Magnitude of the impact")
    journal_entry_id: Optional[UUID] = Field(None, description="Associated journal entry ID")


class EventResponse(BaseModel):
    """Response model for campaign events."""

    id: UUID
    character_id: UUID
    event_type: str
    event_data: Dict
    impact_type: str
    impact_magnitude: int
    timestamp: datetime
    applied: bool
    applied_at: Optional[datetime]
    journal_entry_id: Optional[UUID]


class EventImpactResponse(BaseModel):
    """Response model for event impacts."""

    id: UUID
    event_id: UUID
    character_id: UUID
    impact_type: str
    impact_data: Dict
    applied: bool
    applied_at: Optional[datetime]
    is_reverted: bool
    reverted_at: Optional[datetime]
    notes: Optional[str]


class AddExperienceRequest(BaseModel):
    """Request model for adding experience."""

    amount: int = Field(..., gt=0, description="Amount of experience to add")
    source: str = Field(..., description="Source of the experience")
    reason: str = Field(..., description="Reason for awarding experience")


class AddExperienceResponse(BaseModel):
    """Response model for experience addition."""

    total_experience: int
    leveled_up: bool
    level_data: Optional[Dict] = None


class AddMilestoneRequest(BaseModel):
    """Request model for adding a milestone."""

    title: str = Field(..., description="Title of the milestone")
    description: str = Field(..., description="Description of the milestone")
    milestone_type: str = Field(..., description="Type of milestone")
    data: Optional[Dict] = Field(None, description="Additional milestone data")


class AddAchievementRequest(BaseModel):
    """Request model for adding an achievement."""

    title: str = Field(..., description="Title of the achievement")
    description: str = Field(..., description="Description of the achievement")
    achievement_type: str = Field(..., description="Type of achievement")
    data: Optional[Dict] = Field(None, description="Additional achievement data")


class MilestoneResponse(BaseModel):
    """Response model for milestone data."""

    id: str
    title: str
    description: str
    type: str
    achieved_at: str
    data: Dict


class AchievementResponse(BaseModel):
    """Response model for achievement data."""

    id: str
    title: str
    description: str
    type: str
    achieved_at: str
    data: Dict


class CharacterProgressResponse(BaseModel):
    """Response model for character progress."""

    id: UUID
    character_id: UUID
    experience_points: int
    current_level: int
    previous_level: int
    level_updated_at: Optional[datetime]
    milestones: List[MilestoneResponse]
    achievements: List[AchievementResponse]
