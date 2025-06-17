"""
Essential D&D 5e/2024 Constants Package

Streamlined constants package following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
"""

# Import all essential constants and functions
from .dnd_mechanics import (
    # Core mechanics
    ABILITY_SCORES,
    ABILITY_SCORE_RANGES,
    SKILLS_BY_ABILITY,
    ALL_SKILLS,
    SKILL_TO_ABILITY,
    PROFICIENCY_BONUS_BY_LEVEL,
    
    # Magic system
    SPELL_SCHOOLS,
    SPELL_LEVELS,
    CANTRIP_DAMAGE_SCALING,
    
    # Combat and conditions
    DAMAGE_TYPES,
    CONDITIONS,
    WEAPON_PROPERTIES,
    
    # Character progression
    LEVEL_RANGES,
    POWER_TIERS,
    MULTICLASS_REQUIREMENTS,
    
    # World elements
    CURRENCY_CONVERSION,
    ALL_LANGUAGES,
    CREATURE_SIZES,
    
    # Utility functions
    get_ability_modifier,
    is_valid_ability_score,
    get_proficiency_bonus,
    get_cantrip_dice_count,
    get_power_tier,
    convert_currency,
    validate_character_level,
    calculate_ability_modifier,
    calculate_proficiency_bonus,
)

from .character_limits import (
    # Limits constants
    ABILITY_SCORE_LIMITS,
    ABILITY_SCORE_METHODS,
    LEVEL_LIMITS,
    PROFICIENCY_BONUS_LIMITS,
    SKILL_PROFICIENCY_LIMITS,
    LANGUAGE_LIMITS,
    HIT_POINT_LIMITS,
    ARMOR_CLASS_LIMITS,
    ATTACK_BONUS_LIMITS,
    SPELL_LIMITS,
    SPELL_SLOT_LIMITS,
    EQUIPMENT_LIMITS,
    MAGIC_ITEM_LIMITS,
    MULTICLASS_LIMITS,
    FEAT_LIMITS,
    ASI_LIMITS,
    
    # Validation functions
    validate_ability_scores,
    calculate_point_buy_cost,
    validate_point_buy_array,
    get_proficiency_bonus_for_level,
    validate_multiclass_requirements,
)

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Core D&D mechanics
    'ABILITY_SCORES',
    'ABILITY_SCORE_RANGES',
    'SKILLS_BY_ABILITY',
    'ALL_SKILLS',
    'SKILL_TO_ABILITY',
    'PROFICIENCY_BONUS_BY_LEVEL',
    'SPELL_SCHOOLS',
    'SPELL_LEVELS',
    'CANTRIP_DAMAGE_SCALING',
    'DAMAGE_TYPES',
    'CONDITIONS',
    'WEAPON_PROPERTIES',
    'LEVEL_RANGES',
    'POWER_TIERS',
    'MULTICLASS_REQUIREMENTS',
    'CURRENCY_CONVERSION',
    'ALL_LANGUAGES',
    'CREATURE_SIZES',
    
    # Character creation limits
    'ABILITY_SCORE_LIMITS',
    'ABILITY_SCORE_METHODS',
    'LEVEL_LIMITS',
    'PROFICIENCY_BONUS_LIMITS',
    'SKILL_PROFICIENCY_LIMITS',
    'LANGUAGE_LIMITS',
    'HIT_POINT_LIMITS',
    'ARMOR_CLASS_LIMITS',
    'ATTACK_BONUS_LIMITS',
    'SPELL_LIMITS',
    'SPELL_SLOT_LIMITS',
    'EQUIPMENT_LIMITS',
    'MAGIC_ITEM_LIMITS',
    'MULTICLASS_LIMITS',
    'FEAT_LIMITS',
    'ASI_LIMITS',
    
    # Utility functions
    'get_ability_modifier',
    'is_valid_ability_score',
    'get_proficiency_bonus',
    'get_cantrip_dice_count',
    'get_power_tier',
    'convert_currency',
    'validate_character_level',
    'calculate_ability_modifier',
    'calculate_proficiency_bonus',
    'validate_ability_scores',
    'calculate_point_buy_cost',
    'validate_point_buy_array',
    'get_proficiency_bonus_for_level',
    'validate_multiclass_requirements',
]

# ============ CONVENIENCE IMPORTS ============

# Most commonly used constants grouped for easy access
CORE_CONSTANTS = {
    'abilities': ABILITY_SCORES,
    'skills': ALL_SKILLS,
    'spell_schools': SPELL_SCHOOLS,
    'damage_types': DAMAGE_TYPES,
    'conditions': CONDITIONS,
    'languages': ALL_LANGUAGES,
}

VALIDATION_FUNCTIONS = {
    'ability_modifier': get_ability_modifier,
    'proficiency_bonus': get_proficiency_bonus,
    'validate_level': validate_character_level,
    'validate_abilities': validate_ability_scores,
    'point_buy_cost': calculate_point_buy_cost,
}

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D 5e/2024 constants package'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/constants",
    "purpose": "unified_constants_access",
    "exports": "essential_dnd_mechanics_and_limits",
    "dependencies": ["dnd_mechanics", "character_limits"],
    "philosophy": "crude_functional_inspired_simplicity"
}