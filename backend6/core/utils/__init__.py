"""
Core Utilities for D&D Character Creation.

SIMPLIFIED VERSION: Essential D&D mechanics with minimal culture support
that enhances character creation without overwhelming complexity.

This module provides simple, reusable functions for character creation,
validation, and basic text processing. Culture features are supportive only.

Philosophy:
- Character creation comes first
- Culture enhances but never restricts
- Simple, supportive features only
- Creative freedom is paramount
"""

from typing import Dict, List, Optional, Any, Union

# ============================================================================
# ESSENTIAL D&D UTILITY IMPORTS
# ============================================================================

# Balance Calculator
from .balance_calculator import (
    calculate_overall_balance_score,
    calculate_power_level_score,
    calculate_utility_score,
    calculate_damage_per_round,
    create_balance_metrics,
)

# Content Utils
from .content_utils import (
    extract_themes_from_content,
    merge_content_themes,
    calculate_thematic_compatibility,
    analyze_content_complexity,
    normalize_content_data,
)

# Naming Validator
from .naming_validator import (
    validate_content_name,
    suggest_name_improvements,
    validate_name_uniqueness,
)

# Mechanical Parser
from .mechanical_parser import (
    MechanicalElement,
    extract_mechanical_elements,
    parse_damage_expression,
    analyze_mechanical_complexity,
)

# Rule Checker
from .rule_checker import (
    validate_ability_scores,
    validate_character_level,
    validate_proficiency_bonus,
    calculate_proficiency_bonus,
    calculate_ability_modifier,
)

# ============================================================================
# SIMPLIFIED CULTURE UTILITIES - Character Creation Focus
# ============================================================================

# Simple Culture Parser
from .culture_parser import (
    SimpleCultureParser,
    parse_culture_response,
    extract_character_names,
)

# Simple Culture Validator  
from .culture_validator import (
    SimpleCultureValidator,
    validate_culture_for_characters,
    quick_culture_assessment,
)

# Simple Text Processing
from .text_processing import (
    format_text_for_character,
    clean_text_for_character_sheet,
    get_pronunciation_hint,
)

# ============================================================================
# SIMPLIFIED EXPORTS - Only What Actually Exists
# ============================================================================

__all__ = [
    # Essential D&D utilities
    'calculate_overall_balance_score',
    'calculate_power_level_score',
    'calculate_utility_score',
    'calculate_damage_per_round',
    'create_balance_metrics',
    
    'extract_themes_from_content',
    'merge_content_themes',
    'calculate_thematic_compatibility',
    'analyze_content_complexity',
    'normalize_content_data',
    
    'validate_content_name',
    'suggest_name_improvements',
    'validate_name_uniqueness',
    
    'MechanicalElement',
    'extract_mechanical_elements',
    'parse_damage_expression',
    'analyze_mechanical_complexity',
    
    'validate_ability_scores',
    'validate_character_level',
    'validate_proficiency_bonus',
    'calculate_proficiency_bonus',
    'calculate_ability_modifier',
    
    # Simple culture utilities (character creation focus)
    'SimpleCultureParser',
    'parse_culture_response',
    'extract_character_names',
    
    'SimpleCultureValidator',
    'validate_culture_for_characters',
    'quick_culture_assessment',
    
    'format_text_for_character',
    'clean_text_for_character_sheet',
    'get_pronunciation_hint',
]

# ============================================================================
# SIMPLIFIED UTILITY REGISTRY
# ============================================================================

UTILITY_REGISTRY = {
    # Balance functions
    'balance_overall': calculate_overall_balance_score,
    'balance_power': calculate_power_level_score,
    'balance_utility': calculate_utility_score,
    'balance_damage_per_round': calculate_damage_per_round,
    
    # Content analysis
    'content_themes': extract_themes_from_content,
    'content_compatibility': calculate_thematic_compatibility,
    'content_complexity': analyze_content_complexity,
    'content_normalize': normalize_content_data,
    
    # Naming validation
    'naming_validate': validate_content_name,
    'naming_suggest': suggest_name_improvements,
    'naming_check_uniqueness': validate_name_uniqueness,
    
    # Mechanical parsing  
    'mechanical_extract': extract_mechanical_elements,
    'mechanical_parse_damage': parse_damage_expression,
    'mechanical_complexity': analyze_mechanical_complexity,
    
    # Rule validation
    'rules_ability_scores': validate_ability_scores,
    'rules_character_level': validate_character_level,
    'rules_proficiency_bonus': validate_proficiency_bonus,
    
    # Simple culture utilities (character creation focus)
    'culture_parse_response': parse_culture_response,
    'culture_extract_names': extract_character_names,
    'culture_validate_for_characters': validate_culture_for_characters,
    'culture_quick_assessment': quick_culture_assessment,
    
    # Simple text processing
    'text_format_for_character': format_text_for_character,
    'text_clean_for_sheet': clean_text_for_character_sheet,
    'text_pronunciation_hint': get_pronunciation_hint,
}

# ============================================================================
# SIMPLIFIED UTILITY ACCESS FUNCTIONS
# ============================================================================

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
    Get organized list of utility functions.
    
    Returns:
        Dictionary organized by utility category
    """
    return {
        "balance": [name for name in UTILITY_REGISTRY if name.startswith('balance_')],
        "content": [name for name in UTILITY_REGISTRY if name.startswith('content_')],
        "naming": [name for name in UTILITY_REGISTRY if name.startswith('naming_')],
        "mechanical": [name for name in UTILITY_REGISTRY if name.startswith('mechanical_')],
        "rules": [name for name in UTILITY_REGISTRY if name.startswith('rules_')],
        "simple_culture": [name for name in UTILITY_REGISTRY if name.startswith('culture_')],
        "text_processing": [name for name in UTILITY_REGISTRY if name.startswith('text_')]
    }


def get_utilities_by_category(category: str) -> List[str]:
    """
    Get utility functions for a specific category.
    
    Args:
        category: Category name (balance, content, naming, mechanical, rules, simple_culture, text_processing)
        
    Returns:
        List of function names in that category
    """
    all_utilities = list_available_utilities()
    return all_utilities.get(category, [])


def validate_utility_availability() -> Dict[str, Any]:
    """
    Simple validation of utility module availability.
    
    Returns:
        Dictionary showing availability of each utility category
    """
    availability = {}
    
    # Check essential D&D utilities
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
    
    # Check simple culture utilities
    try:
        from . import culture_parser
        availability['culture_parser'] = True
    except ImportError:
        availability['culture_parser'] = False
    
    try:
        from . import culture_validator
        availability['culture_validator'] = True
    except ImportError:
        availability['culture_validator'] = False
    
    try:
        from . import text_processing
        availability['text_processing'] = True
    except ImportError:
        availability['text_processing'] = False
    
    return availability


# ============================================================================
# SIMPLE CULTURE FEATURES
# ============================================================================

def get_simple_culture_features() -> Dict[str, Any]:
    """Get available simple culture features."""
    features = {
        "character_name_extraction": False,
        "culture_parsing": False,
        "simple_validation": False,
        "text_processing": False
    }
    
    availability = validate_utility_availability()
    
    if availability.get('culture_parser', False):
        features["culture_parsing"] = True
        features["character_name_extraction"] = True
    
    if availability.get('culture_validator', False):
        features["simple_validation"] = True
    
    if availability.get('text_processing', False):
        features["text_processing"] = True
    
    return {
        "available_features": features,
        "philosophy": "Culture enhances but never restricts character creation",
        "approach": "simple_supportive_only"
    }


def get_essential_d3d_features() -> Dict[str, Any]:
    """Get available essential D&D features."""
    features = {
        "rule_validation": False,
        "balance_calculation": False,
        "mechanical_parsing": False,
        "ability_scores": False,
        "content_analysis": False,
        "naming_validation": False
    }
    
    availability = validate_utility_availability()
    
    if availability.get('rule_checker', False):
        features["rule_validation"] = True
        features["ability_scores"] = True
    
    if availability.get('balance_calculator', False):
        features["balance_calculation"] = True
    
    if availability.get('mechanical_parser', False):
        features["mechanical_parsing"] = True
    
    if availability.get('content_utils', False):
        features["content_analysis"] = True
    
    if availability.get('naming_validator', False):
        features["naming_validation"] = True
    
    return {
        "available_features": features,
        "focus": "essential_d3d_mechanics_only"
    }


# ============================================================================
# SIMPLE CHARACTER CREATION HELPERS
# ============================================================================

def create_character_culture_simple(cultural_concept: str) -> Dict[str, Any]:
    """
    Simple function for creating character-ready cultures.
    
    Args:
        cultural_concept: Any description of desired culture
        
    Returns:
        Dictionary with simple culture data for character creation
    """
    try:
        # Use simple culture parser if available
        if 'culture_parse_response' in UTILITY_REGISTRY:
            parser = UTILITY_REGISTRY['culture_parse_response']
            return parser(cultural_concept)
        else:
            # Fallback - just return the concept as basic culture
            return {
                'name': cultural_concept,
                'description': f"Culture based on: {cultural_concept}",
                'male_names': [],
                'female_names': [],
                'family_names': [],
                'character_ready': True,
                'simple_culture': True
            }
    except Exception:
        # Always return something usable
        return {
            'name': cultural_concept,
            'description': f"Simple culture: {cultural_concept}",
            'character_ready': True,
            'simple_culture': True,
            'fallback': True
        }


def validate_culture_simple(culture_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple culture validation for character creation.
    
    Args:
        culture_data: Culture data to validate
        
    Returns:
        Dictionary with simple validation results
    """
    try:
        # Use simple validator if available
        if 'culture_validate_for_characters' in UTILITY_REGISTRY:
            validator = UTILITY_REGISTRY['culture_validate_for_characters']
            result = validator(culture_data)
            return {
                'is_usable': result.is_usable,
                'character_ready': result.character_ready,
                'suggestions': result.helpful_suggestions,
                'score': result.overall_score
            }
        else:
            # Fallback - always say it's usable
            return {
                'is_usable': True,
                'character_ready': True,
                'suggestions': ["Culture features are optional - continue with character creation"],
                'score': 0.5
            }
    except Exception:
        # Always return something positive
        return {
            'is_usable': True,
            'character_ready': True,
            'suggestions': ["Culture validation had issues, but character creation can continue"],
            'score': 0.3
        }


def extract_names_simple(text: str) -> List[str]:
    """
    Simple name extraction from any text.
    
    Args:
        text: Text to extract names from
        
    Returns:
        List of potential character names
    """
    try:
        # Use name extractor if available
        if 'culture_extract_names' in UTILITY_REGISTRY:
            extractor = UTILITY_REGISTRY['culture_extract_names']
            return extractor(text)
        else:
            # Fallback - basic name extraction
            import re
            # Look for capitalized words that could be names
            words = re.findall(r'\b[A-Z][a-z]+\b', text)
            # Filter out common non-names
            exclude = {'The', 'And', 'Or', 'But', 'In', 'On', 'At', 'To', 'For', 'Of', 'With', 'By'}
            return [word for word in words if word not in exclude][:10]  # Limit to 10
    except Exception:
        return []


# ============================================================================
# SIMPLIFIED MODULE INFORMATION
# ============================================================================

def get_utility_info() -> Dict[str, Any]:
    """Get information about available utilities."""
    availability = validate_utility_availability()
    culture_features = get_simple_culture_features()
    d3d_features = get_essential_d3d_features()
    
    return {
        "total_utilities": len(UTILITY_REGISTRY),
        "available_modules": {k: v for k, v in availability.items() if v},
        "missing_modules": {k: v for k, v in availability.items() if not v},
        "culture_support": culture_features,
        "d3d_support": d3d_features,
        "philosophy": "Culture enhances but never restricts character creation",
        "approach": "simple_essential_only"
    }


def validate_all_utilities() -> Dict[str, Any]:
    """
    Simple validation of all utility systems.
    
    Returns:
        Dictionary with utility system health check
    """
    availability = validate_utility_availability()
    
    # Calculate system health
    available_count = sum(1 for v in availability.values() if v)
    total_count = len(availability)
    system_health = available_count / total_count if total_count > 0 else 0
    
    # Check character creation readiness
    essential_modules = ['rule_checker', 'balance_calculator', 'mechanical_parser']
    culture_modules = ['culture_parser', 'culture_validator', 'text_processing']
    
    essential_ready = sum(1 for mod in essential_modules if availability.get(mod, False))
    culture_ready = sum(1 for mod in culture_modules if availability.get(mod, False))
    
    return {
        'system_health_score': system_health,
        'available_modules': available_count,
        'total_modules': total_count,
        'essential_d3d_ready': essential_ready >= 2,  # At least 2 of 3 essential
        'simple_culture_ready': culture_ready >= 1,   # At least 1 culture utility
        'character_creation_ready': essential_ready >= 1,  # At least 1 essential utility
        'utility_registry_size': len(UTILITY_REGISTRY),
        'recommendations': [
            "Focus on essential D&D mechanics first",
            "Keep culture features simple and supportive", 
            "Prioritize character creation workflow"
        ]
    }


# Add helper functions to exports and registry
__all__.extend([
    'get_utility_function',
    'list_available_utilities', 
    'get_utilities_by_category',
    'validate_utility_availability',
    'get_simple_culture_features',
    'get_essential_d3d_features',
    'create_character_culture_simple',
    'validate_culture_simple',
    'extract_names_simple',
    'get_utility_info',
    'validate_all_utilities'
])

UTILITY_REGISTRY.update({
    'helper_create_culture_simple': create_character_culture_simple,
    'helper_validate_culture_simple': validate_culture_simple,
    'helper_extract_names_simple': extract_names_simple
})

# ============================================================================
# SIMPLIFIED MODULE METADATA
# ============================================================================

__version__ = "1.0.0"
__description__ = "Simplified Core Utilities for D&D Character Creation - Culture Enhances, Never Restricts"

# Simple configuration
ENABLE_CULTURE_FEATURES = True  # But keep them simple
CULTURE_PHILOSOPHY = "enhance_not_restrict"
CHARACTER_CREATION_FIRST = True

# Feature flags
FEATURES = {
    "essential_d3d_mechanics": True,
    "simple_culture_parsing": True,
    "simple_culture_validation": True,
    "character_focused_text_processing": True,
    "balance_calculation": True,
    "content_analysis": True,
    "naming_validation": True,
    "mechanical_parsing": True,
    "rule_validation": True
}

def get_feature_status() -> Dict[str, bool]:
    """Get status of all features."""
    return FEATURES.copy()

def is_culture_support_available() -> bool:
    """Check if simple culture support is available."""
    availability = validate_utility_availability()
    return availability.get('culture_parser', False) or availability.get('culture_validator', False)

def is_d3d_mechanics_available() -> bool:
    """Check if essential D&D mechanics are available."""
    availability = validate_utility_availability()
    return availability.get('rule_checker', False) or availability.get('balance_calculator', False)

# Add feature functions to exports
__all__.extend(['get_feature_status', 'is_culture_support_available', 'is_d3d_mechanics_available'])

# ============================================================================
# SIMPLIFIED MODULE MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("D&D Character Creator - Simplified Core Utilities")
    print("Essential D&D + Simple Culture Support")
    print("=" * 60)
    
    validation = validate_all_utilities()
    print(f"Total Utilities Available: {validation['utility_registry_size']}")
    print(f"Available Modules: {validation['available_modules']}/{validation['total_modules']}")
    print(f"System Health Score: {validation['system_health_score']:.1%}")
    
    print(f"\nCharacter Creation Ready: {validation['character_creation_ready']}")
    print(f"Essential D&D Ready: {validation['essential_d3d_ready']}")
    print(f"Simple Culture Ready: {validation['simple_culture_ready']}")
    
    print("\nAvailable Utility Categories:")
    categories = list_available_utilities()
    for category, utilities in categories.items():
        print(f"  {category.replace('_', ' ').title()}: {len(utilities)} utilities")
    
    culture_features = get_simple_culture_features()
    print(f"\n✅ Simple Culture Features:")
    for feature, available in culture_features['available_features'].items():
        status = "✓" if available else "✗"
        print(f"   {status} {feature.replace('_', ' ').title()}")
    
    d3d_features = get_essential_d3d_features()
    print(f"\n✅ Essential D&D Features:")
    for feature, available in d3d_features['available_features'].items():
        status = "✓" if available else "✗"
        print(f"   {status} {feature.replace('_', ' ').title()}")
    
    print(f"\n📝 Philosophy: {culture_features['philosophy']}")
    print("🎲 Character creation comes first!")
    print("✨ Culture enhances creativity!")
    print("=" * 60)