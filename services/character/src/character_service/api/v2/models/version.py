"""Version control API models."""
from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, constr


class VersionBase(BaseModel):
    """Base model for version information."""

    id: UUID
    character_id: UUID
    parent_version_id: Optional[UUID] = None
    label: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    created_by: str


class VersionResponse(VersionBase):
    """Response model for version information."""

    metadata: Optional[Dict[str, Any]] = None


class VersionListResponse(BaseModel):
    """Response model for version list."""

    versions: List[VersionResponse]
    total: int
    limit: int
    offset: int


class VersionCompareResponse(BaseModel):
    """Response model for version comparison."""

    version_a: UUID
    version_b: UUID
    diff: Dict[str, Any]
    changes: Dict[str, List[Dict[str, Any]]]
    metadata: Dict[str, Optional[Dict[str, Any]]]


class VersionTreeNode(BaseModel):
    """Model for version tree nodes."""

    id: UUID
    character_id: UUID
    parent_version_id: Optional[UUID] = None
    label: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    created_by: str
    metadata: Optional[Dict[str, Any]] = None
    children: List["VersionTreeNode"] = Field(default_factory=list)


class VersionRestoreRequest(BaseModel):
    """Request model for version restoration."""

    label: Optional[str] = None
    description: Optional[str] = None
    restored_by: constr(min_length=1, max_length=255)


class MilestoneRequest(BaseModel):
    """Request model for marking milestones."""

    milestone_type: Literal["story", "character", "campaign"]
    label: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MilestoneResponse(BaseModel):
    """Response model for milestone information."""

    id: UUID
    version_id: UUID
    milestone_type: str
    label: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
