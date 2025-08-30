"""Rules models for the character service.

This module provides models for game rules, including core rules,
optional rules, and house rules.
"""

from typing import Dict, List, Optional
from uuid import UUID

from pydantic import Field
from sqlmodel import JSON

from .base import BaseDBModel, BaseVersionedDBModel

class Rule(BaseDBModel):
    """Base model for game rules."""
    name: str
    description: str
    type: str  # core, optional, house
    category: str  # combat, spellcasting, etc.
    source: str
    enabled: bool = True
    priority: int = 0
    overrides: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict, sa_column=JSON)

class CombatRule(Rule):
    """Combat-specific rules."""
    affects: List[str] = Field(default_factory=list)  # attack, damage, initiative, etc.
    modifiers: Dict = Field(default_factory=dict, sa_column=JSON)
    conditions: List[Dict] = Field(default_factory=list)
    exceptions: List[Dict] = Field(default_factory=list)

class SpellcastingRule(Rule):
    """Spellcasting-specific rules."""
    spell_types: List[str] = Field(default_factory=list)
    components_affected: List[str] = Field(default_factory=list)
    modifiers: Dict = Field(default_factory=dict, sa_column=JSON)
    restrictions: List[Dict] = Field(default_factory=list)

class AbilityCheckRule(Rule):
    """Rules for ability checks and saving throws."""
    abilities_affected: List[str] = Field(default_factory=list)
    skills_affected: List[str] = Field(default_factory=list)
    modifiers: Dict = Field(default_factory=dict, sa_column=JSON)
    circumstances: List[Dict] = Field(default_factory=list)

class RestRule(Rule):
    """Rules for short and long rests."""
    rest_type: str  # short, long
    duration: str
    activities_allowed: List[str] = Field(default_factory=list)
    healing: Dict = Field(default_factory=dict, sa_column=JSON)
    resource_recovery: Dict = Field(default_factory=dict, sa_column=JSON)

class MovementRule(Rule):
    """Rules for movement and positioning."""
    movement_types: List[str] = Field(default_factory=list)
    terrain_effects: Dict = Field(default_factory=dict, sa_column=JSON)
    special_rules: List[Dict] = Field(default_factory=list)

class EquipmentRule(Rule):
    """Rules for equipment and items."""
    item_types: List[str] = Field(default_factory=list)
    usage_rules: Dict = Field(default_factory=dict, sa_column=JSON)
    restrictions: List[Dict] = Field(default_factory=list)

class CharacterCreationRule(Rule):
    """Rules for character creation."""
    affects: List[str] = Field(default_factory=list)  # abilities, race, class, etc.
    options_allowed: Dict = Field(default_factory=dict, sa_column=JSON)
    restrictions: List[Dict] = Field(default_factory=list)
    homebrew_guidelines: Optional[Dict] = None

class RuleSet(BaseVersionedDBModel):
    """Collection of game rules."""
    name: str
    description: str
    owner_id: UUID
    campaign_id: Optional[UUID] = None
    type: str  # standard, variant, house
    base_ruleset: Optional[str] = None
    
    # Core Rules
    combat_rules: List[CombatRule] = Field(default_factory=list)
    spellcasting_rules: List[SpellcastingRule] = Field(default_factory=list)
    ability_check_rules: List[AbilityCheckRule] = Field(default_factory=list)
    rest_rules: List[RestRule] = Field(default_factory=list)
    movement_rules: List[MovementRule] = Field(default_factory=list)
    equipment_rules: List[EquipmentRule] = Field(default_factory=list)
    character_creation_rules: List[CharacterCreationRule] = Field(default_factory=list)
    
    # Custom Rules
    custom_rules: List[Rule] = Field(default_factory=list)
    house_rules: Dict[str, List[Rule]] = Field(default_factory=dict)
    variant_rules: Dict[str, List[Rule]] = Field(default_factory=dict)
    
    # Rule Management
    enabled_rules: List[str] = Field(default_factory=list)
    disabled_rules: List[str] = Field(default_factory=list)
    rule_overrides: Dict[str, Dict] = Field(default_factory=dict)
    
    # Validation and Compatibility
    validated: bool = False
    validation_errors: List[str] = Field(default_factory=list)
    compatibility_warnings: List[str] = Field(default_factory=list)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    source_materials: List[str] = Field(default_factory=list)
    notes: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict = Field(default_factory=dict, sa_column=JSON)
