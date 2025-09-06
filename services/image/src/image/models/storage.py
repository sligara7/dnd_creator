"""Storage models for image service."""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Enum as SQLAEnum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from image.models.base import Base


class ImageType(str, Enum):
    """Types of images that can be stored."""
    MAP_TACTICAL = "map_tactical"
    MAP_CAMPAIGN = "map_campaign"
    CHARACTER_PORTRAIT = "character_portrait"
    ITEM = "item"
    MONSTER = "monster"
    OVERLAY = "overlay"


class ImageFormat(str, Enum):
    """Supported image formats."""
    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"


class StorageLocation(str, Enum):
    """Storage locations for image data."""
    S3 = "s3"
    CDN = "cdn"
    LOCAL = "local"


class Image(Base):
    """Model for stored images."""

    __tablename__ = "images"

    # Required by base class but explicitly defined for clarity
    id: Mapped[UUID] = mapped_column(
        PGUUID, primary_key=True, default=uuid4
    )

    # Core image metadata
    type: Mapped[ImageType] = mapped_column(
        SQLAEnum(ImageType), nullable=False
    )
    format: Mapped[ImageFormat] = mapped_column(
        SQLAEnum(ImageFormat), nullable=False
    )
    content_hash: Mapped[str] = mapped_column(
        String, nullable=False, index=True
    )
    size_bytes: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    width: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    height: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    # Storage information
    location: Mapped[StorageLocation] = mapped_column(
        SQLAEnum(StorageLocation), nullable=False
    )
    storage_path: Mapped[str] = mapped_column(
        String, nullable=False
    )
    cdn_url: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )

    # Theme and metadata
    theme: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )
    metadata: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict
    )
    tags: Mapped[List[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )

    # Deduplication and version control
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )
    parent_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID, ForeignKey("images.id"), nullable=True
    )
    parent: Mapped[Optional["Image"]] = relationship(
        "Image", remote_side=[id], backref="versions"
    )

    # Reference tracking
    source_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID, nullable=True, index=True
    )
    source_type: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )

    # Cache control
    cache_key: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, index=True
    )
    cache_ttl: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True  # Seconds
    )

    # Timestamps (from base class)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Soft delete (from base class)
    is_deleted: Mapped[bool] = mapped_column(
        default=False, nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True
    )

    def __repr__(self) -> str:
        """Return string representation of the image."""
        return (f"<Image(id={self.id}, type={self.type}, "
                f"location={self.location}>")


class ImageRelationship(Base):
    """Model for tracking relationships between images."""

    __tablename__ = "image_relationships"

    # Required by base class but explicitly defined for clarity
    id: Mapped[UUID] = mapped_column(
        PGUUID, primary_key=True, default=uuid4
    )

    # Relationship endpoints
    source_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("images.id"), nullable=False
    )
    target_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("images.id"), nullable=False
    )

    # Relationship metadata
    type: Mapped[str] = mapped_column(
        String, nullable=False  # e.g., "overlay", "variant"
    )
    metadata: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict
    )

    # Timestamps (from base class)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Soft delete (from base class)
    is_deleted: Mapped[bool] = mapped_column(
        default=False, nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True
    )

    # Relationships
    source: Mapped[Image] = relationship(
        "Image", foreign_keys=[source_id], backref="source_relationships"
    )
    target: Mapped[Image] = relationship(
        "Image", foreign_keys=[target_id], backref="target_relationships"
    )

    def __repr__(self) -> str:
        """Return string representation of the relationship."""
        return (f"<ImageRelationship(source={self.source_id}, "
                f"target={self.target_id}, type={self.type}>")


class ImageAccess(Base):
    """Model for tracking image access patterns."""

    __tablename__ = "image_access"

    # Required by base class but explicitly defined for clarity
    id: Mapped[UUID] = mapped_column(
        PGUUID, primary_key=True, default=uuid4
    )

    # Access metadata
    image_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("images.id"), nullable=False
    )
    access_type: Mapped[str] = mapped_column(
        String, nullable=False  # e.g., "view", "download"
    )
    source_service: Mapped[str] = mapped_column(
        String, nullable=False
    )
    request_id: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )
    response_time_ms: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    cache_hit: Mapped[bool] = mapped_column(
        default=False, nullable=False
    )
    error: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )

    # Access timestamp
    accessed_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # Relationship
    image: Mapped[Image] = relationship(
        "Image", backref="access_logs"
    )

    def __repr__(self) -> str:
        """Return string representation of the access record."""
        return (f"<ImageAccess(image_id={self.image_id}, "
                f"type={self.access_type}, hit={self.cache_hit}>")
