"""
Core D&D rule validation functions.

This module provides pure functions for validating content against D&D 5e rules,
supporting the Creative Content Framework's validation-first design with
comprehensive rule compliance checking.
"""

from typing import Dict, List, Optional, Any, Set, Tuple
from ..enums.content_types import ContentType, ContentRarity
from ..enums.dnd_constants import Ability, Skill, DamageType, Condition, SpellLevel
from ..enums.validation_types import ValidationSeverity, RuleCompliance


# === CORE RULE VALIDATION FUNCTIONS ===

def validate_ability_scores(ability_scores: Dict[str, int], method: str = "standard") -> List[Dict[str, Any]]:
    """
    Validate ability scores follow D&D rules.
    
    Args:
        ability_scores: Dictionary of ability scores
        method: Generation method ("standard", "point_buy", "array", "rolled")
        
    Returns:
        List of validation issues
    """
    issues = []
    
    # Check all six abilities are present
    required_abilities = {ability.value for ability in Ability}
    provided_abilities = set(ability_scores.keys())
    
    missing = required_abilities - provided_abilities
    if missing:
        issues.append({
            "severity": ValidationSeverity.ERROR,
            "rule": "ability_scores_complete",
            "message": f"Missing ability scores: {', '.join(missing)}",
            "compliance": RuleCompliance.CORE_RULES
        })
    
    extra = provided_abilities - required_abilities
    if extra:
        issues.append({
            "severity": ValidationSeverity.WARNING,
            "rule": "ability_scores_valid",
            "message": f"Unknown ability scores: {', '.join(extra)}",
            "compliance": RuleCompliance.CORE_RULES
        })
    
    # Validate individual scores
    for ability, score in ability_scores.items():
        if ability in required_abilities:
            issues.extend(_validate_single_ability_score(ability, score, method))
    
    # Validate score distribution for specific methods
    valid_scores = [score for ability, score in ability_scores.items() 
                   if ability in required_abilities]
    
    if method == "point_buy":
        issues.extend(_validate_point_buy_scores(valid_scores))
    elif method == "array":
        issues.extend(_validate_standard_array_scores(valid_scores))
    
    return issues


def validate_character_level(class_levels: Dict[str, int], total_level: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Validate character level distribution follows multiclassing rules.
    
    Args:
        class_levels: Dictionary of class names to levels
        total_level: Expected total level (calculated if None)
        
    Returns:
        List of validation issues
    """
    issues = []
    
    if not class_levels:
        issues.append({
            "severity": ValidationSeverity.ERROR,
            "rule": "character_has_class",
            "message": "Character must have at least one class level",
            "compliance": RuleCompliance.CORE_RULES
        })
        return issues
    
    # Calculate total level
    calculated_total = sum(class_levels.values())
    
    if total_level is not None and calculated_total != total_level:
        issues.append({
            "severity": ValidationSeverity.ERROR,
            "rule": "level_consistency",
            "message": f"Total level mismatch: calculated {calculated_total}, expected {total_level}",
            "compliance": RuleCompliance.CORE_RULES
        })
    
    # Validate total level limit
    if calculated_total > 20:
        issues.append({
            "severity": ValidationSeverity.ERROR,
            "rule": "maximum_level",
            "message": f"Total level ({calculated_total}) exceeds maximum (20)",
            "compliance": RuleCompliance.CORE_RULES
        })
    
    if calculated_total < 1:
        issues.append({
            "severity": ValidationSeverity.ERROR,
            "rule": "minimum_level",
            "message": "Character must have at least level 1",
            "compliance": RuleCompliance.CORE_RULES
        })
    
    # Validate individual class levels
    for class_name, level in class_levels.items():
        if level < 1:
            issues.append({
                "severity": ValidationSeverity.ERROR,
                "rule": "class_minimum_level",
                "message": f"Class {class_name} level ({level}) must be at least 1",
                "compliance": RuleCompliance.CORE_RULES
            })
        elif level > 20:
            issues.append({
                "severity": ValidationSeverity.ERROR,
                "rule": "class_maximum_level",
                "message": f"Class {class_name} level ({level}) exceeds maximum (20)",
                "compliance": RuleCompliance.CORE_RULES
            })
    
    return issues


def validate_proficiency_bonus(level: int, proficiency_bonus: int) -> List[Dict[str, Any]]:
    """
    Validate proficiency bonus matches character level.
    
    Args:
        level: Character level
        proficiency_bonus: Claimed proficiency bonus
        
    Returns:
        List of validation issues
    """
    expected_bonus = calculate_proficiency_bonus(level)
    
    if proficiency_bonus != expected_bonus:
        return [{
            "severity": ValidationSeverity.ERROR,
            "rule": "proficiency_bonus_calculation",
            "message": f"Proficiency bonus should be +{expected_bonus} at level {level}, not +{proficiency_bonus}",
            "compliance": RuleCompliance.CORE_RULES
        }]
    
    return []


def validate_hit_points(
    level: int,
    constitution_modifier: int,
    hit_dice: List[int],
    hit_points: int,
    method: str = "average"
) -> List[Dict[str, Any]]:
    """
    Validate hit points calculation.
    
    Args:
        level: Character level
        constitution_modifier: Constitution modifier
        hit_dice: List of hit dice used (e.g., [8, 8, 6] for Fighter 2/Rogue 1)
        hit_points: Claimed hit points
        method: Calculation method ("max", "average", "rolled")
        
    Returns:
        List of validation issues
    """
    issues = []
    
    if level != len(hit_dice):
        issues.append({
            "severity": ValidationSeverity.ERROR,
            "rule": "hit_dice_count",
            "message": f"Hit dice count ({len(hit_dice)}) doesn't match level ({level})",
            "compliance": RuleCompliance.CORE_RULES
        })
        return issues
    
    # Calculate expected HP based on method
    if method == "max":
        expected_hp = sum(hit_dice) + (constitution_modifier * level)
        min_hp = max_hp = expected_hp
    elif method == "average":
        expected_hp = sum((die + 1) // 2 + die // 2 for die in hit_dice) + (constitution_modifier * level)
        min_hp = max_hp = expected_hp
    else:  # rolled
        min_hp = len(hit_dice) + (constitution_modifier * level)  # All 1s
        max_hp = sum(hit_dice) + (constitution_modifier * level)   # All max
    
    # Validate HP is within acceptable range
    if method in ["max", "average"]:
        if hit_points != expected_hp:
            issues.append({
                "severity": ValidationSeverity.ERROR,
                "rule": "hit_points_calculation",
                "message": f"Hit points should be {expected_hp} using {method} method, not {hit_points}",
                "compliance": RuleCompliance.CORE_RULES
            })
    else:  # rolled method
        if hit_points < min_hp:
            issues.append({
                "severity": ValidationSeverity.ERROR,
                "rule": "hit_points_minimum",
                "message": f"Hit points ({hit_points}) below minimum possible ({min_hp})",
                "compliance": RuleCompliance.CORE_RULES
            })
        elif hit_points > max_hp:
            issues.append({
                "severity": ValidationSeverity.ERROR,
                "rule": "hit_points_maximum",
                "message": f"Hit points ({hit_points}) above maximum possible ({max_hp})",
                "compliance": RuleCompliance.CORE_RULES
            })
    
    return issues


def validate_armor_class(
    base_ac: int,
    armor_bonus: int,
    shield_bonus: int,
    dex_modifier: int,
    natural_armor: int = 0,
    other_bonuses: int = 0,
    max_dex_bonus: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Validate armor class calculation.
    
    Args:
        base_ac: Base AC (10 for unarmored, or armor's base AC)
        armor_bonus: AC bonus from armor
        shield_bonus: AC bonus from shield
        dex_modifier: Dexterity modifier
        natural_armor: Natural armor bonus
        other_bonuses: Other miscellaneous bonuses
        max_dex_bonus: Maximum Dex bonus allowed by armor
        
    Returns:
        List of validation issues
    """
    issues = []
    
    # Apply max dex bonus restriction
    effective_dex_bonus = dex_modifier
    if max_dex_bonus is not None:
        effective_dex_bonus = min(dex_modifier, max_dex_bonus)
    
    # Calculate expected AC
    expected_ac = base_ac + armor_bonus + shield_bonus + effective_dex_bonus + natural_armor + other_bonuses
    
    # Validate components are reasonable
    if armor_bonus < 0:
        issues.append({
            "severity": ValidationSeverity.ERROR,
            "rule": "armor_bonus_valid",
            "message": f"Armor bonus cannot be negative ({armor_bonus})",
            "compliance": RuleCompliance.CORE_RULES
        })
    
    if shield_bonus < 0 or shield_bonus > 3:
        issues.append({
            "severity": ValidationSeverity.WARNING,
            "rule": "shield_bonus_reasonable",
            "message": f"Shield bonus ({shield_bonus}) seems unusual",
            "compliance": RuleCompliance.CORE_RULES
        })
    
    return issues


def validate_saving_throws(
    ability_modifiers: Dict[str, int],
    proficiency_bonus: int,
    saving_throw_proficiencies: List[str],
    saving_throw_bonuses: Dict[str, int]
) -> List[Dict[str, Any]]:
    """
    Validate saving throw calculations.
    
    Args:
        ability_modifiers: Ability modifiers
        proficiency_bonus: Proficiency bonus
        saving_throw_proficiencies: List of proficient saving throws
        saving_throw_bonuses: Calculated saving throw bonuses
        
    Returns:
        List of validation issues
    """
    issues = []
    
    for ability in Ability:
        ability_name = ability.value
        modifier = ability_modifiers.get(ability_name, 0)
        is_proficient = ability_name in saving_throw_proficiencies
        claimed_bonus = saving_throw_bonuses.get(ability_name, modifier)
        
        expected_bonus = modifier + (proficiency_bonus if is_proficient else 0)
        
        if claimed_bonus != expected_bonus:
            issues.append({
                "severity": ValidationSeverity.ERROR,
                "rule": "saving_throw_calculation",
                "message": f"{ability_name.capitalize()} saving throw should be +{expected_bonus}, not +{claimed_bonus}",
                "compliance": RuleCompliance.CORE_RULES
            })
    
    return issues


def validate_spell_slots(
    class_levels: Dict[str, int],
    spell_slots: Dict[int, int],
    caster_type: str = "full"
) -> List[Dict[str, Any]]:
    """
    Validate spell slot allocation follows spellcasting rules.
    
    Args:
        class_levels: Character class levels
        spell_slots: Spell slots by level {1: 4, 2: 3, ...}
        caster_type: Type of caster ("full", "half", "third", "warlock")
        
    Returns:
        List of validation issues
    """
    issues = []
    
    # Calculate effective caster level
    total_level = sum(class_levels.values())
    
    if caster_type == "full":
        caster_level = total_level
    elif caster_type == "half":
        caster_level = total_level // 2
    elif caster_type == "third":
        caster_level = total_level // 3
    elif caster_type == "warlock":
        # Warlock has special slot progression
        return _validate_warlock_spell_slots(total_level, spell_slots)
    else:
        issues.append({
            "severity": ValidationSeverity.ERROR,
            "rule": "valid_caster_type",
            "message": f"Unknown caster type: {caster_type}",
            "compliance": RuleCompliance.CORE_RULES
        })
        return issues
    
    # Get expected spell slots
    expected_slots = get_spell_slots_by_level(caster_level)
    
    # Compare expected vs actual
    for spell_level in range(1, 10):
        expected = expected_slots.get(spell_level, 0)
        actual = spell_slots.get(spell_level, 0)
        
        if actual != expected:
            issues.append({
                "severity": ValidationSeverity.ERROR,
                "rule": "spell_slots_calculation",
                "message": f"Level {spell_level} spell slots should be {expected}, not {actual}",
                "compliance": RuleCompliance.CORE_RULES
            })
    
    return issues


def validate_content_rarity_balance(content_type: ContentType, rarity: ContentRarity, power_level: float) -> List[Dict[str, Any]]:
    """
    Validate content power level matches its rarity.
    
    Args:
        content_type: Type of content
        rarity: Declared rarity
        power_level: Calculated power level (0.0-1.0)
        
    Returns:
        List of validation issues
    """
    issues = []
    
    # Expected power ranges by rarity
    rarity_ranges = {
        ContentRarity.COMMON: (0.0, 0.3),
        ContentRarity.UNCOMMON: (0.2, 0.5),
        ContentRarity.RARE: (0.4, 0.7),
        ContentRarity.VERY_RARE: (0.6, 0.9),
        ContentRarity.LEGENDARY: (0.8, 1.0),
    }
    
    if rarity in rarity_ranges:
        min_power, max_power = rarity_ranges[rarity]
        
        if power_level < min_power:
            issues.append({
                "severity": ValidationSeverity.WARNING,
                "rule": "rarity_power_match",
                "message": f"{rarity.value.title()} {content_type.value} seems underpowered (power: {power_level:.2f})",
                "compliance": RuleCompliance.BALANCE_GUIDELINES
            })
        elif power_level > max_power:
            issues.append({
                "severity": ValidationSeverity.WARNING,
                "rule": "rarity_power_match",
                "message": f"{rarity.value.title()} {content_type.value} seems overpowered (power: {power_level:.2f})",
                "compliance": RuleCompliance.BALANCE_GUIDELINES
            })
    
    return issues


# === HELPER CALCULATION FUNCTIONS ===

def calculate_proficiency_bonus(level: int) -> int:
    """Calculate proficiency bonus for a given level."""
    if level < 1:
        return 0
    elif level <= 4:
        return 2
    elif level <= 8:
        return 3
    elif level <= 12:
        return 4
    elif level <= 16:
        return 5
    else:
        return 6


def calculate_ability_modifier(ability_score: int) -> int:
    """Calculate ability modifier from ability score."""
    return (ability_score - 10) // 2


def get_spell_slots_by_level(caster_level: int) -> Dict[int, int]:
    """Get spell slots for a given caster level."""
    # Standard spell slot progression table
    spell_slot_table = {
        1: {1: 2},
        2: {1: 3},
        3: {1: 4, 2: 2},
        4: {1: 4, 2: 3},
        5: {1: 4, 2: 3, 3: 2},
        6: {1: 4, 2: 3, 3: 3},
        7: {1: 4, 2: 3, 3: 3, 4: 1},
        8: {1: 4, 2: 3, 3: 3, 4: 2},
        9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
        10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
        11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
        12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
        13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
        14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
        15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
        16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
        17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
        18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1},
        19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1},
        20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1},
    }
    
    return spell_slot_table.get(caster_level, {})


def validate_multiclass_prerequisites(
    current_classes: Dict[str, int],
    new_class: str,
    ability_scores: Dict[str, int]
) -> List[Dict[str, Any]]:
    """
    Validate multiclassing prerequisites.
    
    Args:
        current_classes: Current class levels
        new_class: Class being multiclassed into
        ability_scores: Character's ability scores
        
    Returns:
        List of validation issues
    """
    issues = []
    
    # Multiclass prerequisites (simplified - would need full class data)
    prerequisites = {
        "barbarian": {"strength": 13},
        "bard": {"charisma": 13},
        "cleric": {"wisdom": 13},
        "druid": {"wisdom": 13},
        "fighter": {"strength": 13, "dexterity": 13},  # Either/or
        "monk": {"dexterity": 13, "wisdom": 13},
        "paladin": {"strength": 13, "charisma": 13},
        "ranger": {"dexterity": 13, "wisdom": 13},
        "rogue": {"dexterity": 13},
        "sorcerer": {"charisma": 13},
        "warlock": {"charisma": 13},
        "wizard": {"intelligence": 13},
    }
    
    if new_class.lower() in prerequisites:
        reqs = prerequisites[new_class.lower()]
        
        # Check if any requirement is met (for classes with either/or requirements)
        if isinstance(list(reqs.values())[0], int):  # Single requirement per ability
            for ability, min_score in reqs.items():
                actual_score = ability_scores.get(ability, 0)
                if actual_score < min_score:
                    issues.append({
                        "severity": ValidationSeverity.ERROR,
                        "rule": "multiclass_prerequisites",
                        "message": f"Multiclassing into {new_class} requires {ability.title()} {min_score}+ (have {actual_score})",
                        "compliance": RuleCompliance.CORE_RULES
                    })
    
    return issues


# === PRIVATE HELPER FUNCTIONS ===

def _validate_single_ability_score(ability: str, score: int, method: str) -> List[Dict[str, Any]]:
    """Validate a single ability score."""
    issues = []
    
    # Basic range check
    if score < 1:
        issues.append({
            "severity": ValidationSeverity.ERROR,
            "rule": "ability_score_minimum",
            "message": f"{ability.title()} score ({score}) below minimum (1)",
            "compliance": RuleCompliance.CORE_RULES
        })
    elif score > 30:
        issues.append({
            "severity": ValidationSeverity.ERROR,
            "rule": "ability_score_maximum",
            "message": f"{ability.title()} score ({score}) above maximum (30)",
            "compliance": RuleCompliance.CORE_RULES
        })
    
    # Method-specific validation
    if method in ["standard", "point_buy", "array"]:
        if score > 15:  # Before racial bonuses
            issues.append({
                "severity": ValidationSeverity.WARNING,
                "rule": "ability_score_generation_method",
                "message": f"{ability.title()} score ({score}) unusually high for {method} method",
                "compliance": RuleCompliance.CORE_RULES
            })
    
    return issues


def _validate_point_buy_scores(scores: List[int]) -> List[Dict[str, Any]]:
    """Validate scores follow point buy rules."""
    issues = []
    
    # Point buy allows 8-15 before racial bonuses
    for score in scores:
        if score < 8 or score > 15:
            issues.append({
                "severity": ValidationSeverity.WARNING,
                "rule": "point_buy_range",
                "message": f"Score {score} outside point buy range (8-15)",
                "compliance": RuleCompliance.CORE_RULES
            })
            break  # Only report once
    
    return issues


def _validate_standard_array_scores(scores: List[int]) -> List[Dict[str, Any]]:
    """Validate scores match standard array."""
    standard_array = [15, 14, 13, 12, 10, 8]
    sorted_scores = sorted(scores, reverse=True)
    
    if sorted_scores != standard_array:
        return [{
            "severity": ValidationSeverity.ERROR,
            "rule": "standard_array_match",
            "message": f"Scores {sorted_scores} don't match standard array {standard_array}",
            "compliance": RuleCompliance.CORE_RULES
        }]
    
    return []


def _validate_warlock_spell_slots(level: int, spell_slots: Dict[int, int]) -> List[Dict[str, Any]]:
    """Validate warlock-specific spell slot progression."""
    issues = []
    
    # Warlock spell slot progression
    warlock_slots = {
        1: {1: 1}, 2: {1: 2}, 3: {2: 2}, 4: {2: 2}, 5: {3: 2},
        6: {3: 2}, 7: {4: 2}, 8: {4: 2}, 9: {5: 2}, 10: {5: 2},
        11: {5: 3}, 12: {5: 3}, 13: {5: 3}, 14: {5: 3}, 15: {5: 3},
        16: {5: 3}, 17: {5: 4}, 18: {5: 4}, 19: {5: 4}, 20: {5: 4}
    }
    
    expected = warlock_slots.get(level, {})
    
    # Warlock only has slots of one level
    for spell_level, slot_count in spell_slots.items():
        expected_count = expected.get(spell_level, 0)
        if slot_count != expected_count:
            issues.append({
                "severity": ValidationSeverity.ERROR,
                "rule": "warlock_spell_slots",
                "message": f"Warlock level {level} should have {expected_count} level {spell_level} slots, not {slot_count}",
                "compliance": RuleCompliance.CORE_RULES
            })
    
    return issues