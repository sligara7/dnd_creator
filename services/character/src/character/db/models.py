"""SQLAlchemy ORM models.

This module provides SQLAlchemy ORM models for the character service.
These models map the core domain models to database tables.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import JSON, Column, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

class CharacterModel(SQLModel, table=True):
    """SQLAlchemy model for D&D characters.
    
    This model maps the domain Character model to database tables.
    """
    __tablename__ = "characters"
    
    # Basic Info
    id: UUID = Field(
        default=None,
        primary_key=True,
        nullable=False,
    )
    name: str = Field(
        nullable=False,
        max_length=100,
    )
    player_name: Optional[str] = Field(
        nullable=True,
        max_length=100,
    )
    campaign_id: Optional[UUID] = Field(
        nullable=True,
        foreign_key="campaigns.id",
    )
    description: Optional[str] = Field(
        nullable=True,
    )
    gender: Optional[str] = Field(
        nullable=True,
        max_length=50,
    )
    pronouns: Optional[str] = Field(
        nullable=True,
        max_length=50,
    )
    faith: Optional[str] = Field(
        nullable=True,
        max_length=100,
    )
    
    # Appearance
    age: Optional[int] = Field(
        nullable=True,
    )
    height: Optional[str] = Field(
        nullable=True,
        max_length=50,
    )
    weight: Optional[str] = Field(
        nullable=True,
        max_length=50,
    )
    size: str = Field(
        nullable=False,
        max_length=20,
    )
    eye_color: Optional[str] = Field(
        nullable=True,
        max_length=50,
    )
    hair_color: Optional[str] = Field(
        nullable=True,
        max_length=50,
    )
    skin_color: Optional[str] = Field(
        nullable=True,
        max_length=50,
    )
    appearance_notes: Optional[str] = Field(
        nullable=True,
    )
    
    # Core Character Elements
    race_id: UUID = Field(
        nullable=False,
        foreign_key="races.id",
    )
    background_id: UUID = Field(
        nullable=False,
        foreign_key="backgrounds.id",
    )
    
    # Alignment and Personality
    alignment_moral: str = Field(
        nullable=False,
        max_length=20,
    )
    alignment_ethical: str = Field(
        nullable=False,
        max_length=20,
    )
    personality_traits: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )
    ideals: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )
    bonds: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )
    flaws: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )
    
    # Combat Stats
    armor_class: int = Field(
        default=10,
    )
    initiative_bonus: int = Field(
        default=0,
    )
    hit_point_maximum: int = Field(
        default=0,
    )
    current_hit_points: int = Field(
        default=0,
    )
    temporary_hit_points: int = Field(
        default=0,
    )
    hit_dice: Dict[str, int] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
    )
    death_save_successes: int = Field(
        default=0,
    )
    death_save_failures: int = Field(
        default=0,
    )
    
    # Spellcasting
    spellcasting_ability: Optional[str] = Field(
        nullable=True,
        max_length=20,
    )
    
    # Movement and Senses
    vision_types: Dict[str, int] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
    )
    movement_modes: Dict[str, int] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
    )
    
    # Resistances and Immunities
    damage_resistances: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )
    damage_immunities: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )
    damage_vulnerabilities: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )
    condition_immunities: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )
    
    # Active Effects
    active_conditions: Dict[str, Dict] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
    )
    active_effects: List[Dict] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )
    temporary_bonuses: Dict[str, List[Dict]] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
    )
    
    # Character Development
    background_story: Optional[str] = Field(
        nullable=True,
    )
    notes: Dict[str, str] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
    )
    goals: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )
    connections: List[Dict] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )
    
    # Metadata
    tags: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )
    custom_fields: Dict = Field(
        default_factory=dict,
        sa_column=Column(JSON),
    )
    flags: Dict[str, bool] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
    )
    
    # Relationships
    race = Relationship(
        back_populates="characters",
        sa_relationship_kwargs={"lazy": "joined"},
    )
    background = Relationship(
        back_populates="characters",
        sa_relationship_kwargs={"lazy": "joined"},
    )
    abilities = Relationship(
        back_populates="character",
        sa_relationship_kwargs={"lazy": "joined"},
    )
    skills = Relationship(
        back_populates="character",
        sa_relationship_kwargs={"lazy": "joined"},
    )
    equipment = Relationship(
        back_populates="character",
        sa_relationship_kwargs={"lazy": "joined"},
    )

class AbilityModel(SQLModel, table=True):
    """SQLAlchemy model for character abilities."""
    __tablename__ = "abilities"
    
    id: UUID = Field(default=None, primary_key=True)
    character_id: UUID = Field(foreign_key="characters.id")
    type: str = Field(max_length=20)
    base_score: int
    bonuses: Dict[str, int] = Field(default_factory=dict, sa_column=Column(JSON))
    penalties: Dict[str, int] = Field(default_factory=dict, sa_column=Column(JSON))
    overrides: Dict[str, int] = Field(default_factory=dict, sa_column=Column(JSON))
    saving_throw_proficient: bool = False
    
    # Relationships
    character = Relationship(back_populates="abilities")

class SkillModel(SQLModel, table=True):
    """SQLAlchemy model for character skills."""
    __tablename__ = "skills"
    
    id: UUID = Field(default=None, primary_key=True)
    character_id: UUID = Field(foreign_key="characters.id")
    name: str = Field(max_length=50)
    ability: str = Field(max_length=20)
    proficiency: str = Field(max_length=20)
    bonuses: Dict[str, int] = Field(default_factory=dict, sa_column=Column(JSON))
    advantage_sources: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    disadvantage_sources: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Relationships
    character = Relationship(back_populates="skills")

class EquipmentModel(SQLModel, table=True):
    """SQLAlchemy model for character equipment."""
    __tablename__ = "equipment"
    
    id: UUID = Field(default=None, primary_key=True)
    character_id: UUID = Field(foreign_key="characters.id")
    name: str = Field(max_length=100)
    type: str = Field(max_length=50)
    quantity: int = Field(default=1)
    weight: float = Field(default=0.0)
    equipped: bool = Field(default=False)
    attuned: bool = Field(default=False)
    container: Optional[str] = Field(nullable=True, max_length=100)
    properties: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    metadata: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Relationships
    character = Relationship(back_populates="equipment")

class WeaponModel(EquipmentModel, table=True):
    """SQLAlchemy model for character weapons."""
    __tablename__ = "weapons"
    
    weapon_type: str = Field(max_length=50)
    damage_dice: str = Field(max_length=20)
    damage_type: str = Field(max_length=20)
    versatile_damage_dice: Optional[str] = Field(nullable=True, max_length=20)
    range_normal: Optional[int] = None
    range_long: Optional[int] = None
    ammunition: Optional[str] = Field(nullable=True, max_length=50)
    loading: bool = False
    finesse: bool = False
    reach: bool = False
    thrown: bool = False
    two_handed: bool = False
    versatile: bool = False
    special_properties: List[str] = Field(default_factory=list, sa_column=Column(JSON))

class ArmorModel(EquipmentModel, table=True):
    """SQLAlchemy model for character armor."""
    __tablename__ = "armor"
    
    armor_type: str = Field(max_length=50)
    base_ac: int
    dex_bonus: bool = True
    max_dex_bonus: Optional[int] = None
    strength_requirement: Optional[int] = None
    stealth_disadvantage: bool = False

class RaceModel(SQLModel, table=True):
    """SQLAlchemy model for character races."""
    __tablename__ = "races"
    
    id: UUID = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: str
    size: str = Field(max_length=20)
    base_speed: int
    ability_bonuses: Dict[str, int] = Field(default_factory=dict, sa_column=Column(JSON))
    ability_choices: Optional[Dict] = Field(nullable=True, sa_column=Column(JSON))
    languages: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    extra_languages: int = 0
    traits: List[Dict] = Field(default_factory=list, sa_column=Column(JSON))
    subraces: List[Dict] = Field(default_factory=list, sa_column=Column(JSON))
    source: str = Field(max_length=100)
    metadata: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Relationships
    characters = Relationship(back_populates="race")

class BackgroundModel(SQLModel, table=True):
    """SQLAlchemy model for character backgrounds."""
    __tablename__ = "backgrounds"
    
    id: UUID = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: str
    skill_proficiencies: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    tool_proficiencies: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    languages: int = 0
    equipment: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    feature: Dict = Field(sa_column=Column(JSON))
    personality_traits: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    ideals: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    bonds: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    flaws: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    source: str = Field(max_length=100)
    metadata: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Relationships
    characters = Relationship(back_populates="background")
