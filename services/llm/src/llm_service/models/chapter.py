"""Models for campaign chapter organization."""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .theme import ThemeContext


class ChapterType(str, Enum):
    """Types of campaign chapters."""
    MAIN_QUEST = "main_quest"
    SIDE_QUEST = "side_quest"
    CHARACTER_ARC = "character_arc"
    WORLD_EVENT = "world_event"
    INTERLUDE = "interlude"
    CLIMAX = "climax"
    EPILOGUE = "epilogue"


class ChapterStatus(str, Enum):
    """Status of a campaign chapter."""
    DRAFT = "draft"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class StoryBeat(BaseModel):
    """Key story beat within a chapter."""
    beat_id: UUID = Field(description="Unique identifier")
    title: str = Field(description="Story beat title")
    description: str = Field(description="Story beat description")
    order: int = Field(description="Order within the section")
    requirements: Optional[Dict[str, str]] = Field(
        default=None,
        description="Prerequisites or requirements"
    )
    outcomes: Optional[Dict[str, str]] = Field(
        default=None,
        description="Potential outcomes"
    )
    metadata: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional metadata"
    )


class ChapterSection(BaseModel):
    """Section within a campaign chapter."""
    section_id: UUID = Field(description="Unique identifier")
    title: str = Field(description="Section title")
    description: str = Field(description="Section description")
    order: int = Field(description="Order within the chapter")
    story_beats: List[StoryBeat] = Field(
        default_factory=list,
        description="Story beats in this section"
    )
    theme_context: Optional[ThemeContext] = Field(
        default=None,
        description="Theme context for this section"
    )
    requirements: Optional[Dict[str, str]] = Field(
        default=None,
        description="Section requirements"
    )
    metadata: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional metadata"
    )


class ChapterReference(BaseModel):
    """Reference to another chapter."""
    chapter_id: UUID = Field(description="Referenced chapter ID")
    relationship: str = Field(description="Relationship type")
    metadata: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional metadata"
    )


class Chapter(BaseModel):
    """Campaign chapter organization."""
    chapter_id: UUID = Field(description="Unique identifier")
    campaign_id: UUID = Field(description="Parent campaign ID")
    title: str = Field(description="Chapter title")
    description: str = Field(description="Chapter description")
    chapter_type: ChapterType = Field(description="Type of chapter")
    status: ChapterStatus = Field(description="Current status")
    order: int = Field(description="Order in campaign")
    sections: List[ChapterSection] = Field(
        default_factory=list,
        description="Chapter sections"
    )
    theme_context: Optional[ThemeContext] = Field(
        default=None,
        description="Theme context for this chapter"
    )
    references: List[ChapterReference] = Field(
        default_factory=list,
        description="References to other chapters"
    )
    prerequisites: Optional[Dict[str, str]] = Field(
        default=None,
        description="Chapter prerequisites"
    )
    metadata: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional metadata"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ChapterOrganization(BaseModel):
    """Overall chapter organization for a campaign."""
    campaign_id: UUID = Field(description="Campaign ID")
    chapters: List[Chapter] = Field(description="Campaign chapters")
    theme_context: Optional[ThemeContext] = Field(
        default=None,
        description="Overall theme context"
    )
    metadata: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional metadata"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Request/Response models
class CreateChapterRequest(BaseModel):
    """Request to create a new chapter."""
    campaign_id: UUID = Field(description="Parent campaign ID")
    title: str = Field(description="Chapter title")
    description: str = Field(description="Chapter description")
    chapter_type: ChapterType = Field(description="Type of chapter")
    order: Optional[int] = Field(
        default=None,
        description="Desired order (auto-assigned if not specified)"
    )
    theme_context: Optional[ThemeContext] = Field(
        default=None,
        description="Theme context for this chapter"
    )
    prerequisites: Optional[Dict[str, str]] = Field(
        default=None,
        description="Chapter prerequisites"
    )
    metadata: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional metadata"
    )


class UpdateChapterRequest(BaseModel):
    """Request to update an existing chapter."""
    title: Optional[str] = Field(default=None, description="Chapter title")
    description: Optional[str] = Field(default=None, description="Chapter description")
    chapter_type: Optional[ChapterType] = Field(default=None, description="Type of chapter")
    status: Optional[ChapterStatus] = Field(default=None, description="Chapter status")
    order: Optional[int] = Field(default=None, description="Chapter order")
    theme_context: Optional[ThemeContext] = Field(
        default=None,
        description="Theme context for this chapter"
    )
    prerequisites: Optional[Dict[str, str]] = Field(
        default=None,
        description="Chapter prerequisites"
    )
    metadata: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional metadata"
    )


class CreateSectionRequest(BaseModel):
    """Request to create a new chapter section."""
    title: str = Field(description="Section title")
    description: str = Field(description="Section description")
    order: Optional[int] = Field(
        default=None,
        description="Desired order (auto-assigned if not specified)"
    )
    theme_context: Optional[ThemeContext] = Field(
        default=None,
        description="Theme context for this section"
    )
    requirements: Optional[Dict[str, str]] = Field(
        default=None,
        description="Section requirements"
    )
    metadata: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional metadata"
    )


class UpdateSectionRequest(BaseModel):
    """Request to update an existing section."""
    title: Optional[str] = Field(default=None, description="Section title")
    description: Optional[str] = Field(default=None, description="Section description")
    order: Optional[int] = Field(default=None, description="Section order")
    theme_context: Optional[ThemeContext] = Field(
        default=None,
        description="Theme context for this section"
    )
    requirements: Optional[Dict[str, str]] = Field(
        default=None,
        description="Section requirements"
    )
    metadata: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional metadata"
    )


class CreateStoryBeatRequest(BaseModel):
    """Request to create a new story beat."""
    title: str = Field(description="Story beat title")
    description: str = Field(description="Story beat description")
    order: Optional[int] = Field(
        default=None,
        description="Desired order (auto-assigned if not specified)"
    )
    requirements: Optional[Dict[str, str]] = Field(
        default=None,
        description="Prerequisites or requirements"
    )
    outcomes: Optional[Dict[str, str]] = Field(
        default=None,
        description="Potential outcomes"
    )
    metadata: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional metadata"
    )


class UpdateStoryBeatRequest(BaseModel):
    """Request to update an existing story beat."""
    title: Optional[str] = Field(default=None, description="Story beat title")
    description: Optional[str] = Field(default=None, description="Story beat description")
    order: Optional[int] = Field(default=None, description="Story beat order")
    requirements: Optional[Dict[str, str]] = Field(
        default=None,
        description="Prerequisites or requirements"
    )
    outcomes: Optional[Dict[str, str]] = Field(
        default=None,
        description="Potential outcomes"
    )
    metadata: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional metadata"
    )


class ChapterReferenceRequest(BaseModel):
    """Request to add a chapter reference."""
    target_chapter_id: UUID = Field(description="Referenced chapter ID")
    relationship: str = Field(description="Relationship type")
    metadata: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional metadata"
    )
