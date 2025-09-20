"""Character database models for storage service."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import (
    JSON, Boolean, Column, DateTime, Enum as SQLAEnum, Float,
    ForeignKey, Integer, String, Table
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PGUUID
from sqlalchemy.orm import Mapped, declarative_base, relationship

Base = declarative_base()


class Alignment(str, Enum):
    """Character alignment options."""
    LAWFUL_GOOD = "LG"
    NEUTRAL_GOOD = "NG"
    CHAOTIC_GOOD = "CG"
    LAWFUL_NEUTRAL = "LN"
    NEUTRAL = "N"
    CHAOTIC_NEUTRAL = "CN"
    LAWFUL_EVIL = "LE"
    NEUTRAL_EVIL = "NE"
    CHAOTIC_EVIL = "CE"


class ResourceRecharge(str, Enum):
    """Resource recharge timing."""
    SHORT_REST = "short_rest"
    LONG_REST = "long_rest"
    DAWN = "dawn"


class Character(Base):
    """Character model storing core character information."""
    __tablename__ = "characters"

    # Base Fields
    id: Mapped[UUID] = Column(PGUUID, primary_key=True)
    name: Mapped[str] = Column(String, nullable=False)
    player_name: Mapped[Optional[str]] = Column(String)
    class_name: Mapped[str] = Column(String, nullable=False)
    level: Mapped[int] = Column(Integer, nullable=False)
    background: Mapped[str] = Column(String, nullable=False)
    race: Mapped[str] = Column(String, nullable=False)
    alignment: Mapped[Alignment] = Column(SQLAEnum(Alignment), nullable=False)
    experience_points: Mapped[int] = Column(Integer, default=0)

    # Character Details
    age: Mapped[Optional[int]] = Column(Integer)
    height: Mapped[Optional[str]] = Column(String)
    weight: Mapped[Optional[str]] = Column(String)
    eye_color: Mapped[Optional[str]] = Column(String)
    skin_color: Mapped[Optional[str]] = Column(String)
    hair_color: Mapped[Optional[str]] = Column(String)

    # Ability Scores
    strength: Mapped[int] = Column(Integer, nullable=False)
    dexterity: Mapped[int] = Column(Integer, nullable=False)
    constitution: Mapped[int] = Column(Integer, nullable=False)
    intelligence: Mapped[int] = Column(Integer, nullable=False)
    wisdom: Mapped[int] = Column(Integer, nullable=False)
    charisma: Mapped[int] = Column(Integer, nullable=False)

    # Health & Resources
    max_hit_points: Mapped[int] = Column(Integer, nullable=False)
    current_hit_points: Mapped[int] = Column(Integer, nullable=False)
    temporary_hit_points: Mapped[int] = Column(Integer, default=0)
    hit_dice_total: Mapped[str] = Column(String, nullable=False)  # e.g., "4d8"
    hit_dice_current: Mapped[int] = Column(Integer, nullable=False)
    death_save_successes: Mapped[int] = Column(Integer, default=0)
    death_save_failures: Mapped[int] = Column(Integer, default=0)
    exhaustion_level: Mapped[int] = Column(Integer, default=0)
    inspiration: Mapped[bool] = Column(Boolean, default=False)

    # Proficiencies (as arrays)
    languages: Mapped[List[str]] = Column(ARRAY(String), default=list)
    weapon_proficiencies: Mapped[List[str]] = Column(ARRAY(String), default=list)
    armor_proficiencies: Mapped[List[str]] = Column(ARRAY(String), default=list)
    tool_proficiencies: Mapped[List[str]] = Column(ARRAY(String), default=list)
    saving_throw_proficiencies: Mapped[List[str]] = Column(ARRAY(String), default=list)
    skill_proficiencies: Mapped[List[str]] = Column(ARRAY(String), default=list)

    # Character Personality
    personality_traits: Mapped[List[str]] = Column(ARRAY(String), default=list)
    ideals: Mapped[List[str]] = Column(ARRAY(String), default=list)
    bonds: Mapped[List[str]] = Column(ARRAY(String), default=list)
    flaws: Mapped[List[str]] = Column(ARRAY(String), default=list)

    # Rich Text Fields
    backstory: Mapped[str] = Column(String, default="")
    notes: Mapped[str] = Column(String, default="")

    # Foreign Keys and Relationships
    theme_id: Mapped[Optional[UUID]] = Column(PGUUID, ForeignKey("themes.id"))
    campaign_id: Mapped[Optional[UUID]] = Column(PGUUID)
    owner_id: Mapped[UUID] = Column(PGUUID, nullable=False)

    # Relationships
    inventory = relationship("Inventory", back_populates="character", uselist=False)
    spellcasting = relationship("Spellcasting", back_populates="character", uselist=False)
    conditions = relationship("CharacterCondition", back_populates="character")
    journal_entries = relationship("JournalEntry", back_populates="character")
    class_resources = relationship("ClassResource", back_populates="character")

    # Metadata and State
    created_at: Mapped[datetime] = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(
        DateTime, 
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    is_deleted: Mapped[bool] = Column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = Column(DateTime)
    version: Mapped[int] = Column(Integer, default=1)

    # Additional Data
    metadata: Mapped[Dict] = Column(JSON, default=dict)


class CharacterCondition(Base):
    """Active conditions affecting a character."""
    __tablename__ = "character_conditions"

    id: Mapped[UUID] = Column(PGUUID, primary_key=True)
    character_id: Mapped[UUID] = Column(PGUUID, ForeignKey("characters.id"), nullable=False)
    condition_name: Mapped[str] = Column(String, nullable=False)
    source: Mapped[str] = Column(String)
    duration: Mapped[Optional[int]] = Column(Integer)  # Duration in rounds, if applicable
    start_time: Mapped[datetime] = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time: Mapped[Optional[datetime]] = Column(DateTime)
    notes: Mapped[str] = Column(String)

    # Relationships
    character = relationship("Character", back_populates="conditions")


class ClassResource(Base):
    """Character class-specific resources (ki points, sorcery points, etc.)."""
    __tablename__ = "class_resources"

    id: Mapped[UUID] = Column(PGUUID, primary_key=True)
    character_id: Mapped[UUID] = Column(PGUUID, ForeignKey("characters.id"), nullable=False)
    name: Mapped[str] = Column(String, nullable=False)
    maximum: Mapped[int] = Column(Integer, nullable=False)
    current: Mapped[int] = Column(Integer, nullable=False)
    recharge: Mapped[ResourceRecharge] = Column(
        SQLAEnum(ResourceRecharge),
        nullable=False,
        default=ResourceRecharge.LONG_REST
    )

    # Relationships
    character = relationship("Character", back_populates="class_resources")


class Inventory(Base):
    """Character inventory and equipment."""
    __tablename__ = "inventories"

    id: Mapped[UUID] = Column(PGUUID, primary_key=True)
    character_id: Mapped[UUID] = Column(PGUUID, ForeignKey("characters.id"), nullable=False, unique=True)

    # Currency
    copper: Mapped[int] = Column(Integer, default=0)
    silver: Mapped[int] = Column(Integer, default=0)
    electrum: Mapped[int] = Column(Integer, default=0)
    gold: Mapped[int] = Column(Integer, default=0)
    platinum: Mapped[int] = Column(Integer, default=0)

    # Equipment Slots
    armor_slot: Mapped[Optional[UUID]] = Column(PGUUID)
    shield_slot: Mapped[Optional[UUID]] = Column(PGUUID)
    weapon_slots: Mapped[List[UUID]] = Column(ARRAY(PGUUID), default=list)
    attuned_items: Mapped[List[UUID]] = Column(ARRAY(PGUUID), default=list)

    # Relationships
    character = relationship("Character", back_populates="inventory")
    items = relationship("InventoryItem", back_populates="inventory")


class InventoryItem(Base):
    """Items in a character's inventory."""
    __tablename__ = "inventory_items"

    id: Mapped[UUID] = Column(PGUUID, primary_key=True)
    inventory_id: Mapped[UUID] = Column(PGUUID, ForeignKey("inventories.id"), nullable=False)
    name: Mapped[str] = Column(String, nullable=False)
    description: Mapped[str] = Column(String)
    quantity: Mapped[int] = Column(Integer, default=1)
    weight: Mapped[float] = Column(Float, default=0.0)
    value_cp: Mapped[int] = Column(Integer, default=0)  # Value in copper pieces
    properties: Mapped[Dict] = Column(JSON, default=dict)
    
    # Equipment Data
    is_equipped: Mapped[bool] = Column(Boolean, default=False)
    requires_attunement: Mapped[bool] = Column(Boolean, default=False)
    is_attuned: Mapped[bool] = Column(Boolean, default=False)

    # Relationships
    inventory = relationship("Inventory", back_populates="items")


class Spellcasting(Base):
    """Character spellcasting information."""
    __tablename__ = "spellcasting"

    id: Mapped[UUID] = Column(PGUUID, primary_key=True)
    character_id: Mapped[UUID] = Column(PGUUID, ForeignKey("characters.id"), nullable=False, unique=True)
    spellcasting_ability: Mapped[str] = Column(String, nullable=False)  # INT, WIS, CHA
    spell_class: Mapped[str] = Column(String, nullable=False)
    
    # Spell Slots
    slots_total: Mapped[Dict[int, int]] = Column(JSON, default=dict)  # level: total
    slots_expended: Mapped[Dict[int, int]] = Column(JSON, default=dict)  # level: used

    # Spells
    spells_known: Mapped[List[UUID]] = Column(ARRAY(PGUUID), default=list)
    spells_prepared: Mapped[List[UUID]] = Column(ARRAY(PGUUID), default=list)

    # Concentration
    concentrating: Mapped[bool] = Column(Boolean, default=False)
    concentration_spell_id: Mapped[Optional[UUID]] = Column(PGUUID)

    # Relationships
    character = relationship("Character", back_populates="spellcasting")


class JournalEntry(Base):
    """Character journal entries tracking progress and events."""
    __tablename__ = "journal_entries"

    id: Mapped[UUID] = Column(PGUUID, primary_key=True)
    character_id: Mapped[UUID] = Column(PGUUID, ForeignKey("characters.id"), nullable=False)
    session_date: Mapped[datetime] = Column(DateTime, nullable=False)
    content: Mapped[str] = Column(String, nullable=False)
    xp_gained: Mapped[int] = Column(Integer, default=0)
    milestones: Mapped[List[str]] = Column(ARRAY(String), default=list)
    dm_notes: Mapped[Optional[str]] = Column(String)
    
    created_at: Mapped[datetime] = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    character = relationship("Character", back_populates="journal_entries")


# Theme and Version Control Models
class Theme(Base):
    """Theme information for characters and content."""
    __tablename__ = "themes"

    id: Mapped[UUID] = Column(PGUUID, primary_key=True)
    name: Mapped[str] = Column(String, nullable=False, unique=True)
    description: Mapped[str] = Column(String)
    parent_id: Mapped[Optional[UUID]] = Column(PGUUID, ForeignKey("themes.id"))
    created_at: Mapped[datetime] = Column(DateTime, nullable=False, default=datetime.utcnow)
    metadata: Mapped[Dict] = Column(JSON, default=dict)

    # Self-referential relationship for theme hierarchy
    parent = relationship("Theme", remote_side=[id])


class CharacterVersion(Base):
    """Version history for characters."""
    __tablename__ = "character_versions"

    id: Mapped[UUID] = Column(PGUUID, primary_key=True)
    character_id: Mapped[UUID] = Column(PGUUID, ForeignKey("characters.id"), nullable=False)
    version_number: Mapped[int] = Column(Integer, nullable=False)
    theme_id: Mapped[Optional[UUID]] = Column(PGUUID, ForeignKey("themes.id"))
    parent_version_id: Mapped[Optional[UUID]] = Column(PGUUID, ForeignKey("character_versions.id"))
    data: Mapped[Dict] = Column(JSON, nullable=False)  # Complete character state
    created_at: Mapped[datetime] = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by: Mapped[UUID] = Column(PGUUID, nullable=False)
    
    # Change tracking
    changes: Mapped[List[str]] = Column(ARRAY(String), default=list)
    reason: Mapped[Optional[str]] = Column(String)

    # Relationships
    theme = relationship("Theme")
    parent_version = relationship("CharacterVersion", remote_side=[id])