"""Spellcasting models for the character service.

This module provides models for spells, spellcasting classes, and spell management.
"""

from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import Field
from sqlmodel import JSON

from .base import BaseDBModel, BaseVersionedDBModel

class SpellcastingAbility(str, Enum):
    """Valid spellcasting abilities."""
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"

class SpellSchool(str, Enum):
    """Schools of magic."""
    ABJURATION = "abjuration"
    CONJURATION = "conjuration"
    DIVINATION = "divination"
    ENCHANTMENT = "enchantment"
    EVOCATION = "evocation"
    ILLUSION = "illusion"
    NECROMANCY = "necromancy"
    TRANSMUTATION = "transmutation"

class SpellType(str, Enum):
    """Types of spells."""
    CANTRIP = "cantrip"
    SPELL = "spell"

class SpellComponent(str, Enum):
    """Spell components."""
    VERBAL = "verbal"
    SOMATIC = "somatic"
    MATERIAL = "material"

class SpellDuration(str, Enum):
    """Spell duration types."""
    INSTANTANEOUS = "instantaneous"
    ROUNDS = "rounds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    UNTIL_DISPELLED = "until_dispelled"
    SPECIAL = "special"

class SpellRange(str, Enum):
    """Spell range types."""
    SELF = "self"
    TOUCH = "touch"
    FEET = "feet"
    SIGHT = "sight"
    UNLIMITED = "unlimited"
    SPECIAL = "special"

class SpellArea(str, Enum):
    """Spell area of effect types."""
    CONE = "cone"
    CUBE = "cube"
    CYLINDER = "cylinder"
    LINE = "line"
    SPHERE = "sphere"
    SPECIAL = "special"

class Spell(BaseDBModel):
    """D&D spell definition."""
    name: str
    level: int = Field(ge=0, le=9)
    school: SpellSchool
    type: SpellType = SpellType.SPELL
    casting_time: str
    range: SpellRange
    range_value: Optional[int] = None
    components: List[SpellComponent]
    material_components: Optional[str] = None
    material_cost: Optional[int] = None
    duration: SpellDuration
    duration_value: Optional[int] = None
    concentration: bool = False
    ritual: bool = False
    description: str
    higher_levels: Optional[str] = None
    
    # Damage and Healing
    damage_type: Optional[str] = None
    damage_dice: Optional[str] = None
    healing_dice: Optional[str] = None
    
    # Area of Effect
    area_type: Optional[SpellArea] = None
    area_size: Optional[int] = None
    
    # Class Access
    classes: List[str] = Field(default_factory=list)
    subclasses: List[str] = Field(default_factory=list)
    
    # Source and Variants
    source: str
    homebrew: bool = False
    variants: List[Dict] = Field(default_factory=list)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    properties: Dict = Field(default_factory=dict, sa_column=JSON)

class SpellcastingClass(BaseDBModel):
    """Spellcasting configuration for a character class."""
    class_name: str
    spellcasting_ability: SpellcastingAbility
    ritual_casting: bool = False
    spells_known: Dict[int, int] = Field(default_factory=dict)  # level -> spells known
    spell_slots: Dict[int, Dict[int, int]] = Field(default_factory=dict)  # class level -> {spell level -> slots}
    cantrips_known: Dict[int, int] = Field(default_factory=dict)  # level -> cantrips known
    
    # Class Features
    prepared_spells_formula: Optional[str] = None  # e.g. "level + ability_modifier"
    spell_list: str  # e.g. "Arcane", "Divine", "Primal"
    multiclass_requirements: Optional[Dict] = None
    
    # Additional Features
    has_spellbook: bool = False
    flexible_casting: bool = False
    spell_mastery: bool = False
    signature_spells: bool = False
    
    # Metadata
    source: str
    properties: Dict = Field(default_factory=dict, sa_column=JSON)

class CharacterSpellcasting(BaseVersionedDBModel):
    """Character's spellcasting configuration and known/prepared spells."""
    character_id: UUID
    
    # Primary Spellcasting Class Info
    primary_class: str
    spellcasting_ability: SpellcastingAbility
    spell_save_dc: int
    spell_attack_bonus: int
    
    # Spell Slots and Preparation
    total_spell_slots: Dict[int, int] = Field(default_factory=dict)  # spell level -> slots
    used_spell_slots: Dict[int, int] = Field(default_factory=dict)
    spells_prepared: List[str] = Field(default_factory=list)
    spells_known: List[str] = Field(default_factory=list)
    cantrips_known: List[str] = Field(default_factory=list)
    
    # Spellbook (for classes that use one)
    spellbook_spells: List[str] = Field(default_factory=list)
    ritual_spells: List[str] = Field(default_factory=list)
    
    # Class-Specific Features
    class_spell_features: Dict = Field(default_factory=dict, sa_column=JSON)
    metamagic_options: List[str] = Field(default_factory=list)
    
    # Additional Sources
    magic_items_spells: List[Dict] = Field(default_factory=list)
    racial_spells: List[Dict] = Field(default_factory=list)
    feat_spells: List[Dict] = Field(default_factory=list)
    
    # Spell Management
    custom_spells: List[Dict] = Field(default_factory=list)
    spell_notes: Dict[str, str] = Field(default_factory=dict)
    favorite_spells: List[str] = Field(default_factory=list)
    spell_statistics: Dict = Field(default_factory=dict, sa_column=JSON)
    
    # Validation and Limits
    spells_per_level_limit: Dict[int, int] = Field(default_factory=dict)
    validation_errors: List[str] = Field(default_factory=list)
    
    # Metadata
    properties: Dict = Field(default_factory=dict, sa_column=JSON)

class SpellcastingChange(BaseDBModel):
    """Tracks changes to a character's spellcasting."""
    character_id: UUID
    character_level: int
    change_type: str  # learned, prepared, forgot, cast, slot_restored
    spell_name: Optional[str] = None
    spell_level: Optional[int] = None
    spell_source: Optional[str] = None
    previous_state: Dict = Field(default_factory=dict, sa_column=JSON)
    new_state: Dict = Field(default_factory=dict, sa_column=JSON)
    notes: Optional[str] = None
