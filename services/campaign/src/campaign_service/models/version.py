"""Version control models for campaign versioning."""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from campaign_service.models.base import Base


class VersionType(str, Enum):
    """Type of version."""

    SKELETON = "skeleton"  # Initial campaign structure
    DRAFT = "draft"  # Work in progress
    PUBLISHED = "published"  # Ready for play
    PLAYED = "played"  # Session complete
    BRANCH = "branch"  # Branch point
    MERGE = "merge"  # Merge commit


class BranchType(str, Enum):
    """Type of branch."""

    MAIN = "main"  # Main timeline
    ALTERNATE = "alternate"  # Alternate timeline
    PLAYER_CHOICE = "player_choice"  # Branch based on player decisions
    EXPERIMENTAL = "experimental"  # Testing changes
    PARALLEL = "parallel"  # Parallel development


class Version(Base):
    """Version model representing a campaign state version."""

    __tablename__ = "versions"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    campaign_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False
    )
    branch_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("branches.id"), nullable=False
    )
    version_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    parent_hashes: Mapped[List[str]] = mapped_column(ARRAY(String(64)), nullable=False)
    version_type: Mapped[VersionType] = mapped_column(
        String(50), nullable=False, default=VersionType.DRAFT
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Timestamps and soft delete
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="versions")
    branch: Mapped["Branch"] = relationship("Branch", back_populates="versions")


class Branch(Base):
    """Branch model representing a campaign timeline branch."""

    __tablename__ = "branches"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    campaign_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    branch_type: Mapped[BranchType] = mapped_column(
        String(50), nullable=False, default=BranchType.MAIN
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)
    parent_branch_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("branches.id"), nullable=True
    )
    base_version_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Timestamps and soft delete
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="branches")
    versions: Mapped[List["Version"]] = relationship(
        "Version", back_populates="branch", cascade="all, delete-orphan"
    )
    child_branches: Mapped[List["Branch"]] = relationship(
        "Branch",
        backref=relationship("Branch", remote_side=[id]),
        cascade="all, delete-orphan",
    )


class StateTransition(Base):
    """State transition model for tracking campaign state changes."""

    __tablename__ = "state_transitions"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    campaign_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False
    )
    version_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("versions.id"), nullable=False
    )
    from_state: Mapped[dict] = mapped_column(JSONB, nullable=True)  # Null for initial state
    to_state: Mapped[dict] = mapped_column(JSONB, nullable=False)
    transition_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="state_transitions")
    version: Mapped["Version"] = relationship("Version", back_populates="state_transitions")


# Update Campaign model relationships
from campaign_service.models.campaign import Campaign  # noqa
Campaign.versions = relationship("Version", back_populates="campaign", cascade="all, delete-orphan")
Campaign.branches = relationship("Branch", back_populates="campaign", cascade="all, delete-orphan")
Campaign.state_transitions = relationship("StateTransition", back_populates="campaign", cascade="all, delete-orphan")

# Add reverse relationship to Version model
Version.state_transitions = relationship("StateTransition", back_populates="version", cascade="all, delete-orphan")
