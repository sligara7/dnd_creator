"""API schemas for chapter operations."""
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChapterType(str, Enum):
    """Types of chapter content."""
    INTRODUCTION = "introduction"   # Campaign opener
    TRANSITION = "transition"       # Between major arcs
    MILESTONE = "milestone"        # Key story points
    COMBAT = "combat"             # Combat-focused
    ROLEPLAY = "roleplay"         # Social interaction
    EXPLORATION = "exploration"    # World exploration
    INVESTIGATION = "investigation"  # Mystery solving
    CLIMAX = "climax"             # Major confrontations
    EPILOGUE = "epilogue"         # Campaign closer


class ChapterStatus(str, Enum):
    """Chapter progression status."""
    DRAFT = "draft"           # Initial generation
    REFINED = "refined"       # After edits/refinements
    READY = "ready"          # Ready to play
    IN_PROGRESS = "in_progress"  # Currently being played
    COMPLETED = "completed"   # Finished playing
    SKIPPED = "skipped"      # Bypassed by players


class PartyRequirements(BaseModel):
    """Party requirements for a chapter."""
    level_range: Dict[str, int] = Field(
        ...,
        description="Min and max party level",
        example={"min": 1, "max": 4}
    )
    party_size: Dict[str, int] = Field(
        ...,
        description="Min and max party size",
        example={"min": 3, "max": 6}
    )


class Encounter(BaseModel):
    """Combat or non-combat encounter."""
    id: UUID
    type: str
    description: str
    difficulty: str
    rewards: List[str]
    prerequisites: List[str] = Field(default_factory=list)


class Objective(BaseModel):
    """Chapter objective."""
    id: UUID
    description: str
    type: str  # main, side, optional
    completion_criteria: List[str]
    rewards: List[str]
    prerequisites: List[Dict[str, str]] = Field(default_factory=list)


class NPCRole(BaseModel):
    """NPC's role in the chapter."""
    npc_id: UUID
    role: str  # ally, enemy, neutral
    significance: str  # major, minor
    interaction_points: List[str]
    secrets: List[str] = Field(default_factory=list)


class LocationRole(BaseModel):
    """Location's role in the chapter."""
    location_id: UUID
    role: str  # primary, secondary
    significance: str  # major, minor
    key_features: List[str]
    secrets: List[str] = Field(default_factory=list)


class ChapterContent(BaseModel):
    """Complete chapter content."""
    title: str
    summary: str
    objectives: List[Objective]
    encounters: List[Encounter]
    npcs: List[NPCRole]
    locations: List[LocationRole]
    hooks: List[str]
    rewards: List[Dict[str, str]]
    notes: str = ""


class CreateChapterRequest(BaseModel):
    """Request model for chapter creation."""
    title: str = Field(..., min_length=1, max_length=200)
    chapter_type: ChapterType
    theme: str = Field(..., description="Theme alignment")
    requirements: PartyRequirements
    dependencies: List[UUID] = Field(default_factory=list)
    generation_flags: Dict[str, bool] = Field(
        default_factory=lambda: {
            "generate_encounters": True,
            "generate_npcs": True,
            "generate_maps": True,
        }
    )


class ChapterDependency(BaseModel):
    """Chapter dependency information."""
    chapter_id: UUID
    dependency_type: str  # required, optional
    reason: str


class Chapter(BaseModel):
    """Complete chapter model with metadata."""
    id: UUID
    campaign_id: UUID
    type: ChapterType
    status: ChapterStatus
    content: ChapterContent
    theme: str
    dependencies: List[ChapterDependency] = Field(default_factory=list)
    version: str  # Git-like hash
    created_at: str
    updated_at: str


class CreateChapterResponse(BaseModel):
    """Response model for chapter creation."""
    id: UUID
    chapter: Chapter
    generation_notes: Optional[str] = None


class UpdateChapterRequest(BaseModel):
    """Request model for chapter update."""
    title: Optional[str] = None
    summary: Optional[str] = None
    objectives: Optional[List[Objective]] = None
    encounters: Optional[List[Encounter]] = None
    npcs: Optional[List[NPCRole]] = None
    locations: Optional[List[LocationRole]] = None
    hooks: Optional[List[str]] = None
    rewards: Optional[List[Dict[str, str]]] = None
    notes: Optional[str] = None
    status: Optional[ChapterStatus] = None
    dependencies: Optional[List[ChapterDependency]] = None
    commit_message: str = Field(..., min_length=1)


class UpdateChapterResponse(BaseModel):
    """Response model for chapter update."""
    id: UUID
    chapter: Chapter
    update_notes: Optional[str] = None
