"""
Pure utility functions for the D&D Creative Content Framework.

This module provides stateless, reusable functions for content processing,
validation, and analysis. These utilities support the framework's core
operations without depending on external state or services.
"""

from typing import Dict, List

# Balance Calculator
from .balance_calculator import (
    calculate_overall_balance_score,
    calculate_power_level_score,
    calculate_utility_score,
    calculate_versatility_score,
    calculate_scaling_score,
    calculate_damage_per_round,
    parse_average_damage,
    calculate_survivability_score,
    calculate_resource_efficiency,
    create_balance_metrics,
)

# Content Utils
from .content_utils import (
    extract_themes_from_content,
    merge_content_themes,
    filter_content_by_theme,
    calculate_thematic_compatibility,
    group_content_by_theme,
    analyze_content_complexity,
    find_content_dependencies,
    suggest_complementary_content,
    serialize_content_collection,
    deserialize_content_collection,
    validate_content_structure,
    normalize_content_data,
)

# Naming Validator
from .naming_validator import (
    validate_content_name,
    suggest_name_improvements,
    generate_name_variations,
    validate_name_uniqueness,
    check_name_authenticity,
)

# Mechanical Parser
from .mechanical_parser import (
    MechanicalElement,
    extract_mechanical_elements,
    parse_damage_expression,
    analyze_mechanical_complexity,
    extract_spell_components,
    extract_scaling_information,
    validate_mechanical_consistency,
    get_category_patterns,
    get_category_keywords,
    get_all_mechanical_keywords,
    categorize_keyword,
    find_mechanical_keywords_in_text,
)

# Rule Checker
from .rule_checker import (
    validate_ability_scores,
    validate_character_level,
    validate_proficiency_bonus,
    validate_hit_points,
    validate_armor_class,
    validate_saving_throws,
    validate_spell_slots,
    validate_content_rarity_balance,
    validate_multiclass_prerequisites,
    calculate_proficiency_bonus,
    calculate_ability_modifier,
    get_spell_slots_by_level,
)

__all__ = [
    # Balance Calculator
    'calculate_overall_balance_score',
    'calculate_power_level_score',
    'calculate_utility_score',
    'calculate_versatility_score',
    'calculate_scaling_score',
    'calculate_damage_per_round',
    'parse_average_damage',
    'calculate_survivability_score',
    'calculate_resource_efficiency',
    'create_balance_metrics',
    
    # Content Utils
    'extract_themes_from_content',
    'merge_content_themes',
    'filter_content_by_theme',
    'calculate_thematic_compatibility',
    'group_content_by_theme',
    'analyze_content_complexity',
    'find_content_dependencies',
    'suggest_complementary_content',
    'serialize_content_collection',
    'deserialize_content_collection',
    'validate_content_structure',
    'normalize_content_data',
    
    # Naming Validator
    'validate_content_name',
    'suggest_name_improvements',
    'generate_name_variations',
    'validate_name_uniqueness',
    'check_name_authenticity',
    
    # Mechanical Parser
    'MechanicalElement',
    'extract_mechanical_elements',
    'parse_damage_expression',
    'analyze_mechanical_complexity',
    'extract_spell_components',
    'extract_scaling_information',
    'validate_mechanical_consistency',
    'get_category_patterns',
    'get_category_keywords',
    'get_all_mechanical_keywords',
    'categorize_keyword',
    'find_mechanical_keywords_in_text',
    
    # Rule Checker
    'validate_ability_scores',
    'validate_character_level',
    'validate_proficiency_bonus',
    'validate_hit_points',
    'validate_armor_class',
    'validate_saving_throws',
    'validate_spell_slots',
    'validate_content_rarity_balance',
    'validate_multiclass_prerequisites',
    'calculate_proficiency_bonus',
    'calculate_ability_modifier',
    'get_spell_slots_by_level',
]

# Utility function registry for dynamic access
UTILITY_REGISTRY = {
    # Balance functions
    'balance_overall': calculate_overall_balance_score,
    'balance_power': calculate_power_level_score,
    'balance_utility': calculate_utility_score,
    'balance_versatility': calculate_versatility_score,
    'balance_scaling': calculate_scaling_score,
    'balance_damage_per_round': calculate_damage_per_round,
    'balance_survivability': calculate_survivability_score,
    'balance_resource_efficiency': calculate_resource_efficiency,
    
    # Content analysis
    'content_themes': extract_themes_from_content,
    'content_compatibility': calculate_thematic_compatibility,
    'content_complexity': analyze_content_complexity,
    'content_dependencies': find_content_dependencies,
    'content_validate_structure': validate_content_structure,
    'content_normalize': normalize_content_data,
    
    # Naming validation
    'naming_validate': validate_content_name,
    'naming_suggest': suggest_name_improvements,
    'naming_generate_variants': generate_name_variations,
    'naming_check_uniqueness': validate_name_uniqueness,
    'naming_check_authenticity': check_name_authenticity,
    
    # Mechanical parsing
    'mechanical_extract': extract_mechanical_elements,
    'mechanical_parse_damage': parse_damage_expression,
    'mechanical_complexity': analyze_mechanical_complexity,
    'mechanical_spell_components': extract_spell_components,
    'mechanical_scaling': extract_scaling_information,
    'mechanical_validate': validate_mechanical_consistency,
    
    # Rule validation
    'rules_ability_scores': validate_ability_scores,
    'rules_character_level': validate_character_level,
    'rules_hit_points': validate_hit_points,
    'rules_armor_class': validate_armor_class,
    'rules_saving_throws': validate_saving_throws,
    'rules_spell_slots': validate_spell_slots,
    'rules_rarity_balance': validate_content_rarity_balance,
    'rules_multiclass': validate_multiclass_prerequisites,
}


def get_utility_function(function_name: str):
    """
    Get utility function by name for dynamic access.
    
    Args:
        function_name: Name of the utility function
        
    Returns:
        Function object or None if not found
    """
    return UTILITY_REGISTRY.get(function_name)


def list_available_utilities() -> Dict[str, List[str]]:
    """
    Get organized list of available utility functions.
    
    Returns:
        Dictionary organized by utility category
    """
    return {
        "balance": [name for name in UTILITY_REGISTRY if name.startswith('balance_')],
        "content": [name for name in UTILITY_REGISTRY if name.startswith('content_')],
        "naming": [name for name in UTILITY_REGISTRY if name.startswith('naming_')],
        "mechanical": [name for name in UTILITY_REGISTRY if name.startswith('mechanical_')],
        "rules": [name for name in UTILITY_REGISTRY if name.startswith('rules_')]
    }


def get_utilities_by_category(category: str) -> List[str]:
    """
    Get utility functions for a specific category.
    
    Args:
        category: Category name (balance, content, naming, mechanical, rules)
        
    Returns:
        List of function names in that category
    """
    all_utilities = list_available_utilities()
    return all_utilities.get(category, [])


def validate_utility_availability() -> Dict[str, bool]:
    """
    Check which utility modules are available and working.
    
    Returns:
        Dictionary showing availability of each utility category
    """
    availability = {}
    
    try:
        from . import balance_calculator
        availability['balance_calculator'] = True
    except ImportError:
        availability['balance_calculator'] = False
    
    try:
        from . import content_utils
        availability['content_utils'] = True
    except ImportError:
        availability['content_utils'] = False
    
    try:
        from . import naming_validator
        availability['naming_validator'] = True
    except ImportError:
        availability['naming_validator'] = False
    
    try:
        from . import mechanical_parser
        availability['mechanical_parser'] = True
    except ImportError:
        availability['mechanical_parser'] = False
    
    try:
        from . import rule_checker
        availability['rule_checker'] = True
    except ImportError:
        availability['rule_checker'] = False
    
    return availability