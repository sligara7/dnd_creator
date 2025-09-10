"""Version control models for campaign service.

This module implements a Git-like version control system for campaigns, allowing:
- Branch management for different campaign variations
- Commit history tracking
- Detailed change records
- State management
"""
from datetime import datetime, UTC
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from campaign_service.models.base import Base


class BranchType(str, Enum):
    """Types of branches in the campaign version control system."""

    MAIN = "main"  # The primary campaign branch
    FEATURE = "feature"  # New features or quest lines
    VARIANT = "variant"  # Alternative campaign paths
    RELEASE = "release"  # Prepared/stabilized version
    HOTFIX = "hotfix"  # Emergency fixes


class BranchState(str, Enum):
    """States that a branch can be in."""

    ACTIVE = "active"  # Branch is being actively developed
    MERGED = "merged"  # Branch has been merged into its base
    ARCHIVED = "archived"  # Branch is no longer active but preserved
    ABANDONED = "abandoned"  # Branch is no longer maintained


class Branch(Base):
    """Represents a campaign branch."""

    __tablename__ = "campaign_branches"

    # Core fields
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    type: Mapped[BranchType] = mapped_column(
        String(50),
        nullable=False,
        default=BranchType.FEATURE
    )
    state: Mapped[BranchState] = mapped_column(
        String(50),
        nullable=False,
        default=BranchState.ACTIVE
    )

    # References
    base_branch_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("campaign_branches.id"),
        nullable=True
    )
    campaign_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("campaigns.id"),
        nullable=False
    )

    # Metadata
    meta: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )

    # Relationships
    commits: Mapped[List["Commit"]] = relationship(
        "Commit",
        back_populates="branch",
        cascade="all, delete-orphan"
    )
    base_branch: Mapped[Optional["Branch"]] = relationship(
        "Branch",
        remote_side=[id],
        back_populates="derived_branches"
    )
    derived_branches: Mapped[List["Branch"]] = relationship(
        "Branch",
        back_populates="base_branch",
        cascade="all, delete-orphan"
    )

    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        """Validate branch name format."""
        if " " in value:
            raise ValueError(
                "Branch name cannot contain spaces. Use hyphens or slashes."
            )
        return value

    @validates("base_branch_id")
    def validate_base_branch(self, key: str, value: Optional[UUID]) -> Optional[UUID]:
        """Validate base branch reference.
        
        A branch can:
        - Have no base branch (root/main branch)
        - Reference another branch as its base
        But cannot:
        - Reference itself as its base branch
        """
        # Root branch case - no base branch is valid
        if value is None:
            return None
            
        # Prevent self-reference only if we have an ID and it matches base_branch_id
        if self.id is not None and value == self.id:
            raise ValueError("Branch cannot reference itself as base branch")
            
        return value


class Commit(Base):
    """Represents a commit in the version control system."""

    __tablename__ = "campaign_commits"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    branch_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("campaign_branches.id"),
        nullable=False
    )
    parent_commit_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("campaign_commits.id"),
        nullable=True
    )
    meta: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    # Relationships
    branch: Mapped["Branch"] = relationship(
        "Branch",
        back_populates="commits"
    )
    changes: Mapped[List["Change"]] = relationship(
        "Change",
        back_populates="commit",
        cascade="all, delete-orphan"
    )
    parent_commit: Mapped[Optional["Commit"]] = relationship(
        "Commit",
        remote_side=[id],
        back_populates="child_commits"
    )
    child_commits: Mapped[List["Commit"]] = relationship(
        "Commit",
        back_populates="parent_commit"
    )


class Change(Base):
    """Represents a single change in a commit."""

    __tablename__ = "campaign_changes"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    commit_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("campaign_commits.id"),
        nullable=False
    )
    entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False
    )
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    field_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    old_value: Mapped[Optional[Dict]] = mapped_column(
        JSONB,
        nullable=True
    )
    new_value: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False
    )
    meta: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    # Relationships
    commit: Mapped["Commit"] = relationship(
        "Commit",
        back_populates="changes"
    )
