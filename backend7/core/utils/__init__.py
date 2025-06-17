"""
Essential D&D Character Creator Utilities Module

Streamlined utilities module following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
Maintains overarching functionality of crude_functional.py approach.

Utilities provide simple, direct helper functions for D&D character creation.
All utilities follow crude_functional.py philosophy of straightforward, effective processing.
"""

from typing import Dict, List, Tuple, Optional, Any, Union

# ============ CORE UTILITY IMPORTS ============

# Balance and scoring utilities
from .balance_calculator import (
    calculate_character_balance,
    calculate_power_level,
    assess_character_viability,
    get_balance_recommendations,
    calculate_combat_effectiveness,
    validate_character_balance
)

# Content analysis utilities
from .content_utils import (
    analyze_character_content,
    validate_content_completeness,
    generate_content_suggestions,
    check_content_consistency,
    extract_character_themes,
    summarize_character_concept
)

# Naming validation utilities
from .naming_validator import (
    validate_character_name,
    validate_name_components,
    get_cultural_name_suggestions,
    suggest_name_variations,
    comprehensive_name_validation,
    NameCreativity,
    CustomizationScope
)

# Mechanical parsing utilities
from .mechanical_parser import (
    parse_ability_scores,
    parse_skills,
    parse_spell_data,
    parse_equipment_data,
    calculate_ability_modifier,
    calculate_proficiency_bonus,
    calculate_skill_bonus,
    parse_dice_expression,
    validate_mechanical_data
)

# Rule checking utilities
from .rule_checker import (
    validate_character_rules,
    check_ability_score_rules,
    check_class_rules,
    check_multiclass_rules,
    validate_traditional_dnd_compatibility,
    calculate_compatibility_score
)

# Culture parsing utilities
from .culture_parser import (
    parse_culture_data,
    expand_culture_data,
    get_cultural_suggestions,
    check_cultural_compatibility,
    generate_cultural_background
)

# Culture validation utilities
from .culture_validator import (
    validate_culture_choice,
    validate_cultural_compatibility,
    get_culture_enhancement_suggestions,
    comprehensive_culture_validation
)

# Text processing utilities
from .text_processing import (
    clean_text,
    normalize_dnd_text,
    sanitize_name,
    format_description,
    parse_dice_notation,
    format_ability_score,
    format_modifier,
    validate_character_name as validate_name_text
)

# ============ CONVENIENCE UTILITY FUNCTIONS ============

def quick_character_validation(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Quick character validation - crude_functional.py comprehensive check."""
    if not character_data:
        return {
            "valid": False,
            "errors": ["No character data provided"],
            "warnings": [],
            "suggestions": ["Provide basic character information"]
        }
    
    results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "suggestions": []
    }
    
    # Quick rule check
    rules_valid, rule_violations, rule_warnings = validate_character_rules(character_data)
    if not rules_valid:
        results["valid"] = False
        results["errors"].extend(rule_violations)
    results["warnings"].extend(rule_warnings)
    
    # Quick balance check
    balance_score = calculate_character_balance(character_data)
    if balance_score < 0.3:
        results["warnings"].append("Character may be underpowered")
    elif balance_score > 0.9:
        results["warnings"].append("Character may be overpowered")
    
    # Quick completeness check
    content_valid, content_suggestions = validate_content_completeness(character_data)
    results["suggestions"].extend(content_suggestions)
    
    return results

def format_character_summary(character_data: Dict[str, Any]) -> str:
    """Format character summary - crude_functional.py summary formatting."""
    if not character_data:
        return "Empty Character"
    
    # Extract basic info
    name = character_data.get("name", "Unnamed")
    race = character_data.get("race", "Unknown Race")
    char_class = character_data.get("class", "Unknown Class")
    level = character_data.get("level", 1)
    
    # Format basic summary
    summary = f"{name} - Level {level} {race} {char_class}"
    
    # Add ability scores if available
    abilities = character_data.get("ability_scores", {})
    if abilities:
        ability_summary = []
        for ability, score in abilities.items():
            if isinstance(score, int):
                formatted = format_ability_score(score)
                ability_summary.append(f"{ability.title()}: {formatted}")
        
        if ability_summary:
            summary += "\n" + " | ".join(ability_summary)
    
    return summary

def parse_character_input(input_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Parse character input - crude_functional.py flexible input parsing."""
    if not input_data:
        return {}
    
    if isinstance(input_data, dict):
        return normalize_character_dict(input_data)
    elif isinstance(input_data, str):
        return parse_character_string(input_data)
    else:
        return {}

def normalize_character_dict(character_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize character dictionary - crude_functional.py dict normalization."""
    if not character_dict:
        return {}
    
    normalized = {}
    
    # Basic character fields
    basic_fields = ["name", "race", "class", "level", "background"]
    for field in basic_fields:
        if field in character_dict:
            value = character_dict[field]
            if isinstance(value, str):
                normalized[field] = clean_text(value)
            else:
                normalized[field] = value
    
    # Parse ability scores
    if "ability_scores" in character_dict:
        normalized["ability_scores"] = parse_ability_scores(character_dict["ability_scores"])
    
    # Parse skills
    if "skills" in character_dict:
        normalized["skills"] = parse_skills(character_dict["skills"])
    
    # Parse spells
    if "spells" in character_dict:
        normalized["spells"] = character_dict["spells"]  # Keep as-is for now
    
    # Parse equipment
    if "equipment" in character_dict:
        normalized["equipment"] = character_dict["equipment"]  # Keep as-is for now
    
    return normalized

def parse_character_string(character_string: str) -> Dict[str, Any]:
    """Parse character from string - crude_functional.py string parsing."""
    if not character_string:
        return {}
    
    # Very simple string parsing - expect format like:
    # "Name: John, Race: Human, Class: Fighter, Level: 5"
    
    character_data = {}
    
    # Split by comma and parse key-value pairs
    parts = character_string.split(",")
    for part in parts:
        if ":" in part:
            key, value = part.split(":", 1)
            key = key.strip().lower()
            value = value.strip()
            
            # Map common keys
            key_mapping = {
                "name": "name",
                "race": "race", 
                "class": "class",
                "level": "level",
                "background": "background"
            }
            
            mapped_key = key_mapping.get(key, key)
            
            # Convert level to int
            if mapped_key == "level":
                try:
                    character_data[mapped_key] = int(value)
                except ValueError:
                    character_data[mapped_key] = 1
            else:
                character_data[mapped_key] = value
    
    return character_data

def get_character_recommendations(character_data: Dict[str, Any]) -> List[str]:
    """Get character recommendations - crude_functional.py recommendation engine."""
    if not character_data:
        return ["Create a basic character with name, race, class, and level"]
    
    recommendations = []
    
    # Balance recommendations
    balance_recs = get_balance_recommendations(character_data)
    recommendations.extend(balance_recs)
    
    # Content recommendations
    content_recs = generate_content_suggestions(character_data)
    recommendations.extend(content_recs)
    
    # Cultural recommendations
    if "culture" in character_data:
        culture_recs = get_cultural_suggestions(character_data["culture"], character_data)
        recommendations.extend(culture_recs)
    
    # Name recommendations
    if "name" not in character_data or not character_data["name"]:
        race = character_data.get("race", "")
        culture = character_data.get("culture", "")
        if race:
            name_recs = get_cultural_name_suggestions(race, culture)
            recommendations.extend([f"Consider {rec}" for rec in name_recs[:3]])
    
    # Remove duplicates
    return list(set(recommendations))

def validate_and_enhance_character(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and enhance character - crude_functional.py comprehensive processing."""
    if not character_data:
        return {
            "character": {},
            "validation": {"valid": False, "errors": ["No character data"]},
            "enhancements": [],
            "recommendations": ["Start with basic character information"]
        }
    
    # Normalize input
    normalized_character = normalize_character_dict(character_data)
    
    # Validate
    validation_result = quick_character_validation(normalized_character)
    
    # Get recommendations
    recommendations = get_character_recommendations(normalized_character)
    
    # Simple enhancements
    enhancements = []
    
    # Add missing ability scores
    if "ability_scores" not in normalized_character:
        normalized_character["ability_scores"] = parse_ability_scores({})
        enhancements.append("Added default ability scores")
    
    # Add level if missing
    if "level" not in normalized_character:
        normalized_character["level"] = 1
        enhancements.append("Set default level to 1")
    
    return {
        "character": normalized_character,
        "validation": validation_result,
        "enhancements": enhancements,
        "recommendations": recommendations
    }

# ============ UTILITY AGGREGATION FUNCTIONS ============

def get_all_character_data(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get all character data with analysis - crude_functional.py comprehensive data."""
    if not character_data:
        return {}
    
    result = {
        "basic_info": extract_basic_character_info(character_data),
        "mechanical_data": extract_mechanical_data(character_data),
        "cultural_data": extract_cultural_data(character_data),
        "balance_analysis": get_balance_analysis(character_data),
        "compatibility_check": get_compatibility_check(character_data),
        "content_analysis": get_content_analysis(character_data)
    }
    
    return result

def extract_basic_character_info(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract basic character info - crude_functional.py basic extraction."""
    basic_fields = ["name", "race", "class", "level", "background"]
    return {field: character_data.get(field, "") for field in basic_fields}

def extract_mechanical_data(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract mechanical data - crude_functional.py mechanical extraction."""
    mechanical_fields = ["ability_scores", "skills", "spells", "equipment", "hit_points"]
    return {field: character_data.get(field, {}) for field in mechanical_fields}

def extract_cultural_data(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract cultural data - crude_functional.py cultural extraction."""
    cultural_fields = ["culture", "background", "languages", "traits"]
    return {field: character_data.get(field, {}) for field in cultural_fields}

def get_balance_analysis(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get balance analysis - crude_functional.py balance analysis."""
    balance_score = calculate_character_balance(character_data)
    power_level = calculate_power_level(character_data)
    viability = assess_character_viability(character_data)
    
    return {
        "balance_score": balance_score,
        "power_level": power_level,
        "viability": viability,
        "recommendations": get_balance_recommendations(character_data)
    }

def get_compatibility_check(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get compatibility check - crude_functional.py compatibility analysis."""
    return validate_traditional_dnd_compatibility(character_data)

def get_content_analysis(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get content analysis - crude_functional.py content analysis."""
    completeness_valid, completeness_suggestions = validate_content_completeness(character_data)
    themes = extract_character_themes(character_data)
    concept = summarize_character_concept(character_data)
    
    return {
        "completeness_valid": completeness_valid,
        "suggestions": completeness_suggestions,
        "themes": themes,
        "concept": concept
    }

# ============ UTILITY HELPER FUNCTIONS ============

def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get value from dict - crude_functional.py safe access."""
    if not isinstance(data, dict):
        return default
    return data.get(key, default)

def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert to int - crude_functional.py safe conversion."""
    if isinstance(value, int):
        return value
    elif isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    else:
        return default

def safe_str(value: Any, default: str = "") -> str:
    """Safely convert to string - crude_functional.py safe conversion."""
    if value is None:
        return default
    elif isinstance(value, str):
        return value
    else:
        return str(value)

def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries - crude_functional.py dict merging."""
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result

def filter_empty_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """Filter out empty values - crude_functional.py filtering."""
    if not isinstance(data, dict):
        return {}
    
    filtered = {}
    for key, value in data.items():
        if value is not None and value != "" and value != {}:
            filtered[key] = value
    
    return filtered

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Core utility imports (re-exported)
    'calculate_character_balance',
    'validate_character_rules',
    'parse_ability_scores',
    'validate_character_name',
    'parse_culture_data',
    'clean_text',
    
    # Convenience functions
    'quick_character_validation',
    'format_character_summary',
    'parse_character_input',
    'get_character_recommendations',
    'validate_and_enhance_character',
    
    # Aggregation functions
    'get_all_character_data',
    'extract_basic_character_info',
    'extract_mechanical_data',
    'extract_cultural_data',
    'get_balance_analysis',
    'get_compatibility_check',
    'get_content_analysis',
    
    # Helper functions
    'safe_get',
    'safe_int',
    'safe_str',
    'merge_dicts',
    'filter_empty_values',
    
    # Enums and classes
    'NameCreativity',
    'CustomizationScope',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D character creator utilities'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/utils",
    "focus": "utility_aggregation_and_convenience",
    "line_target": 400,
    "dependencies": [
        "balance_calculator",
        "content_utils", 
        "naming_validator",
        "mechanical_parser",
        "rule_checker",
        "culture_parser",
        "culture_validator",
        "text_processing"
    ],
    "philosophy": "crude_functional_inspired_utility_aggregation",
    "maintains_crude_functional_approach": True
}

# Utility Module Philosophy
UTILITY_PRINCIPLES = {
    "simple_aggregation": "Aggregate utilities without complex orchestration",
    "convenience_functions": "Provide convenient entry points for common tasks",
    "crude_functional_style": "Maintain crude_functional.py directness and simplicity",
    "minimal_abstraction": "Avoid over-engineering utility combinations",
    "practical_helpers": "Focus on practical utility functions for character creation"
}

# Utility Usage Examples
USAGE_EXAMPLES = {
    "quick_validation": "quick_character_validation(character_data)",
    "parse_input": "parse_character_input(user_input)",
    "get_recommendations": "get_character_recommendations(character_data)",
    "full_processing": "validate_and_enhance_character(character_data)",
    "format_summary": "format_character_summary(character_data)"
}