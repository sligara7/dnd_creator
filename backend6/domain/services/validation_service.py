from typing import Dict, List, Any, Optional, Protocol
from abc import ABC, abstractmethod
import logging
from dataclasses import dataclass

from ...core.entities.character import Character

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Value object for validation results."""
    is_valid: bool
    issues: List[str]
    warnings: List[str]
    validator_name: str
    
    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0
    
    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.is_valid,
            "issues": self.issues,
            "warnings": self.warnings,
            "validator": self.validator_name
        }

@dataclass
class ComprehensiveValidationResult:
    """Comprehensive validation result combining multiple validators."""
    overall_valid: bool
    individual_results: Dict[str, ValidationResult]
    all_issues: List[str]
    all_warnings: List[str]
    recommendations: List[str]
    
    @property
    def total_validators(self) -> int:
        return len(self.individual_results)
    
    @property
    def passed_validators(self) -> int:
        return sum(1 for result in self.individual_results.values() if result.is_valid)
    
    @property
    def validation_coverage(self) -> str:
        return f"{self.passed_validators}/{self.total_validators}"

class CharacterValidator(Protocol):
    """Protocol defining the interface for character validators."""
    
    def validate(self, character: Character) -> ValidationResult:
        """Validate a character and return results."""
        ...

class ValidationService:
    """
    Domain service for character validation.
    
    Orchestrates multiple validators and provides comprehensive validation results.
    """
    
    def __init__(self, validators: List[CharacterValidator]):
        self.validators = validators
    
    def validate_character(self, character: Character) -> ComprehensiveValidationResult:
        """
        Perform comprehensive character validation using all available validators.
        
        Args:
            character: Character entity to validate
            
        Returns:
            ComprehensiveValidationResult with comprehensive validation data
        """
        individual_results = {}
        all_issues = []
        all_warnings = []
        overall_valid = True
        
        for validator in self.validators:
            try:
                result = validator.validate(character)
                validator_name = getattr(validator, 'name', validator.__class__.__name__)
                
                individual_results[validator_name] = result
                
                # Collect unique issues and warnings
                new_issues = [issue for issue in result.issues if issue not in all_issues]
                new_warnings = [warning for warning in result.warnings if warning not in all_warnings]
                
                all_issues.extend(new_issues)
                all_warnings.extend(new_warnings)
                
                overall_valid = overall_valid and result.is_valid
                
            except Exception as e:
                logger.error(f"Validator {validator.__class__.__name__} failed: {e}")
                
                error_result = ValidationResult(
                    is_valid=False,
                    issues=[f"Validator error: {str(e)}"],
                    warnings=[],
                    validator_name=validator.__class__.__name__
                )
                
                individual_results[validator.__class__.__name__] = error_result
                all_issues.append(f"Validator {validator.__class__.__name__} failed: {str(e)}")
                overall_valid = False
        
        recommendations = self._generate_recommendations(all_issues, all_warnings, character)
        
        return ComprehensiveValidationResult(
            overall_valid=overall_valid,
            individual_results=individual_results,
            all_issues=all_issues,
            all_warnings=all_warnings,
            recommendations=recommendations
        )
    
    def validate_character_creation_step(self, character: Character, step: str) -> ValidationResult:
        """
        Validate a specific step in character creation.
        
        Args:
            character: Character entity
            step: Validation step name
            
        Returns:
            ValidationResult for the specific step
        """
        step_validators = {
            "ability_scores": self._validate_ability_scores,
            "class_selection": self._validate_class_selection,
            "equipment": self._validate_equipment,
            "proficiencies": self._validate_proficiencies
        }
        
        validator_func = step_validators.get(step)
        if not validator_func:
            return ValidationResult(
                is_valid=False,
                issues=[f"Unknown validation step: {step}"],
                warnings=[],
                validator_name="step_validator"
            )
        
        return validator_func(character)
    
    def _validate_ability_scores(self, character: Character) -> ValidationResult:
        """Validate character ability scores."""
        issues = []
        warnings = []
        
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        
        for ability in abilities:
            score = character.get_ability_score_value(ability)
            
            if score < 1 or score > 30:
                issues.append(f"{ability.title()} score ({score}) must be between 1-30")
            elif score < 8:
                warnings.append(f"{ability.title()} score ({score}) is very low")
            elif score > 18 and character.total_level == 1:
                warnings.append(f"{ability.title()} score ({score}) is exceptionally high for level 1")
        
        # Check total scores for point buy/standard array compliance
        total_scores = sum(character.get_ability_score_value(ability) for ability in abilities)
        if total_scores < 60:
            warnings.append(f"Total ability scores ({total_scores}) are quite low")
        elif total_scores > 90:
            warnings.append(f"Total ability scores ({total_scores}) are very high")
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            validator_name="ability_scores"
        )
    
    def _validate_class_selection(self, character: Character) -> ValidationResult:
        """Validate character class selection."""
        issues = []
        warnings = []
        
        if not character.character_classes:
            issues.append("Character must have at least one class")
            return ValidationResult(
                is_valid=False,
                issues=issues,
                warnings=warnings,
                validator_name="class_selection"
            )
        
        total_level = character.total_level
        if total_level > 20:
            issues.append(f"Total character level ({total_level}) exceeds maximum (20)")
        
        # Multiclassing validation
        if character.is_multiclass:
            for class_name, level in character.character_classes.items():
                if level < 1:
                    issues.append(f"Invalid level for {class_name}: {level}")
            
            # Check for early multiclassing
            if any(level < 3 for level in character.character_classes.values()):
                warnings.append("Multiclassing before level 3 may limit access to important class features")
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            validator_name="class_selection"
        )
    
    def _validate_equipment(self, character: Character) -> ValidationResult:
        """Validate character equipment."""
        issues = []
        warnings = []
        
        if not character.equipment:
            warnings.append("Character has no equipment")
        
        # Check for basic necessities
        has_weapon = any("weapon" in str(item).lower() for item in character.equipment)
        has_armor = any("armor" in str(item).lower() for item in character.equipment)
        
        if not has_weapon:
            warnings.append("Character has no weapons equipped")
        
        if not has_armor and character.total_level > 1:
            warnings.append("Character has no armor equipped")
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            validator_name="equipment"
        )
    
    def _validate_proficiencies(self, character: Character) -> ValidationResult:
        """Validate character proficiencies."""
        issues = []
        warnings = []
        
        # Check for reasonable number of skill proficiencies
        skill_count = len(character.skill_proficiencies)
        if skill_count == 0:
            warnings.append("Character has no skill proficiencies")
        elif skill_count > 10:
            warnings.append(f"Character has many skill proficiencies ({skill_count})")
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            validator_name="proficiencies"
        )
    
    def _generate_recommendations(self, issues: List[str], warnings: List[str], 
                                character: Character) -> List[str]:
        """Generate helpful recommendations based on validation results."""
        recommendations = []
        
        if issues:
            recommendations.append("❌ Fix all validation errors before finalizing character")
        
        if warnings:
            recommendations.append("⚠️ Review warnings to ensure character meets expectations")
        
        if not issues and not warnings:
            recommendations.append("✅ Character validation passed! Ready for gameplay")
        
        # Character-specific recommendations
        if character.total_level == 1:
            recommendations.append("💡 Consider your character's background and motivations")
        
        if character.is_multiclass:
            recommendations.append("📚 Review multiclass rules and prerequisites")
        
        return recommendations