"""Theme-related database models."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import JSON, ForeignKey, String, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from character_service.models.base import Base


class Theme(Base):
    """Theme model for defining character themes."""
    __tablename__ = "themes"

    # Basic fields
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Theme configuration
    base_modifiers: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    ability_adjustments: Mapped[Dict[str, int]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    
    # Requirements and restrictions
    level_requirement: Mapped[int] = mapped_column(Integer, default=1)
    class_restrictions: Mapped[List[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    race_restrictions: Mapped[List[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    
    # Version control
    version: Mapped[int] = mapped_column(Integer, default=1)
    parent_theme_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("themes.id"),
        nullable=True,
    )
    
    # Relationships
    features: Mapped[List["ThemeFeature"]] = relationship(
        "ThemeFeature",
        back_populates="theme",
        cascade="all, delete-orphan",
    )
    equipment_changes: Mapped[List["ThemeEquipment"]] = relationship(
        "ThemeEquipment",
        back_populates="theme",
        cascade="all, delete-orphan",
    )
    progression_rules: Mapped[List["ProgressionRule"]] = relationship(
        "ProgressionRule",
        back_populates="theme",
        cascade="all, delete-orphan",
    )
    character_states: Mapped[List["ThemeState"]] = relationship(
        "ThemeState",
        back_populates="theme",
    )


class ThemeFeature(Base):
    """Model for theme-specific features."""
    __tablename__ = "theme_features"

    theme_id: Mapped[UUID] = mapped_column(
        ForeignKey("themes.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    level_granted: Mapped[int] = mapped_column(Integer, default=1)
    mechanics: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    is_optional: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    theme: Mapped[Theme] = relationship(
        "Theme",
        back_populates="features",
    )


class ThemeEquipment(Base):
    """Model for theme-specific equipment changes."""
    __tablename__ = "theme_equipment"

    theme_id: Mapped[UUID] = mapped_column(
        ForeignKey("themes.id"),
        nullable=False,
    )
    item_id: Mapped[UUID] = mapped_column(
        ForeignKey("items.id"),
        nullable=False,
    )
    operation: Mapped[str] = mapped_column(String, nullable=False)  # add/remove/replace
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    requirements: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    
    # Relationships
    theme: Mapped[Theme] = relationship(
        "Theme",
        back_populates="equipment_changes",
    )


class ProgressionRule(Base):
    """Model for theme progression rules."""
    __tablename__ = "theme_progression_rules"

    theme_id: Mapped[UUID] = mapped_column(
        ForeignKey("themes.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    trigger_type: Mapped[str] = mapped_column(String, nullable=False)
    trigger_conditions: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    effects: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    
    # Relationships
    theme: Mapped[Theme] = relationship(
        "Theme",
        back_populates="progression_rules",
    )


class ThemeState(Base):
    """Model for tracking character theme state."""
    __tablename__ = "theme_states"

    character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id"),
        nullable=False,
    )
    theme_id: Mapped[UUID] = mapped_column(
        ForeignKey("themes.id"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    applied_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    deactivated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    applied_features: Mapped[List[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    applied_modifiers: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    progress_state: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    
    # Relationships
    theme: Mapped[Theme] = relationship(
        "Theme",
        back_populates="character_states",
    )


class ThemeTransition(Base):
    """Model for tracking theme transitions."""
    __tablename__ = "theme_transitions"

    character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id"),
        nullable=False,
    )
    from_theme_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("themes.id"),
        nullable=True,
    )
    to_theme_id: Mapped[UUID] = mapped_column(
        ForeignKey("themes.id"),
        nullable=False,
    )
    transition_type: Mapped[str] = mapped_column(String, nullable=False)
    triggered_by: Mapped[str] = mapped_column(String, nullable=False)
    campaign_event_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("campaign_events.id"),
        nullable=True,
    )
    changes: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    rolled_back: Mapped[bool] = mapped_column(Boolean, default=False)
    rollback_reason: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
