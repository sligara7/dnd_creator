"""Models for character features and abilities."""
from enum import Enum, auto
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from character_service.models.base import Base


class FeatureType(Enum):
    """Types of character features."""
    CLASS = auto()
    RACIAL = auto()
    BACKGROUND = auto()


class ResourceType(Enum):
    """Types of character resources."""
    LONG_REST = auto()  # Recharges on long rest
    SHORT_REST = auto()  # Recharges on short rest
    PERMANENT = auto()   # Always available


class Feature(Base):
    """Model for character features."""

    __tablename__ = "features"

    character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    feature_type: Mapped[str] = mapped_column(String(20), nullable=False)
    level_gained: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # Class/Race/Background name
    resource_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    uses_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    uses_remaining: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)  # For feature-specific data


class Proficiency(Base):
    """Model for character proficiencies."""

    __tablename__ = "proficiencies"

    character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    proficiency_type: Mapped[str] = mapped_column(String(20), nullable=False)  # Skill, Tool, etc.
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # Where proficiency came from


# Update Character model relationships
from character_service.models.character import Character
Character.features = relationship("Feature", backref="character", lazy="selectin")
Character.proficiencies = relationship("Proficiency", backref="character", lazy="selectin")
