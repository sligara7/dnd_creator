"""Theme models."""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import (
    Column,
    String,
    Float,
    JSON,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from campaign_service.models.base import Base


@dataclass
class ThemeElement:
    """Theme element with type and weight."""
    name: str
    type: str  # tone, narrative, visual
    weight: float


class Theme(Base):
    """Theme model."""
    __tablename__ = "themes"
    
    # Core fields
    name = Column(String, nullable=False)
    description = Column(String)
    elements = Column(JSON, nullable=False)  # List[ThemeElement]
    validation_rules = Column(JSON, nullable=False)  # Dict


class ThemeVersion(Base):
    """Theme version model for tracking theme changes."""
    __tablename__ = "theme_versions"
    
    theme_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("themes.id", ondelete="CASCADE"),
        nullable=False,
    )
    campaign_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String, nullable=False)
    modifications = Column(JSON, nullable=False)  # Dict[str, float]
    active = Column(Boolean, default=False)


class ThemedNPC(Base):
    """NPC with theme elements."""
    __tablename__ = "themed_npcs"
    
    campaign_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    theme_elements = Column(JSON, nullable=False)  # Dict[str, Dict[str, float]]
    inherit_theme = Column(Boolean, default=True)


class ThemedLocation(Base):
    """Location with theme elements."""
    __tablename__ = "themed_locations"
    
    campaign_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    theme_elements = Column(JSON, nullable=False)  # Dict[str, Dict[str, float]]
    inherit_theme = Column(Boolean, default=True)