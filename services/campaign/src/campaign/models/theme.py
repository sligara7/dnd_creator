"""Database models for the theme system."""

from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import (Boolean, Column, DateTime, Enum as SQLAEnum, Float,
                     ForeignKey, Integer, String, Table)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class ThemeType(str, Enum):
    """Enumeration of theme types."""
    FANTASY = "fantasy"
    HORROR = "horror"
    MYSTERY = "mystery"
    POLITICAL = "political"
    WAR = "war"
    EXPLORATION = "exploration"
    INTRIGUE = "intrigue"
    DUNGEON = "dungeon"
    WILDERNESS = "wilderness"
    URBAN = "urban"
    PLANAR = "planar"
    NAUTICAL = "nautical"


class ThemeTone(str, Enum):
    """Enumeration of theme tones."""
    DARK = "dark"
    LIGHT = "light"
    NEUTRAL = "neutral"
    GRITTY = "gritty"
    HEROIC = "heroic"
    COMEDIC = "comedic"
    TRAGIC = "tragic"


class ThemeIntensity(str, Enum):
    """Enumeration of theme intensity levels."""
    SUBTLE = "subtle"
    MODERATE = "moderate"
    STRONG = "strong"
    OVERWHELMING = "overwhelming"


# Association table for theme combinations
theme_combinations = Table(
    "theme_combinations",
    Base.metadata,
    Column("primary_theme_id", PGUUID, ForeignKey("themes.id"), primary_key=True),
    Column("secondary_theme_id", PGUUID, ForeignKey("themes.id"), primary_key=True),
    Column("weight", Float, nullable=False, default=1.0),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
)


class Theme(Base):
    """Theme model for campaign themes."""
    __tablename__ = "themes"

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[ThemeType] = mapped_column(SQLAEnum(ThemeType), nullable=False)
    tone: Mapped[ThemeTone] = mapped_column(SQLAEnum(ThemeTone), nullable=False)
    intensity: Mapped[ThemeIntensity] = mapped_column(
        SQLAEnum(ThemeIntensity), nullable=False
    )
    
    # Theme attributes and rules stored as JSONB
    attributes: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    validation_rules: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    generation_prompts: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    style_guide: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Relationships
    combined_themes: Mapped[List["Theme"]] = relationship(
        "Theme",
        secondary=theme_combinations,
        primaryjoin=id == theme_combinations.c.primary_theme_id,
        secondaryjoin=id == theme_combinations.c.secondary_theme_id,
        back_populates="combined_with"
    )
    combined_with: Mapped[List["Theme"]] = relationship(
        "Theme",
        secondary=theme_combinations,
        primaryjoin=id == theme_combinations.c.secondary_theme_id,
        secondaryjoin=id == theme_combinations.c.primary_theme_id,
        back_populates="combined_themes"
    )
    world_effects: Mapped[List["WorldEffect"]] = relationship(
        "WorldEffect", back_populates="theme"
    )

    # Timestamps and soft delete
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class WorldEffectType(str, Enum):
    """Enumeration of world effect types."""
    ENVIRONMENT = "environment"
    CLIMATE = "climate"
    POPULATION = "population"
    FACTION = "faction"
    ECONOMY = "economy"
    POLITICS = "politics"
    CULTURE = "culture"


class WorldEffect(Base):
    """Model for theme-driven world effects."""
    __tablename__ = "world_effects"

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    theme_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("themes.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    effect_type: Mapped[WorldEffectType] = mapped_column(
        SQLAEnum(WorldEffectType), nullable=False
    )
    
    # Effect details stored as JSONB
    parameters: Mapped[dict] = mapped_column(JSONB, nullable=False)
    conditions: Mapped[dict] = mapped_column(JSONB, nullable=False)
    impact_scale: Mapped[float] = mapped_column(Float, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)  # In days

    # Relationships
    theme: Mapped[Theme] = relationship("Theme", back_populates="world_effects")
    affected_locations: Mapped[List["Location"]] = relationship("Location", back_populates="world_effects")
    affected_factions: Mapped[List["Faction"]] = relationship("Faction", back_populates="world_effects")

    # Timestamps and soft delete
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class Location(Base):
    """Model for campaign locations affected by world effects."""
    __tablename__ = "locations"

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    campaign_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("campaigns.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    location_type: Mapped[str] = mapped_column(String, nullable=False)
    
    # Location details stored as JSONB
    attributes: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    state: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Relationships
    world_effects: Mapped[List[WorldEffect]] = relationship(
        "WorldEffect", back_populates="affected_locations"
    )

    # Timestamps and soft delete
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class Faction(Base):
    """Model for campaign factions affected by world effects."""
    __tablename__ = "factions"

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    campaign_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("campaigns.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    faction_type: Mapped[str] = mapped_column(String, nullable=False)
    
    # Faction details stored as JSONB
    attributes: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    state: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    relationships: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Relationships
    world_effects: Mapped[List[WorldEffect]] = relationship(
        "WorldEffect", back_populates="affected_factions"
    )

    # Timestamps and soft delete
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
