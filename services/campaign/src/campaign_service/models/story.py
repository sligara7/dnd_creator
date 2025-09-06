"""Story management models for the campaign service."""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text, Integer
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from campaign_service.models.base import Base
from campaign_service.models.campaign import Campaign, Chapter


class PlotType(str, Enum):
    """Plot type enumeration."""

    MAIN = "main"  # Main storyline
    SIDE = "side"  # Side quests and subplots
    CHARACTER = "character"  # Character-focused plots
    FACTION = "faction"  # Faction-related plots
    MYSTERY = "mystery"  # Mystery or investigation plots
    HIDDEN = "hidden"  # Hidden plots (for Antitheticon)


class PlotState(str, Enum):
    """Plot state enumeration."""

    PLANNED = "planned"  # Initial planning stage
    ACTIVE = "active"  # Currently in progress
    RESOLVED = "resolved"  # Completed with resolution
    ABANDONED = "abandoned"  # Abandoned or bypassed


class Plot(Base):
    """Plot model representing a storyline or quest."""

    __tablename__ = "plots"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    campaign_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    plot_type: Mapped[PlotType] = mapped_column(
        String(50), nullable=False, default=PlotType.SIDE
    )
    state: Mapped[PlotState] = mapped_column(
        String(50), nullable=False, default=PlotState.PLANNED
    )
    content: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Relationships
    parent_plot_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("plots.id"),
        nullable=True,
    )
    arc_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("story_arcs.id"),
        nullable=True,
    )

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
    campaign: Mapped["Campaign"] = relationship("Campaign")
    arc: Mapped[Optional["StoryArc"]] = relationship("StoryArc", back_populates="plots")
    subplots: Mapped[List["Plot"]] = relationship(
        "Plot",
        backref="parent_plot",
        remote_side=[id],
        cascade="all, delete-orphan",
    )
    chapters: Mapped[List["PlotChapter"]] = relationship(
        "PlotChapter", back_populates="plot", cascade="all, delete-orphan"
    )


class StoryArcType(str, Enum):
    """Story arc type enumeration."""

    CAMPAIGN = "campaign"  # Overall campaign arc
    CHARACTER = "character"  # Character development arc
    WORLD = "world"  # World event arc
    THEME = "theme"  # Thematic arc


class StoryArc(Base):
    """Story arc model representing a major storyline arc."""

    __tablename__ = "story_arcs"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    campaign_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    arc_type: Mapped[StoryArcType] = mapped_column(
        String(50), nullable=False, default=StoryArcType.CAMPAIGN
    )
    content: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Ordering
    sequence_number: Mapped[int] = mapped_column(nullable=False)

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
    campaign: Mapped["Campaign"] = relationship("Campaign")
    plots: Mapped[List["Plot"]] = relationship("Plot", back_populates="arc")


class PlotChapter(Base):
    """Association table between plots and chapters with plot-specific chapter data."""

    __tablename__ = "plot_chapters"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    plot_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("plots.id"), nullable=False
    )
    chapter_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False
    )

    # Plot-specific chapter details
    plot_content: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    plot_order: Mapped[int] = mapped_column(Integer, nullable=False)  # Order in the plot

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    plot: Mapped["Plot"] = relationship("Plot", back_populates="chapters")
    chapter: Mapped["Chapter"] = relationship("Chapter")


class NPCRelationType(str, Enum):
    """NPC relationship type enumeration."""

    ALLY = "ally"  # Friendly to party
    ENEMY = "enemy"  # Hostile to party
    NEUTRAL = "neutral"  # Neutral to party
    RIVAL = "rival"  # Competitive but not hostile
    MENTOR = "mentor"  # Teaches/guides party
    PATRON = "patron"  # Provides quests/support
    CONTACT = "contact"  # Information source
    HIDDEN = "hidden"  # True relationship hidden (Antitheticon)


class NPCRelationship(Base):
    """NPC relationship model tracking relationships between NPCs and plots/arcs."""

    __tablename__ = "npc_relationships"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    campaign_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False
    )
    npc_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), nullable=False
    )  # References NPC in catalog
    relation_type: Mapped[NPCRelationType] = mapped_column(
        String(50), nullable=False, default=NPCRelationType.NEUTRAL
    )

    # Optional plot/arc relationships
    plot_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("plots.id"),
        nullable=True,
    )
    arc_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("story_arcs.id"),
        nullable=True,
    )

    # Relationship details
    description: Mapped[str] = mapped_column(Text, nullable=True)
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

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
    campaign: Mapped["Campaign"] = relationship("Campaign")
    plot: Mapped[Optional["Plot"]] = relationship("Plot")
    arc: Mapped[Optional["StoryArc"]] = relationship("StoryArc")
