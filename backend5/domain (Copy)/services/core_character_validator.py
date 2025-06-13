from typing import List
from ..services.validation_service import CharacterValidator, ValidationResult
from ...core.entities.character import Character

class CoreCharacterValidator:
    """Core character validation following D&D 5e rules."""
    
    name = "core_rules"
    
    def validate(self, character: Character) -> ValidationResult:
        """Validate character against core D&D rules."""
        issues = []
        warnings = []
        
        # Basic identity validation
        if not character.name.strip():
            warnings.append("Character name is empty")
        
        if not character.species:
            issues.append("Character species is required")
        
        # Level validation
        if character.total_level < 1:
            issues.append("Character must have at least 1 level")
        elif character.total_level > 20:
            issues.append("Character level cannot exceed 20")
        
        # Ability score validation
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            score = character.get_ability_score_value(ability)
            if score < 1 or score > 30:
                issues.append(f"{ability.title()} score ({score}) must be between 1-30")
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            validator_name=self.name
        )

# filepath: /home/ajs7/dnd_tools/dnd_char_creator/backend5/domain/validators/multiclass_validator.py
class MulticlassValidator:
    """Validator for multiclass character rules."""
    
    name = "multiclass_rules"
    
    def validate(self, character: Character) -> ValidationResult:
        """Validate multiclass requirements."""
        issues = []
        warnings = []
        
        if not character.is_multiclass:
            return ValidationResult(
                is_valid=True,
                issues=[],
                warnings=[],
                validator_name=self.name
            )
        
        # Multiclass prerequisite validation would go here
        # This would require access to multiclass rules
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            validator_name=self.name
        )

# filepath: /home/ajs7/dnd_tools/dnd_char_creator/backend5/domain/validators/optimization_validator.py
class OptimizationValidator:
    """Validator for character optimization suggestions."""
    
    name = "optimization"
    
    def validate(self, character: Character) -> ValidationResult:
        """Provide optimization suggestions."""
        issues = []
        warnings = []
        
        # Check for odd ability scores (optimization opportunity)
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            score = character.get_ability_score_value(ability)
            if score % 2 == 1 and score < 20:
                warnings.append(f"Consider improving {ability} from {score} to {score + 1} for better modifier")
        
        return ValidationResult(
            is_valid=True,  # Optimization warnings don't make character invalid
            issues=issues,
            warnings=warnings,
            validator_name=self.name
        )