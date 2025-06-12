import sys
import os
from typing import Dict, List, Any, Optional, Union, Tuple
import logging

# Add project paths for imports
sys.path.append('/home/ajs7/dnd_tools/dnd_char_creator/backend4')
sys.path.append('/home/ajs7/dnd_tools/dnd_char_creator/backend')

# Core imports
from character_sheet import CharacterSheet
from create_rules import CreateRules

# Try to import legacy validators with fallbacks
try:
    from backend.core.character.character_validator import CharacterValidator
    LEGACY_VALIDATOR_AVAILABLE = True
except ImportError:
    print("Warning: Legacy CharacterValidator not found, using simplified validation")
    LEGACY_VALIDATOR_AVAILABLE = False

try:
    from backend.services.validation_service import ValidationService
    VALIDATION_SERVICE_AVAILABLE = True
except ImportError:
    print("Warning: ValidationService not found")
    VALIDATION_SERVICE_AVAILABLE = False

logger = logging.getLogger(__name__)


class ValidationResult:
    """Structured validation result container."""
    
    def __init__(self, valid: bool = True, issues: List[str] = None, 
                 warnings: List[str] = None, validator_name: str = "unknown"):
        self.valid = valid
        self.issues = issues or []
        self.warnings = warnings or []
        self.validator_name = validator_name
        self.total_checks = len(self.issues) + len(self.warnings) if self.issues or self.warnings else 1
        self.passed_checks = 1 if valid else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "valid": self.valid,
            "issues": self.issues,
            "warnings": self.warnings,
            "validator": self.validator_name,
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks
        }


class SimplifiedCharacterValidator:
    """Fallback validator when legacy systems aren't available."""
    
    def validate_full_character(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic character validation."""
        issues = []
        warnings = []
        
        # Basic required fields
        required_fields = ["name", "species", "level", "classes", "ability_scores"]
        for field in required_fields:
            if field not in character_data or not character_data[field]:
                issues.append(f"Missing required field: {field}")
        
        # Validate ability scores
        if "ability_scores" in character_data:
            for ability, score in character_data["ability_scores"].items():
                if not isinstance(score, int) or score < 1 or score > 30:
                    issues.append(f"Invalid {ability} score: {score} (must be 1-30)")
        
        # Validate level
        if "level" in character_data:
            level = character_data["level"]
            if not isinstance(level, int) or level < 1 or level > 20:
                issues.append(f"Invalid character level: {level} (must be 1-20)")
        
        # Validate classes
        if "classes" in character_data:
            classes = character_data["classes"]
            if isinstance(classes, dict):
                total_levels = sum(classes.values())
                if total_levels != character_data.get("level", 1):
                    warnings.append(f"Class levels ({total_levels}) don't match character level ({character_data.get('level', 1)})")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "total_checks": len(issues) + len(warnings) + 1,
            "passed_checks": len(issues) == 0
        }


class UnifiedCharacterValidator:
    """
    Unified character validator that combines multiple validation approaches.
    
    This validator attempts to use:
    1. Legacy CharacterValidator (if available)
    2. ValidationService (if available) 
    3. CreateRules comprehensive validation
    4. Simplified fallback validation
    """
    
    def __init__(self):
        # Initialize available validators
        self.legacy_validator = None
        self.validation_service = None
        self.create_rules = CreateRules()
        self.simplified_validator = SimplifiedCharacterValidator()
        
        # Try to initialize legacy systems
        if LEGACY_VALIDATOR_AVAILABLE:
            try:
                self.legacy_validator = CharacterValidator()
                logger.info("Legacy CharacterValidator initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize legacy validator: {e}")
        
        if VALIDATION_SERVICE_AVAILABLE:
            try:
                self.validation_service = ValidationService()
                logger.info("ValidationService initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize validation service: {e}")
    
    def validate_character(self, character_data: Dict[str, Any], 
                          character_sheet: Optional[CharacterSheet] = None) -> Dict[str, Any]:
        """
        Comprehensive character validation using all available validators.
        
        Args:
            character_data: Character data dictionary
            character_sheet: Optional CharacterSheet object for advanced validation
            
        Returns:
            Comprehensive validation results
        """
        results = {}
        all_issues = []
        all_warnings = []
        overall_valid = True
        
        # 1. Legacy validator
        if self.legacy_validator:
            try:
                legacy_result = self.legacy_validator.validate_full_character(character_data)
                results["legacy_validation"] = ValidationResult(
                    valid=legacy_result.get("valid", False),
                    issues=legacy_result.get("issues", []),
                    warnings=legacy_result.get("warnings", []),
                    validator_name="legacy"
                ).to_dict()
                
                all_issues.extend(legacy_result.get("issues", []))
                all_warnings.extend(legacy_result.get("warnings", []))
                overall_valid = overall_valid and legacy_result.get("valid", False)
                
            except Exception as e:
                logger.error(f"Legacy validation failed: {e}")
                results["legacy_validation"] = ValidationResult(
                    valid=False,
                    issues=[f"Legacy validation error: {str(e)}"],
                    validator_name="legacy"
                ).to_dict()
                overall_valid = False
        
        # 2. Simplified validation (always run as baseline)
        try:
            simple_result = self.simplified_validator.validate_full_character(character_data)
            results["simplified_validation"] = ValidationResult(
                valid=simple_result.get("valid", False),
                issues=simple_result.get("issues", []),
                warnings=simple_result.get("warnings", []),
                validator_name="simplified"
            ).to_dict()
            
            # Only add issues if not already caught by legacy validator
            new_issues = [issue for issue in simple_result.get("issues", []) if issue not in all_issues]
            new_warnings = [warning for warning in simple_result.get("warnings", []) if warning not in all_warnings]
            
            all_issues.extend(new_issues)
            all_warnings.extend(new_warnings)
            overall_valid = overall_valid and simple_result.get("valid", False)
            
        except Exception as e:
            logger.error(f"Simplified validation failed: {e}")
            results["simplified_validation"] = ValidationResult(
                valid=False,
                issues=[f"Simplified validation error: {str(e)}"],
                validator_name="simplified"
            ).to_dict()
            overall_valid = False
        
        # 3. CreateRules validation (if character sheet available)
        if character_sheet:
            try:
                rules_validation = self.create_rules.validate_entire_character_sheet(character_sheet)
                
                rules_issues = [msg for valid, msg in rules_validation if not valid]
                rules_warnings = []  # CreateRules might not distinguish warnings
                
                results["rules_validation"] = ValidationResult(
                    valid=all(valid for valid, _ in rules_validation),
                    issues=rules_issues,
                    warnings=rules_warnings,
                    validator_name="create_rules"
                ).to_dict()
                
                # Add unique issues
                new_rules_issues = [issue for issue in rules_issues if issue not in all_issues]
                all_issues.extend(new_rules_issues)
                overall_valid = overall_valid and all(valid for valid, _ in rules_validation)
                
            except Exception as e:
                logger.error(f"CreateRules validation failed: {e}")
                results["rules_validation"] = ValidationResult(
                    valid=False,
                    issues=[f"Rules validation error: {str(e)}"],
                    validator_name="create_rules"
                ).to_dict()
                overall_valid = False
        else:
            logger.info("Character sheet not provided, skipping CreateRules validation")
        
        # 4. ValidationService (if available and character sheet provided)
        if self.validation_service and character_sheet:
            try:
                # Assuming ValidationService has a similar interface
                service_result = self.validation_service.validate_character(character_data)
                results["service_validation"] = ValidationResult(
                    valid=service_result.get("valid", False),
                    issues=service_result.get("issues", []),
                    warnings=service_result.get("warnings", []),
                    validator_name="validation_service"
                ).to_dict()
                
                # Add unique issues
                new_service_issues = [issue for issue in service_result.get("issues", []) if issue not in all_issues]
                new_service_warnings = [warning for warning in service_result.get("warnings", []) if warning not in all_warnings]
                
                all_issues.extend(new_service_issues)
                all_warnings.extend(new_service_warnings)
                overall_valid = overall_valid and service_result.get("valid", False)
                
            except Exception as e:
                logger.error(f"ValidationService failed: {e}")
                results["service_validation"] = ValidationResult(
                    valid=False,
                    issues=[f"Service validation error: {str(e)}"],
                    validator_name="validation_service"
                ).to_dict()
                overall_valid = False
        
        # Compile final results
        total_validators = len([v for v in results.values() if v])
        passed_validators = len([v for v in results.values() if v and v.get("valid", False)])
        
        return {
            "overall_valid": overall_valid,
            "summary": {
                "total_issues": len(all_issues),
                "total_warnings": len(all_warnings),
                "validators_run": total_validators,
                "validators_passed": passed_validators,
                "validation_coverage": f"{passed_validators}/{total_validators}" if total_validators > 0 else "0/0"
            },
            "all_issues": all_issues,
            "all_warnings": all_warnings,
            "detailed_results": results,
            "recommendations": self._generate_recommendations(all_issues, all_warnings)
        }
    
    def validate_character_creation_step(self, step_name: str, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a specific step in character creation."""
        if step_name == "ability_scores":
            return self._validate_ability_scores(character_data.get("ability_scores", {}))
        elif step_name == "class_selection":
            return self._validate_class_selection(character_data.get("classes", {}))
        elif step_name == "equipment":
            return self._validate_equipment(character_data)
        else:
            # Default to full validation
            return self.validate_character(character_data)
    
    def _validate_ability_scores(self, ability_scores: Dict[str, int]) -> Dict[str, Any]:
        """Validate ability scores specifically."""
        issues = []
        warnings = []
        
        required_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        
        for ability in required_abilities:
            if ability not in ability_scores:
                issues.append(f"Missing ability score: {ability}")
            else:
                score = ability_scores[ability]
                if score < 8:
                    warnings.append(f"{ability.title()} score ({score}) is very low")
                elif score > 18:
                    warnings.append(f"{ability.title()} score ({score}) is exceptionally high for starting character")
        
        total_score = sum(ability_scores.values())
        if total_score < 60:
            warnings.append(f"Total ability scores ({total_score}) are quite low")
        elif total_score > 90:
            warnings.append(f"Total ability scores ({total_score}) are very high")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "step": "ability_scores"
        }
    
    def _validate_class_selection(self, classes: Dict[str, int]) -> Dict[str, Any]:
        """Validate class selection and levels."""
        issues = []
        warnings = []
        
        if not classes:
            issues.append("No classes selected")
        else:
            total_levels = sum(classes.values())
            if len(classes) > 1 and min(classes.values()) < 3:
                warnings.append("Multiclassing before level 3 may limit class features")
            
            for class_name, level in classes.items():
                if level < 1:
                    issues.append(f"Invalid level for {class_name}: {level}")
                elif level > 20:
                    issues.append(f"Class level too high for {class_name}: {level}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "step": "class_selection"
        }
    
    def _validate_equipment(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate equipment selection."""
        issues = []
        warnings = []
        
        # Basic equipment validation
        weapons = character_data.get("weapons", [])
        armor = character_data.get("armor", {})
        
        if not weapons:
            warnings.append("No weapons equipped")
        
        if isinstance(armor, dict) and not armor.get("name"):
            warnings.append("No armor equipped")
        elif isinstance(armor, str) and not armor:
            warnings.append("No armor equipped")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "step": "equipment"
        }
    
    def _generate_recommendations(self, issues: List[str], warnings: List[str]) -> List[str]:
        """Generate helpful recommendations based on validation results."""
        recommendations = []
        
        if issues:
            recommendations.append("Fix all validation errors before finalizing character")
        
        if warnings:
            recommendations.append("Review warnings to ensure character meets your expectations")
        
        if not issues and not warnings:
            recommendations.append("Character validation passed! Ready for gameplay")
        
        # Specific recommendations based on common issues
        ability_issues = [issue for issue in issues if "ability" in issue.lower()]
        if ability_issues:
            recommendations.append("Consider using point buy or standard array for balanced ability scores")
        
        class_issues = [issue for issue in issues if "class" in issue.lower()]
        if class_issues:
            recommendations.append("Verify class selection meets multiclassing prerequisites")
        
        return recommendations
    
    def get_validation_summary(self, validation_result: Dict[str, Any]) -> str:
        """Generate a human-readable validation summary."""
        if validation_result["overall_valid"]:
            return f"✅ Character validation passed ({validation_result['summary']['validation_coverage']} validators)"
        else:
            issues = len(validation_result["all_issues"])
            warnings = len(validation_result["all_warnings"])
            return f"❌ Character validation failed: {issues} issues, {warnings} warnings"


# Factory function for easy instantiation
def create_unified_validator() -> UnifiedCharacterValidator:
    """Create a unified validator with proper error handling."""
    try:
        return UnifiedCharacterValidator()
    except Exception as e:
        logger.error(f"Failed to create unified validator: {e}")
        # Return a minimal validator as fallback
        return UnifiedCharacterValidator()


# Convenience function for quick validation
def validate_character_quick(character_data: Dict[str, Any], 
                           character_sheet: Optional[CharacterSheet] = None) -> bool:
    """Quick validation that returns just True/False."""
    validator = create_unified_validator()
    result = validator.validate_character(character_data, character_sheet)
    return result["overall_valid"]