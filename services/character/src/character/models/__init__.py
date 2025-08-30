"""Models for the character service.

This package provides all the models used in the character service.
"""

from .base import (
    APIResponse,
    AuditMixin,
    BaseDBModel, 
    BaseVersionedDBModel,
    PaginatedResponse,
    Status,
    VersionMixin,
)

from .character import (
    Ability,
    Armor,
    Background,
    Character,
    CharacterAction,
    CharacterActionTemplate,
    ClassLevel,
    Equipment,
    Feature,
    Language,
    Race,
    Skill,
    Tool,
    Weapon,
)

from .custom_content import (
    ContentCategory,
    ContentRating,
    CustomContent,
)

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
    Rarity,
    Size,
    VisionType,
    WeaponType,
)

from .journal import (
    CampaignJournal,
    CharacterJournal,
    JournalEntry,
)

from .rules import (
    AbilityCheckRule,
    CharacterCreationRule,
    CombatRule,
    EquipmentRule,
    MovementRule,
    RestRule,
    Rule,
    RuleSet,
    SpellcastingRule,
)

from .spellcasting import (
    CharacterSpellcasting,
    Spell,
    SpellArea,
    SpellcastingAbility,
    SpellcastingChange,
    SpellcastingClass,
    SpellComponent,
    SpellDuration,
    SpellRange,
    SpellSchool,
    SpellType,
)

__all__ = [
    # Base models
    "APIResponse",
    "AuditMixin",
    "BaseDBModel", 
    "BaseVersionedDBModel",
    "PaginatedResponse",
    "Status",
    "VersionMixin",

    # Character models
    "Ability",
    "Armor",
    "Background",
    "Character",
    "CharacterAction",
    "CharacterActionTemplate", 
    "ClassLevel",
    "Equipment",
    "Feature",
    "Language",
    "Race",
    "Skill",
    "Tool",
    "Weapon",

    # Custom content models
    "ContentCategory",
    "ContentRating",
    "CustomContent",

    # Enums
    "AbilityType",
    "AlignmentEthical",
    "AlignmentMoral", 
    "ArmorType",
    "Condition",
    "DamageType",
    "FeatureCategory",
    "FeatureType",
    "FeatureUsage",
    "MovementType",
    "ProficiencyLevel",
    "Rarity",
    "Size",
    "VisionType",
    "WeaponType",

    # Journal models
    "CampaignJournal",
    "CharacterJournal",
    "JournalEntry",

    # Rules models
    "AbilityCheckRule",
    "CharacterCreationRule",
    "CombatRule",
    "EquipmentRule", 
    "MovementRule",
    "RestRule",
    "Rule",
    "RuleSet",
    "SpellcastingRule",

    # Spellcasting models
    "CharacterSpellcasting",
    "Spell",
    "SpellArea",
    "SpellcastingAbility",
    "SpellcastingChange",
    "SpellcastingClass",
    "SpellComponent", 
    "SpellDuration",
    "SpellRange",
    "SpellSchool",
    "SpellType",
]
