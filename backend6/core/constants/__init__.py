"""
Core Constants for the D&D Creative Content Framework.

This module provides all constant values used throughout the system,
organized by their domain purpose according to Clean Architecture principles.
"""

# Balance and Power Level Constants
from .balance_thresholds import (
    DAMAGE_THRESHOLDS,
    ARMOR_CLASS_THRESHOLDS,
    HIT_POINT_THRESHOLDS,
    MECHANICAL_LIMITS,
    POWER_SCALING_FACTORS,
    POWER_BUDGET_BY_TIER,
    FEATURE_BASE_COSTS,
    REVIEW_THRESHOLDS,
    BALANCE_TOLERANCE,
    OFFICIAL_CONTENT_BENCHMARKS,
    get_power_threshold,
    calculate_feature_cost,
    is_within_balance_threshold
)

# D&D Core Mechanics Constants
from .dnd_mechanics import (
    ABILITY_SCORES,
    ABILITY_SCORE_RANGES,
    SKILLS_BY_ABILITY,
    ALL_SKILLS,
    SKILL_TO_ABILITY,
    SPELL_SCHOOLS,
    SPELL_LEVELS,
    DAMAGE_TYPES,
    CONDITIONS,
    WEAPON_PROPERTIES,
    CREATURE_SIZES,
    CURRENCY_CONVERSION,
    MULTICLASS_REQUIREMENTS,
    PROFICIENCY_BONUS_BY_LEVEL,
    POWER_TIERS,
    get_ability_modifier,
    is_valid_ability_score,
    get_proficiency_bonus,
    convert_currency,
    get_power_tier
)

# Character Progression Constants
from .progression import (
    LEVEL_RANGES,
    PROGRESSION_BREAKPOINTS,
    SCALING_PATTERNS,
    CANTRIP_DAMAGE_SCALING,
    THEMATIC_MILESTONES,
    POWER_PROGRESSION_CURVE,
    CUSTOMIZATION_BUDGET_BY_LEVEL,
    SIGNATURE_FEATURE_TIMING,
    get_cantrip_dice_count,
    get_expected_power_level,
    get_tier_from_level,
    calculate_multiclass_caster_level
)

# Content Generation Limits
from .generation_limits import (
    GENERATION_SESSION_LIMITS,
    CREATIVITY_LEVEL_LIMITS,
    COMPLEXITY_LIMITS,
    ABSOLUTE_POWER_LIMITS,
    CONTENT_DISTRIBUTION_REQUIREMENTS,
    THEMATIC_DEVIATION_LIMITS,
    NAMING_LIMITS,
    TIME_LIMITS,
    RESOURCE_LIMITS,
    get_generation_limit,
    get_complexity_limit,
    get_time_limit
)

# Export all public constants organized by architectural concern
__all__ = [
    # ============ BALANCE AND VALIDATION CONSTANTS ============
    'DAMAGE_THRESHOLDS',
    'ARMOR_CLASS_THRESHOLDS', 
    'HIT_POINT_THRESHOLDS',
    'MECHANICAL_LIMITS',
    'POWER_SCALING_FACTORS',
    'POWER_BUDGET_BY_TIER',
    'FEATURE_BASE_COSTS',
    'REVIEW_THRESHOLDS',
    'BALANCE_TOLERANCE',
    'OFFICIAL_CONTENT_BENCHMARKS',
    
    # ============ D&D CORE MECHANICS CONSTANTS ============
    'ABILITY_SCORES',
    'ABILITY_SCORE_RANGES',
    'SKILLS_BY_ABILITY',
    'ALL_SKILLS',
    'SKILL_TO_ABILITY',
    'SPELL_SCHOOLS',
    'SPELL_LEVELS',
    'DAMAGE_TYPES',
    'CONDITIONS',
    'WEAPON_PROPERTIES',
    'CREATURE_SIZES',
    'CURRENCY_CONVERSION',
    'MULTICLASS_REQUIREMENTS',
    'PROFICIENCY_BONUS_BY_LEVEL',
    'POWER_TIERS',
    
    # ============ CHARACTER PROGRESSION CONSTANTS ============
    'LEVEL_RANGES',
    'PROGRESSION_BREAKPOINTS',
    'SCALING_PATTERNS',
    'CANTRIP_DAMAGE_SCALING',
    'THEMATIC_MILESTONES',
    'POWER_PROGRESSION_CURVE',
    'CUSTOMIZATION_BUDGET_BY_LEVEL',
    'SIGNATURE_FEATURE_TIMING',
    
    # ============ GENERATION LIMITS CONSTANTS ============
    'GENERATION_SESSION_LIMITS',
    'CREATIVITY_LEVEL_LIMITS',
    'COMPLEXITY_LIMITS',
    'ABSOLUTE_POWER_LIMITS',
    'CONTENT_DISTRIBUTION_REQUIREMENTS',
    'THEMATIC_DEVIATION_LIMITS',
    'NAMING_LIMITS',
    'TIME_LIMITS',
    'RESOURCE_LIMITS',
    
    # ============ UTILITY FUNCTIONS ============
    'get_ability_modifier',
    'is_valid_ability_score',
    'get_proficiency_bonus',
    'convert_currency',
    'get_power_tier',
    'get_cantrip_dice_count',
    'get_expected_power_level',
    'get_tier_from_level',
    'calculate_multiclass_caster_level',
    'get_power_threshold',
    'calculate_feature_cost',
    'is_within_balance_threshold',
    'get_generation_limit',
    'get_complexity_limit',
    'get_time_limit',
]

# Constant registry organized by Clean Architecture concerns
CONSTANT_REGISTRY = {
    # ============ CORE LAYER CONSTANTS ============
    'core_mechanics': {
        'abilities': ABILITY_SCORES,
        'skills': ALL_SKILLS,
        'damage_types': DAMAGE_TYPES,
        'conditions': CONDITIONS,
        'spell_schools': SPELL_SCHOOLS,
        'power_tiers': POWER_TIERS
    },
    
    # ============ DOMAIN LAYER CONSTANTS ============
    'balance_validation': {
        'damage_thresholds': DAMAGE_THRESHOLDS,
        'mechanical_limits': MECHANICAL_LIMITS,
        'power_scaling': POWER_SCALING_FACTORS,
        'balance_tolerance': BALANCE_TOLERANCE
    },
    'character_progression': {
        'level_ranges': LEVEL_RANGES,
        'progression_breakpoints': PROGRESSION_BREAKPOINTS,
        'thematic_milestones': THEMATIC_MILESTONES,
        'power_curve': POWER_PROGRESSION_CURVE
    },
    
    # ============ APPLICATION LAYER CONSTANTS ============
    'generation_constraints': {
        'session_limits': GENERATION_SESSION_LIMITS,
        'complexity_limits': COMPLEXITY_LIMITS,
        'time_limits': TIME_LIMITS,
        'resource_limits': RESOURCE_LIMITS
    }
}

def get_constants_by_category(category: str) -> dict:
    """
    Get constants for a specific category.
    
    Args:
        category: Category name (core_mechanics, balance_validation, etc.)
        
    Returns:
        Dictionary of constants for the category
    """
    return CONSTANT_REGISTRY.get(category, {})

def get_all_constant_categories() -> list[str]:
    """Get list of all available constant categories."""
    return list(CONSTANT_REGISTRY.keys())

def search_constants(search_term: str) -> dict[str, dict]:
    """
    Search for constants containing a specific term.
    
    Args:
        search_term: Term to search for
        
    Returns:
        Dictionary of matching constants by category
    """
    results = {}
    search_lower = search_term.lower()
    
    for category, constants in CONSTANT_REGISTRY.items():
        matching_constants = {}
        for const_name, const_value in constants.items():
            if search_lower in const_name.lower():
                matching_constants[const_name] = const_value
        
        if matching_constants:
            results[category] = matching_constants
    
    return results

def validate_constant_integrity() -> list[str]:
    """
    Validate that all constants are properly defined and consistent.
    
    Returns:
        List of validation issues (empty if all constants are valid)
    """
    issues = []
    
    # Check that core mechanics constants are present
    required_core = ['abilities', 'skills', 'damage_types']
    for req in required_core:
        if req not in CONSTANT_REGISTRY.get('core_mechanics', {}):
            issues.append(f"Missing required core mechanic constant: {req}")
    
    # Check that balance constants are reasonable
    if 'balance_validation' in CONSTANT_REGISTRY:
        balance_constants = CONSTANT_REGISTRY['balance_validation']
        if 'balance_tolerance' in balance_constants:
            for mode, tolerance in balance_constants['balance_tolerance'].items():
                if not isinstance(tolerance, (int, float)) or tolerance < 0 or tolerance > 1:
                    issues.append(f"Invalid balance tolerance for {mode}: {tolerance}")
    
    return issues

# Module metadata
__version__ = '1.0.0'  
__description__ = 'Clean Architecture constants for D&D Creative Content Framework'

# Validate constants on import
_VALIDATION_ISSUES = validate_constant_integrity()
if _VALIDATION_ISSUES:
    import warnings
    warnings.warn(f"Constant validation issues found: {_VALIDATION_ISSUES}")