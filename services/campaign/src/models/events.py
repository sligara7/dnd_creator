"""Database models for events and messaging."""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text, JSON, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseTimestampModel


class Event(BaseTimestampModel):
    """Base event model."""
    __tablename__ = "events"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )
    campaign_id: Mapped[UUID] = mapped_column(
        ForeignKey("campaigns.id"),
        nullable=False
    )
    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    payload: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False
    )
    is_processed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )

    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign",
        backref="events"
    )


class MessageHub(BaseTimestampModel):
    """Message hub integration model."""
    __tablename__ = "message_hubs"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    connection_details: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    last_heartbeat: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    error_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False
    )


class MessageQueue(BaseTimestampModel):
    """Message queue model."""
    __tablename__ = "message_queues"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )
    message_hub_id: Mapped[UUID] = mapped_column(
        ForeignKey("message_hubs.id"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    message_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    config: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Relationships
    message_hub: Mapped[MessageHub] = relationship(
        "MessageHub",
        backref="queues"
    )


class PublishedMessage(BaseTimestampModel):
    """Published message tracking model."""
    __tablename__ = "published_messages"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )
    message_hub_id: Mapped[UUID] = mapped_column(
        ForeignKey("message_hubs.id"),
        nullable=False
    )
    queue_id: Mapped[UUID] = mapped_column(
        ForeignKey("message_queues.id"),
        nullable=False
    )
    message_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    correlation_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    payload: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False
    )
    is_confirmed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    confirmation_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    retry_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False
    )
    error_details: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # Relationships
    message_hub: Mapped[MessageHub] = relationship(
        "MessageHub"
    )
    queue: Mapped[MessageQueue] = relationship(
        "MessageQueue"
    )
