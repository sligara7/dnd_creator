"""Campaign models for the campaign service."""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from campaign_service.models.base import Base


class CampaignType(str, Enum):
    """Campaign type enumeration."""

    TRADITIONAL = "traditional"
    ANTITHETICON = "antitheticon"


class CampaignState(str, Enum):
    """Campaign state enumeration."""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Campaign(Base):
    """Campaign model representing a D&D campaign."""

    __tablename__ = "campaigns"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    campaign_type: Mapped[CampaignType] = mapped_column(
        String(50), nullable=False, default=CampaignType.TRADITIONAL
    )
    state: Mapped[CampaignState] = mapped_column(
        String(50), nullable=False, default=CampaignState.DRAFT
    )
    theme_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    theme_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    campaign_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    
    # Creator and ownership
    creator_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    owner_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)

    # Timestamps and soft delete
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    chapters: Mapped[List["Chapter"]] = relationship(
        "Chapter",
        back_populates="campaign",
        cascade="all, delete-orphan",
    )


class ChapterType(str, Enum):
    """Chapter type enumeration."""

    INTRODUCTION = "introduction"
    STORY = "story"
    SIDE_QUEST = "side_quest"
    BOSS_BATTLE = "boss_battle"
    FINALE = "finale"


class ChapterState(str, Enum):
    """Chapter state enumeration."""

    DRAFT = "draft"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Chapter(Base):
    """Chapter model representing a campaign chapter."""

    __tablename__ = "chapters"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    campaign_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    chapter_type: Mapped[ChapterType] = mapped_column(
        String(50), nullable=False, default=ChapterType.STORY
    )
    state: Mapped[ChapterState] = mapped_column(
        String(50), nullable=False, default=ChapterState.DRAFT
    )
    sequence_number: Mapped[int] = mapped_column(nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    chapter_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Dependencies
    prerequisites: Mapped[List[UUID]] = mapped_column(
        JSONB, nullable=False, default=list
    )  # List of chapter IDs that must be completed first
    
    # Timestamps and soft delete
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign", back_populates="chapters"
    )
