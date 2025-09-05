"""Character version control models."""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy import (
    String,
    DateTime,
    Boolean,
    JSON,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from character_service.domain.base import Base


class ChangeType(str, Enum):
    """Types of character changes."""

    ABILITY_SCORE = "ability_score"
    CLASS_FEATURE = "class_feature"
    EQUIPMENT = "equipment"
    LEVEL = "level"
    PROFICIENCY = "proficiency"
    RESOURCE = "resource"
    SPELL = "spell"
    THEME = "theme"
    OTHER = "other"


class ChangeSource(str, Enum):
    """Sources of character changes."""

    USER = "user"
    STORY = "story"
    THEME = "theme"
    CAMPAIGN = "campaign"
    SYSTEM = "system"


class CharacterVersion(Base):
    """Character version model.

    A version represents a snapshot of a character's state at a point in time.
    Versions form a tree structure, with each version potentially having a parent
    version and multiple child versions.
    """

    __tablename__ = "character_versions"
    __table_args__ = (
        Index("ix_character_versions_character_id", "character_id"),
        Index("ix_character_versions_parent_version_id", "parent_version_id"),
        Index("ix_character_versions_created_at", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID,
        primary_key=True,
    )

    character_id: Mapped[UUID] = mapped_column(
        PGUUID,
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    )

    parent_version_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID,
        ForeignKey("character_versions.id", ondelete="SET NULL"),
        nullable=True,
    )

    label: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True,
    )

    state: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
    )

    changes: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    created_by: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Relationships
    parent_version = relationship(
        "CharacterVersion",
        remote_side=[id],
        backref="child_versions",
    )


class CharacterChange(Base):
    """Character change model.

    A change represents a single modification to a character's state, such as
    an ability score adjustment or equipment addition.
    """

    __tablename__ = "character_changes"
    __table_args__ = (
        Index("ix_character_changes_character_id", "character_id"),
        Index("ix_character_changes_version_id", "version_id"),
        Index("ix_character_changes_created_at", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID,
        primary_key=True,
    )

    character_id: Mapped[UUID] = mapped_column(
        PGUUID,
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    )

    version_id: Mapped[UUID] = mapped_column(
        PGUUID,
        ForeignKey("character_versions.id", ondelete="CASCADE"),
        nullable=False,
    )

    change_type: Mapped[ChangeType] = mapped_column(
        String(50),
        nullable=False,
    )

    source: Mapped[ChangeSource] = mapped_column(
        String(50),
        nullable=False,
    )

    attribute_path: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    old_value: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    new_value: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    created_by: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


class VersionMetadata(Base):
    """Version metadata model.

    Stores additional information about character versions for efficient
    querying and analysis.
    """

    __tablename__ = "version_metadata"
    __table_args__ = (
        Index("ix_version_metadata_version_id", "version_id"),
        Index("ix_version_metadata_character_id", "character_id"),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID,
        primary_key=True,
    )

    version_id: Mapped[UUID] = mapped_column(
        PGUUID,
        ForeignKey("character_versions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    character_id: Mapped[UUID] = mapped_column(
        PGUUID,
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    )

    level: Mapped[int] = mapped_column(
        nullable=False,
    )

    class_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    active_theme_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID,
        nullable=True,
    )

    ability_scores: Mapped[Dict[str, int]] = mapped_column(
        JSON,
        nullable=False,
    )

    campaign_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID,
        nullable=True,
    )

    branch_point: Mapped[Optional[UUID]] = mapped_column(
        PGUUID,
        ForeignKey("character_versions.id", ondelete="SET NULL"),
        nullable=True,
    )

    is_milestone: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
