"""
Balance and Validation Exceptions for the D&D Creative Content Framework.

This module defines exceptions related to D&D 5e/2024 rule violations,
content balance failures, power level issues, and validation pipeline problems.
These exceptions represent business rule violations and failure states
in the D&D content validation domain.

Following Clean Architecture principles, these exceptions are:
- Infrastructure-independent (don't depend on specific validation engines)
- Focused on D&D balance and validation business rules
- Designed for proper error handling and recovery strategies
- Aligned with the content validation and balance checking workflow
"""

from typing import Dict, List, Optional, Any, Union
from ..enums.balance_levels import BalanceLevel, PowerTier, BalanceMode
from ..enums.content_types import ContentType, ContentRarity, ThemeCategory
from ..enums.validation_types import ValidationType, ValidationSeverity, RuleCompliance
from ..enums.game_mechanics import AbilityScore, Skill, SavingThrow, DamageType, Condition


# ============ BASE BALANCE AND VALIDATION EXCEPTIONS ============

class BalanceError(Exception):
    """Base exception for all balance and validation errors."""
    
    def __init__(
        self,
        message: str,
        content_type: Optional[ContentType] = None,
        balance_level: Optional[BalanceLevel] = None,
        power_tier: Optional[PowerTier] = None,
        context: Optional[Dict[str, Any]] = None,
        recovery_suggestions: Optional[List[str]] = None
    ):
        super().__init__(message)
        self.content_type = content_type
        self.balance_level = balance_level
        self.power_tier = power_tier
        self.context = context or {}
        self.recovery_suggestions = recovery_suggestions or []
    
    def __str__(self) -> str:
        parts = [super().__str__()]
        
        if self.content_type:
            parts.append(f"Content: {self.content_type.value}")
        
        if self.balance_level:
            parts.append(f"Balance: {self.balance_level.value}")
        
        if self.power_tier:
            parts.append(f"Tier: {self.power_tier.value}")
        
        if self.recovery_suggestions:
            parts.append(f"Suggestions: {'; '.join(self.recovery_suggestions[:2])}")
        
        return " | ".join(parts)

    def add_context(self, key: str, value: Any) -> None:
        """Add contextual information to the exception."""
        self.context[key] = value

    def add_recovery_suggestion(self, suggestion: str) -> None:
        """Add a recovery suggestion to the exception."""
        if suggestion not in self.recovery_suggestions:
            self.recovery_suggestions.append(suggestion)


class ValidationError(BalanceError):
    """Base exception for validation failures."""
    
    def __init__(
        self,
        message: str,
        validation_type: Optional[ValidationType] = None,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        rule_name: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.validation_type = validation_type
        self.severity = severity
        self.field_name = field_name
        self.field_value = field_value
        self.rule_name = rule_name
    
    def __str__(self) -> str:
        parts = [super().__str__()]
        
        if self.validation_type:
            parts.append(f"Type: {self.validation_type.value}")
        
        parts.append(f"Severity: {self.severity.value}")
        
        if self.field_name:
            parts.append(f"Field: {self.field_name}")
        
        if self.rule_name:
            parts.append(f"Rule: {self.rule_name}")
        
        return " | ".join(parts)


# ============ D&D RULE VIOLATION EXCEPTIONS ============

class RuleViolationError(ValidationError):
    """Exception for D&D 5e/2024 rule violations."""
    
    def __init__(
        self,
        rule_name: str,
        rule_description: str,
        compliance_level: RuleCompliance = RuleCompliance.CORE_RULES,
        violating_value: Optional[Any] = None,
        expected_value: Optional[Any] = None,
        **kwargs
    ):
        message = f"D&D rule violation: {rule_description}"
        if violating_value is not None and expected_value is not None:
            message += f" (got: {violating_value}, expected: {expected_value})"
        
        super().__init__(
            message,
            validation_type=ValidationType.RULE_COMPLIANCE,
            rule_name=rule_name,
            **kwargs
        )
        self.rule_description = rule_description
        self.compliance_level = compliance_level
        self.violating_value = violating_value
        self.expected_value = expected_value


class AbilityScoreViolation(RuleViolationError):
    """Exception for ability score rule violations."""
    
    def __init__(
        self,
        ability: Union[str, AbilityScore],
        score: int,
        min_allowed: Optional[int] = None,
        max_allowed: Optional[int] = None,
        character_level: Optional[int] = None,
        **kwargs
    ):
        ability_name = ability.value if isinstance(ability, AbilityScore) else ability
        
        if min_allowed is not None and score < min_allowed:
            rule_desc = f"{ability_name} score {score} below minimum {min_allowed}"
        elif max_allowed is not None and score > max_allowed:
            rule_desc = f"{ability_name} score {score} above maximum {max_allowed}"
        else:
            rule_desc = f"Invalid {ability_name} score: {score}"
        
        if character_level:
            rule_desc += f" at level {character_level}"
        
        super().__init__(
            rule_name="ability_score_limits",
            rule_description=rule_desc,
            field_name=f"ability_scores.{ability_name.lower()}",
            field_value=score,
            violating_value=score,
            expected_value=f"{min_allowed}-{max_allowed}" if min_allowed and max_allowed else None,
            **kwargs
        )
        self.ability = ability_name
        self.score = score
        self.min_allowed = min_allowed
        self.max_allowed = max_allowed
        self.character_level = character_level


class CharacterLevelViolation(RuleViolationError):
    """Exception for character level rule violations."""
    
    def __init__(
        self,
        current_level: int,
        violation_type: str,
        class_levels: Optional[Dict[str, int]] = None,
        max_level: int = 20,
        **kwargs
    ):
        if violation_type == "exceeds_maximum":
            rule_desc = f"Character level {current_level} exceeds maximum ({max_level})"
        elif violation_type == "below_minimum":
            rule_desc = f"Character level {current_level} below minimum (1)"
        elif violation_type == "multiclass_mismatch":
            total_class_levels = sum(class_levels.values()) if class_levels else 0
            rule_desc = f"Character level {current_level} doesn't match sum of class levels ({total_class_levels})"
        else:
            rule_desc = f"Invalid character level: {current_level} ({violation_type})"
        
        super().__init__(
            rule_name="character_level_limits",
            rule_description=rule_desc,
            field_name="character_level",
            field_value=current_level,
            violating_value=current_level,
            expected_value=f"1-{max_level}" if violation_type != "multiclass_mismatch" else total_class_levels,
            **kwargs
        )
        self.current_level = current_level
        self.violation_type = violation_type
        self.class_levels = class_levels or {}
        self.max_level = max_level


class MulticlassViolation(RuleViolationError):
    """Exception for multiclassing rule violations."""
    
    def __init__(
        self,
        class_name: str,
        violation_type: str,
        required_abilities: Optional[Dict[str, int]] = None,
        current_abilities: Optional[Dict[str, int]] = None,
        **kwargs
    ):
        if violation_type == "prerequisite_not_met":
            rule_desc = f"Multiclassing into {class_name} requires: "
            if required_abilities:
                reqs = [f"{ability.title()} {score}+" for ability, score in required_abilities.items()]
                rule_desc += ", ".join(reqs)
            
            if current_abilities:
                current = [f"{ability.title()} {score}" for ability, score in current_abilities.items()]
                rule_desc += f" (current: {', '.join(current)})"
        elif violation_type == "invalid_class":
            rule_desc = f"Cannot multiclass into unknown class: {class_name}"
        else:
            rule_desc = f"Multiclassing violation for {class_name}: {violation_type}"
        
        super().__init__(
            rule_name="multiclass_prerequisites",
            rule_description=rule_desc,
            field_name="multiclass_requirements",
            field_value=class_name,
            **kwargs
        )
        self.class_name = class_name
        self.violation_type = violation_type
        self.required_abilities = required_abilities or {}
        self.current_abilities = current_abilities or {}


class ProficiencyViolation(RuleViolationError):
    """Exception for proficiency rule violations."""
    
    def __init__(
        self,
        proficiency_type: str,
        item: str,
        character_level: Optional[int] = None,
        expected_bonus: Optional[int] = None,
        actual_bonus: Optional[int] = None,
        **kwargs
    ):
        if proficiency_type == "bonus_calculation":
            rule_desc = f"Proficiency bonus should be +{expected_bonus} at level {character_level}, not +{actual_bonus}"
        elif proficiency_type == "invalid_proficiency":
            rule_desc = f"Character is not proficient with {item}"
        elif proficiency_type == "duplicate_proficiency":
            rule_desc = f"Duplicate proficiency: {item}"
        elif proficiency_type == "conflicting_expertise":
            rule_desc = f"Cannot have expertise in {item} without proficiency"
        else:
            rule_desc = f"Proficiency violation with {item}: {proficiency_type}"
        
        super().__init__(
            rule_name="proficiency_rules",
            rule_description=rule_desc,
            field_name="proficiencies",
            field_value=item,
            **kwargs
        )
        self.proficiency_type = proficiency_type
        self.item = item
        self.character_level = character_level
        self.expected_bonus = expected_bonus
        self.actual_bonus = actual_bonus


class SpellcastingViolation(RuleViolationError):
    """Exception for spellcasting rule violations."""
    
    def __init__(
        self,
        violation_type: str,
        spell_name: Optional[str] = None,
        spell_level: Optional[int] = None,
        caster_level: Optional[int] = None,
        spellcasting_class: Optional[str] = None,
        available_slots: Optional[Dict[int, int]] = None,
        **kwargs
    ):
        if violation_type == "insufficient_level":
            rule_desc = f"Caster level {caster_level} insufficient for {spell_level}-level spell '{spell_name}'"
        elif violation_type == "no_spell_slots":
            rule_desc = f"No available {spell_level}-level spell slots for '{spell_name}'"
        elif violation_type == "unknown_spell":
            rule_desc = f"Spell '{spell_name}' not known by {spellcasting_class}"
        elif violation_type == "invalid_spell_level":
            rule_desc = f"Invalid spell level: {spell_level} (must be 0-9)"
        elif violation_type == "concentration_conflict":
            rule_desc = f"Cannot cast concentration spell '{spell_name}' while concentrating"
        else:
            rule_desc = f"Spellcasting violation: {violation_type}"
            if spell_name:
                rule_desc += f" (spell: {spell_name})"
        
        super().__init__(
            rule_name="spellcasting_rules",
            rule_description=rule_desc,
            field_name="spellcasting",
            field_value=spell_name,
            **kwargs
        )
        self.violation_type = violation_type
        self.spell_name = spell_name
        self.spell_level = spell_level
        self.caster_level = caster_level
        self.spellcasting_class = spellcasting_class
        self.available_slots = available_slots or {}


# ============ CONTENT BALANCE EXCEPTIONS ============

class ContentBalanceError(BalanceError):
    """Exception for content balance violations."""
    
    def __init__(
        self,
        content_name: str,
        balance_issue: str,
        power_level: Optional[float] = None,
        expected_power_range: Optional[tuple] = None,
        rarity: Optional[ContentRarity] = None,
        **kwargs
    ):
        message = f"Content balance violation for '{content_name}': {balance_issue}"
        if power_level and expected_power_range:
            message += f" (power: {power_level:.2f}, expected: {expected_power_range[0]:.2f}-{expected_power_range[1]:.2f})"
        
        super().__init__(message, **kwargs)
        self.content_name = content_name
        self.balance_issue = balance_issue
        self.power_level = power_level
        self.expected_power_range = expected_power_range
        self.rarity = rarity


class PowerLevelViolation(ContentBalanceError):
    """Exception for power level balance violations."""
    
    def __init__(
        self,
        content_name: str,
        violation_type: str,
        actual_power: float,
        expected_power: float,
        tolerance: float = 0.1,
        **kwargs
    ):
        power_diff = abs(actual_power - expected_power)
        percentage_diff = (power_diff / expected_power) * 100
        
        if violation_type == "overpowered":
            balance_issue = f"Content is overpowered by {percentage_diff:.1f}%"
        elif violation_type == "underpowered":
            balance_issue = f"Content is underpowered by {percentage_diff:.1f}%"
        else:
            balance_issue = f"Power level violation: {violation_type}"
        
        super().__init__(
            content_name=content_name,
            balance_issue=balance_issue,
            power_level=actual_power,
            expected_power_range=(expected_power - tolerance, expected_power + tolerance),
            **kwargs
        )
        self.violation_type = violation_type
        self.actual_power = actual_power
        self.expected_power = expected_power
        self.tolerance = tolerance
        self.power_difference = power_diff


class RarityMismatchError(ContentBalanceError):
    """Exception for content rarity vs power level mismatches."""
    
    def __init__(
        self,
        content_name: str,
        declared_rarity: ContentRarity,
        actual_power_rarity: ContentRarity,
        power_level: float,
        **kwargs
    ):
        balance_issue = f"Declared rarity ({declared_rarity.value}) doesn't match power level rarity ({actual_power_rarity.value})"
        
        super().__init__(
            content_name=content_name,
            balance_issue=balance_issue,
            power_level=power_level,
            rarity=declared_rarity,
            **kwargs
        )
        self.declared_rarity = declared_rarity
        self.actual_power_rarity = actual_power_rarity


class ThemeConsistencyError(ContentBalanceError):
    """Exception for theme consistency violations."""
    
    def __init__(
        self,
        content_name: str,
        theme_issue: str,
        conflicting_themes: Optional[List[ThemeCategory]] = None,
        expected_themes: Optional[List[ThemeCategory]] = None,
        **kwargs
    ):
        balance_issue = f"Theme consistency violation: {theme_issue}"
        if conflicting_themes:
            theme_names = [theme.value for theme in conflicting_themes]
            balance_issue += f" (conflicting: {', '.join(theme_names)})"
        
        super().__init__(
            content_name=content_name,
            balance_issue=balance_issue,
            **kwargs
        )
        self.theme_issue = theme_issue
        self.conflicting_themes = conflicting_themes or []
        self.expected_themes = expected_themes or []


class MechanicalComplexityError(ContentBalanceError):
    """Exception for mechanical complexity violations."""
    
    def __init__(
        self,
        content_name: str,
        complexity_issue: str,
        actual_complexity: Optional[int] = None,
        max_complexity: Optional[int] = None,
        **kwargs
    ):
        if actual_complexity and max_complexity:
            balance_issue = f"Mechanical complexity {actual_complexity} exceeds maximum {max_complexity}: {complexity_issue}"
        else:
            balance_issue = f"Mechanical complexity violation: {complexity_issue}"
        
        super().__init__(
            content_name=content_name,
            balance_issue=balance_issue,
            **kwargs
        )
        self.complexity_issue = complexity_issue
        self.actual_complexity = actual_complexity
        self.max_complexity = max_complexity


# ============ VALIDATION PIPELINE EXCEPTIONS ============

class ValidationPipelineError(ValidationError):
    """Exception for validation pipeline failures."""
    
    def __init__(
        self,
        pipeline_stage: str,
        pipeline_issue: str,
        stage_input: Optional[Dict[str, Any]] = None,
        stage_output: Optional[Dict[str, Any]] = None,
        stage_errors: Optional[List[ValidationError]] = None,
        **kwargs
    ):
        message = f"Validation pipeline failed at {pipeline_stage}: {pipeline_issue}"
        if stage_errors:
            message += f" ({len(stage_errors)} stage errors)"
        
        super().__init__(
            message,
            validation_type=ValidationType.PIPELINE,
            **kwargs
        )
        self.pipeline_stage = pipeline_stage
        self.pipeline_issue = pipeline_issue
        self.stage_input = stage_input or {}
        self.stage_output = stage_output or {}
        self.stage_errors = stage_errors or []


class SchemaValidationError(ValidationError):
    """Exception for schema validation failures."""
    
    def __init__(
        self,
        schema_name: str,
        schema_version: Optional[str] = None,
        validation_errors: Optional[List[str]] = None,
        invalid_fields: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Schema validation failed for {schema_name}"
        if schema_version:
            message += f" (version {schema_version})"
        
        if validation_errors:
            message += f": {'; '.join(validation_errors[:3])}"
            if len(validation_errors) > 3:
                message += f" (and {len(validation_errors) - 3} more)"
        
        super().__init__(
            message,
            validation_type=ValidationType.SCHEMA,
            **kwargs
        )
        self.schema_name = schema_name
        self.schema_version = schema_version
        self.validation_errors = validation_errors or []
        self.invalid_fields = invalid_fields or []


class FieldValidationError(ValidationError):
    """Exception for individual field validation failures."""
    
    def __init__(
        self,
        field_name: str,
        field_value: Any,
        constraint_type: str,
        constraint_value: Optional[Any] = None,
        constraint_description: Optional[str] = None,
        **kwargs
    ):
        if constraint_type == "required":
            message = f"Required field '{field_name}' is missing or empty"
        elif constraint_type == "type":
            expected_type = constraint_value if isinstance(constraint_value, str) else type(constraint_value).__name__
            actual_type = type(field_value).__name__
            message = f"Field '{field_name}' has invalid type: expected {expected_type}, got {actual_type}"
        elif constraint_type == "length":
            message = f"Field '{field_name}' length constraint violated"
            if constraint_description:
                message += f": {constraint_description}"
        elif constraint_type == "range":
            message = f"Field '{field_name}' value {field_value} outside allowed range"
            if constraint_value:
                message += f": {constraint_value}"
        elif constraint_type == "pattern":
            message = f"Field '{field_name}' doesn't match required pattern"
        elif constraint_type == "enum":
            message = f"Field '{field_name}' value '{field_value}' not in allowed values"
            if constraint_value:
                message += f": {constraint_value}"
        else:
            message = f"Field '{field_name}' validation failed: {constraint_type}"
        
        super().__init__(
            message,
            validation_type=ValidationType.FIELD,
            field_name=field_name,
            field_value=field_value,
            **kwargs
        )
        self.constraint_type = constraint_type
        self.constraint_value = constraint_value
        self.constraint_description = constraint_description


class DataIntegrityError(ValidationError):
    """Exception for data integrity validation failures."""
    
    def __init__(
        self,
        integrity_type: str,
        integrity_description: str,
        affected_fields: Optional[List[str]] = None,
        integrity_constraints: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Data integrity violation: {integrity_description}"
        if affected_fields:
            message += f" (affects: {', '.join(affected_fields)})"
        
        super().__init__(
            message,
            validation_type=ValidationType.INTEGRITY,
            **kwargs
        )
        self.integrity_type = integrity_type
        self.integrity_description = integrity_description
        self.affected_fields = affected_fields or []
        self.integrity_constraints = integrity_constraints or {}


class ReferenceValidationError(ValidationError):
    """Exception for reference/relationship validation failures."""
    
    def __init__(
        self,
        reference_field: str,
        reference_value: Any,
        target_type: str,
        reference_type: str = "foreign_key",
        target_constraints: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        if reference_type == "foreign_key":
            message = f"Foreign key reference failed: {reference_field}='{reference_value}' not found in {target_type}"
        elif reference_type == "circular":
            message = f"Circular reference detected in {reference_field}: {reference_value}"
        elif reference_type == "orphaned":
            message = f"Orphaned reference in {reference_field}: {reference_value} has no parent"
        elif reference_type == "invalid_target":
            message = f"Invalid reference target in {reference_field}: {reference_value}"
        else:
            message = f"Reference validation failed for {reference_field}: {reference_type}"
        
        super().__init__(
            message,
            validation_type=ValidationType.REFERENCE,
            field_name=reference_field,
            field_value=reference_value,
            **kwargs
        )
        self.reference_field = reference_field
        self.reference_value = reference_value
        self.target_type = target_type
        self.reference_type = reference_type
        self.target_constraints = target_constraints or {}


# ============ VALIDATION RESULT CLASSES ============

class ValidationResult:
    """Container for validation results with enhanced reporting capabilities."""
    
    def __init__(
        self,
        is_valid: bool = True,
        errors: Optional[List[ValidationError]] = None,
        warnings: Optional[List[ValidationError]] = None,
        info: Optional[List[ValidationError]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.info = info or []
        self.context = context or {}
        self._update_validity()
    
    def _update_validity(self):
        """Update validity based on current errors."""
        self.is_valid = len(self.errors) == 0
    
    @property
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
    
    @property
    def has_info(self) -> bool:
        """Check if there are any info messages."""
        return len(self.info) > 0
    
    @property
    def total_issues(self) -> int:
        """Get total count of all issues."""
        return len(self.errors) + len(self.warnings) + len(self.info)
    
    @property
    def critical_errors(self) -> List[ValidationError]:
        """Get all critical errors."""
        return [error for error in self.errors if error.severity == ValidationSeverity.CRITICAL]
    
    @property
    def has_critical_errors(self) -> bool:
        """Check if there are any critical errors."""
        return len(self.critical_errors) > 0
    
    def add_error(self, error: ValidationError):
        """Add an error to the validation result."""
        self.errors.append(error)
        self._update_validity()
    
    def add_warning(self, warning: ValidationError):
        """Add a warning to the validation result."""
        self.warnings.append(warning)
    
    def add_info(self, info: ValidationError):
        """Add an info message to the validation result."""
        self.info.append(info)
    
    def merge(self, other: 'ValidationResult'):
        """Merge another validation result into this one."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)
        self.context.update(other.context)
        self._update_validity()
    
    def filter_by_severity(self, severity: ValidationSeverity) -> List[ValidationError]:
        """Get all issues with a specific severity level."""
        all_issues = self.errors + self.warnings + self.info
        return [issue for issue in all_issues if issue.severity == severity]
    
    def filter_by_type(self, validation_type: ValidationType) -> List[ValidationError]:
        """Get all issues of a specific validation type."""
        all_issues = self.errors + self.warnings + self.info
        return [issue for issue in all_issues if issue.validation_type == validation_type]
    
    def get_most_severe_error(self) -> Optional[ValidationError]:
        """Get the most severe error."""
        if not self.errors:
            return None
        return max(self.errors, key=lambda e: get_validation_severity_level(e))


class BalanceAnalysisResult(ValidationResult):
    """Extended validation result for balance analysis."""
    
    def __init__(
        self,
        balance_score: Optional[float] = None,
        power_level: Optional[float] = None,
        balance_mode: Optional[BalanceMode] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.balance_score = balance_score
        self.power_level = power_level
        self.balance_mode = balance_mode
    
    @property
    def is_balanced(self) -> bool:
        """Check if content is considered balanced."""
        return self.is_valid and self.balance_score is not None and self.balance_score >= 0.7
    
    @property
    def balance_quality(self) -> str:
        """Get balance quality assessment."""
        if self.balance_score is None:
            return "unknown"
        elif self.balance_score >= 0.9:
            return "excellent"
        elif self.balance_score >= 0.8:
            return "good"
        elif self.balance_score >= 0.7:
            return "acceptable"
        elif self.balance_score >= 0.6:
            return "questionable"
        else:
            return "poor"


# ============ UTILITY FUNCTIONS FOR EXCEPTION HANDLING ============

def categorize_balance_error(error: Exception) -> str:
    """
    Categorize a balance/validation error for handling and routing.
    
    Args:
        error: The exception to categorize
        
    Returns:
        Error category string
    """
    if isinstance(error, RuleViolationError):
        return "rule_violation"
    elif isinstance(error, ContentBalanceError):
        return "content_balance"
    elif isinstance(error, ValidationPipelineError):
        return "validation_pipeline"
    elif isinstance(error, SchemaValidationError):
        return "schema_validation"
    elif isinstance(error, FieldValidationError):
        return "field_validation"
    elif isinstance(error, DataIntegrityError):
        return "data_integrity"
    elif isinstance(error, ReferenceValidationError):
        return "reference_validation"
    elif isinstance(error, ValidationError):
        return "general_validation"
    elif isinstance(error, BalanceError):
        return "general_balance"
    else:
        return "unknown"


def get_validation_severity_level(error: ValidationError) -> int:
    """
    Get numeric severity level for sorting/prioritizing validation errors.
    
    Args:
        error: The validation error to assess
        
    Returns:
        Severity level (higher = more severe)
    """
    severity_map = {
        ValidationSeverity.INFO: 1,
        ValidationSeverity.WARNING: 2,
        ValidationSeverity.ERROR: 3,
        ValidationSeverity.CRITICAL: 4
    }
    
    return severity_map.get(error.severity, 2)


def is_critical_validation_error(error: ValidationError) -> bool:
    """
    Check if validation error is critical and should stop processing.
    
    Args:
        error: The validation error to check
        
    Returns:
        True if this is a critical error
    """
    return error.severity == ValidationSeverity.CRITICAL


def is_core_rule_violation(error: RuleViolationError) -> bool:
    """
    Check if violation is against core D&D rules vs optional/balance guidelines.
    
    Args:
        error: The rule violation to check
        
    Returns:
        True if this violates core D&D rules
    """
    return error.compliance_level == RuleCompliance.CORE_RULES


def suggest_balance_fix(error: BalanceError) -> List[str]:
    """
    Generate suggested fixes for a balance error.
    
    Args:
        error: The balance error to fix
        
    Returns:
        List of suggested fixes
    """
    suggestions = list(error.recovery_suggestions)
    
    if isinstance(error, PowerLevelViolation):
        if error.violation_type == "overpowered":
            suggestions.extend([
                f"Reduce power level by {error.power_difference:.2f}",
                "Add limitations or costs to abilities",
                "Increase resource requirements",
                "Reduce duration or frequency of use"
            ])
        elif error.violation_type == "underpowered":
            suggestions.extend([
                f"Increase power level by {error.power_difference:.2f}",
                "Add additional benefits or effects",
                "Reduce limitations or costs",
                "Increase duration or frequency of use"
            ])
    
    elif isinstance(error, RarityMismatchError):
        suggestions.extend([
            f"Change rarity from {error.declared_rarity.value} to {error.actual_power_rarity.value}",
            f"Adjust power level to match {error.declared_rarity.value} rarity",
            "Add prerequisites or requirements for higher rarity",
            "Consider variant versions at different rarities"
        ])
    
    elif isinstance(error, AbilityScoreViolation):
        if error.min_allowed and error.score < error.min_allowed:
            suggestions.append(f"Increase {error.ability} score to at least {error.min_allowed}")
        elif error.max_allowed and error.score > error.max_allowed:
            suggestions.append(f"Reduce {error.ability} score to at most {error.max_allowed}")
    
    elif isinstance(error, MulticlassViolation):
        if error.violation_type == "prerequisite_not_met":
            for ability, required in error.required_abilities.items():
                current = error.current_abilities.get(ability, 0)
                if current < required:
                    suggestions.append(f"Increase {ability} to {required}")
    
    return suggestions


def group_validation_errors_by_field(errors: List[ValidationError]) -> Dict[str, List[ValidationError]]:
    """
    Group validation errors by field name for organized reporting.
    
    Args:
        errors: List of validation errors
        
    Returns:
        Dictionary mapping field names to errors
    """
    grouped = {}
    
    for error in errors:
        field_name = error.field_name or "general"
        if field_name not in grouped:
            grouped[field_name] = []
        grouped[field_name].append(error)
    
    return grouped


def group_validation_errors_by_type(errors: List[ValidationError]) -> Dict[str, List[ValidationError]]:
    """
    Group validation errors by validation type for organized reporting.
    
    Args:
        errors: List of validation errors
        
    Returns:
        Dictionary mapping validation types to errors
    """
    grouped = {}
    
    for error in errors:
        validation_type = error.validation_type.value if error.validation_type else "unknown"
        if validation_type not in grouped:
            grouped[validation_type] = []
        grouped[validation_type].append(error)
    
    return grouped


def group_balance_errors_by_category(errors: List[BalanceError]) -> Dict[str, List[BalanceError]]:
    """
    Group balance errors by category for organized reporting.
    
    Args:
        errors: List of balance errors
        
    Returns:
        Dictionary mapping categories to errors
    """
    grouped = {}
    
    for error in errors:
        category = categorize_balance_error(error)
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(error)
    
    return grouped


def create_validation_summary(result: ValidationResult) -> Dict[str, Any]:
    """
    Create a comprehensive summary of validation results for reporting.
    
    Args:
        result: The validation result to summarize
        
    Returns:
        Summary dictionary with detailed breakdown
    """
    summary = {
        "is_valid": result.is_valid,
        "total_issues": result.total_issues,
        "error_count": len(result.errors),
        "warning_count": len(result.warnings),
        "info_count": len(result.info),
        "critical_error_count": len(result.critical_errors) if hasattr(result, 'critical_errors') else 0,
        "errors_by_type": group_validation_errors_by_type(result.errors),
        "errors_by_field": group_validation_errors_by_field(result.errors),
        "warnings_by_type": group_validation_errors_by_type(result.warnings),
        "most_severe": None,
        "context": result.context
    }
    
    # Add balance-specific information if available
    if isinstance(result, BalanceAnalysisResult):
        summary.update({
            "balance_score": result.balance_score,
            "power_level": result.power_level,
            "balance_mode": result.balance_mode.value if result.balance_mode else None,
            "is_balanced": result.is_balanced,
            "balance_quality": result.balance_quality
        })
    
    # Find most severe error
    all_issues = result.errors + result.warnings + result.info
    if all_issues:
        most_severe = max(all_issues, key=get_validation_severity_level)
        summary["most_severe"] = {
            "message": str(most_severe),
            "severity": most_severe.severity.value,
            "type": most_severe.validation_type.value if most_severe.validation_type else "unknown",
            "field": most_severe.field_name,
            "suggestions": suggest_balance_fix(most_severe) if isinstance(most_severe, BalanceError) else []
        }
    
    return summary


def validate_content_balance(
    content_data: Dict[str, Any],
    content_type: ContentType,
    balance_level: BalanceLevel = BalanceLevel.STANDARD
) -> BalanceAnalysisResult:
    """
    Perform comprehensive balance validation on content.
    
    Args:
        content_data: The content to validate
        content_type: Type of content being validated
        balance_level: Balance standards to apply
        
    Returns:
        Balance analysis result with validation details
    """
    result = BalanceAnalysisResult(
        balance_mode=BalanceMode.STRICT if balance_level == BalanceLevel.CONSERVATIVE else BalanceMode.STANDARD,
        context={"content_type": content_type.value, "balance_level": balance_level.value}
    )
    
    # This is a framework - actual validation logic would be implemented
    # in the domain services layer following Clean Architecture
    
    return result


# ============ MODULE METADATA ============

__version__ = '2.0.0'
__description__ = 'Balance and validation exceptions for D&D Creative Content Framework'
__author__ = 'D&D Character Creator Backend6'

# Clean Architecture compliance metadata
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/exceptions",
    "dependencies": ["core/enums"],
    "dependents": ["domain/services", "application/use_cases", "infrastructure"],
    "infrastructure_independent": True,
    "focuses_on": "D&D balance and validation business rules"
}

# Exception statistics
EXCEPTION_STATISTICS = {
    "base_exceptions": 2,
    "rule_violation_exceptions": 5,
    "content_balance_exceptions": 5,
    "validation_pipeline_exceptions": 4,
    "result_classes": 2,
    "total_exception_types": 16,
    "utility_functions": 11
}