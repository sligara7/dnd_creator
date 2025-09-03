"""Models for handling planes of existence and transitions."""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, ForeignKey, JSON, String, Table
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import relationship

from .base import Base


class Plane(Base):
    """Model for tracking planes of existence."""

    __tablename__ = "planes"

    id = Column(PgUUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # material, ethereal, astral, etc
    description = Column(String, nullable=True)
    physics_rules = Column(JSON, nullable=False, default={})  # How physics work
    magic_rules = Column(JSON, nullable=False, default={})  # How magic works
    base_effects = Column(JSON, nullable=False, default={})  # Default effects on entities
    transition_rules = Column(JSON, nullable=False, default={})  # Rules for entering/exiting
    metadata = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    campaigns = relationship("Campaign", secondary="campaign_planes")
    chapters = relationship("Chapter", secondary="chapter_planes")
    locations = relationship("MapLocation", secondary="plane_locations")


class PlaneTransition(Base):
    """Model for tracking transitions between planes."""

    __tablename__ = "plane_transitions"

    id = Column(PgUUID(as_uuid=True), primary_key=True)
    campaign_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False
    )
    chapter_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("chapters.id", ondelete="CASCADE"),
        nullable=True
    )
    source_plane_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("planes.id"),
        nullable=False
    )
    target_plane_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("planes.id"),
        nullable=False
    )
    transition_type = Column(String(50), nullable=False)  # permanent, temporary, etc
    trigger_conditions = Column(JSON, nullable=False)  # What causes the transition
    effects = Column(JSON, nullable=False)  # Effects during transition
    duration = Column(JSON, nullable=True)  # For temporary transitions
    affected_entities = Column(JSON, nullable=False)  # Characters/items affected
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    campaign = relationship("Campaign", back_populates="plane_transitions")
    chapter = relationship("Chapter", back_populates="plane_transitions")
    source_plane = relationship(
        "Plane",
        foreign_keys=[source_plane_id],
        backref="source_transitions"
    )
    target_plane = relationship(
        "Plane",
        foreign_keys=[target_plane_id],
        backref="target_transitions"
    )


class EntityPlaneManifestation(Base):
    """Model for tracking how entities manifest in different planes."""

    __tablename__ = "entity_plane_manifestations"

    id = Column(PgUUID(as_uuid=True), primary_key=True)
    entity_id = Column(String(255), nullable=False)  # Character/Item ID
    entity_type = Column(String(50), nullable=False)  # character, item, etc
    plane_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("planes.id", ondelete="CASCADE"),
        nullable=False
    )
    manifestation_type = Column(String(50), nullable=False)  # physical, spiritual, etc
    attributes = Column(JSON, nullable=False)  # Modified attributes in this plane
    abilities = Column(JSON, nullable=False)  # Modified abilities in this plane
    restrictions = Column(JSON, nullable=False)  # Restrictions in this plane
    special_effects = Column(JSON, nullable=False, default={})  # Unique effects
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    plane = relationship("Plane")


# Association tables
campaign_planes = Table(
    "campaign_planes",
    Base.metadata,
    Column(
        "campaign_id",
        PgUUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "plane_id",
        PgUUID(as_uuid=True),
        ForeignKey("planes.id", ondelete="CASCADE"),
        primary_key=True
    )
)

chapter_planes = Table(
    "chapter_planes",
    Base.metadata,
    Column(
        "chapter_id",
        PgUUID(as_uuid=True),
        ForeignKey("chapters.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "plane_id",
        PgUUID(as_uuid=True),
        ForeignKey("planes.id", ondelete="CASCADE"),
        primary_key=True
    )
)

plane_locations = Table(
    "plane_locations",
    Base.metadata,
    Column(
        "plane_id",
        PgUUID(as_uuid=True),
        ForeignKey("planes.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "location_id",
        PgUUID(as_uuid=True),
        ForeignKey("map_locations.id", ondelete="CASCADE"),
        primary_key=True
    )
)
