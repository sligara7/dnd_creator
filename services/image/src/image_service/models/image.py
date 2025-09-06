"""Image-related database models."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import JSON, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from image_service.core.constants import (
    DEFAULT_GRID_COLOR,
    DEFAULT_GRID_OPACITY,
    DEFAULT_GRID_SIZE,
    FORMAT_PNG,
    IMAGE_TYPE_MAP,
    MAP_SUBTYPE_TACTICAL,
)
from image_service.models.base import BaseModel


class Image(BaseModel):
    """Base image model."""

    __tablename__ = "images"

    # Basic information
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    subtype: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Image data
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    format: Mapped[str] = mapped_column(
        String(50), nullable=False, default=FORMAT_PNG
    )
    width: Mapped[int] = mapped_column(nullable=False)
    height: Mapped[int] = mapped_column(nullable=False)
    size: Mapped[int] = mapped_column(nullable=False)  # in bytes

    # Theme and style information
    theme: Mapped[str] = mapped_column(String(50), nullable=False)
    style_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )

    # Generation metadata
    generation_params: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )
    source_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relations
    overlays: Mapped[List["ImageOverlay"]] = relationship(
        back_populates="image", cascade="all, delete-orphan"
    )


class ImageOverlay(BaseModel):
    """Image overlay model."""

    __tablename__ = "image_overlays"

    # Basic information
    image_id: Mapped[UUID] = mapped_column(
        nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Overlay data
    data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    style: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)

    # Relations
    image: Mapped[Image] = relationship(back_populates="overlays")


class MapGrid(BaseModel):
    """Map grid configuration model."""

    __tablename__ = "map_grids"

    # Basic information
    image_id: Mapped[UUID] = mapped_column(
        nullable=False, index=True, unique=True
    )
    enabled: Mapped[bool] = mapped_column(nullable=False, default=True)

    # Grid configuration
    size: Mapped[int] = mapped_column(nullable=False, default=DEFAULT_GRID_SIZE)
    color: Mapped[str] = mapped_column(
        String(50), nullable=False, default=DEFAULT_GRID_COLOR
    )
    opacity: Mapped[float] = mapped_column(
        nullable=False, default=DEFAULT_GRID_OPACITY
    )

    # Relations
    image: Mapped[Image] = relationship()


class GenerationTask(BaseModel):
    """Image generation task model."""

    __tablename__ = "generation_tasks"

    # Task information
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[int] = mapped_column(nullable=False)

    # Generation parameters
    params: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Error tracking
    attempts: Mapped[int] = mapped_column(nullable=False, default=0)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_attempt: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Retry configuration
    retry_count: Mapped[int] = mapped_column(nullable=False, default=0)
    max_retries: Mapped[int] = mapped_column(nullable=False, default=3)
    retry_delay: Mapped[int] = mapped_column(nullable=False, default=5)  # seconds

    # Relations
    image: Mapped[Optional[Image]] = relationship()
