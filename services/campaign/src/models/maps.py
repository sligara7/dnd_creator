"""Map and location tracking models."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Table
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import relationship

from .base import Base


class MapLocation(Base):
    """Model for tracking locations and their associated maps."""

    __tablename__ = "map_locations"

    id = Column(PgUUID(as_uuid=True), primary_key=True)
    campaign_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False
    )
    parent_location_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("map_locations.id", ondelete="SET NULL"),
        nullable=True
    )
    name = Column(String(255), nullable=False)
    location_type = Column(String(50), nullable=False)  # world, region, city, building, etc
    description = Column(String, nullable=True)
    coordinates = Column(JSON, nullable=True)  # For placement on parent map
    metadata = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    campaign = relationship("Campaign", back_populates="locations")
    parent_location = relationship(
        "MapLocation",
        remote_side=[id],
        backref="child_locations"
    )
    maps = relationship("LocationMap", back_populates="location")


class LocationMap(Base):
    """Model for tracking map images and their versions."""

    __tablename__ = "location_maps"

    id = Column(PgUUID(as_uuid=True), primary_key=True)
    location_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("map_locations.id", ondelete="CASCADE"),
        nullable=False
    )
    image_id = Column(String(255), nullable=False)  # ID from image service
    map_type = Column(String(50), nullable=False)  # terrain, political, dungeon, etc
    is_current = Column(Boolean, default=True, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    prompt = Column(String, nullable=True)  # Original prompt used to generate
    style_params = Column(JSON, nullable=True)  # Style parameters used
    metadata = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    location = relationship("MapLocation", back_populates="maps")
    encounters = relationship("EncounterMap", back_populates="map")


class EncounterMap(Base):
    """Model for tracking encounter-specific map versions."""

    __tablename__ = "encounter_maps"

    id = Column(PgUUID(as_uuid=True), primary_key=True)
    encounter_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("encounters.id", ondelete="CASCADE"),
        nullable=False
    )
    map_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("location_maps.id", ondelete="CASCADE"),
        nullable=False
    )
    overlay_image_id = Column(String(255), nullable=True)  # Optional encounter-specific overlay
    marker_data = Column(JSON, nullable=True)  # Encounter-specific markers/annotations
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    encounter = relationship("Encounter", back_populates="maps")
    map = relationship("LocationMap", back_populates="encounters")
