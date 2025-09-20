"""Models for image storage database."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, relationship

from storage.core.database import Base


class Image(Base):
    """Image model."""

    __tablename__ = "images"

    # Base fields
    id: Mapped[UUID] = Column(PGUUID, primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = Column(Boolean, nullable=False, default=False)

    # Basic information
    type: Mapped[str] = Column(String(50), nullable=False)
    subtype: Mapped[str] = Column(String(50), nullable=False)
    name: Mapped[str] = Column(String(255), nullable=False)
    description: Mapped[Optional[str]] = Column(Text, nullable=True)

    # Image data
    url: Mapped[str] = Column(String(1024), nullable=False)
    format: Mapped[str] = Column(String(50), nullable=False, default="png")
    width: Mapped[int] = Column(Integer, nullable=False)
    height: Mapped[int] = Column(Integer, nullable=False)
    size: Mapped[int] = Column(Integer, nullable=False)  # in bytes

    # Theme and style information
    theme: Mapped[str] = Column(String(50), nullable=False)
    style_data: Mapped[Optional[Dict[str, Any]]] = Column(JSONB, nullable=True)

    # Generation metadata
    generation_params: Mapped[Optional[Dict[str, Any]]] = Column(JSONB, nullable=True)
    source_id: Mapped[Optional[UUID]] = Column(PGUUID, nullable=True)
    source_type: Mapped[Optional[str]] = Column(String(50), nullable=True)

    # Relationships
    overlays: Mapped[List["ImageOverlay"]] = relationship(
        back_populates="image", cascade="all, delete-orphan"
    )
    grid: Mapped[Optional["MapGrid"]] = relationship(
        back_populates="image", cascade="all, delete-orphan", uselist=False
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Image(id={self.id}, name={self.name}, type={self.type})>"


class ImageOverlay(Base):
    """Image overlay model."""

    __tablename__ = "image_overlays"

    # Base fields
    id: Mapped[UUID] = Column(PGUUID, primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = Column(Boolean, nullable=False, default=False)

    # Basic information
    image_id: Mapped[UUID] = Column(
        PGUUID, ForeignKey("images.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = Column(String(50), nullable=False)
    name: Mapped[str] = Column(String(255), nullable=False)
    description: Mapped[Optional[str]] = Column(Text, nullable=True)

    # Overlay data
    data: Mapped[Dict[str, Any]] = Column(JSONB, nullable=False)
    style: Mapped[Dict[str, Any]] = Column(JSONB, nullable=False)

    # Relationships
    image: Mapped[Image] = relationship(back_populates="overlays")

    def __repr__(self) -> str:
        """String representation."""
        return f"<ImageOverlay(id={self.id}, name={self.name}, type={self.type})>"


class MapGrid(Base):
    """Map grid configuration model."""

    __tablename__ = "map_grids"

    # Base fields
    id: Mapped[UUID] = Column(PGUUID, primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = Column(Boolean, nullable=False, default=False)

    # Configuration
    image_id: Mapped[UUID] = Column(
        PGUUID, ForeignKey("images.id", ondelete="CASCADE"), nullable=False
    )
    enabled: Mapped[bool] = Column(Boolean, nullable=False, default=True)
    size: Mapped[int] = Column(Integer, nullable=False, default=50)
    color: Mapped[str] = Column(String(50), nullable=False, default="#000000")
    opacity: Mapped[float] = Column(Float, nullable=False, default=0.5)

    # Relationships
    image: Mapped[Image] = relationship(back_populates="grid")

    def __repr__(self) -> str:
        """String representation."""
        return f"<MapGrid(id={self.id}, image_id={self.image_id}, enabled={self.enabled})>"


class GenerationTask(Base):
    """Image generation task model."""

    __tablename__ = "generation_tasks"

    # Base fields
    id: Mapped[UUID] = Column(PGUUID, primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = Column(Boolean, nullable=False, default=False)

    # Task information
    type: Mapped[str] = Column(String(50), nullable=False)
    status: Mapped[str] = Column(String(50), nullable=False)
    priority: Mapped[int] = Column(Integer, nullable=False)

    # Task data
    params: Mapped[Dict[str, Any]] = Column(JSONB, nullable=False)
    result: Mapped[Optional[Dict[str, Any]]] = Column(JSONB, nullable=True)

    # Error tracking
    attempts: Mapped[int] = Column(Integer, nullable=False, default=0)
    last_error: Mapped[Optional[str]] = Column(Text, nullable=True)
    last_attempt: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)

    # Retry configuration
    retry_count: Mapped[int] = Column(Integer, nullable=False, default=0)
    max_retries: Mapped[int] = Column(Integer, nullable=False, default=3)
    retry_delay: Mapped[int] = Column(Integer, nullable=False, default=5)  # seconds

    def __repr__(self) -> str:
        """String representation."""
        return f"<GenerationTask(id={self.id}, type={self.type}, status={self.status})>"


class Theme(Base):
    """Theme model."""

    __tablename__ = "themes"

    # Base fields
    id: Mapped[UUID] = Column(PGUUID, primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = Column(Boolean, nullable=False, default=False)

    # Basic information
    name: Mapped[str] = Column(String(50), nullable=False, unique=True)
    display_name: Mapped[str] = Column(String(255), nullable=False)
    description: Mapped[Optional[str]] = Column(Text, nullable=True)

    # Configuration
    config: Mapped[Dict[str, Any]] = Column(JSONB, nullable=False)
    variables: Mapped[Dict[str, Any]] = Column(JSONB, nullable=False)
    prompts: Mapped[Dict[str, Any]] = Column(JSONB, nullable=False)
    styles: Mapped[Dict[str, Any]] = Column(JSONB, nullable=False)

    # Relationships
    variations: Mapped[List["ThemeVariation"]] = relationship(
        back_populates="theme", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Theme(id={self.id}, name={self.name})>"


class ThemeVariation(Base):
    """Theme variation model."""

    __tablename__ = "theme_variations"

    # Base fields
    id: Mapped[UUID] = Column(PGUUID, primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = Column(Boolean, nullable=False, default=False)

    # Basic information
    theme_id: Mapped[UUID] = Column(
        PGUUID, ForeignKey("themes.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = Column(String(50), nullable=False)
    display_name: Mapped[str] = Column(String(255), nullable=False)
    description: Mapped[Optional[str]] = Column(Text, nullable=True)

    # Configuration
    config_override: Mapped[Dict[str, Any]] = Column(JSONB, nullable=False)
    variable_override: Mapped[Dict[str, Any]] = Column(JSONB, nullable=False)

    # Relationships
    theme: Mapped[Theme] = relationship(back_populates="variations")

    def __repr__(self) -> str:
        """String representation."""
        return f"<ThemeVariation(id={self.id}, name={self.name}, theme_id={self.theme_id})>"


class StylePreset(Base):
    """Style preset model."""

    __tablename__ = "style_presets"

    # Base fields
    id: Mapped[UUID] = Column(PGUUID, primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = Column(Boolean, nullable=False, default=False)

    # Basic information
    name: Mapped[str] = Column(String(50), nullable=False, unique=True)
    display_name: Mapped[str] = Column(String(255), nullable=False)
    description: Mapped[Optional[str]] = Column(Text, nullable=True)
    category: Mapped[str] = Column(String(50), nullable=False)

    # Configuration
    config: Mapped[Dict[str, Any]] = Column(JSONB, nullable=False)
    prompts: Mapped[Dict[str, Any]] = Column(JSONB, nullable=False)
    compatibility: Mapped[List[str]] = Column(JSONB, nullable=False)

    def __repr__(self) -> str:
        """String representation."""
        return f"<StylePreset(id={self.id}, name={self.name}, category={self.category})>"


class ThemeElement(Base):
    """Theme element model."""

    __tablename__ = "theme_elements"

    # Base fields
    id: Mapped[UUID] = Column(PGUUID, primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = Column(Boolean, nullable=False, default=False)

    # Basic information
    category: Mapped[str] = Column(String(50), nullable=False)
    name: Mapped[str] = Column(String(50), nullable=False)
    display_name: Mapped[str] = Column(String(255), nullable=False)
    description: Mapped[Optional[str]] = Column(Text, nullable=True)

    # Configuration
    config: Mapped[Dict[str, Any]] = Column(JSONB, nullable=False)
    prompts: Mapped[Dict[str, Any]] = Column(JSONB, nullable=False)
    compatibility: Mapped[List[str]] = Column(JSONB, nullable=False)

    __table_args__ = (
        UniqueConstraint("category", "name", name="uq_theme_elements_category_name"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<ThemeElement(id={self.id}, category={self.category}, name={self.name})>"