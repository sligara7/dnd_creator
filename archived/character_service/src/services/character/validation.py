"""
Character validation service.

This service handles validation of character data including:
- Basic character data validation
- Rules compliance checking
- Custom content validation
- Character balance validation
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

from src.services.data.rules import (
    validate_ability_score_ranges,
    validate_custom_species_balance,
    validate_custom_class_balance
)

logger = logging.getLogger(__name__)

@dataclass
class CreationResult:
    """Result of a character creation validation."""
    success: bool
    error: Optional[str] = None
    warnings: List[str] = None
    data: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.data is None:
            self.data = {}

def validate_character_data(character_data: Dict[str, Any]) -> CreationResult:
    """
    Validate character data against D&D 5e rules.
    
    This is the main validation entry point that coordinates all validation checks.
    """
    # Validate basic structure first
    basic_validation = validate_basic_structure(character_data)
    if not basic_validation.success:
        return basic_validation
    
    # Validate ability scores
    ability_validation = validate_ability_score_ranges(character_data.get("ability_scores", {}))
    if not ability_validation.success:
        return ability_validation
    
    # Validate custom content if present
    if character_data.get("custom_content"):
        custom_validation = validate_custom_content(
            character_data, 
            character_data["custom_content"]
        )
        if not custom_validation.success:
            return custom_validation
    
    # All validations passed
    return CreationResult(
        success=True,
        data={"validation_passed": True},
        warnings=[]
    )

def validate_basic_structure(character_data: Dict[str, Any]) -> CreationResult:
    """Validate basic character data structure."""
    required_fields = ["name", "player_name", "species", "background"]
    missing_fields = [
        field for field in required_fields 
        if not character_data.get(field)
    ]
    
    if missing_fields:
        return CreationResult(
            success=False,
            error=f"Missing required fields: {', '.join(missing_fields)}"
        )
    
    warnings = []
    
    # Validate name length
    if len(character_data["name"]) > 100:
        warnings.append("Character name is unusually long")
    
    # Validate class selection
    character_classes = character_data.get("character_classes", {})
    if not character_classes:
        return CreationResult(
            success=False,
            error="At least one character class is required"
        )
    
    # Check total level
    total_level = sum(character_classes.values())
    if total_level < 1:
        return CreationResult(
            success=False,
            error="Total character level must be at least 1"
        )
    
    if total_level > 20:
        return CreationResult(
            success=False,
            error="Total character level cannot exceed 20"
        )
    
    return CreationResult(
        success=True,
        data={"basic_structure_valid": True},
        warnings=warnings
    )

def validate_custom_content(character_data: Dict[str, Any], 
                          custom_content: Dict[str, Any]) -> CreationResult:
    """Validate custom content against balance guidelines."""
    warnings = []
    
    # Validate custom species if present
    if "species" in custom_content:
        species_validation = validate_custom_species_balance(custom_content["species"])
        if not species_validation.success:
            return species_validation
        warnings.extend(species_validation.warnings or [])
    
    # Validate custom class if present
    if "class" in custom_content:
        class_validation = validate_custom_class_balance(custom_content["class"])
        if not class_validation.success:
            return class_validation
        warnings.extend(class_validation.warnings or [])
    
    # Validate custom features
    if "features" in custom_content:
        features = custom_content["features"]
        if len(features) > 3:
            warnings.append("Large number of custom features may affect balance")
        
        for feature in features:
            if not all(k in feature for k in ["name", "description", "level"]):
                return CreationResult(
                    success=False,
                    error="Custom features must include name, description, and level"
                )
    
    return CreationResult(
        success=True,
        data={"custom_content_valid": True},
        warnings=warnings
    )

def validate_multiclass_requirements(character_data: Dict[str, Any]) -> CreationResult:
    """Validate multiclass ability score requirements."""
    if len(character_data.get("character_classes", {})) <= 1:
        return CreationResult(success=True)
    
    ability_scores = character_data.get("ability_scores", {})
    
    # Multiclass requirements by class
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
        "Wizard": {"intelligence": 13}
    }
    
    for class_name in character_data["character_classes"]:
        if class_name in requirements:
            for ability, minimum in requirements[class_name].items():
                if ability_scores.get(ability, 0) < minimum:
                    return CreationResult(
                        success=False,
                        error=f"Multiclassing into {class_name} requires {ability} 13"
                    )
    
    return CreationResult(success=True)
