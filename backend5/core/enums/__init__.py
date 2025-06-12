"""
Core enumerations for the D&D Creative Content Framework.

This module provides all enumerated types used throughout the system,
organized by their primary purpose and domain.
"""

from .content_types import (
    ContentType,
    ContentRarity,
    ContentSource,
    EquipmentCategory,
    WeaponType,
    ArmorType,
    WeaponProperty,
    FeatCategory,
    SpeciesSize,
    BackstoryElement,
)

from .generation_methods import (
    GenerationMethod,
    LLMProvider,
    TemplateType,
    GenerationComplexity,
    IterationMethod,
)

from .validation_types import (
    ValidationType,
    ValidationSeverity,
    ValidationStatus,
    BalanceCategory,
    RuleCompliance,
)

from .dnd_constants import (
    Ability,
    Skill,
    ProficiencyLevel,
    DamageType,
    Condition,
    SpellcastingType,
    ClassResource,
    SubclassType,
    Currency,
    SpellLevel,
    CastingTime,
    SpellRange,
    SpellDuration,
    MagicSchool,
    AreaOfEffect,
    SkillCategory,
    DNDConstants,
)

from .mechanical_category import (
    MechanicalCategory,
)

__all__ = [
    # Content Types
    'ContentType',
    'ContentRarity',
    'ContentSource',
    'EquipmentCategory',
    'WeaponType',
    'ArmorType',
    'WeaponProperty',
    'FeatCategory',
    'SpeciesSize',
    'BackstoryElement',
    
    # Generation Methods
    'GenerationMethod',
    'LLMProvider',
    'TemplateType',
    'GenerationComplexity',
    'IterationMethod',
    
    # Validation Types
    'ValidationType',
    'ValidationSeverity',
    'ValidationStatus',
    'BalanceCategory',
    'RuleCompliance',
    
    # D&D Constants
    'Ability',
    'Skill',
    'ProficiencyLevel',
    'DamageType',
    'Condition',
    'SpellcastingType',
    'ClassResource',
    'SubclassType',
    'Currency',
    'SpellLevel',
    'CastingTime',
    'SpellRange',
    'SpellDuration',
    'MagicSchool',
    'AreaOfEffect',
    'SkillCategory',
    'DNDConstants',
    
    # Mechanical Analysis
    'MechanicalCategory',
]

# Enum Registry for dynamic loading
ENUM_REGISTRY = {
    # Content Types
    'content_type': ContentType,
    'content_rarity': ContentRarity,
    'content_source': ContentSource,
    'equipment_category': EquipmentCategory,
    'weapon_type': WeaponType,
    'armor_type': ArmorType,
    'weapon_property': WeaponProperty,
    'feat_category': FeatCategory,
    'species_size': SpeciesSize,
    'backstory_element': BackstoryElement,
    
    # Generation Methods
    'generation_method': GenerationMethod,
    'llm_provider': LLMProvider,
    'template_type': TemplateType,
    'generation_complexity': GenerationComplexity,
    'iteration_method': IterationMethod,
    
    # Validation Types
    'validation_type': ValidationType,
    'validation_severity': ValidationSeverity,
    'validation_status': ValidationStatus,
    'balance_category': BalanceCategory,
    'rule_compliance': RuleCompliance,
    
    # D&D Constants
    'ability': Ability,
    'skill': Skill,
    'proficiency_level': ProficiencyLevel,
    'damage_type': DamageType,
    'condition': Condition,
    'spellcasting_type': SpellcastingType,
    'class_resource': ClassResource,
    'subclass_type': SubclassType,
    'currency': Currency,
    'spell_level': SpellLevel,
    'casting_time': CastingTime,
    'spell_range': SpellRange,
    'spell_duration': SpellDuration,
    'magic_school': MagicSchool,
    'area_of_effect': AreaOfEffect,
    'skill_category': SkillCategory,
    
    # Mechanical Analysis
    'mechanical_category': MechanicalCategory,
}


def get_enum_class(enum_type: str):
    """
    Get enum class by type name.
    
    Args:
        enum_type: String identifier for the enum type
        
    Returns:
        Enum class or None if not found
    """
    return ENUM_REGISTRY.get(enum_type.lower())


def list_available_enums() -> list[str]:
    """
    Get list of all available enum types.
    
    Returns:
        List of enum type names
    """
    return list(ENUM_REGISTRY.keys())


def get_enums_by_category() -> dict[str, list[str]]:
    """
    Get enums organized by their functional category.
    
    Returns:
        Dictionary of categories with their enum types
    """
    return {
        "content_types": [
            "content_type", "content_rarity", "content_source", "equipment_category",
            "weapon_type", "armor_type", "weapon_property", "feat_category",
            "species_size", "backstory_element"
        ],
        "generation_methods": [
            "generation_method", "llm_provider", "template_type",
            "generation_complexity", "iteration_method"
        ],
        "validation_types": [
            "validation_type", "validation_severity", "validation_status",
            "balance_category", "rule_compliance"
        ],
        "dnd_constants": [
            "ability", "skill", "proficiency_level", "damage_type", "condition",
            "spellcasting_type", "class_resource", "subclass_type", "currency",
            "spell_level", "casting_time", "spell_range", "spell_duration",
            "magic_school", "area_of_effect", "skill_category"
        ],
        "mechanical_analysis": [
            "mechanical_category"
        ]
    }