"""API models for story management endpoints."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class PlotBase(BaseModel):
    """Base class for plot data."""
    title: str
    description: str
    is_major: bool = False
    status: str  # e.g., 'active', 'resolved', 'abandoned'


class PlotCreate(PlotBase):
    """Data required to create a new plot."""
    campaign_id: UUID
    parent_plot_id: Optional[UUID] = None
    chapter_id: Optional[UUID] = None


class PlotUpdate(PlotBase):
    """Data that can be updated on a plot."""
    pass


class PlotResponse(PlotBase):
    """Full plot data including system fields."""
    id: UUID
    campaign_id: UUID
    parent_plot_id: Optional[UUID]
    chapter_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime


class StoryArcBase(BaseModel):
    """Base class for story arc data."""
    title: str
    description: str
    arc_type: str  # e.g., 'character', 'world', 'faction'
    status: str  # e.g., 'active', 'complete', 'abandoned'


class StoryArcCreate(StoryArcBase):
    """Data required to create a new story arc."""
    campaign_id: UUID
    plot_ids: List[UUID]


class StoryArcUpdate(StoryArcBase):
    """Data that can be updated on a story arc."""
    plot_ids: Optional[List[UUID]]


class StoryArcResponse(StoryArcBase):
    """Full story arc data including system fields."""
    id: UUID
    campaign_id: UUID
    plots: List[PlotResponse]
    created_at: datetime
    updated_at: datetime


class NPCRelationshipBase(BaseModel):
    """Base class for NPC relationship data."""
    npc_id: UUID
    character_id: UUID
    relationship_type: str  # e.g., 'ally', 'rival', 'mentor'
    strength: int  # Scale of 1-10
    description: str
    status: str  # e.g., 'active', 'strained', 'broken'


class NPCRelationshipCreate(NPCRelationshipBase):
    """Data required to create a new NPC relationship."""
    campaign_id: UUID


class NPCRelationshipUpdate(NPCRelationshipBase):
    """Data that can be updated on an NPC relationship."""
    pass


class NPCRelationshipResponse(NPCRelationshipBase):
    """Full NPC relationship data including system fields."""
    id: UUID
    campaign_id: UUID
    created_at: datetime
    updated_at: datetime


class ChapterBase(BaseModel):
    """Base class for chapter data."""
    title: str
    description: str
    order: int
    chapter_type: str  # e.g., 'introduction', 'development', 'climax'
    status: str  # e.g., 'planned', 'active', 'complete'


class ChapterCreate(ChapterBase):
    """Data required to create a new chapter."""
    campaign_id: UUID
    prerequisite_chapter_ids: Optional[List[UUID]] = None
    plot_ids: Optional[List[UUID]] = None


class ChapterUpdate(ChapterBase):
    """Data that can be updated on a chapter."""
    prerequisite_chapter_ids: Optional[List[UUID]]
    plot_ids: Optional[List[UUID]]


class ChapterResponse(ChapterBase):
    """Full chapter data including system fields."""
    id: UUID
    campaign_id: UUID
    prerequisite_chapters: List["ChapterResponse"]
    plots: List[PlotResponse]
    created_at: datetime
    updated_at: datetime
