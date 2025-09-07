"""Content models for NPCs, locations, and related entities."""
from datetime import datetime
from typing import List, Optional, Dict
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseTimestampModel


class NPC(BaseTimestampModel):
    """NPC model."""
    __tablename__ = "npcs"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )
    campaign_id: Mapped[UUID] = mapped_column(
        ForeignKey("campaigns.id"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    importance: Mapped[str] = mapped_column(
        String(20),  # major, minor, background
        nullable=False
    )
    race: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    class_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    personality: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False
    )
    goals: Mapped[List[str]] = mapped_column(
        ARRAY(String(200)),
        nullable=False,
        default=list
    )
    secrets: Mapped[List[str]] = mapped_column(
        ARRAY(String(200)),
        nullable=False,
        default=list
    )
    faction: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    location_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("locations.id"),
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )
    is_alive: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )
    death_chapter_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("chapters.id"),
        nullable=True
    )
    npc_metadata: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict
    )

    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign",
        back_populates="npcs"
    )
    location: Mapped[Optional["Location"]] = relationship(
        "Location",
        back_populates="npcs"
    )
    death_chapter: Mapped[Optional["Chapter"]] = relationship(
        "Chapter"
    )
    chapter_appearances: Mapped[List["ChapterNPC"]] = relationship(
        "ChapterNPC",
        back_populates="npc"
    )


class Location(BaseTimestampModel):
    """Location model."""
    __tablename__ = "locations"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )
    campaign_id: Mapped[UUID] = mapped_column(
        ForeignKey("campaigns.id"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    type: Mapped[str] = mapped_column(
        String(100),  # city, dungeon, wilderness, etc.
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    environment: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    points_of_interest: Mapped[List[Dict]] = mapped_column(
        JSONB,
        nullable=False,
        default=list
    )
    secrets: Mapped[List[str]] = mapped_column(
        ARRAY(String(200)),
        nullable=False,
        default=list
    )
    parent_location_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("locations.id"),
        nullable=True
    )
    is_discovered: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )
    discovery_chapter_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("chapters.id"),
        nullable=True
    )
    is_accessible: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )
    location_metadata: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict
    )

    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign",
        back_populates="locations"
    )
    parent_location: Mapped[Optional["Location"]] = relationship(
        "Location",
        remote_side=[id],
        backref="child_locations"
    )
    discovery_chapter: Mapped[Optional["Chapter"]] = relationship(
        "Chapter"
    )
    npcs: Mapped[List["NPC"]] = relationship(
        "NPC",
        back_populates="location"
    )
    chapter_appearances: Mapped[List["ChapterLocation"]] = relationship(
        "ChapterLocation",
        back_populates="location"
    )


class ChapterNPC(BaseTimestampModel):
    """NPC appearance in a chapter."""
    __tablename__ = "chapter_npcs"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )
    chapter_id: Mapped[UUID] = mapped_column(
        ForeignKey("chapters.id"),
        nullable=False
    )
    npc_id: Mapped[UUID] = mapped_column(
        ForeignKey("npcs.id"),
        nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(100),  # ally, enemy, neutral
        nullable=False
    )
    significance: Mapped[str] = mapped_column(
        String(20),  # major, minor
        nullable=False
    )
    location_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("locations.id"),
        nullable=True
    )
    interaction_points: Mapped[List[str]] = mapped_column(
        ARRAY(String(200)),
        nullable=False,
        default=list
    )
    chapter_npc_metadata: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict
    )

    # Relationships
    chapter: Mapped["Chapter"] = relationship(
        "Chapter",
        back_populates="npcs"
    )
    npc: Mapped["NPC"] = relationship(
        "NPC",
        back_populates="chapter_appearances"
    )
    location: Mapped[Optional["Location"]] = relationship(
        "Location"
    )


class ChapterLocation(BaseTimestampModel):
    """Location appearance in a chapter."""
    __tablename__ = "chapter_locations"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )
    chapter_id: Mapped[UUID] = mapped_column(
        ForeignKey("chapters.id"),
        nullable=False
    )
    location_id: Mapped[UUID] = mapped_column(
        ForeignKey("locations.id"),
        nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(100),  # primary, secondary
        nullable=False
    )
    significance: Mapped[str] = mapped_column(
        String(20),  # major, minor
        nullable=False
    )
    description_override: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    state_changes: Mapped[List[Dict]] = mapped_column(
        JSONB,
        nullable=False,
        default=list
    )
    chapter_location_metadata: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict
    )

    # Relationships
    chapter: Mapped["Chapter"] = relationship(
        "Chapter",
        back_populates="locations"
    )
    location: Mapped["Location"] = relationship(
        "Location",
        back_populates="chapter_appearances"
    )
