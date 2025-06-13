"""
D&D rule violation exceptions for the D&D Creative Content Framework.

This module defines exceptions related to violations of D&D 5e rules,
including character creation rules, combat mechanics, spellcasting rules,
and content balance violations.
"""

from typing import Dict, List, Optional, Any, Union
from ..enums.content_types import ContentType, ContentRarity
from ..enums.dnd_constants import Ability, Skill, DamageType, Condition
from ..enums.validation_types import RuleCompliance, ValidationSeverity


class RuleViolationError(Exception):
    """Base exception for all D&D rule violations."""
    
    def __init__(
        self,
        message: str,
        rule_name: str,
        compliance_level: RuleCompliance = RuleCompliance.CORE_RULES,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        context: Optional[Dict[str, Any]] = None,
        suggested_fix: Optional[str] = None
    ):
        super().__init__(message)
        self.rule_name = rule_name
        self.compliance_level = compliance_level
        self.severity = severity
        self.context = context or {}
        self.suggested_fix = suggested_fix
    
    def __str__(self) -> str:
        parts = [super().__str__()]
        parts.append(f"Rule: {self.rule_name}")
        parts.append(f"Compliance: {self.compliance_level.value}")
        parts.append(f"Severity: {self.severity.value}")
        
        if self.suggested_fix:
            parts.append(f"Suggested Fix: {self.suggested_fix}")
        
        return " | ".join(parts)


class AbilityScoreViolation(RuleViolationError):
    """Exception for ability score rule violations."""
    
    def __init__(
        self,
        ability: Union[str, Ability],
        score: int,
        min_allowed: Optional[int] = None,
        max_allowed: Optional[int] = None,
        **kwargs
    ):
        ability_name = ability.value if isinstance(ability, Ability) else ability
        
        if min_allowed is not None and score < min_allowed:
            message = f"{ability_name} score {score} below minimum {min_allowed}"
        elif max_allowed is not None and score > max_allowed:
            message = f"{ability_name} score {score} above maximum {max_allowed}"
        else:
            message = f"Invalid {ability_name} score: {score}"
        
        super().__init__(
            message,
            rule_name="ability_score_limits",
            **kwargs
        )
        self.ability = ability_name
        self.score = score
        self.min_allowed = min_allowed
        self.max_allowed = max_allowed


class CharacterLevelViolation(RuleViolationError):
    """Exception for character level rule violations."""
    
    def __init__(
        self,
        current_level: int,
        violation_type: str,
        class_levels: Optional[Dict[str, int]] = None,
        **kwargs
    ):
        if violation_type == "exceeds_maximum":
            message = f"Character level {current_level} exceeds maximum (20)"
        elif violation_type == "below_minimum":
            message = f"Character level {current_level} below minimum (1)"
        elif violation_type == "multiclass_mismatch":
            total_class_levels = sum(class_levels.values()) if class_levels else 0
            message = f"Character level {current_level} doesn't match sum of class levels ({total_class_levels})"
        else:
            message = f"Invalid character level: {current_level} ({violation_type})"
        
        super().__init__(
            message,
            rule_name="character_level_limits",
            **kwargs
        )
        self.current_level = current_level
        self.violation_type = violation_type
        self.class_levels = class_levels or {}


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
            message = f"Multiclassing into {class_name} requires: "
            if required_abilities:
                reqs = [f"{ability.title()} {score}+" for ability, score in required_abilities.items()]
                message += ", ".join(reqs)
        elif violation_type == "invalid_class":
            message = f"Cannot multiclass into unknown class: {class_name}"
        else:
            message = f"Multiclassing violation for {class_name}: {violation_type}"
        
        super().__init__(
            message,
            rule_name="multiclass_prerequisites",
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
            message = f"Proficiency bonus should be +{expected_bonus} at level {character_level}, not +{actual_bonus}"
        elif proficiency_type == "invalid_proficiency":
            message = f"Character is not proficient with {item}"
        elif proficiency_type == "duplicate_proficiency":
            message = f"Duplicate proficiency: {item}"
        else:
            message = f"Proficiency violation with {item}: {proficiency_type}"
        
        super().__init__(
            message,
            rule_name="proficiency_rules",
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
        available_slots: Optional[Dict[int, int]] = None,
        **kwargs
    ):
        if violation_type == "insufficient_level":
            message = f"Caster level {caster_level} insufficient for {spell_level}-level spell '{spell_name}'"
        elif violation_type == "no_spell_slots":
            message = f"No available {spell_level}-level spell slots for '{spell_name}'"
        elif violation_type == "unknown_spell":
            message = f"Spell '{spell_name}' not known by character"
        elif violation_type == "invalid_spell_level":
            message = f"Invalid spell level: {spell_level}"
        else:
            message = f"Spellcasting violation: {violation_type}"
            if spell_name:
                message += f" (spell: {spell_name})"
        
        super().__init__(
            message,
            rule_name="spellcasting_rules",
            **kwargs
        )
        self.violation_type = violation_type
        self.spell_name = spell_name
        self.spell_level = spell_level
        self.caster_level = caster_level
        self.available_slots = available_slots or {}


class CombatRuleViolation(RuleViolationError):
    """Exception for combat rule violations."""
    
    def __init__(
        self,
        violation_type: str,
        action_name: Optional[str] = None,
        action_type: Optional[str] = None,
        resource_cost: Optional[Dict[str, int]] = None,
        **kwargs
    ):
        if violation_type == "action_economy":
            message = f"Cannot use {action_name} as {action_type} - action economy violation"
        elif violation_type == "insufficient_resources":
            message = f"Insufficient resources for {action_name}"
            if resource_cost:
                costs = [f"{resource}: {cost}" for resource, cost in resource_cost.items()]
                message += f" (requires: {', '.join(costs)})"
        elif violation_type == "invalid_target":
            message = f"Invalid target for {action_name}"
        elif violation_type == "out_of_range":
            message = f"{action_name} target is out of range"
        else:
            message = f"Combat rule violation: {violation_type}"
            if action_name:
                message += f" (action: {action_name})"
        
        super().__init__(
            message,
            rule_name="combat_rules",
            **kwargs
        )
        self.violation_type = violation_type
        self.action_name = action_name
        self.action_type = action_type
        self.resource_cost = resource_cost or {}


class EquipmentViolation(RuleViolationError):
    """Exception for equipment rule violations."""
    
    def __init__(
        self,
        violation_type: str,
        item_name: str,
        character_class: Optional[str] = None,
        required_proficiency: Optional[str] = None,
        **kwargs
    ):
        if violation_type == "proficiency_required":
            message = f"Character lacks proficiency to use {item_name}"
            if required_proficiency:
                message += f" (requires: {required_proficiency})"
        elif violation_type == "class_restriction":
            message = f"{character_class} cannot use {item_name}"
        elif violation_type == "attunement_limit":
            message = f"Cannot attune to {item_name} - attunement limit exceeded"
        elif violation_type == "prerequisite_not_met":
            message = f"Prerequisites not met for {item_name}"
        else:
            message = f"Equipment violation with {item_name}: {violation_type}"
        
        super().__init__(
            message,
            rule_name="equipment_rules",
            **kwargs
        )
        self.violation_type = violation_type
        self.item_name = item_name
        self.character_class = character_class
        self.required_proficiency = required_proficiency


class BalanceViolation(RuleViolationError):
    """Exception for content balance rule violations."""
    
    def __init__(
        self,
        content_type: ContentType,
        content_name: str,
        violation_type: str,
        power_level: Optional[float] = None,
        expected_range: Optional[tuple] = None,
        rarity: Optional[ContentRarity] = None,
        **kwargs
    ):
        if violation_type == "overpowered":
            message = f"{content_type.value} '{content_name}' is overpowered"
            if power_level and expected_range:
                message += f" (power: {power_level:.2f}, expected: {expected_range[0]:.2f}-{expected_range[1]:.2f})"
        elif violation_type == "underpowered":
            message = f"{content_type.value} '{content_name}' is underpowered"
            if power_level and expected_range:
                message += f" (power: {power_level:.2f}, expected: {expected_range[0]:.2f}-{expected_range[1]:.2f})"
        elif violation_type == "rarity_mismatch":
            message = f"{content_type.value} '{content_name}' power doesn't match {rarity.value if rarity else 'declared'} rarity"
        else:
            message = f"Balance violation in {content_type.value} '{content_name}': {violation_type}"
        
        super().__init__(
            message,
            rule_name="content_balance",
            compliance_level=RuleCompliance.BALANCE_GUIDELINES,
            **kwargs
        )
        self.content_type = content_type
        self.content_name = content_name
        self.violation_type = violation_type
        self.power_level = power_level
        self.expected_range = expected_range
        self.rarity = rarity


class FeatureUsageViolation(RuleViolationError):
    """Exception for feature usage rule violations."""
    
    def __init__(
        self,
        feature_name: str,
        violation_type: str,
        usage_limit: Optional[str] = None,
        current_uses: Optional[int] = None,
        max_uses: Optional[int] = None,
        **kwargs
    ):
        if violation_type == "usage_exceeded":
            message = f"Feature '{feature_name}' usage exceeded"
            if current_uses is not None and max_uses is not None:
                message += f" ({current_uses}/{max_uses})"
            elif usage_limit:
                message += f" (limit: {usage_limit})"
        elif violation_type == "cooldown_active":
            message = f"Feature '{feature_name}' is on cooldown"
        elif violation_type == "prerequisite_not_met":
            message = f"Prerequisites not met for feature '{feature_name}'"
        else:
            message = f"Feature usage violation for '{feature_name}': {violation_type}"
        
        super().__init__(
            message,
            rule_name="feature_usage_limits",
            **kwargs
        )
        self.feature_name = feature_name
        self.violation_type = violation_type
        self.usage_limit = usage_limit
        self.current_uses = current_uses
        self.max_uses = max_uses


class RestingViolation(RuleViolationError):
    """Exception for resting rule violations."""
    
    def __init__(
        self,
        rest_type: str,
        violation_type: str,
        time_elapsed: Optional[float] = None,
        required_time: Optional[float] = None,
        **kwargs
    ):
        if violation_type == "insufficient_time":
            message = f"{rest_type} rest interrupted - insufficient time"
            if time_elapsed is not None and required_time is not None:
                message += f" ({time_elapsed}h/{required_time}h)"
        elif violation_type == "already_rested":
            message = f"Cannot take another {rest_type} rest"
        elif violation_type == "combat_interruption":
            message = f"{rest_type} rest interrupted by combat"
        else:
            message = f"Resting violation for {rest_type} rest: {violation_type}"
        
        super().__init__(
            message,
            rule_name="resting_rules",
            **kwargs
        )
        self.rest_type = rest_type
        self.violation_type = violation_type
        self.time_elapsed = time_elapsed
        self.required_time = required_time


class ConditionViolation(RuleViolationError):
    """Exception for condition rule violations."""
    
    def __init__(
        self,
        condition: Union[str, Condition],
        violation_type: str,
        conflicting_condition: Optional[str] = None,
        **kwargs
    ):
        condition_name = condition.value if isinstance(condition, Condition) else condition
        
        if violation_type == "mutually_exclusive":
            message = f"Condition '{condition_name}' conflicts with '{conflicting_condition}'"
        elif violation_type == "invalid_condition":
            message = f"Unknown condition: '{condition_name}'"
        elif violation_type == "immunity_violation":
            message = f"Character is immune to condition '{condition_name}'"
        else:
            message = f"Condition violation with '{condition_name}': {violation_type}"
        
        super().__init__(
            message,
            rule_name="condition_rules",
            **kwargs
        )
        self.condition = condition_name
        self.violation_type = violation_type
        self.conflicting_condition = conflicting_condition


# === UTILITY FUNCTIONS ===

def categorize_rule_violation(error: RuleViolationError) -> str:
    """
    Categorize a rule violation for handling and logging.
    
    Args:
        error: The rule violation to categorize
        
    Returns:
        Category string
    """
    if isinstance(error, AbilityScoreViolation):
        return "ability_scores"
    elif isinstance(error, CharacterLevelViolation):
        return "character_level"
    elif isinstance(error, MulticlassViolation):
        return "multiclassing"
    elif isinstance(error, ProficiencyViolation):
        return "proficiency"
    elif isinstance(error, SpellcastingViolation):
        return "spellcasting"
    elif isinstance(error, CombatRuleViolation):
        return "combat"
    elif isinstance(error, EquipmentViolation):
        return "equipment"
    elif isinstance(error, BalanceViolation):
        return "balance"
    elif isinstance(error, FeatureUsageViolation):
        return "feature_usage"
    elif isinstance(error, RestingViolation):
        return "resting"
    elif isinstance(error, ConditionViolation):
        return "conditions"
    else:
        return "general"


def get_violation_severity_level(error: RuleViolationError) -> int:
    """
    Get numeric severity level for sorting/prioritizing violations.
    
    Args:
        error: The rule violation to assess
        
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


def is_core_rule_violation(error: RuleViolationError) -> bool:
    """
    Check if violation is against core D&D rules vs optional/balance guidelines.
    
    Args:
        error: The rule violation to check
        
    Returns:
        True if this violates core rules
    """
    return error.compliance_level == RuleCompliance.CORE_RULES


def suggest_violation_fix(error: RuleViolationError) -> Optional[str]:
    """
    Generate suggested fix for a rule violation.
    
    Args:
        error: The rule violation to fix
        
    Returns:
        Suggested fix string or None
    """
    if error.suggested_fix:
        return error.suggested_fix
    
    # Generate generic suggestions based on violation type
    if isinstance(error, AbilityScoreViolation):
        if error.min_allowed and error.score < error.min_allowed:
            return f"Increase {error.ability} score to at least {error.min_allowed}"
        elif error.max_allowed and error.score > error.max_allowed:
            return f"Reduce {error.ability} score to at most {error.max_allowed}"
    
    elif isinstance(error, MulticlassViolation):
        if error.violation_type == "prerequisite_not_met":
            fixes = []
            for ability, required in error.required_abilities.items():
                current = error.current_abilities.get(ability, 0)
                if current < required:
                    fixes.append(f"Increase {ability} to {required}")
            return "; ".join(fixes)
    
    elif isinstance(error, SpellcastingViolation):
        if error.violation_type == "insufficient_level":
            return f"Reach caster level {error.spell_level} to cast {error.spell_name}"
        elif error.violation_type == "no_spell_slots":
            return f"Take a long rest to regain {error.spell_level}-level spell slots"
    
    return None


def group_violations_by_category(violations: List[RuleViolationError]) -> Dict[str, List[RuleViolationError]]:
    """
    Group violations by their category for organized reporting.
    
    Args:
        violations: List of rule violations
        
    Returns:
        Dictionary mapping categories to violations
    """
    grouped = {}
    
    for violation in violations:
        category = categorize_rule_violation(violation)
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(violation)
    
    return grouped