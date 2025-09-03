"""Session notes and feedback models."""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text, DateTime, JSON, Boolean
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseTimestampModel


class SessionNote(BaseTimestampModel):
    """Session notes model for DM feedback and observations."""
    __tablename__ = "session_notes"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )
    campaign_id: Mapped[UUID] = mapped_column(
        ForeignKey("campaigns.id"),
        nullable=False
    )
    chapter_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("chapters.id"),
        nullable=True
    )
    session_number: Mapped[int] = mapped_column(
        nullable=False
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    narrative: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    dm_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    players_present: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False
    )
    objectives_completed: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list
    )
    significant_events: Mapped[List[Dict]] = mapped_column(
        JSONB,
        nullable=False,
        default=list
    )
    character_interactions: Mapped[List[Dict]] = mapped_column(
        JSONB,
        nullable=False,
        default=list
    )
    plot_decisions: Mapped[List[Dict]] = mapped_column(
        JSONB,
        nullable=False,
        default=list
    )
    feedback_status: Mapped[str] = mapped_column(
        String(20),  # pending, processed, applied
        nullable=False,
        default="pending"
    )
    feedback_processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    metadata: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict
    )

    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign",
        back_populates="session_notes"
    )
    chapter: Mapped[Optional["Chapter"]] = relationship(
        "Chapter",
        back_populates="session_notes"
    )
    character_records: Mapped[List["SessionCharacterRecord"]] = relationship(
        "SessionCharacterRecord",
        back_populates="session_note",
        cascade="all, delete-orphan"
    )


class SessionCharacterRecord(BaseTimestampModel):
    """Record of character interactions and events during a session."""
    __tablename__ = "session_character_records"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )
    session_note_id: Mapped[UUID] = mapped_column(
        ForeignKey("session_notes.id"),
        nullable=False
    )
    character_id: Mapped[str] = mapped_column(
        String(100),  # ID from character service
        nullable=False
    )
    character_type: Mapped[str] = mapped_column(
        String(20),  # player, npc
        nullable=False
    )
    interactions: Mapped[List[Dict]] = mapped_column(
        JSONB,
        nullable=False,
        default=list
    )
    significant_actions: Mapped[List[Dict]] = mapped_column(
        JSONB,
        nullable=False,
        default=list
    )
    rewards_earned: Mapped[List[Dict]] = mapped_column(
        JSONB,
        nullable=False,
        default=list
    )
    consequences: Mapped[List[Dict]] = mapped_column(
        JSONB,
        nullable=False,
        default=list
    )
    traits_demonstrated: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list
    )
    feedback_sent: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )
    feedback_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    metadata: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict
    )

    # Relationships
    session_note: Mapped[SessionNote] = relationship(
        "SessionNote",
        back_populates="character_records"
    )
