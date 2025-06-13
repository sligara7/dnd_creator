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
    
from typing import Dict, Any, List
from ...core.abstractions.character_validator import ICharacterValidator
from ...core.constants.mechanics import DND5E_ABILITY_SCORES, DND5E_CLASSES, DND5E_SPECIES
from ...core.constants.validation import MIN_ABILITY_SCORE, MAX_ABILITY_SCORE, MAX_CHARACTER_LEVEL
from ..value_objects.validation_result import ValidationResult

class CoreCharacterValidator(ICharacterValidator):
    """Core D&D 5e character validation using framework abstractions."""
    
    @property
    def name(self) -> str:
        return "dnd5e_core"
    
    def get_validation_priority(self) -> int:
        return 1  # Run first
    
    def can_validate(self, character_data: Dict[str, Any]) -> bool:
        """Always can validate basic character structure."""
        return isinstance(character_data, dict)
    
    def validate(self, character_data: Dict[str, Any]) -> ValidationResult:
        """Validate core D&D 5e character requirements."""
        issues = []
        warnings = []
        recommendations = []
        
        # Basic required fields
        if not character_data.get("name"):
            issues.append("Character name is required")
        
        # Species validation
        species = character_data.get("species")
        if not species:
            issues.append("Character species is required")
        elif species not in DND5E_SPECIES:
            issues.append(f"Unknown species: {species}")
            recommendations.append(f"Valid species: {', '.join(DND5E_SPECIES)}")
        
        # Level validation
        level = character_data.get("level", 0)
        if not isinstance(level, int) or level < 1:
            issues.append("Character level must be at least 1")
        elif level > MAX_CHARACTER_LEVEL:
            issues.append(f"Character level cannot exceed {MAX_CHARACTER_LEVEL}")
        
        # Ability scores validation
        ability_scores = character_data.get("ability_scores", {})
        if not ability_scores:
            issues.append("Ability scores are required")
        else:
            for ability_name in DND5E_ABILITY_SCORES:
                if ability_name not in ability_scores:
                    issues.append(f"Missing ability score: {ability_name}")
                else:
                    score = ability_scores[ability_name]
                    if not isinstance(score, int):
                        issues.append(f"Invalid {ability_name} score: must be integer")
                    elif score < MIN_ABILITY_SCORE:
                        issues.append(f"{ability_name} score ({score}) below minimum ({MIN_ABILITY_SCORE})")
                    elif score > MAX_ABILITY_SCORE:
                        issues.append(f"{ability_name} score ({score}) above maximum ({MAX_ABILITY_SCORE})")
                    elif score < 8:
                        warnings.append(f"{ability_name.title()} score ({score}) is very low")
                        recommendations.append(f"Consider raising {ability_name} for better character effectiveness")
        
        # Class validation
        classes = character_data.get("classes", {})
        if not classes:
            issues.append("Character must have at least one class")
        else:
            total_class_levels = 0
            for class_name, class_level in classes.items():
                if class_name not in DND5E_CLASSES:
                    issues.append(f"Unknown class: {class_name}")
                elif not isinstance(class_level, int) or class_level < 1:
                    issues.append(f"Invalid level for {class_name}: {class_level}")
                else:
                    total_class_levels += class_level
            
            if total_class_levels != level:
                issues.append(f"Class levels ({total_class_levels}) don't match character level ({level})")
        
        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            validator_name=self.name,
            recommendations=recommendations
        )

class AbilityScoreValidator(ICharacterValidator):
    """Specialized validator for ability score rules."""
    
    @property
    def name(self) -> str:
        return "dnd5e_ability_scores"
    
    def get_validation_priority(self) -> int:
        return 2
    
    def can_validate(self, character_data: Dict[str, Any]) -> bool:
        return "ability_scores" in character_data
    
    def validate(self, character_data: Dict[str, Any]) -> ValidationResult:
        """Validate ability score generation methods and balance."""
        issues = []
        warnings = []
        recommendations = []
        
        ability_scores = character_data.get("ability_scores", {})
        if not ability_scores:
            return ValidationResult(
                valid=False,
                issues=["No ability scores to validate"],
                warnings=[],
                validator_name=self.name
            )
        
        scores = list(ability_scores.values())
        total_score = sum(scores)
        
        # Point buy validation (27 points)
        if self._is_point_buy(scores):
            recommendations.append("Character uses Point Buy system (balanced)")
        # Standard array validation
        elif sorted(scores) == [8, 10, 12, 13, 14, 15]:
            recommendations.append("Character uses Standard Array (balanced)")
        # Rolling validation
        else:
            if total_score < 60:
                warnings.append(f"Total ability scores ({total_score}) are quite low")
                recommendations.append("Consider using Point Buy or Standard Array for more balanced scores")
            elif total_score > 84:  # Extremely high rolls
                warnings.append(f"Total ability scores ({total_score}) are exceptionally high")
                recommendations.append("Verify these scores were generated legitimately")
        
        # Check for dump stats
        min_score = min(scores)
        if min_score < 6:
            warnings.append(f"Minimum ability score ({min_score}) is extremely low")
            recommendations.append("Consider the roleplay implications of very low ability scores")
        
        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            validator_name=self.name,
            recommendations=recommendations
        )
    
    def _is_point_buy(self, scores: List[int]) -> bool:
        """Check if scores follow point buy rules."""
        point_buy_costs = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
        total_cost = sum(point_buy_costs.get(score, 999) for score in scores)
        return total_cost == 27

class MulticlassValidator(ICharacterValidator):
    """Validator for multiclassing prerequisites."""
    
    @property
    def name(self) -> str:
        return "dnd5e_multiclass"
    
    def get_validation_priority(self) -> int:
        return 3
    
    def can_validate(self, character_data: Dict[str, Any]) -> bool:
        classes = character_data.get("classes", {})
        return len(classes) > 1
    
    def validate(self, character_data: Dict[str, Any]) -> ValidationResult:
        """Validate multiclassing prerequisites and balance."""
        issues = []
        warnings = []
        recommendations = []
        
        classes = character_data.get("classes", {})
        ability_scores = character_data.get("ability_scores", {})
        
        # Check multiclassing prerequisites
        multiclass_requirements = {
            "barbarian": ("strength", 13),
            "bard": ("charisma", 13),
            "cleric": ("wisdom", 13),
            "druid": ("wisdom", 13),
            "fighter": ("strength", 13),  # or dexterity 13
            "monk": ("dexterity", 13),  # and wisdom 13
            "paladin": ("strength", 13),  # and charisma 13
            "ranger": ("dexterity", 13),  # and wisdom 13
            "rogue": ("dexterity", 13),
            "sorcerer": ("charisma", 13),
            "warlock": ("charisma", 13),
            "wizard": ("intelligence", 13)
        }
        
        for class_name in classes.keys():
            if class_name in multiclass_requirements:
                req_ability, req_score = multiclass_requirements[class_name]
                actual_score = ability_scores.get(req_ability, 0)
                if actual_score < req_score:
                    issues.append(f"Multiclass {class_name} requires {req_ability} {req_score}, but character has {actual_score}")
        
        # Warn about multiclassing complexity
        if len(classes) > 2:
            warnings.append("Multiclassing with 3+ classes can be complex for new players")
            recommendations.append("Consider focusing on 1-2 classes for simpler gameplay")
        
        # Check for early multiclassing
        for class_name, level in classes.items():
            if level < 3 and len(classes) > 1:
                warnings.append(f"{class_name} multiclassed before level 3 - missing core class features")
        
        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            validator_name=self.name,
            recommendations=recommendations
        )