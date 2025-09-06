"""Story management API schemas."""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from campaign_service.models.story import NPCRelationType, PlotState, PlotType, StoryArcType


class StoryArcBase(BaseModel):
    """Base story arc schema."""

    title: str = Field(max_length=255)
    description: Optional[str] = None
    arc_type: StoryArcType
    content: Optional[Dict] = Field(default_factory=dict)
    metadata: Optional[Dict] = Field(default_factory=dict)


class StoryArcCreate(StoryArcBase):
    """Story arc creation schema."""

    sequence_number: Optional[int] = None


class StoryArcRead(StoryArcBase):
    """Story arc read schema."""

    id: UUID
    campaign_id: UUID
    sequence_number: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        orm_mode = True


class StoryArcList(BaseModel):
    """Story arc list schema."""

    items: List[StoryArcRead]
    total: int
    skip: int
    limit: int


class PlotBase(BaseModel):
    """Base plot schema."""

    title: str = Field(max_length=255)
    description: Optional[str] = None
    plot_type: PlotType
    content: Optional[Dict] = Field(default_factory=dict)
    metadata: Optional[Dict] = Field(default_factory=dict)


class PlotCreate(PlotBase):
    """Plot creation schema."""

    arc_id: Optional[UUID] = None
    parent_plot_id: Optional[UUID] = None


class PlotRead(PlotBase):
    """Plot read schema."""

    id: UUID
    campaign_id: UUID
    arc_id: Optional[UUID] = None
    parent_plot_id: Optional[UUID] = None
    state: PlotState
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        orm_mode = True


class PlotList(BaseModel):
    """Plot list schema."""

    items: List[PlotRead]
    total: int
    skip: int
    limit: int


class PlotChapterCreate(BaseModel):
    """Plot chapter creation schema."""

    plot_content: Dict = Field(default_factory=dict)
    plot_order: Optional[int] = None


class PlotChapterRead(BaseModel):
    """Plot chapter read schema."""

    id: UUID
    plot_id: UUID
    chapter_id: UUID
    plot_content: Dict
    plot_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        orm_mode = True


class PlotStateUpdate(BaseModel):
    """Plot state update schema."""

    new_state: PlotState
    reason: str
    metadata: Optional[Dict] = Field(default_factory=dict)


class NPCRelationshipBase(BaseModel):
    """Base NPC relationship schema."""

    npc_id: UUID
    relation_type: NPCRelationType
    description: str
    metadata: Optional[Dict] = Field(default_factory=dict)


class NPCRelationshipCreate(NPCRelationshipBase):
    """NPC relationship creation schema."""

    plot_id: Optional[UUID] = None
    arc_id: Optional[UUID] = None


class NPCRelationshipRead(NPCRelationshipBase):
    """NPC relationship read schema."""

    id: UUID
    campaign_id: UUID
    plot_id: Optional[UUID] = None
    arc_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        orm_mode = True


class NPCRelationshipList(BaseModel):
    """NPC relationship list schema."""

    items: List[NPCRelationshipRead]
    total: int
    skip: int
    limit: int


class StoryStructureRead(BaseModel):
    """Story structure read schema."""

    campaign_id: str
    arcs: List[Dict]
    standalone_plots: List[Dict]
