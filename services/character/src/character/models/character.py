"""Character models for the character service.

This module provides models for D&D characters and their components,
including abilities, proficiencies, and features.
"""

from datetime import datetime
from typing import Dict, List, Optional, Set
from uuid import UUID

from pydantic import Field
from sqlmodel import JSON

from .base import BaseDBModel, BaseVersionedDBModel
from .enums import (
    AbilityType,
    AlignmentEthical,
    AlignmentMoral,
    ArmorType,
    Condition,
    DamageType,
    FeatureCategory,
    FeatureType,
    FeatureUsage,
    MovementType,
    ProficiencyLevel,
    Size,
    VisionType,
    WeaponType,
)

class Ability(BaseDBModel):
    """Character ability score."""
    character_id: UUID
    type: AbilityType
    base_score: int = Field(ge=1, le=30)
    bonuses: Dict[str, int] = Field(default_factory=dict)
    penalties: Dict[str, int] = Field(default_factory=dict)
    overrides: Dict[str, int] = Field(default_factory=dict)
    saving_throw_proficient: bool = False

    @property
    def score(self) -> int:
        """Calculate total ability score."""
        if self.overrides:
            return max(self.overrides.values())
        
        total = self.base_score
        total += sum(self.bonuses.values())
        total -= sum(self.penalties.values())
        return max(1, min(30, total))

    @property
    def modifier(self) -> int:
        """Calculate ability modifier."""
        return (self.score - 10) // 2

class Skill(BaseDBModel):
    """Character skill proficiency."""
    character_id: UUID
    name: str
    ability: AbilityType
    proficiency: ProficiencyLevel = ProficiencyLevel.NONE
    bonuses: Dict[str, int] = Field(default_factory=dict)
    advantage_sources: List[str] = Field(default_factory=list)
    disadvantage_sources: List[str] = Field(default_factory=list)

class Tool(BaseDBModel):
    """Tool proficiency."""
    character_id: UUID
    name: str
    type: str
    proficiency: ProficiencyLevel = ProficiencyLevel.NONE
    abilities: List[AbilityType] = Field(default_factory=list)
    bonuses: Dict[str, int] = Field(default_factory=dict)

class Language(BaseDBModel):
    """Known language."""
    character_id: UUID
    name: str
    script: Optional[str] = None
    source: str
    fluency: str = "native"  # native, learned, limited
    notes: Optional[str] = None

class Feature(BaseDBModel):
    """Character feature/trait."""
    character_id: UUID
    name: str
    description: str
    type: FeatureType
    category: FeatureCategory
    source: str
    usage: FeatureUsage = FeatureUsage.ALWAYS
    uses_total: Optional[int] = None
    uses_remaining: Optional[int] = None
    recharge: Optional[str] = None
    prerequisites: Optional[Dict] = None
    effects: Dict = Field(default_factory=dict, sa_column=JSON)
    metadata: Dict = Field(default_factory=dict, sa_column=JSON)

class Equipment(BaseDBModel):
    """Character equipment."""
    character_id: UUID
    name: str
    type: str
    quantity: int = Field(default=1, ge=0)
    weight: float = 0.0
    equipped: bool = False
    attuned: bool = False
    container: Optional[str] = None
    properties: Dict = Field(default_factory=dict, sa_column=JSON)
    metadata: Dict = Field(default_factory=dict, sa_column=JSON)

class Weapon(Equipment):
    """Character weapon."""
    weapon_type: WeaponType
    damage_dice: str
    damage_type: DamageType
    versatile_damage_dice: Optional[str] = None
    range_normal: Optional[int] = None
    range_long: Optional[int] = None
    ammunition: Optional[str] = None
    loading: bool = False
    finesse: bool = False
    reach: bool = False
    thrown: bool = False
    two_handed: bool = False
    versatile: bool = False
    special_properties: List[str] = Field(default_factory=list)

class Armor(Equipment):
    """Character armor."""
    armor_type: ArmorType
    base_ac: int
    dex_bonus: bool = True
    max_dex_bonus: Optional[int] = None
    strength_requirement: Optional[int] = None
    stealth_disadvantage: bool = False

class Race(BaseDBModel):
    """Character race/species."""
    name: str
    description: str
    size: Size
    base_speed: int
    ability_bonuses: Dict[AbilityType, int] = Field(default_factory=dict)
    ability_choices: Optional[Dict] = None
    languages: List[str] = Field(default_factory=list)
    extra_languages: int = 0
    traits: List[Feature] = Field(default_factory=list)
    subraces: List[Dict] = Field(default_factory=list)
    source: str
    metadata: Dict = Field(default_factory=dict, sa_column=JSON)

class Background(BaseDBModel):
    """Character background."""
    name: str
    description: str
    skill_proficiencies: List[str] = Field(default_factory=list)
    tool_proficiencies: List[str] = Field(default_factory=list)
    languages: int = 0
    equipment: List[str] = Field(default_factory=list)
    feature: Feature
    personality_traits: List[str] = Field(default_factory=list)
    ideals: List[str] = Field(default_factory=list)
    bonds: List[str] = Field(default_factory=list)
    flaws: List[str] = Field(default_factory=list)
    source: str
    metadata: Dict = Field(default_factory=dict, sa_column=JSON)

class ClassLevel(BaseDBModel):
    """Single level in a character class."""
    character_id: UUID
    class_name: str
    subclass_name: Optional[str] = None
    level: int = Field(ge=1, le=20)
    hp_rolled: Optional[int] = None
    features_granted: List[Feature] = Field(default_factory=list)
    choices_made: Dict = Field(default_factory=dict, sa_column=JSON)

class Character(BaseVersionedDBModel):
    """Core D&D character."""
    # Basic Info
    name: str
    player_name: Optional[str] = None
    campaign_id: Optional[UUID] = None
    description: Optional[str] = None
    gender: Optional[str] = None
    pronouns: Optional[str] = None
    faith: Optional[str] = None
    
    # Appearance
    age: Optional[int] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    size: Size = Size.MEDIUM
    eye_color: Optional[str] = None
    hair_color: Optional[str] = None
    skin_color: Optional[str] = None
    appearance_notes: Optional[str] = None
    
    # Core Character Elements
    race_id: UUID
    background_id: UUID
    classes: List[ClassLevel] = Field(default_factory=list)
    
    # Alignment and Personality
    alignment_moral: AlignmentMoral = AlignmentMoral.NEUTRAL
    alignment_ethical: AlignmentEthical = AlignmentEthical.NEUTRAL
    personality_traits: List[str] = Field(default_factory=list)
    ideals: List[str] = Field(default_factory=list)
    bonds: List[str] = Field(default_factory=list)
    flaws: List[str] = Field(default_factory=list)
    
    # Abilities and Skills (relationship fields)
    abilities: Optional[List[Ability]] = None
    skills: Optional[List[Skill]] = None
    tool_proficiencies: Optional[List[Tool]] = None
    languages: Optional[List[Language]] = None
    
    # Features and Proficiencies
    features: List[Feature] = Field(default_factory=list)
    other_proficiencies: Dict[str, List[str]] = Field(default_factory=dict)
    weapon_proficiencies: Set[WeaponType] = Field(default_factory=set)
    armor_proficiencies: Set[ArmorType] = Field(default_factory=set)
    
    # Combat Stats
    armor_class: int = 10
    initiative_bonus: int = 0
    speed: Dict[MovementType, int] = Field(default_factory=dict)
    hit_point_maximum: int = 0
    current_hit_points: int = 0
    temporary_hit_points: int = 0
    hit_dice: Dict[str, int] = Field(default_factory=dict)
    death_save_successes: int = 0
    death_save_failures: int = 0
    
    # Equipment (relationship fields)
    equipment: Optional[List[Equipment]] = None
    weapons: Optional[List[Weapon]] = None
    armor: Optional[List[Armor]] = None
    
    # Spellcasting (tracked in separate models)
    spellcasting_ability: Optional[AbilityType] = None
    
    # Senses and Movement
    vision_types: Dict[VisionType, int] = Field(default_factory=dict)
    movement_modes: Dict[MovementType, int] = Field(default_factory=dict)
    
    # Resistances and Immunities
    damage_resistances: Set[DamageType] = Field(default_factory=set)
    damage_immunities: Set[DamageType] = Field(default_factory=set)
    damage_vulnerabilities: Set[DamageType] = Field(default_factory=set)
    condition_immunities: Set[Condition] = Field(default_factory=set)
    
    # Active Effects
    active_conditions: Dict[Condition, Dict] = Field(default_factory=dict)
    active_effects: List[Dict] = Field(default_factory=list)
    temporary_bonuses: Dict[str, List[Dict]] = Field(default_factory=dict)
    
    # Character Development
    background_story: Optional[str] = None
    notes: Dict[str, str] = Field(default_factory=dict)
    goals: List[str] = Field(default_factory=list)
    connections: List[Dict] = Field(default_factory=list)
    
    # Validation and Generation
    validated: bool = False
    validation_errors: List[str] = Field(default_factory=list)
    generation_prompt: Optional[str] = None
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict = Field(default_factory=dict, sa_column=JSON)
    flags: Dict[str, bool] = Field(default_factory=dict)
    
    @property
    def total_level(self) -> int:
        """Calculate total character level."""
        return sum(c.level for c in self.classes)
    
    @property
    def proficiency_bonus(self) -> int:
        """Calculate proficiency bonus."""
        return 2 + ((self.total_level - 1) // 4)

class CharacterActionTemplate(BaseDBModel):
    """Template for common character actions."""
    name: str
    action_type: str  # action, bonus action, reaction, free
    description: str
    requirements: List[str] = Field(default_factory=list)
    effects: List[Dict] = Field(default_factory=list)
    related_features: List[str] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict, sa_column=JSON)

class CharacterAction(BaseDBModel):
    """Specific instance of a character action."""
    character_id: UUID
    template_id: Optional[UUID] = None
    name: str
    action_type: str
    description: str
    requirements_met: bool = True
    custom_effects: List[Dict] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict, sa_column=JSON)
