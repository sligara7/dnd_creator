"""Version control API schemas."""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from campaign_service.models.version import BranchType, VersionType


class VersionMetadata(BaseModel):
    """Version metadata."""

    initialized_at: Optional[str] = None
    initialized_by: Optional[str] = None
    restored_from: Optional[str] = None
    restored_at: Optional[str] = None
    source_branch: Optional[str] = None
    target_branch: Optional[str] = None
    resource_versions: Optional[Dict[str, Dict[str, Dict[str, str]]]] = None


class VersionCreate(BaseModel):
    """Request model for version creation."""

    content: Dict = Field(
        ...,
        description="Version content",
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Version title",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Commit message",
    )
    author: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Version author",
    )
    version_type: Optional[VersionType] = Field(
        None,
        description="Version type",
    )
    metadata: Optional[Dict] = Field(
        None,
        description="Additional metadata",
    )


class BranchCreate(BaseModel):
    """Request model for branch creation."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Branch name",
    )
    branch_type: BranchType = Field(
        ...,
        description="Branch type",
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Branch description",
    )
    base_version_hash: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="Base version hash",
    )
    parent_branch_id: Optional[UUID] = Field(
        None,
        description="Parent branch ID",
    )
    metadata: Optional[Dict] = Field(
        None,
        description="Additional metadata",
    )


class BranchMerge(BaseModel):
    """Request model for branch merging."""

    source_branch_id: UUID = Field(
        ...,
        description="Source branch ID",
    )
    target_branch_id: UUID = Field(
        ...,
        description="Target branch ID",
    )
    author: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Merge author",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Merge message",
    )
    metadata: Optional[Dict] = Field(
        None,
        description="Additional metadata",
    )


class VersionRead(BaseModel):
    """Response model for version details."""

    id: UUID
    campaign_id: UUID
    branch_id: UUID
    version_hash: str
    parent_hashes: List[str]
    version_type: VersionType
    title: str
    message: str
    author: str
    content: Dict
    metadata: Dict
    created_at: datetime
    is_deleted: bool
    deleted_at: Optional[datetime]

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class BranchRead(BaseModel):
    """Response model for branch details."""

    id: UUID
    campaign_id: UUID
    name: str
    branch_type: BranchType
    description: str
    parent_branch_id: Optional[UUID]
    base_version_hash: str
    metadata: Dict
    created_at: datetime
    is_deleted: bool
    deleted_at: Optional[datetime]

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class StateTransitionRead(BaseModel):
    """Response model for state transition details."""

    id: UUID
    campaign_id: UUID
    version_id: UUID
    from_state: Optional[Dict]
    to_state: Dict
    transition_type: str
    reason: str
    metadata: Dict
    created_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class VersionList(BaseModel):
    """Response model for version list."""

    items: List[VersionRead]
    total: int
    skip: int
    limit: int


class BranchList(BaseModel):
    """Response model for branch list."""

    items: List[BranchRead]
    total: int
    skip: int
    limit: int
