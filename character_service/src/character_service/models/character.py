"""Character model."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from character_service.models.base import Base

class Character(Base):
    """Character model for D&D 5e characters."""
    
    __tablename__ = "characters"

    # Basic Information
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # Base Stats
    strength: Mapped[int] = mapped_column(Integer, nullable=False)
    dexterity: Mapped[int] = mapped_column(Integer, nullable=False)
    constitution: Mapped[int] = mapped_column(Integer, nullable=False)
    intelligence: Mapped[int] = mapped_column(Integer, nullable=False)
    wisdom: Mapped[int] = mapped_column(Integer, nullable=False)
    charisma: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # HP and Combat Stats
    max_hit_points: Mapped[int] = mapped_column(Integer, nullable=False)
    current_hit_points: Mapped[int] = mapped_column(Integer, nullable=False)
    temporary_hit_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Character Details
    race: Mapped[str] = mapped_column(String(50), nullable=False)
    character_class: Mapped[str] = mapped_column(String(50), nullable=False)
    background: Mapped[str] = mapped_column(String(100), nullable=False)

    # Multiclass tracking (list of {"class": str, "level": int})
    classes: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
