"""
Database models for the D&D Character Creator.
"""
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Character(Base):
    """Database model for D&D characters."""
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    player_name = Column(String(100), nullable=True)
    
    # Character basics
    species = Column(String(50), nullable=False)
    background = Column(String(50), nullable=True)
    alignment = Column(String(20), nullable=True)
    level = Column(Integer, default=1)
    
    # Character classes (stored as JSON)
    character_classes = Column(JSON, nullable=False, default=dict)
    
    # Ability scores
    strength = Column(Integer, default=10)
    dexterity = Column(Integer, default=10)
    constitution = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    wisdom = Column(Integer, default=10)
    charisma = Column(Integer, default=10)
    
    # Derived stats
    armor_class = Column(Integer, default=10)
    hit_points = Column(Integer, default=1)
    proficiency_bonus = Column(Integer, default=2)
    
    # Character data (stored as JSON for flexibility)
    equipment = Column(JSON, nullable=True, default=dict)
    features = Column(JSON, nullable=True, default=dict)
    spells = Column(JSON, nullable=True, default=dict)
    skills = Column(JSON, nullable=True, default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Additional character data
    backstory = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert character to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "player_name": self.player_name,
            "species": self.species,
            "background": self.background,
            "alignment": self.alignment,
            "level": self.level,
            "character_classes": self.character_classes,
            "abilities": {
                "strength": self.strength,
                "dexterity": self.dexterity,
                "constitution": self.constitution,
                "intelligence": self.intelligence,
                "wisdom": self.wisdom,
                "charisma": self.charisma
            },
            "armor_class": self.armor_class,
            "hit_points": self.hit_points,
            "proficiency_bonus": self.proficiency_bonus,
            "equipment": self.equipment,
            "features": self.features,
            "spells": self.spells,
            "skills": self.skills,
            "backstory": self.backstory,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active
        }


class CharacterSession(Base):
    """Database model for character creation sessions."""
    __tablename__ = "character_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), unique=True, index=True)  # UUID
    character_id = Column(Integer, nullable=True)  # Links to Character if saved
    
    # Session data
    current_step = Column(String(50), default="basic_info")
    session_data = Column(JSON, nullable=True, default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)


class CustomContent(Base):
    """Database model for user-created custom content."""
    __tablename__ = "custom_content"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    content_type = Column(String(50), nullable=False)  # "species", "class", "spell", etc.
    
    # Content data
    content_data = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    
    # Metadata
    created_by = Column(String(100), nullable=True)  # Future: user system
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
