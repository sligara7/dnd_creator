"""Character validation rules.

This module provides validation rules specific to D&D 5e characters,
including ability scores, class requirements, and character creation rules.
"""

from typing import Dict, Any, List
from ..core.validation import (
    ValidationResult,
    Validator,
    required_fields,
    field_type,
    field_length,
    field_range,
    field_choices,
)
from ..models.character import Character
from ..models.enums import (
    AbilityType,
    AlignmentMoral,
    AlignmentEthical,
    Size,
)

def validate_character_data(data: Dict[str, Any]) -> ValidationResult:
    """Validate complete character data.
    
    This is the main validation entry point that coordinates all validation checks.
    
    Args:
        data: Character data to validate
        
    Returns:
        Validation result with errors and warnings
    """
    # Required field validation
    required = required_fields([
        "name",
        "player_name", 
        "race_id",
        "background_id",
        "classes",
    ])
    result = required(data)
    if not result.valid:
        return result
    
    # Basic data validation
    basic = validate_basic_data(data)
    result.merge(basic)
    if not result.valid:
        return result
        
    # Ability scores
    if "abilities" in data:
        ability = validate_ability_scores(data["abilities"])
        result.merge(ability)
        if not result.valid:
            return result
            
    # Custom content
    if "custom_content" in data:
        custom = validate_custom_content(data["custom_content"])
        result.merge(custom)
        if not result.valid:
            return result
            
    # Multiclass requirements
    if len(data.get("classes", [])) > 1:
        multiclass = validate_multiclass_requirements(data)
        result.merge(multiclass)
        if not result.valid:
            return result
            
    return result

def validate_basic_data(data: Dict[str, Any]) -> ValidationResult:
    """Validate basic character data structure and fields.
    
    Args:
        data: Character data to validate
        
    Returns:
        Validation result
    """
    # Create validator with rules
    validator = Validator([
        field_length("name", min_len=1, max_len=100),
        field_length("player_name", min_len=1, max_len=100),
        field_type("description", str),
        field_choices("size", [s.value for s in Size]),
        field_choices("alignment_moral", [a.value for a in AlignmentMoral]),
        field_choices("alignment_ethical", [a.value for a in AlignmentEthical]),
    ])
    
    result = validator.validate(data)
    
    # Validate character level
    classes = data.get("classes", [])
    if not classes:
        result.add_error("At least one character class is required")
    else:
        total_level = sum(c.level for c in classes)
        if total_level < 1:
            result.add_error("Total character level must be at least 1")
        elif total_level > 20:
            result.add_error("Total character level cannot exceed 20")
            
        # Check for duplicate classes
        class_names = [c.class_name for c in classes]
        if len(class_names) != len(set(class_names)):
            result.add_error("Duplicate character classes are not allowed")
            
    return result

def validate_ability_scores(abilities: Dict[str, Any]) -> ValidationResult:
    """Validate character ability scores.
    
    Args:
        abilities: Ability score data
        
    Returns:
        Validation result
    """
    result = ValidationResult()
    
    # Verify all abilities are present
    required = [a.value for a in AbilityType]
    missing = [a for a in required if a not in abilities]
    if missing:
        result.add_error(f"Missing ability scores: {', '.join(missing)}")
        return result
        
    # Validate each ability score
    for ability_name, ability_data in abilities.items():
        # Basic structure
        if not isinstance(ability_data, dict):
            result.add_error(f"Invalid ability data format for {ability_name}")
            continue
            
        # Score range
        score = ability_data.get("score", 0)
        if score < 1:
            result.add_error(f"{ability_name} score cannot be less than 1")
        elif score > 30:
            result.add_error(f"{ability_name} score cannot exceed 30")
            
        # Bonuses/penalties
        for bonus in ability_data.get("bonuses", {}).values():
            if abs(bonus) > 10:
                result.add_warning(f"Unusually large {ability_name} score modifier: {bonus}")
                
    return result

def validate_custom_content(content: Dict[str, Any]) -> ValidationResult:
    """Validate custom character content.
    
    Args:
        content: Custom content data
        
    Returns:
        Validation result
    """
    result = ValidationResult()
    
    # Validate each custom feature
    features = content.get("features", [])
    if len(features) > 3:
        result.add_warning("Large number of custom features may affect balance")
        
    for feature in features:
        # Required fields
        if not all(k in feature for k in ["name", "description", "level"]):
            result.add_error(
                "Custom features must include name, description, and level"
            )
            continue
            
        # Name/description length
        if len(feature["name"]) > 100:
            result.add_warning("Feature name is unusually long")
            
        if len(feature["description"]) < 10:
            result.add_warning("Feature description is very short")
        elif len(feature["description"]) > 1000:
            result.add_warning("Feature description is very long")
            
        # Level range
        if feature["level"] < 1 or feature["level"] > 20:
            result.add_error("Feature level must be between 1 and 20")
            
    return result

def validate_multiclass_requirements(data: Dict[str, Any]) -> ValidationResult:
    """Validate multiclass ability score requirements.
    
    Args:
        data: Character data
        
    Returns:
        Validation result
    """
    result = ValidationResult()
    
    # Get ability scores
    abilities = data.get("abilities", {})
    
    # Requirements by class
    requirements = {
        "Barbarian": {"strength": 13},
        "Bard": {"charisma": 13},
        "Cleric": {"wisdom": 13},
        "Druid": {"wisdom": 13},
        "Fighter": {"strength": 13, "dexterity": 13},
        "Monk": {"dexterity": 13, "wisdom": 13},
        "Paladin": {"strength": 13, "charisma": 13},
        "Ranger": {"dexterity": 13, "wisdom": 13},
        "Rogue": {"dexterity": 13},
        "Sorcerer": {"charisma": 13},
        "Warlock": {"charisma": 13},
        "Wizard": {"intelligence": 13},
    }
    
    # Check each class's requirements
    for class_level in data.get("classes", []):
        class_name = class_level.class_name
        if class_name in requirements:
            for ability, minimum in requirements[class_name].items():
                score = abilities.get(ability, {}).get("score", 0)
                if score < minimum:
                    result.add_error(
                        f"Multiclassing into {class_name} requires "
                        f"{ability} score of {minimum}"
                    )
                    
    return result
