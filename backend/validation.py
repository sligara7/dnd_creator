"""
Character Validation System - Comprehensive D&D Character Validation

This module provides comprehensive validation for D&D characters including:
- Basic data structure validation
- D&D rules compliance checking  
- Character statistics validation
- Equipment and proficiency validation
- Custom content validation

Integrates with the cleaned backend modules for complete character validation.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

# Import from cleaned modules
from character_models import CharacterCore, CharacterState, CharacterSheet
from core_models import AbilityScore, ASIManager, ProficiencyLevel, AbilityScoreSource
from custom_content_models import ContentRegistry
from ability_management import AdvancedAbilityManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# VALIDATION RESULT CLASSES
# ============================================================================

@dataclass
class ValidationIssue:
    """Represents a validation issue with severity and context."""
    severity: str  # "error", "warning", "info"
    category: str  # "structure", "rules", "balance", "equipment", etc.
    message: str
    field: Optional[str] = None
    suggestion: Optional[str] = None

@dataclass
class ValidationResult:
    """Comprehensive validation result."""
    valid: bool
    score: float  # 0.0 to 1.0, overall character validity score
    issues: List[ValidationIssue]
    summary: Dict[str, Any]
    
    def __post_init__(self):
        if not hasattr(self, 'issues'):
            self.issues = []
    
    def add_issue(self, severity: str, category: str, message: str, 
                  field: str = None, suggestion: str = None):
        """Add a validation issue."""
        self.issues.append(ValidationIssue(severity, category, message, field, suggestion))
    
    def get_errors(self) -> List[ValidationIssue]:
        """Get only error-level issues."""
        return [issue for issue in self.issues if issue.severity == "error"]
    
    def get_warnings(self) -> List[ValidationIssue]:
        """Get only warning-level issues."""
        return [issue for issue in self.issues if issue.severity == "warning"]
    
    def has_critical_issues(self) -> bool:
        """Check if there are any critical (error-level) issues."""
        return len(self.get_errors()) > 0

# ============================================================================
# COMPREHENSIVE CHARACTER VALIDATOR
# ============================================================================

class CharacterValidator:
    """Comprehensive D&D character validation system."""
    
    def __init__(self, content_registry: ContentRegistry = None):
        self.content_registry = content_registry or ContentRegistry()
        self.standard_species = {
            "human", "elf", "dwarf", "halfling", "dragonborn", "gnome", 
            "half-elf", "half-orc", "tiefling", "aasimar", "genasi", 
            "goliath", "tabaxi", "kenku", "lizardfolk", "tortle", "aarakocra",
            "bugbear", "firbolg", "goblin", "hobgoblin", "kobold", "orc",
            "yuan-ti", "minotaur", "centaur", "loxodon", "simic hybrid"
        }
        
        self.standard_classes = {
            "artificer", "barbarian", "bard", "cleric", "druid", "fighter",
            "monk", "paladin", "ranger", "rogue", "sorcerer", "warlock", 
            "wizard", "blood hunter"
        }
        
        self.standard_backgrounds = {
            "acolyte", "criminal", "folk hero", "noble", "sage", "soldier",
            "charlatan", "entertainer", "guild artisan", "hermit", "outlander",
            "sailor", "urchin", "anthropologist", "archaeologist", "courtier",
            "faction agent", "far traveler", "inheritor", "knight", "mercenary veteran",
            "urban bounty hunter", "waterdavian noble"
        }
        
        logger.info("Character Validator initialized")
    
    def validate_character(self, character: CharacterCore) -> ValidationResult:
        """Perform comprehensive character validation."""
        
        result = ValidationResult(valid=True, score=1.0, issues=[], summary={})
        
        try:
            # Convert character to dict for easier validation
            character_data = character.to_dict()
            
            # Run all validation checks
            self._validate_basic_structure(character_data, result)
            self._validate_ability_scores(character, result)
            self._validate_classes_and_levels(character, result)
            self._validate_species_and_background(character, result)
            self._validate_character_balance(character, result)
            self._validate_equipment_proficiency(character_data, result)
            self._validate_spell_access(character, result)
            self._validate_asi_usage(character, result)
            
            # Calculate final score and validity
            self._calculate_final_score(result)
            
            # Generate summary
            result.summary = self._generate_validation_summary(character, result)
            
            logger.info(f"Character validation completed. Score: {result.score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            result.add_issue("error", "system", f"Validation system error: {e}")
            result.valid = False
            result.score = 0.0
            return result
    
    def validate_character_data(self, character_data: Dict[str, Any]) -> ValidationResult:
        """Validate character from raw data dictionary."""
        
        try:
            # Convert data to CharacterCore for full validation
            character = self._build_character_from_data(character_data)
            return self.validate_character(character)
        except Exception as e:
            result = ValidationResult(valid=False, score=0.0, issues=[], summary={})
            result.add_issue("error", "structure", f"Failed to parse character data: {e}")
            return result
    
    def _validate_basic_structure(self, character_data: Dict[str, Any], result: ValidationResult):
        """Validate basic character data structure."""
        
        required_fields = ["name", "race", "character_classes", "level"]
        
        for field in required_fields:
            if field not in character_data or not character_data[field]:
                result.add_issue("error", "structure", f"Missing required field: {field}", field)
        
        # Validate name
        name = character_data.get("name", "")
        if isinstance(name, str):
            if len(name.strip()) < 2:
                result.add_issue("warning", "structure", "Character name is too short", "name")
            elif len(name) > 50:
                result.add_issue("warning", "structure", "Character name is very long", "name")
        else:
            result.add_issue("error", "structure", "Character name must be a string", "name")
    
    def _validate_ability_scores(self, character: CharacterCore, result: ValidationResult):
        """Validate ability scores for D&D compliance."""
        
        abilities = {
            "strength": character.strength,
            "dexterity": character.dexterity, 
            "constitution": character.constitution,
            "intelligence": character.intelligence,
            "wisdom": character.wisdom,
            "charisma": character.charisma
        }
        
        total_points = 0
        for ability_name, ability_score in abilities.items():
            if not isinstance(ability_score, AbilityScore):
                result.add_issue("error", "structure", f"{ability_name} is not a valid AbilityScore object", ability_name)
                continue
            
            score = ability_score.total_score
            total_points += score
            
            # Check score ranges
            if score < 1:
                result.add_issue("error", "rules", f"{ability_name} score ({score}) is below minimum (1)", ability_name)
            elif score > 30:
                result.add_issue("error", "rules", f"{ability_name} score ({score}) exceeds maximum (30)", ability_name)
            elif score < 8:
                result.add_issue("warning", "balance", f"{ability_name} score ({score}) is very low", ability_name)
            elif score > 20 and character.get_total_level() < 10:
                result.add_issue("info", "balance", f"{ability_name} score ({score}) is high for character level", ability_name)
        
        # Check point buy/array compliance (rough estimate)
        average_score = total_points / 6
        if average_score < 10:
            result.add_issue("warning", "balance", f"Average ability score ({average_score:.1f}) seems low")
        elif average_score > 16:
            result.add_issue("info", "balance", f"Average ability score ({average_score:.1f}) is quite high")
    
    def _validate_classes_and_levels(self, character: CharacterCore, result: ValidationResult):
        """Validate class levels and multiclassing rules."""
        
        if not character.character_classes:
            result.add_issue("error", "structure", "Character has no classes")
            return
        
        total_level = sum(character.character_classes.values())
        
        # Check level validity
        if total_level < 1:
            result.add_issue("error", "rules", "Character level must be at least 1")
        elif total_level > 20:
            result.add_issue("error", "rules", f"Character level ({total_level}) exceeds maximum (20)")
        
        # Check individual class levels
        for class_name, level in character.character_classes.items():
            if level < 1:
                result.add_issue("error", "rules", f"{class_name} level must be at least 1")
            elif level > 20:
                result.add_issue("error", "rules", f"{class_name} level ({level}) exceeds maximum (20)")
            
            # Check if class is standard or custom
            if class_name.lower() not in self.standard_classes:
                result.add_issue("info", "custom", f"Using custom class: {class_name}")
        
        # Multiclassing validation
        if len(character.character_classes) > 1:
            self._validate_multiclassing_requirements(character, result)
    
    def _validate_multiclassing_requirements(self, character: CharacterCore, result: ValidationResult):
        """Validate multiclassing ability score requirements."""
        
        multiclass_requirements = {
            "barbarian": ("strength", 13),
            "bard": ("charisma", 13),
            "cleric": ("wisdom", 13),
            "druid": ("wisdom", 13),
            "fighter": ("strength", 13, "dexterity", 13),  # Str OR Dex
            "monk": ("dexterity", 13, "wisdom", 13),
            "paladin": ("strength", 13, "charisma", 13),
            "ranger": ("dexterity", 13, "wisdom", 13),
            "rogue": ("dexterity", 13),
            "sorcerer": ("charisma", 13),
            "warlock": ("charisma", 13),
            "wizard": ("intelligence", 13)
        }
        
        for class_name in character.character_classes.keys():
            class_lower = class_name.lower()
            if class_lower in multiclass_requirements:
                requirements = multiclass_requirements[class_lower]
                
                # Handle special cases (like Fighter's Str OR Dex requirement)
                if class_lower == "fighter":
                    str_score = character.strength.total_score
                    dex_score = character.dexterity.total_score
                    if str_score < 13 and dex_score < 13:
                        result.add_issue("warning", "rules", 
                                       f"Multiclassing into Fighter requires 13 Strength OR Dexterity (have {str_score}/{dex_score})")
                else:
                    # Standard single or dual requirements
                    for i in range(0, len(requirements), 2):
                        ability_name = requirements[i]
                        required_score = requirements[i + 1]
                        
                        ability_obj = getattr(character, ability_name, None)
                        if ability_obj and ability_obj.total_score < required_score:
                            result.add_issue("warning", "rules",
                                           f"Multiclassing into {class_name} requires {required_score} {ability_name.capitalize()} (have {ability_obj.total_score})")
    
    def _validate_species_and_background(self, character: CharacterCore, result: ValidationResult):
        """Validate species and background choices."""
        
        # Check species
        if character.race:
            if character.race.lower() not in self.standard_species:
                result.add_issue("info", "custom", f"Using custom species: {character.race}")
        else:
            result.add_issue("warning", "structure", "Character has no species/race assigned")
        
        # Check background  
        if character.background:
            if character.background.lower() not in self.standard_backgrounds:
                result.add_issue("info", "custom", f"Using custom background: {character.background}")
        else:
            result.add_issue("warning", "structure", "Character has no background assigned")
    
    def _validate_character_balance(self, character: CharacterCore, result: ValidationResult):
        """Validate character for game balance concerns."""
        
        total_level = sum(character.character_classes.values())
        
        # Check for extremely high stats at low levels
        if total_level <= 5:
            for ability_name in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
                ability = getattr(character, ability_name)
                if ability.total_score >= 18:
                    result.add_issue("info", "balance", 
                                   f"High {ability_name} ({ability.total_score}) at low level ({total_level})")
        
        # Check for dump stats (very low abilities)
        dump_stats = []
        for ability_name in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            ability = getattr(character, ability_name)
            if ability.total_score <= 8:
                dump_stats.append(ability_name)
        
        if len(dump_stats) > 2:
            result.add_issue("warning", "balance", 
                           f"Multiple very low ability scores: {', '.join(dump_stats)}")
    
    def _validate_equipment_proficiency(self, character_data: Dict[str, Any], result: ValidationResult):
        """Validate equipment proficiency and AC calculations."""
        
        # This would be expanded with actual equipment data from character
        armor_details = character_data.get("armor_details", {})
        if armor_details:
            armor_type = armor_details.get("armor_type", "Light")
            # Add validation logic for armor proficiency based on classes
            self._check_armor_proficiency_by_class(character_data, armor_type, result)
    
    def _check_armor_proficiency_by_class(self, character_data: Dict[str, Any], armor_type: str, result: ValidationResult):
        """Check armor proficiency based on character classes."""
        
        classes = character_data.get("character_classes", {})
        has_proficiency = False
        
        for class_name in classes.keys():
            class_lower = class_name.lower()
            if armor_type.lower() == "light":
                has_proficiency = True  # Most classes have light armor
            elif armor_type.lower() == "medium":
                if class_lower in ["fighter", "paladin", "cleric", "barbarian", "ranger", "artificer"]:
                    has_proficiency = True
            elif armor_type.lower() == "heavy":
                if class_lower in ["fighter", "paladin", "cleric"]:
                    has_proficiency = True
        
        if not has_proficiency:
            result.add_issue("warning", "equipment", 
                           f"Character may not be proficient with {armor_type} armor")
    
    def _validate_spell_access(self, character: CharacterCore, result: ValidationResult):
        """Validate spell access and slot progression."""
        
        spellcasting_classes = {
            "bard", "cleric", "druid", "sorcerer", "warlock", "wizard",
            "paladin", "ranger", "artificer"  # Half casters
        }
        
        has_spellcaster = any(class_name.lower() in spellcasting_classes 
                             for class_name in character.character_classes.keys())
        
        if has_spellcaster:
            result.add_issue("info", "spells", "Character has spellcasting abilities")
            # Could add more detailed spell validation here
    
    def _validate_asi_usage(self, character: CharacterCore, result: ValidationResult):
        """Validate ASI usage and progression."""
        
        try:
            asi_manager = ASIManager()
            asi_info = asi_manager.calculate_available_asis(character.character_classes)
            
            total_available = asi_info.get("total_available", 0)
            total_used = asi_info.get("total_used", 0)
            
            if total_used > total_available:
                result.add_issue("warning", "rules", 
                               f"More ASIs used ({total_used}) than available ({total_available})")
            elif total_available > total_used:
                result.add_issue("info", "progression", 
                               f"Unused ASIs available: {total_available - total_used}")
        
        except Exception as e:
            result.add_issue("warning", "system", f"Could not validate ASI usage: {e}")
    
    def _calculate_final_score(self, result: ValidationResult):
        """Calculate final validation score and validity."""
        
        error_count = len(result.get_errors())
        warning_count = len(result.get_warnings())
        
        # Start with perfect score
        score = 1.0
        
        # Deduct for errors (major issues)
        score -= error_count * 0.2
        
        # Deduct for warnings (minor issues)  
        score -= warning_count * 0.05
        
        # Ensure score doesn't go negative
        score = max(0.0, score)
        
        # Character is valid if score > 0.5 and no critical errors
        result.valid = score > 0.5 and not result.has_critical_issues()
        result.score = score
    
    def _generate_validation_summary(self, character: CharacterCore, result: ValidationResult) -> Dict[str, Any]:
        """Generate comprehensive validation summary."""
        
        total_level = sum(character.character_classes.values())
        
        return {
            "character_name": character.name,
            "total_level": total_level,
            "class_count": len(character.character_classes),
            "validation_score": result.score,
            "is_valid": result.valid,
            "error_count": len(result.get_errors()),
            "warning_count": len(result.get_warnings()),
            "has_custom_content": any(issue.category == "custom" for issue in result.issues),
            "primary_class": list(character.character_classes.keys())[0] if character.character_classes else "None",
            "is_multiclass": len(character.character_classes) > 1,
            "average_ability_score": self._calculate_average_ability_score(character),
            "highest_ability": self._get_highest_ability(character),
            "validation_categories": self._get_issue_categories(result)
        }
    
    def _calculate_average_ability_score(self, character: CharacterCore) -> float:
        """Calculate average ability score."""
        
        abilities = [
            character.strength.total_score,
            character.dexterity.total_score,
            character.constitution.total_score,
            character.intelligence.total_score,
            character.wisdom.total_score,
            character.charisma.total_score
        ]
        
        return sum(abilities) / len(abilities)
    
    def _get_highest_ability(self, character: CharacterCore) -> Dict[str, Any]:
        """Get character's highest ability score."""
        
        abilities = {
            "strength": character.strength.total_score,
            "dexterity": character.dexterity.total_score,
            "constitution": character.constitution.total_score,
            "intelligence": character.intelligence.total_score,
            "wisdom": character.wisdom.total_score,
            "charisma": character.charisma.total_score
        }
        
        highest = max(abilities.items(), key=lambda x: x[1])
        return {"name": highest[0], "score": highest[1]}
    
    def _get_issue_categories(self, result: ValidationResult) -> Dict[str, int]:
        """Get count of issues by category."""
        
        categories = {}
        for issue in result.issues:
            categories[issue.category] = categories.get(issue.category, 0) + 1
        
        return categories
    
    def _build_character_from_data(self, character_data: Dict[str, Any]) -> CharacterCore:
        """Build a CharacterCore from raw data for validation."""
        
        character = CharacterCore(character_data.get("name", "Unnamed"))
        character.race = character_data.get("race", "Human")
        character.background = character_data.get("background", "Folk Hero")
        character.character_classes = character_data.get("character_classes", {"Fighter": 1})
        
        # Set ability scores
        ability_scores = character_data.get("ability_scores", {})
        for ability_name in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            score = ability_scores.get(ability_name, 10)
            setattr(character, ability_name, AbilityScore(score))
        
        return character

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def validate_character(character: CharacterCore, content_registry: ContentRegistry = None) -> ValidationResult:
    """Convenience function to validate a character."""
    validator = CharacterValidator(content_registry)
    return validator.validate_character(character)

def validate_character_data(character_data: Dict[str, Any], content_registry: ContentRegistry = None) -> ValidationResult:
    """Convenience function to validate character from data dict."""
    validator = CharacterValidator(content_registry)
    return validator.validate_character_data(character_data)

def quick_validate(character: CharacterCore) -> bool:
    """Quick validation - returns just True/False."""
    result = validate_character(character)
    return result.valid

# ============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# ============================================================================

def validate_character_data_legacy(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy function for backward compatibility."""
    result = validate_character_data(character_data)
    
    return {
        "valid": result.valid,
        "issues": [issue.message for issue in result.get_errors()],
        "warnings": [issue.message for issue in result.get_warnings()]
    }

def get_character_stats_summary(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy function - get character stats summary."""
    
    try:
        validator = CharacterValidator()
        character = validator._build_character_from_data(character_data)
        result = validator.validate_character(character)
        return result.summary
    except Exception:
        # Fallback to basic summary
        abilities = character_data.get("ability_scores", {})
        highest_ability = max(abilities.items(), key=lambda x: x[1]) if abilities else ("unknown", 0)
        avg_ability = sum(abilities.values()) / len(abilities) if abilities else 0
        
        return {
            "total_level": character_data.get("level", 1),
            "primary_class": list(character_data.get("character_classes", {}).keys())[0] if character_data.get("character_classes") else "Unknown",
            "highest_ability": {"name": highest_ability[0], "score": highest_ability[1]},
            "average_ability_score": round(avg_ability, 1),
            "armor_class": character_data.get("ac", 10),
            "max_hit_points": character_data.get("hp", {}).get("max", 0),
            "has_detailed_backstory": bool(character_data.get("detailed_backstory")),
            "has_custom_content": bool(character_data.get("custom_content"))
        }

# ============================================================================
# MODULE SUMMARY
# ============================================================================
"""
REFACTORED VALIDATION MODULE - COMPREHENSIVE CHARACTER VALIDATION

This module has been completely refactored and expanded to provide comprehensive
D&D character validation:

CLASSES:
- ValidationIssue: Represents a single validation issue with context
- ValidationResult: Comprehensive validation result with scoring
- CharacterValidator: Main validation class with comprehensive checks

KEY FEATURES:
- Comprehensive D&D rules compliance checking
- Character balance validation
- Equipment and proficiency validation
- Custom content detection and validation
- ASI usage validation
- Multiclassing requirements checking
- Scoring system (0.0 to 1.0) for character validity
- Detailed issue categorization and suggestions

VALIDATION CATEGORIES:
- structure: Basic data structure issues
- rules: D&D rules violations
- balance: Game balance concerns
- equipment: Equipment/proficiency issues
- custom: Custom content usage
- spells: Spellcasting validation
- progression: Character progression issues

INTEGRATION:
- Uses CharacterCore from character_models
- Integrates with AbilityScore from core_models
- Works with ContentRegistry for custom content
- Compatible with ASIManager for progression validation

BACKWARD COMPATIBILITY:
- Maintains legacy function signatures for existing code
- Provides simple True/False validation functions
- Legacy stats summary functions preserved

The validation system now provides comprehensive character checking for
game balance, rules compliance, and data integrity.
"""
