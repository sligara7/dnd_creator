from typing import Dict, Any, List, Tuple
import logging

from .content_registry import ContentRegistry
from .constants import RuleConstants

logger = logging.getLogger(__name__)

class CharacterValidationEngine:
    """Specialized engine for comprehensive character validation."""
    
    def __init__(self):
        self.content_registry = ContentRegistry()
        self.constants = RuleConstants()
    
    def validate_character_sheet(self, character_sheet) -> List[Tuple[bool, str]]:
        """Validate an entire character sheet against all rules."""
        results = []
        
        try:
            # Basic character information
            results.extend(self._validate_basic_info(character_sheet))
            
            # Character build validation
            results.extend(self._validate_character_build(character_sheet))
            
            # Equipment and resources
            results.extend(self._validate_equipment_and_resources(character_sheet))
            
            # Multiclass validation
            results.extend(self._validate_multiclass_rules(character_sheet))
            
        except Exception as e:
            logger.error(f"Character validation failed: {e}")
            results.append((False, f"Validation error: {str(e)}"))
        
        return results
    
    def validate_creation_data(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate character data during creation process."""
        issues = []
        warnings = []
        
        # Validate required fields
        required_fields = ["name", "species", "classes", "ability_scores"]
        for field in required_fields:
            if field not in character_data or not character_data[field]:
                issues.append(f"Missing required field: {field}")
        
        # Validate classes
        if "classes" in character_data:
            class_issues = self._validate_classes_data(character_data["classes"])
            issues.extend(class_issues)
        
        # Validate ability scores
        if "ability_scores" in character_data:
            ability_issues = self._validate_ability_scores_data(character_data["ability_scores"])
            issues.extend(ability_issues)
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def _validate_basic_info(self, character_sheet) -> List[Tuple[bool, str]]:
        """Validate basic character information."""
        results = []
        
        # Name validation
        name = character_sheet.get_name() if hasattr(character_sheet, 'get_name') else ""
        if not name or len(name.strip()) < 2:
            results.append((False, "Character name must be at least 2 characters"))
        else:
            results.append((True, "Valid character name"))
        
        # Species validation
        species = character_sheet.get_species() if hasattr(character_sheet, 'get_species') else ""
        if self.content_registry.is_valid_species(species):
            results.append((True, f"Valid species: {species}"))
        else:
            results.append((False, f"Invalid species: {species}"))
        
        return results
    
    def _validate_character_build(self, character_sheet) -> List[Tuple[bool, str]]:
        """Validate character build (classes, levels, abilities)."""
        results = []
        
        # Class validation
        if hasattr(character_sheet, 'get_class_levels'):
            class_levels = character_sheet.get_class_levels()
            
            if not class_levels:
                results.append((False, "Character must have at least one class"))
            else:
                total_level = sum(class_levels.values())
                if total_level > self.constants.MAX_LEVEL:
                    results.append((False, f"Total level ({total_level}) exceeds maximum ({self.constants.MAX_LEVEL})"))
                else:
                    results.append((True, f"Valid total level: {total_level}"))
                
                # Validate each class
                for class_name, level in class_levels.items():
                    if self.content_registry.is_valid_class(class_name):
                        results.append((True, f"Valid class: {class_name} (level {level})"))
                    else:
                        results.append((False, f"Invalid class: {class_name}"))
        
        return results
    
    def _validate_equipment_and_resources(self, character_sheet) -> List[Tuple[bool, str]]:
        """Validate equipment and character resources."""
        results = []
        
        # Basic equipment validation
        if hasattr(character_sheet, 'get_weapons'):
            weapons = character_sheet.get_weapons()
            if isinstance(weapons, list):
                results.append((True, f"Character has {len(weapons)} weapons"))
            else:
                results.append((False, "Weapons data is malformed"))
        
        return results
    
    def _validate_multiclass_rules(self, character_sheet) -> List[Tuple[bool, str]]:
        """Validate multiclass-specific rules."""
        results = []
        
        if hasattr(character_sheet, 'get_class_levels'):
            class_levels = character_sheet.get_class_levels()
            
            if len(class_levels) > 1:
                # This is a multiclass character
                results.append((True, "Multiclass character detected"))
                
                # Validate multiclass requirements would go here
                # This would require ability scores and detailed validation
            else:
                results.append((True, "Single-class character"))
        
        return results
    
    def _validate_classes_data(self, classes_data: Dict[str, int]) -> List[str]:
        """Validate classes data structure."""
        issues = []
        
        if not isinstance(classes_data, dict):
            issues.append("Classes must be a dictionary mapping class names to levels")
            return issues
        
        for class_name, level in classes_data.items():
            if not self.content_registry.is_valid_class(class_name):
                issues.append(f"Invalid class: {class_name}")
            
            if not isinstance(level, int) or level < 1 or level > 20:
                issues.append(f"Invalid level for {class_name}: {level}")
        
        return issues
    
    def _validate_ability_scores_data(self, ability_scores: Dict[str, int]) -> List[str]:
        """Validate ability scores data structure."""
        issues = []
        
        required_abilities = {"strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"}
        
        for ability in required_abilities:
            if ability not in ability_scores:
                issues.append(f"Missing ability score: {ability}")
            else:
                score = ability_scores[ability]
                if not isinstance(score, int) or score < 1 or score > 30:
                    issues.append(f"Invalid {ability} score: {score}")
        
        return issues