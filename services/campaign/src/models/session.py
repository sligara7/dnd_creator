"""Models for session tracking."""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text, DateTime, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseTimestampModel


class Session(BaseTimestampModel):
    """Session model for tracking play sessions."""
    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )
    campaign_id: Mapped[UUID] = mapped_column(
        ForeignKey("campaigns.id"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    session_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    dm_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    players: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False
    )
    chapters_played: Mapped[List[UUID]] = mapped_column(
        ARRAY(String),
        nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20),  # scheduled, in_progress, completed, cancelled
        nullable=False
    )
    version_hash: Mapped[str] = mapped_column(
        String(40),  # Git-like hash
        nullable=False
    )
    metadata: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict
    )

    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign",
        back_populates="sessions"
    )
    events: Mapped[List["SessionEvent"]] = relationship(
        "SessionEvent",
        back_populates="session"
    )
    notes: Mapped[List["SessionNote"]] = relationship(
        "SessionNote",
        back_populates="session"
    )


class SessionEvent(BaseTimestampModel):
    """Session event model."""
    __tablename__ = "session_events"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )
    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("sessions.id"),
        nullable=False
    )
    event_type: Mapped[str] = mapped_column(
        String(50),  # combat, roleplay, discovery, etc.
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    participants: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False
    )
    location_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("locations.id"),
        nullable=True
    )
    npcs_involved: Mapped[List[UUID]] = mapped_column(
        ARRAY(String),
        nullable=False
    )
    outcome: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    metadata: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict
    )

    # Relationships
    session: Mapped[Session] = relationship(
        Session,
        back_populates="events"
    )
    location: Mapped[Optional["Location"]] = relationship(
        "Location"
    )


class SessionNote(BaseTimestampModel):
    """Session note model."""
    __tablename__ = "session_notes"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )
    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("sessions.id"),
        nullable=False
    )
    author: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    note_type: Mapped[str] = mapped_column(
        String(50),  # dm, player, system
        nullable=False
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    is_private: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )
    metadata: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict
    )

    # Relationships
    session: Mapped[Session] = relationship(
        Session,
        back_populates="notes"
    )
