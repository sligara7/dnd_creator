"""Database models for character data."""

from sqlalchemy import (
    Column, String, Integer, DateTime, Boolean, Text,
    ForeignKey, Table, JSON, Float, Enum, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from .base import Base

# Association tables
character_languages = Table(
    'character_languages',
    Base.metadata,
    Column('character_id', UUID(as_uuid=True), ForeignKey('characters.id')),
    Column('language_id', UUID(as_uuid=True), ForeignKey('languages.id'))
)

character_proficiencies = Table(
    'character_proficiencies',
    Base.metadata,
    Column('character_id', UUID(as_uuid=True), ForeignKey('characters.id')),
    Column('proficiency_id', UUID(as_uuid=True), ForeignKey('proficiencies.id')),
    Column('level', String)  # 'proficient' or 'expert'
)

class CharacterDB(Base):
    """Core character information."""
    __tablename__ = 'characters'
    
    # Primary key and metadata
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(String, nullable=False, default='1.0')
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Basic information
    name = Column(String(255), nullable=False)
    player_name = Column(String(255), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey('campaigns.id'))
    status = Column(String(50), default='active')  # active, retired, deceased
    
    # Core attributes
    level = Column(Integer, nullable=False, default=1)
    experience_points = Column(Integer, nullable=False, default=0)
    species = Column(String(100), nullable=False)
    subrace = Column(String(100))
    background = Column(String(100), nullable=False)
    
    # Ability scores
    strength = Column(Integer, nullable=False)
    dexterity = Column(Integer, nullable=False)
    constitution = Column(Integer, nullable=False)
    intelligence = Column(Integer, nullable=False)
    wisdom = Column(Integer, nullable=False)
    charisma = Column(Integer, nullable=False)
    
    # Complex data stored as JSON
    ability_score_increases = Column(JSONB, default=dict)
    class_levels = Column(JSONB, default=dict)  # {"Fighter": 3, "Wizard": 2}
    saving_throws = Column(JSONB, default=dict)
    skill_proficiencies = Column(JSONB, default=dict)
    
    # Character details
    alignment = Column(JSONB)  # {"ethical": "lawful", "moral": "good"}
    appearance = Column(JSONB)
    personality = Column(JSONB)
    background_info = Column(JSONB)
    
    # Audit trail
    audit_log = Column(JSONB, default=list)
    
    # Relationships
    campaign = relationship("CampaignDB", back_populates="characters")
    inventory = relationship("InventoryDB", back_populates="character", uselist=False)
    journal_entries = relationship("JournalEntryDB", back_populates="character")
    combat_state = relationship("CombatStateDB", back_populates="character", uselist=False)
    spellcasting = relationship("SpellcastingDB", back_populates="character", uselist=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('level > 0', name='check_positive_level'),
        CheckConstraint('experience_points >= 0', name='check_positive_xp'),
        CheckConstraint('strength BETWEEN 1 AND 30', name='check_strength_range'),
        CheckConstraint('dexterity BETWEEN 1 AND 30', name='check_dexterity_range'),
        CheckConstraint('constitution BETWEEN 1 AND 30', name='check_constitution_range'),
        CheckConstraint('intelligence BETWEEN 1 AND 30', name='check_intelligence_range'),
        CheckConstraint('wisdom BETWEEN 1 AND 30', name='check_wisdom_range'),
        CheckConstraint('charisma BETWEEN 1 AND 30', name='check_charisma_range'),
    )

class InventoryDB(Base):
    """Character inventory and equipment."""
    __tablename__ = 'inventories'
    
    # Primary key and character link
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id = Column(UUID(as_uuid=True), ForeignKey('characters.id'), nullable=False)
    
    # Equipment slots
    armor = Column(JSONB)  # Detailed armor info
    shield = Column(JSONB)  # Shield info if equipped
    weapons = Column(JSONB, default=list)  # List of equipped weapons
    
    # Inventory contents
    containers = Column(JSONB, default=dict)  # Named containers and their contents
    loose_items = Column(JSONB, default=list)  # Items not in containers
    
    # Currency
    currency = Column(JSONB, default=lambda: {
        "copper": 0, "silver": 0, "electrum": 0, "gold": 0, "platinum": 0
    })
    
    # Magic items
    attuned_items = Column(JSONB, default=list)
    max_attunements = Column(Integer, default=3)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    character = relationship("CharacterDB", back_populates="inventory")

class CombatStateDB(Base):
    """Character's current combat state."""
    __tablename__ = 'combat_states'
    
    # Primary key and character link
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id = Column(UUID(as_uuid=True), ForeignKey('characters.id'), nullable=False)
    
    # Core combat stats
    armor_class = Column(Integer, nullable=False)
    initiative = Column(Integer)
    speed = Column(JSONB, default=lambda: {"walk": 30})
    
    # Hit points
    current_hp = Column(Integer, nullable=False)
    temp_hp = Column(Integer, default=0)
    max_hp = Column(Integer, nullable=False)
    
    # Combat tracking
    conditions = Column(JSONB, default=list)
    exhaustion_level = Column(Integer, default=0)
    death_saves = Column(JSONB, default=lambda: {"successes": 0, "failures": 0})
    
    # Resources
    hit_dice = Column(JSONB, default=dict)
    spell_slots = Column(JSONB, default=dict)
    
    # Active effects
    active_effects = Column(JSONB, default=list)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    character = relationship("CharacterDB", back_populates="combat_state")

class SpellcastingDB(Base):
    """Character's spellcasting information."""
    __tablename__ = 'spellcasting'
    
    # Primary key and character link
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id = Column(UUID(as_uuid=True), ForeignKey('characters.id'), nullable=False)
    
    # Spellcasting ability
    spellcasting_ability = Column(String(50))  # intelligence, wisdom, or charisma
    spell_save_dc = Column(Integer)
    spell_attack_bonus = Column(Integer)
    
    # Spells
    cantrips_known = Column(JSONB, default=list)
    spells_known = Column(JSONB, default=dict)    # By level
    spells_prepared = Column(JSONB, default=list)
    
    # Spell slots
    total_slots = Column(JSONB, default=dict)     # By level
    slots_remaining = Column(JSONB, default=dict)  # By level
    
    # Features
    ritual_casting = Column(Boolean, default=False)
    concentration_spells = Column(JSONB, default=list)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    character = relationship("CharacterDB", back_populates="spellcasting")

# Reference tables
class LanguageDB(Base):
    """Available languages."""
    __tablename__ = 'languages'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    script = Column(String(100))
    description = Column(Text)
    rarity = Column(String(50))  # common, uncommon, rare, etc.

class ProficiencyDB(Base):
    """Available proficiencies."""
    __tablename__ = 'proficiencies'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    type = Column(String(50), nullable=False)  # skill, tool, weapon, armor, etc.
    description = Column(Text)
    ability = Column(String(50))  # Related ability score for skills

class RaceDB(Base):
    """Available races/species."""
    __tablename__ = 'races'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    speed = Column(Integer)
    size = Column(String(50))
    traits = Column(JSONB)
    ability_bonuses = Column(JSONB)
    languages = Column(JSONB)
    subraces = Column(JSONB, default=list)

class BackgroundDB(Base):
    """Available backgrounds."""
    __tablename__ = 'backgrounds'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    feature_name = Column(String(100))
    feature_description = Column(Text)
    skill_proficiencies = Column(JSONB)
    tool_proficiencies = Column(JSONB)
    languages = Column(JSONB)
    equipment = Column(JSONB)
    personality_traits = Column(JSONB)
    ideals = Column(JSONB)
    bonds = Column(JSONB)
    flaws = Column(JSONB)
