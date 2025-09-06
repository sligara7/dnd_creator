"""Campaign content database models."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


class CampaignContent(Base):
    """Base campaign content model."""
    __tablename__ = "campaign_content"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(String(500))
    metadata: Mapped[Dict] = mapped_column(JSON, nullable=False, default=dict)
    theme_context: Mapped[Dict] = mapped_column(JSON, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class StoryContent(CampaignContent):
    """Story content model."""
    __tablename__ = "story_content"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaign_content.id", ondelete="CASCADE"),
        primary_key=True
    )
    plot_points: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    npc_references: Mapped[List[Dict]] = mapped_column(JSON, nullable=False)
    location_references: Mapped[List[Dict]] = mapped_column(JSON, nullable=False)
    hooks: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "story",
    }


class NPCContent(CampaignContent):
    """NPC content model."""
    __tablename__ = "npc_content"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaign_content.id", ondelete="CASCADE"),
        primary_key=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(100))
    personality: Mapped[str] = mapped_column(Text)
    motivations: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    secrets: Mapped[List[str]] = mapped_column(ARRAY(String))
    relationships: Mapped[Dict] = mapped_column(JSON, nullable=False, default=dict)

    __mapper_args__ = {
        "polymorphic_identity": "npc",
    }


class LocationContent(CampaignContent):
    """Location content model."""
    __tablename__ = "location_content"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaign_content.id", ondelete="CASCADE"),
        primary_key=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    points_of_interest: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    occupants: Mapped[List[str]] = mapped_column(ARRAY(String))
    secrets: Mapped[List[str]] = mapped_column(ARRAY(String))
    hooks: Mapped[List[str]] = mapped_column(ARRAY(String))

    __mapper_args__ = {
        "polymorphic_identity": "location",
    }
