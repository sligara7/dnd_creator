from typing import Dict, List, Any, Optional, Protocol, Callable
from abc import ABC, abstractmethod
import logging

from ...core.entities.character import Character
from ...core.value_objects.validation_result import ValidationResult, ValidationIssue, ValidationSeverity
from ..rules.validation_rules import ValidationRules

logger = logging.getLogger(__name__)

class ValidationRule(Protocol):
    """Protocol for validation rules."""
    
    def validate(self, character: Character, context: Dict[str, Any]) -> List[ValidationIssue]:
        """Execute validation rule."""
        ...
    
    @property
    def rule_name(self) -> str:
        """Name of the validation rule."""
        ...

class CharacterValidationEngine:
    """
    Core validation engine for D&D characters.
    
    This service orchestrates multiple validation rules and provides
    comprehensive character validation with detailed reporting.
    """
    
    def __init__(self, validation_rules: ValidationRules):
        self.rules = validation_rules
        self.custom_validators: List[ValidationRule] = []
        self.validation_cache: Dict[str, ValidationResult] = {}
    
    def validate_character_comprehensive(self, character: Character, 
                                       context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Perform comprehensive character validation.
        
        Args:
            character: Character to validate
            context: Additional validation context
            
        Returns:
            ValidationResult with all validation issues
        """
        context = context or {}
        all_issues = []
        
        # Core D&D rules validation
        core_issues = self._validate_core_rules(character, context)
        all_issues.extend(core_issues)
        
        # Class-specific validation
        class_issues = self._validate_class_rules(character, context)
        all_issues.extend(class_issues)
        
        # Species-specific validation
        species_issues = self._validate_species_rules(character, context)
        all_issues.extend(species_issues)
        
        # Equipment validation
        equipment_issues = self._validate_equipment_rules(character, context)
        all_issues.extend(equipment_issues)
        
        # Spell validation
        if character.is_spellcaster:
            spell_issues = self._validate_spell_rules(character, context)
            all_issues.extend(spell_issues)
        
        # Multiclass validation
        if character.is_multiclass:
            multiclass_issues = self._validate_multiclass_rules(character, context)
            all_issues.extend(multiclass_issues)
        
        # Custom validation rules
        custom_issues = self._validate_custom_rules(character, context)
        all_issues.extend(custom_issues)
        
        # Determine overall validity
        is_valid = not any(issue.is_blocking for issue in all_issues)
        
        return ValidationResult(
            is_valid=is_valid,
            issues=all_issues,
            validator_name="comprehensive_validation",
            context=context
        )
    
    def validate_character_creation_step(self, character: Character, step: str,
                                       context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate specific character creation step.
        
        Args:
            character: Character to validate
            step: Creation step to validate
            context: Additional context
            
        Returns:
            ValidationResult for the specific step
        """
        context = context or {}
        
        step_validators = {
            "ability_scores": self._validate_ability_scores_step,
            "species_selection": self._validate_species_selection_step,
            "class_selection": self._validate_class_selection_step,
            "background_selection": self._validate_background_selection_step,
            "equipment_selection": self._validate_equipment_selection_step,
            "spell_selection": self._validate_spell_selection_step,
            "final_review": self._validate_final_review_step
        }
        
        validator = step_validators.get(step)
        if not validator:
            return ValidationResult(
                is_valid=False,
                issues=[ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="UNKNOWN_STEP",
                    message=f"Unknown validation step: {step}"
                )],
                validator_name=f"step_{step}"
            )
        
        issues = validator(character, context)
        is_valid = not any(issue.is_blocking for issue in issues)
        
        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            validator_name=f"step_{step}",
            context=context
        )
    
    def validate_character_optimization(self, character: Character) -> ValidationResult:
        """
        Validate character for optimization opportunities.
        
        Args:
            character: Character to analyze
            
        Returns:
            ValidationResult with optimization suggestions
        """
        issues = []
        
        # Ability score optimization
        ability_suggestions = self._analyze_ability_score_optimization(character)
        issues.extend(ability_suggestions)
        
        # Feat optimization
        feat_suggestions = self._analyze_feat_optimization(character)
        issues.extend(feat_suggestions)
        
        # Equipment optimization
        equipment_suggestions = self._analyze_equipment_optimization(character)
        issues.extend(equipment_suggestions)
        
        # Spell optimization
        if character.is_spellcaster:
            spell_suggestions = self._analyze_spell_optimization(character)
            issues.extend(spell_suggestions)
        
        return ValidationResult(
            is_valid=True,  # Optimization suggestions don't invalidate character
            issues=issues,
            validator_name="optimization_analysis"
        )
    
    def add_custom_validator(self, validator: ValidationRule) -> None:
        """Add custom validation rule."""
        self.custom_validators.append(validator)
    
    def get_validation_report(self, validation_result: ValidationResult) -> str:
        """Generate detailed validation report."""
        if validation_result.is_valid:
            return "✅ Character validation passed successfully!"
        
        report_lines = ["❌ Character validation failed:"]
        
        # Group issues by severity
        errors = validation_result.errors
        warnings = validation_result.warnings
        
        if errors:
            report_lines.append(f"\n🚫 Errors ({len(errors)}):")
            for issue in errors:
                report_lines.append(f"  • {issue.message}")
                if issue.suggested_fix:
                    report_lines.append(f"    💡 Suggestion: {issue.suggested_fix}")
        
        if warnings:
            report_lines.append(f"\n⚠️  Warnings ({len(warnings)}):")
            for issue in warnings:
                report_lines.append(f"  • {issue.message}")
                if issue.suggested_fix:
                    report_lines.append(f"    💡 Suggestion: {issue.suggested_fix}")
        
        return "\n".join(report_lines)
    
    # === Private Validation Methods ===
    
    def _validate_core_rules(self, character: Character, context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate core D&D rules."""
        issues = []
        
        # Basic identity validation
        if not character.name.strip():
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="EMPTY_NAME",
                message="Character name is empty",
                suggested_fix="Enter a character name"
            ))
        
        # Level validation
        if character.total_level < 1:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="INVALID_LEVEL",
                message="Character must have at least 1 level",
                suggested_fix="Add at least one class level"
            ))
        elif character.total_level > 20:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="LEVEL_TOO_HIGH",
                message=f"Character level ({character.total_level}) exceeds maximum (20)",
                suggested_fix="Reduce total character level to 20 or below"
            ))
        
        # Ability score validation
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            score = character.get_ability_score_value(ability)
            if score < 1 or score > 30:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="INVALID_ABILITY_SCORE",
                    message=f"{ability.title()} score ({score}) must be between 1-30",
                    field=ability,
                    suggested_fix="Adjust ability score to valid range (1-30)"
                ))
        
        return issues
    
    def _validate_class_rules(self, character: Character, context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate class-specific rules."""
        issues = []
        
        if not character.character_classes:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="NO_CLASSES",
                message="Character must have at least one class",
                suggested_fix="Select a character class"
            ))
            return issues
        
        for class_name, level in character.character_classes.items():
            if level < 1 or level > 20:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="INVALID_CLASS_LEVEL",
                    message=f"Invalid level for {class_name}: {level}",
                    field=f"classes.{class_name}",
                    suggested_fix="Set class level between 1-20"
                ))
            
            # Class-specific validation
            class_issues = self.rules.validate_class_requirements(character, class_name, level)
            issues.extend(class_issues)
        
        return issues
    
    def _validate_species_rules(self, character: Character, context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate species-specific rules."""
        issues = []
        
        if not character.species:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="NO_SPECIES",
                message="Character must have a species",
                suggested_fix="Select a character species"
            ))
            return issues
        
        # Species-specific validation
        species_issues = self.rules.validate_species_requirements(character, character.species)
        issues.extend(species_issues)
        
        return issues
    
    def _validate_multiclass_rules(self, character: Character, context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate multiclass requirements."""
        issues = []
        
        for class_name in character.character_classes.keys():
            multiclass_issues = self.rules.validate_multiclass_prerequisites(character, class_name)
            issues.extend(multiclass_issues)
        
        return issues
    
    def _validate_equipment_rules(self, character: Character, context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate equipment rules."""
        issues = []
        
        # Basic equipment validation
        equipment_issues = self.rules.validate_equipment_proficiencies(character)
        issues.extend(equipment_issues)
        
        return issues
    
    def _validate_spell_rules(self, character: Character, context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate spell rules."""
        issues = []
        
        # Spell validation
        spell_issues = self.rules.validate_spell_requirements(character)
        issues.extend(spell_issues)
        
        return issues
    
    def _validate_custom_rules(self, character: Character, context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate using custom rules."""
        issues = []
        
        for validator in self.custom_validators:
            try:
                custom_issues = validator.validate(character, context)
                issues.extend(custom_issues)
            except Exception as e:
                logger.error(f"Custom validator {validator.rule_name} failed: {e}")
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="CUSTOM_VALIDATOR_ERROR",
                    message=f"Custom validator '{validator.rule_name}' failed: {str(e)}"
                ))
        
        return issues
    
    # === Step-specific validation methods ===
    
    def _validate_ability_scores_step(self, character: Character, context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate ability scores step."""
        issues = []
        
        # Point buy validation if specified
        if context.get("method") == "point_buy":
            point_buy_issues = self.rules.validate_point_buy_scores(character)
            issues.extend(point_buy_issues)
        
        return issues
    
    def _validate_species_selection_step(self, character: Character, context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate species selection step."""
        return self._validate_species_rules(character, context)
    
    def _validate_class_selection_step(self, character: Character, context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate class selection step."""
        return self._validate_class_rules(character, context)
    
    def _validate_background_selection_step(self, character: Character, context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate background selection step."""
        issues = []
        
        if not character.background:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="NO_BACKGROUND",
                message="Character has no background selected",
                suggested_fix="Select a character background"
            ))
        
        return issues
    
    def _validate_equipment_selection_step(self, character: Character, context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate equipment selection step."""
        return self._validate_equipment_rules(character, context)
    
    def _validate_spell_selection_step(self, character: Character, context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate spell selection step."""
        if character.is_spellcaster:
            return self._validate_spell_rules(character, context)
        return []
    
    def _validate_final_review_step(self, character: Character, context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate final review step."""
        # Run comprehensive validation for final review
        result = self.validate_character_comprehensive(character, context)
        return result.issues
    
    # === Optimization analysis methods ===
    
    def _analyze_ability_score_optimization(self, character: Character) -> List[ValidationIssue]:
        """Analyze ability score optimization opportunities."""
        issues = []
        
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            score = character.get_ability_score_value(ability)
            if score % 2 == 1 and score < 20:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    code="ODD_ABILITY_SCORE",
                    message=f"{ability.title()} score ({score}) is odd - consider increasing to {score + 1}",
                    field=ability,
                    suggested_fix="Increase by 1 for better modifier"
                ))
        
        return issues
    
    def _analyze_feat_optimization(self, character: Character) -> List[ValidationIssue]:
        """Analyze feat optimization opportunities."""
        issues = []
        # Feat analysis logic would go here
        return issues
    
    def _analyze_equipment_optimization(self, character: Character) -> List[ValidationIssue]:
        """Analyze equipment optimization opportunities."""
        issues = []
        # Equipment optimization logic would go here
        return issues
    
    def _analyze_spell_optimization(self, character: Character) -> List[ValidationIssue]:
        """Analyze spell optimization opportunities."""
        issues = []
        # Spell optimization logic would go here
        return issues