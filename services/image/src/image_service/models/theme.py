"""Theme and style-related database models."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import JSON, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from image_service.models.base import BaseModel
from uuid import UUID

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from image_service.models.base import BaseModel


class Theme(BaseModel):
    """Theme model."""

    __tablename__ = "themes"

    # Basic information
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    base_theme: Mapped[Optional[str]] = mapped_column(
        String(50),
        ForeignKey("themes.name"),
        nullable=True,
    )

    # Theme configuration
    config: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Theme configuration including properties and elements",
    )

    # Relations
    variations: Mapped[List["ThemeVariation"]] = relationship(
        back_populates="theme",
        cascade="all, delete-orphan",
    )
    elements: Mapped[List["ThemeElement"]] = relationship(
        back_populates="theme",
        cascade="all, delete-orphan",
    )
    """Theme model for image generation."""

    __tablename__ = "themes"

    # Basic information
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Theme configuration
    config: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    variables: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)

    # Generation settings
    prompts: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    styles: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, nullable=False)

    # Relations
    variations: Mapped[List["ThemeVariation"]] = relationship(
        back_populates="theme", cascade="all, delete-orphan"
    )


class ThemeVariation(BaseModel):
    """Theme variation model."""

    __tablename__ = "theme_variations"

    # Basic information
    theme_id: Mapped[UUID] = mapped_column(
        ForeignKey("themes.id"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Variation configuration
    config: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Variation configuration with property and element overrides",
    )

    # Relations
    theme: Mapped[Theme] = relationship(back_populates="variations")
    """Theme variation model."""

    __tablename__ = "theme_variations"

    # Basic information
    theme_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Variation configuration
    config_override: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    variable_override: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)

    # Relations
    theme: Mapped[Theme] = relationship(back_populates="variations")


class StylePreset(BaseModel):
    """Style preset model."""

    __tablename__ = "style_presets"

    # Basic information
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)

    # Preset configuration
    config: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Preset configuration including elements and modifiers",
    )
    compatibility: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        comment="List of compatible themes",
    )
    """Style preset model."""

    __tablename__ = "style_presets"

    # Basic information
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)

    # Preset configuration
    config: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    prompts: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    compatibility: Mapped[List[str]] = mapped_column(JSONB, nullable=False)


class ThemeElement(BaseModel):
    """Theme element model."""

    __tablename__ = "theme_elements"

    # Basic information
    theme_id: Mapped[UUID] = mapped_column(
        ForeignKey("themes.id"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Element configuration
    config: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Element configuration with modifiers and weights",
    )

    # Relations
    theme: Mapped[Theme] = relationship(back_populates="elements")

    __table_args__ = (
        # Ensure unique element names within a theme
        {"unique_together": ("theme_id", "name")},
    )
    """Theme element model (e.g., architecture, clothing, technology)."""

    __tablename__ = "theme_elements"

    # Basic information
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Element configuration
    config: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    prompts: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    compatibility: Mapped[List[str]] = mapped_column(JSONB, nullable=False)

    class Meta:
        """Model metadata."""
        unique_together = ("category", "name")
