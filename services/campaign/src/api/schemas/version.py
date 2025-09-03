"""API schemas for version control operations."""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class VersionType(str, Enum):
    """Types of version snapshots."""
    SKELETON = "skeleton"     # Initial campaign structure
    DRAFT = "draft"          # Work in progress
    PUBLISHED = "published"   # Ready for play
    PLAYED = "played"        # After session modifications
    BRANCH = "branch"        # Alternative storyline
    MERGE = "merge"          # Combined storylines


class BranchType(str, Enum):
    """Types of campaign branches."""
    MAIN = "main"                 # Primary storyline
    ALTERNATE = "alternate"       # Alternative storyline
    PLAYER_CHOICE = "player_choice"  # Based on player decisions
    EXPERIMENTAL = "experimental"  # Testing new ideas
    PARALLEL = "parallel"         # Simultaneous storylines


class ContentChange(BaseModel):
    """Content change in a version."""
    field: str
    old_value: Optional[str] = None
    new_value: str
    reason: Optional[str] = None


class ContentDiff(BaseModel):
    """Difference between two versions."""
    path: str
    changes: List[ContentChange]
    metadata: Dict[str, str] = Field(default_factory=dict)


class VersionMetadata(BaseModel):
    """Metadata for a version."""
    author: str
    timestamp: datetime
    session_id: Optional[UUID] = None  # If version created during play
    parent_version: Optional[str] = None  # Parent version hash


class CreateVersionRequest(BaseModel):
    """Request model for version creation."""
    title: str = Field(..., min_length=1)
    summary: str
    content: Dict = Field(
        ...,
        description="Campaign/chapter content for this version"
    )
    parent_hashes: List[str] = Field(default_factory=list)
    branch_name: str
    version_type: VersionType
    commit_message: str


class CreateVersionResponse(BaseModel):
    """Response model for version creation."""
    version_hash: str
    metadata: VersionMetadata
    content_summary: Dict[str, str]
    validation_notes: Optional[str] = None


class CreateBranchRequest(BaseModel):
    """Request model for branch creation."""
    name: str = Field(..., min_length=1)
    branch_type: BranchType
    description: str
    from_commit: str  # Version hash to branch from


class CreateBranchResponse(BaseModel):
    """Response model for branch creation."""
    branch_name: str
    base_version: str
    first_version: str
    creation_notes: Optional[str] = None


class BranchInfo(BaseModel):
    """Information about a branch."""
    name: str
    type: BranchType
    description: str
    head_version: str
    versions: List[str]
    created_at: datetime
    last_modified: datetime


class MergeStrategy(str, Enum):
    """Available merge strategies."""
    MANUAL = "manual"       # User resolves all conflicts
    AUTO = "auto"          # Automatic resolution where possible
    CHERRY_PICK = "cherry_pick"  # Select specific changes


class MergeRequest(BaseModel):
    """Request model for branch merging."""
    source_branch: str
    target_branch: str
    strategy: MergeStrategy
    message: str


class MergeConflict(BaseModel):
    """Merge conflict information."""
    path: str
    field: str
    source_value: str
    target_value: str
    resolution_options: List[str]


class MergeResponse(BaseModel):
    """Response model for branch merging."""
    success: bool
    merge_version: Optional[str] = None
    conflicts: List[MergeConflict] = Field(default_factory=list)
    resolution_notes: Optional[str] = None


class PlaySession(BaseModel):
    """Play session information."""
    session_number: int
    session_title: str
    session_date: datetime
    chapters_played: List[str]  # Chapter version hashes
    players_present: List[str]
    dm_name: str
    major_events: List[Dict[str, str]]
    player_decisions: Dict[str, str]
    story_progression: str


class PlayerChoice(BaseModel):
    """Player choice tracking."""
    chapter_version_id: UUID
    choice_description: str
    options_presented: List[str]
    choice_made: Dict[str, str]
    players_involved: List[str]
    immediate_consequences: Dict[str, str]
    long_term_consequences: Dict[str, str]


class VersionSearchQuery(BaseModel):
    """Search parameters for versions."""
    branch: Optional[str] = None
    version_type: Optional[VersionType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    author: Optional[str] = None
    contains_text: Optional[str] = None
