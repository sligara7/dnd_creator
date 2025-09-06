"""Image generation database models."""
import uuid
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, JSON, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


class ImageContent(Base):
    """Base image content model."""
    __tablename__ = "image_content"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    generated_by: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    source_image: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    result_image: Mapped[str] = mapped_column(String(100), nullable=False)
    parameters: Mapped[Dict] = mapped_column(JSON, nullable=False, default=dict)
    metadata: Mapped[Dict] = mapped_column(JSON, nullable=False, default=dict)
    thumbnail: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class CharacterImage(ImageContent):
    """Character portrait model."""
    __tablename__ = "character_images"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("image_content.id", ondelete="CASCADE"),
        primary_key=True
    )
    character_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    image_type: Mapped[str] = mapped_column(String(50), nullable=False)  # portrait, action, etc.
    character_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    equipment_details: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "character",
    }


class LocationImage(ImageContent):
    """Location visualization model."""
    __tablename__ = "location_images"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("image_content.id", ondelete="CASCADE"),
        primary_key=True
    )
    location_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    location_type: Mapped[str] = mapped_column(String(50), nullable=False)
    map_details: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    environment_details: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "location",
    }


class ItemImage(ImageContent):
    """Item illustration model."""
    __tablename__ = "item_images"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("image_content.id", ondelete="CASCADE"),
        primary_key=True
    )
    item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)
    rarity: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    magical_properties: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "item",
    }


class EnhancedImage(ImageContent):
    """Enhanced image model."""
    __tablename__ = "enhanced_images"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("image_content.id", ondelete="CASCADE"),
        primary_key=True
    )
    original_image_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    enhancements: Mapped[Dict] = mapped_column(JSON, nullable=False)
    enhancement_order: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "enhanced",
    }
