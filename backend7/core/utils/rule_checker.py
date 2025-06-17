"""
Essential D&D Rule Checker Utilities

Streamlined rule checking utilities following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
Maintains overarching functionality of crude_functional.py approach.

Rule checker enforces framework for traditional D&D compatibility in modular fashion.
Ensures created characters fit seamlessly into standard D&D gameplay.
"""

from typing import Dict, List, Tuple, Optional, Any, Union
from core.enums import (
    AbilityScore, Skill, SavingThrow, CharacterClass, Race,
    SpellSchool, ActionType, DamageType, CreativityLevel
)

# ============ CORE RULE VALIDATION ============

def validate_character_rules(character_data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
    """Validate character against D&D rules - crude_functional.py modular validation."""
    if not character_data:
        return False, [], ["No character data provided"]
    
    is_valid = True
    violations = []
    warnings = []
    
    # Core rule checks (modular)
    ability_valid, ability_issues = check_ability_score_rules(character_data.get("ability_scores", {}))
    if not ability_valid:
        is_valid = False
        violations.extend(ability_issues)
    
    class_valid, class_issues = check_class_rules(character_data)
    if not class_valid:
        violations.extend(class_issues)
    
    race_valid, race_issues = check_race_rules(character_data)
    if not race_valid:
        violations.extend(race_issues)
    
    spell_valid, spell_warnings = check_spell_rules(character_data)
    warnings.extend(spell_warnings)
    
    equipment_valid, equipment_warnings = check_equipment_rules(character_data)
    warnings.extend(equipment_warnings)
    
    # Multiclass validation if applicable
    if has_multiclass(character_data):
        mc_valid, mc_issues = check_multiclass_rules(character_data)
        if not mc_valid:
            violations.extend(mc_issues)
    
    return is_valid, violations, warnings

def check_ability_score_rules(ability_scores: Dict[str, int]) -> Tuple[bool, List[str]]:
    """Check ability score rules - crude_functional.py ability validation."""
    if not ability_scores:
        return False, ["Missing ability scores"]
    
    violations = []
    required_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    
    # Check all abilities present
    for ability in required_abilities:
        if ability not in ability_scores:
            violations.append(f"Missing {ability} score")
    
    # Check ability score ranges
    for ability, score in ability_scores.items():
        if not isinstance(score, int):
            violations.append(f"{ability} must be integer")
        elif score < 3 or score > 20:
            violations.append(f"{ability} score {score} outside valid range (3-20)")
    
    is_valid = len(violations) == 0
    return is_valid, violations

def check_class_rules(character_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Check class rules - crude_functional.py class validation."""
    violations = []
    
    character_class = character_data.get("class")
    if not character_class:
        return False, ["Character class required"]
    
    level = character_data.get("level", 1)
    if not isinstance(level, int) or level < 1 or level > 20:
        violations.append(f"Invalid character level: {level}")
    
    # Class-specific rule checks
    class_violations = check_class_specific_rules(character_class, character_data)
    violations.extend(class_violations)
    
    is_valid = len(violations) == 0
    return is_valid, violations

def check_race_rules(character_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Check race rules - crude_functional.py race validation."""
    violations = []
    
    race = character_data.get("race")
    if not race:
        return False, ["Character race required"]
    
    # Race-specific rule checks
    race_violations = check_race_specific_rules(race, character_data)
    violations.extend(race_violations)
    
    is_valid = len(violations) == 0
    return is_valid, violations

# ============ CLASS-SPECIFIC RULE CHECKS ============

def check_class_specific_rules(character_class: str, character_data: Dict[str, Any]) -> List[str]:
    """Check class-specific rules - crude_functional.py class-specific validation."""
    violations = []
    
    if not character_class:
        return violations
    
    class_lower = character_class.lower()
    level = character_data.get("level", 1)
    ability_scores = character_data.get("ability_scores", {})
    
    # Spellcaster checks
    if class_lower in ["wizard", "sorcerer", "cleric", "druid", "bard", "warlock"]:
        spellcasting_violations = check_spellcaster_rules(class_lower, character_data)
        violations.extend(spellcasting_violations)
    
    # Class-specific ability requirements
    class_requirements = {
        "barbarian": ("strength", 13),
        "bard": ("charisma", 13),
        "cleric": ("wisdom", 13),
        "druid": ("wisdom", 13),
        "fighter": ("strength", 13),  # or dex for finesse builds
        "monk": ("dexterity", 13),
        "paladin": ("strength", 13),
        "ranger": ("dexterity", 13),
        "rogue": ("dexterity", 13),
        "sorcerer": ("charisma", 13),
        "warlock": ("charisma", 13),
        "wizard": ("intelligence", 13)
    }
    
    if class_lower in class_requirements:
        req_ability, min_score = class_requirements[class_lower]
        actual_score = ability_scores.get(req_ability, 10)
        if actual_score < min_score:
            violations.append(f"{character_class} requires {req_ability} {min_score}+ (has {actual_score})")
    
    return violations

def check_spellcaster_rules(character_class: str, character_data: Dict[str, Any]) -> List[str]:
    """Check spellcaster rules - crude_functional.py spellcaster validation."""
    violations = []
    
    level = character_data.get("level", 1)
    spells = character_data.get("spells", [])
    ability_scores = character_data.get("ability_scores", {})
    
    # Determine spellcasting ability
    spellcasting_abilities = {
        "wizard": "intelligence",
        "sorcerer": "charisma",
        "cleric": "wisdom",
        "druid": "wisdom",
        "bard": "charisma",
        "warlock": "charisma",
        "paladin": "charisma",
        "ranger": "wisdom"
    }
    
    spellcasting_ability = spellcasting_abilities.get(character_class, "intelligence")
    spell_ability_score = ability_scores.get(spellcasting_ability, 10)
    
    # Check spell slots vs level
    if spells:
        spell_violations = validate_spell_slots(character_class, level, spells)
        violations.extend(spell_violations)
    
    # Check spellcasting ability minimum
    if spell_ability_score < 13:
        violations.append(f"{character_class} spellcaster needs {spellcasting_ability} 13+ for effective spellcasting")
    
    return violations

def check_race_specific_rules(race: str, character_data: Dict[str, Any]) -> List[str]:
    """Check race-specific rules - crude_functional.py race-specific validation."""
    violations = []
    
    if not race:
        return violations
    
    race_lower = race.lower()
    ability_scores = character_data.get("ability_scores", {})
    
    # Check racial ability score modifiers are applied
    racial_bonuses = get_racial_ability_bonuses(race_lower)
    if racial_bonuses:
        # This is informational - we don't enforce it strictly
        pass
    
    # Race-specific restrictions (minimal - D&D 2024 is more flexible)
    race_restrictions = check_racial_restrictions(race_lower, character_data)
    violations.extend(race_restrictions)
    
    return violations

def get_racial_ability_bonuses(race: str) -> Dict[str, int]:
    """Get racial ability bonuses - crude_functional.py racial bonuses."""
    # Simplified racial bonuses (D&D 2024 is more flexible)
    racial_bonuses = {
        "human": {"all": 1},  # Flexible bonuses
        "elf": {"dexterity": 2},
        "dwarf": {"constitution": 2},
        "halfling": {"dexterity": 2},
        "dragonborn": {"strength": 2, "charisma": 1},
        "gnome": {"intelligence": 2},
        "half-elf": {"charisma": 2},
        "half-orc": {"strength": 2, "constitution": 1},
        "tiefling": {"intelligence": 1, "charisma": 2}
    }
    
    return racial_bonuses.get(race, {})

def check_racial_restrictions(race: str, character_data: Dict[str, Any]) -> List[str]:
    """Check racial restrictions - crude_functional.py minimal restrictions."""
    violations = []
    
    # D&D 2024 has very few racial restrictions
    # Most restrictions are cultural, not racial
    
    # Dragonborn breath weapon consistency
    if race == "dragonborn":
        dragon_ancestry = character_data.get("dragon_ancestry")
        if dragon_ancestry:
            # Just ensure consistency if specified
            pass
    
    # Minimal restrictions - D&D 2024 philosophy
    return violations

# ============ MULTICLASS RULE CHECKS ============

def has_multiclass(character_data: Dict[str, Any]) -> bool:
    """Check if character has multiclass - crude_functional.py multiclass detection."""
    class_levels = character_data.get("class_levels", {})
    classes = character_data.get("classes", [])
    
    return len(class_levels) > 1 or len(classes) > 1

def check_multiclass_rules(character_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Check multiclass rules - crude_functional.py multiclass validation."""
    violations = []
    
    class_levels = character_data.get("class_levels", {})
    ability_scores = character_data.get("ability_scores", {})
    
    if not class_levels:
        return True, violations
    
    # Check multiclass prerequisites
    for class_name, level in class_levels.items():
        if level > 0:
            prereq_violations = check_multiclass_prerequisites(class_name, ability_scores)
            violations.extend(prereq_violations)
    
    # Check spell slot calculations
    if has_multiple_casters(class_levels):
        slot_violations = check_multiclass_spellcasting(class_levels, character_data)
        violations.extend(slot_violations)
    
    is_valid = len(violations) == 0
    return is_valid, violations

def check_multiclass_prerequisites(class_name: str, ability_scores: Dict[str, int]) -> List[str]:
    """Check multiclass prerequisites - crude_functional.py prerequisite validation."""
    violations = []
    
    # Multiclass prerequisites (both in and out)
    prerequisites = {
        "barbarian": [("strength", 13)],
        "bard": [("charisma", 13)],
        "cleric": [("wisdom", 13)],
        "druid": [("wisdom", 13)],
        "fighter": [("strength", 13), ("dexterity", 13)],  # Either
        "monk": [("dexterity", 13), ("wisdom", 13)],  # Both
        "paladin": [("strength", 13), ("charisma", 13)],  # Both
        "ranger": [("dexterity", 13), ("wisdom", 13)],  # Both
        "rogue": [("dexterity", 13)],
        "sorcerer": [("charisma", 13)],
        "warlock": [("charisma", 13)],
        "wizard": [("intelligence", 13)]
    }
    
    class_prereqs = prerequisites.get(class_name.lower(), [])
    
    for ability, min_score in class_prereqs:
        actual_score = ability_scores.get(ability, 10)
        if actual_score < min_score:
            violations.append(f"Multiclass {class_name} requires {ability} {min_score}+ (has {actual_score})")
    
    return violations

def has_multiple_casters(class_levels: Dict[str, int]) -> bool:
    """Check if has multiple spellcasting classes - crude_functional.py caster detection."""
    spellcasting_classes = ["bard", "cleric", "druid", "sorcerer", "warlock", "wizard", "paladin", "ranger"]
    
    caster_count = 0
    for class_name, level in class_levels.items():
        if class_name.lower() in spellcasting_classes and level > 0:
            caster_count += 1
    
    return caster_count > 1

def check_multiclass_spellcasting(class_levels: Dict[str, int], character_data: Dict[str, Any]) -> List[str]:
    """Check multiclass spellcasting - crude_functional.py spellcasting validation."""
    violations = []
    
    # Complex multiclass spellcasting rules - simplified check
    total_caster_levels = calculate_caster_levels(class_levels)
    
    spells = character_data.get("spells", [])
    if spells:
        # Check spell levels are appropriate for caster level
        max_spell_level = get_max_spell_level_for_caster_level(total_caster_levels)
        
        for spell in spells:
            spell_level = spell.get("level", 0) if isinstance(spell, dict) else 0
            if spell_level > max_spell_level:
                violations.append(f"Spell level {spell_level} too high for caster level {total_caster_levels}")
    
    return violations

def calculate_caster_levels(class_levels: Dict[str, int]) -> int:
    """Calculate total caster levels - crude_functional.py caster level calculation."""
    full_casters = ["bard", "cleric", "druid", "sorcerer", "wizard"]
    half_casters = ["paladin", "ranger"]
    third_casters = ["eldritch_knight", "arcane_trickster"]  # Subclasses
    
    total_levels = 0
    
    for class_name, level in class_levels.items():
        class_lower = class_name.lower()
        
        if class_lower in full_casters:
            total_levels += level
        elif class_lower in half_casters:
            total_levels += level // 2
        elif class_lower in third_casters:
            total_levels += level // 3
        elif class_lower == "warlock":
            # Warlock is special - pact magic
            total_levels += level  # Simplified
    
    return total_levels

def get_max_spell_level_for_caster_level(caster_level: int) -> int:
    """Get max spell level for caster level - crude_functional.py spell level calculation."""
    if caster_level >= 17:
        return 9
    elif caster_level >= 15:
        return 8
    elif caster_level >= 13:
        return 7
    elif caster_level >= 11:
        return 6
    elif caster_level >= 9:
        return 5
    elif caster_level >= 7:
        return 4
    elif caster_level >= 5:
        return 3
    elif caster_level >= 3:
        return 2
    elif caster_level >= 1:
        return 1
    else:
        return 0

# ============ SPELL RULE VALIDATION ============

def check_spell_rules(character_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Check spell rules - crude_functional.py spell validation."""
    warnings = []
    
    spells = character_data.get("spells", [])
    character_class = character_data.get("class", "")
    level = character_data.get("level", 1)
    
    if not spells:
        return True, warnings
    
    # Check spell access by class
    for spell in spells:
        if isinstance(spell, dict):
            spell_warnings = validate_spell_access(spell, character_class, level)
            warnings.extend(spell_warnings)
    
    # Check spell slot usage
    slot_warnings = validate_spell_slots(character_class, level, spells)
    warnings.extend(slot_warnings)
    
    return True, warnings  # Spells are warnings, not violations

def validate_spell_access(spell: Dict[str, Any], character_class: str, level: int) -> List[str]:
    """Validate spell access - crude_functional.py spell access validation."""
    warnings = []
    
    spell_name = spell.get("name", "Unknown")
    spell_level = spell.get("level", 0)
    
    # Check if class can cast this spell level
    max_spell_level = get_max_spell_level_for_class_level(character_class, level)
    
    if spell_level > max_spell_level:
        warnings.append(f"{spell_name} (level {spell_level}) too high for {character_class} level {level}")
    
    return warnings

def get_max_spell_level_for_class_level(character_class: str, level: int) -> int:
    """Get max spell level for class and level - crude_functional.py class spell levels."""
    if not character_class:
        return 0
    
    class_lower = character_class.lower()
    
    # Full casters
    if class_lower in ["bard", "cleric", "druid", "sorcerer", "wizard"]:
        return get_max_spell_level_for_caster_level(level)
    
    # Half casters
    if class_lower in ["paladin", "ranger"]:
        return get_max_spell_level_for_caster_level(level // 2)
    
    # Warlock (special case)
    if class_lower == "warlock":
        return min(5, (level + 1) // 2)
    
    # Non-casters
    return 0

def validate_spell_slots(character_class: str, level: int, spells: List[Any]) -> List[str]:
    """Validate spell slots - crude_functional.py spell slot validation."""
    warnings = []
    
    if not spells or not character_class:
        return warnings
    
    # Count spells by level
    spell_counts = {}
    for spell in spells:
        if isinstance(spell, dict):
            spell_level = spell.get("level", 0)
            spell_counts[spell_level] = spell_counts.get(spell_level, 0) + 1
    
    # Check against typical spell slots (simplified)
    expected_slots = get_expected_spell_slots(character_class, level)
    
    for spell_level, count in spell_counts.items():
        expected_count = expected_slots.get(spell_level, 0)
        if count > expected_count * 2:  # Very lenient check
            warnings.append(f"Many level {spell_level} spells for {character_class} level {level}")
    
    return warnings

def get_expected_spell_slots(character_class: str, level: int) -> Dict[int, int]:
    """Get expected spell slots - crude_functional.py spell slot expectations."""
    # Simplified spell slot table
    if character_class.lower() in ["bard", "cleric", "druid", "sorcerer", "wizard"]:
        # Full caster progression (simplified)
        if level >= 9:
            return {1: 4, 2: 3, 3: 3, 4: 3, 5: 1}
        elif level >= 5:
            return {1: 4, 2: 3, 3: 2}
        elif level >= 3:
            return {1: 4, 2: 2}
        elif level >= 1:
            return {1: 2}
    
    return {}

# ============ EQUIPMENT RULE VALIDATION ============

def check_equipment_rules(character_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Check equipment rules - crude_functional.py equipment validation."""
    warnings = []
    
    equipment = character_data.get("equipment", [])
    character_class = character_data.get("class", "")
    level = character_data.get("level", 1)
    
    if not equipment:
        return True, warnings
    
    # Check equipment appropriateness
    for item in equipment:
        if isinstance(item, dict):
            item_warnings = validate_equipment_item(item, character_class, level)
            warnings.extend(item_warnings)
    
    return True, warnings  # Equipment issues are warnings

def validate_equipment_item(item: Dict[str, Any], character_class: str, level: int) -> List[str]:
    """Validate equipment item - crude_functional.py item validation."""
    warnings = []
    
    item_name = item.get("name", "Unknown")
    item_rarity = item.get("rarity", "common")
    magical = item.get("magical", False)
    
    # Check magic item appropriateness for level
    if magical and item_rarity.lower() in ["legendary", "artifact"]:
        if level < 17:
            warnings.append(f"{item_name} ({item_rarity}) very powerful for level {level}")
    elif magical and item_rarity.lower() == "very_rare":
        if level < 11:
            warnings.append(f"{item_name} ({item_rarity}) powerful for level {level}")
    
    return warnings

# ============ COMPATIBILITY VALIDATION ============

def validate_traditional_dnd_compatibility(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate traditional D&D compatibility - crude_functional.py compatibility check."""
    if not character_data:
        return {
            "compatible": False,
            "compatibility_score": 0,
            "violations": ["No character data"],
            "warnings": [],
            "suggestions": ["Provide basic character information"]
        }
    
    # Run all rule checks
    is_valid, violations, warnings = validate_character_rules(character_data)
    
    # Calculate compatibility score
    compatibility_score = calculate_compatibility_score(character_data, violations, warnings)
    
    # Generate suggestions
    suggestions = generate_compatibility_suggestions(violations, warnings)
    
    return {
        "compatible": is_valid and compatibility_score >= 0.8,
        "compatibility_score": compatibility_score,
        "violations": violations,
        "warnings": warnings,
        "suggestions": suggestions,
        "ready_for_play": is_valid and compatibility_score >= 0.9
    }

def calculate_compatibility_score(
    character_data: Dict[str, Any],
    violations: List[str],
    warnings: List[str]
) -> float:
    """Calculate compatibility score - crude_functional.py scoring."""
    base_score = 1.0
    
    # Deduct for violations (major issues)
    base_score -= len(violations) * 0.2
    
    # Deduct for warnings (minor issues)
    base_score -= len(warnings) * 0.05
    
    # Bonus for completeness
    required_fields = ["class", "race", "level", "ability_scores"]
    present_fields = sum(1 for field in required_fields if field in character_data)
    completeness_bonus = (present_fields / len(required_fields)) * 0.1
    
    return max(0.0, min(1.0, base_score + completeness_bonus))

def generate_compatibility_suggestions(violations: List[str], warnings: List[str]) -> List[str]:
    """Generate compatibility suggestions - crude_functional.py suggestions."""
    suggestions = []
    
    if violations:
        suggestions.append("Fix rule violations for D&D compatibility")
        
        # Specific suggestions based on violation types
        if any("ability" in v.lower() for v in violations):
            suggestions.append("Ensure all ability scores are present and valid (3-20)")
        
        if any("class" in v.lower() for v in violations):
            suggestions.append("Verify class requirements and prerequisites")
        
        if any("multiclass" in v.lower() for v in violations):
            suggestions.append("Check multiclass prerequisites and restrictions")
    
    if warnings:
        suggestions.append("Consider addressing warnings for optimal gameplay")
    
    if not violations and not warnings:
        suggestions.append("Character is fully compatible with traditional D&D")
    
    return suggestions

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Core validation
    'validate_character_rules',
    'check_ability_score_rules',
    'check_class_rules',
    'check_race_rules',
    
    # Class-specific checks
    'check_class_specific_rules',
    'check_spellcaster_rules',
    'check_race_specific_rules',
    
    # Multiclass validation
    'has_multiclass',
    'check_multiclass_rules',
    'check_multiclass_prerequisites',
    'calculate_caster_levels',
    
    # Spell validation
    'check_spell_rules',
    'validate_spell_access',
    'validate_spell_slots',
    
    # Equipment validation
    'check_equipment_rules',
    'validate_equipment_item',
    
    # Compatibility validation
    'validate_traditional_dnd_compatibility',
    'calculate_compatibility_score',
    'generate_compatibility_suggestions',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D rule checking utilities'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/utils",
    "focus": "rule_validation_utilities",
    "line_target": 200,
    "dependencies": ["core.enums"],
    "philosophy": "crude_functional_inspired_modular_rule_enforcement",
    "maintains_crude_functional_approach": True,
    "rule_enforcement_philosophy": "ensure_traditional_dnd_compatibility"
}

# Rule Checking Philosophy
RULE_CHECKING_PRINCIPLES = {
    "modular_validation": "Each rule check is independent and modular",
    "traditional_compatibility": "Ensures characters fit standard D&D gameplay",
    "clear_violations": "Distinguishes between violations and warnings",
    "compatibility_scoring": "Provides quantitative compatibility assessment",
    "actionable_feedback": "Offers specific suggestions for rule compliance"
}