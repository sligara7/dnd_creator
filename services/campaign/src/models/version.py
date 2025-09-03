"""Database models for version control."""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseTimestampModel


class Version(BaseTimestampModel):
    """Version snapshot model."""
    __tablename__ = "versions"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )
    campaign_id: Mapped[UUID] = mapped_column(
        ForeignKey("campaigns.id"),
        nullable=False
    )
    hash: Mapped[str] = mapped_column(
        String(40),  # Git-like SHA-1
        nullable=False,
        unique=True,
        index=True
    )
    parent_hashes: Mapped[List[str]] = mapped_column(
        ARRAY(String(40)),
        nullable=False
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    author: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    branch: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    tag: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    snapshot: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False
    )
    metadata: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False
    )

    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign",
        backref="versions"
    )


class Branch(BaseTimestampModel):
    """Branch tracking model."""
    __tablename__ = "branches"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )
    campaign_id: Mapped[UUID] = mapped_column(
        ForeignKey("campaigns.id"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    head: Mapped[str] = mapped_column(
        String(40),  # Git-like SHA-1
        ForeignKey("versions.hash"),
        nullable=False
    )
    base: Mapped[Optional[str]] = mapped_column(
        String(40),  # Git-like SHA-1
        ForeignKey("versions.hash"),
        nullable=True
    )
    is_merged: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )
    merged_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    metadata: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False
    )

    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign",
        backref="branches"
    )
    head_version: Mapped[Version] = relationship(
        "Version",
        foreign_keys=[head]
    )
    base_version: Mapped[Optional[Version]] = relationship(
        "Version",
        foreign_keys=[base]
    )


class MergeRequest(BaseTimestampModel):
    """Merge request model."""
    __tablename__ = "merge_requests"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )
    campaign_id: Mapped[UUID] = mapped_column(
        ForeignKey("campaigns.id"),
        nullable=False
    )
    source_branch: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    target_branch: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    author: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    reviewers: Mapped[List[str]] = mapped_column(
        ARRAY(String(100)),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    merged_by: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    merged_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    merge_commit_hash: Mapped[Optional[str]] = mapped_column(
        String(40),  # Git-like SHA-1
        nullable=True
    )
    metadata: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False
    )

    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign",
        backref="merge_requests"
    )


class Conflict(BaseTimestampModel):
    """Version control conflict model."""
    __tablename__ = "conflicts"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )
    campaign_id: Mapped[UUID] = mapped_column(
        ForeignKey("campaigns.id"),
        nullable=False
    )
    merge_request_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("merge_requests.id"),
        nullable=True
    )
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    entity_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    conflict_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    source_version: Mapped[str] = mapped_column(
        String(40),  # Git-like SHA-1
        nullable=False
    )
    target_version: Mapped[str] = mapped_column(
        String(40),  # Git-like SHA-1
        nullable=False
    )
    resolution: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    resolved_by: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    resolution_data: Mapped[Optional[Dict]] = mapped_column(
        JSONB,
        nullable=True
    )

    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign",
        backref="conflicts"
    )
    merge_request: Mapped[Optional[MergeRequest]] = relationship(
        "MergeRequest",
        backref="conflicts"
    )
