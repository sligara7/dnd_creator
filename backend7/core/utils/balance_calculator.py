"""
Essential D&D Balance Calculator Utilities

Streamlined balance calculation utilities following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
Maintains overarching functionality of crude_functional.py approach.

Balance calculation focuses on fair, fun character creation with simple assessments.
"""

from typing import Dict, List, Tuple, Optional, Any, Union
from core.enums import (
    AbilityScore, PowerLevel, BalanceTier, StatGenMethod,
    WealthLevel, MagicItemRarity, DifficultyScale
)

# ============ CORE BALANCE FUNCTIONS ============

def calculate_character_balance(character_data: Dict[str, Any]) -> float:
    """Calculate character balance score - crude_functional.py simple scoring."""
    if not character_data:
        return 0.0
    
    balance_score = 0.5  # Start at neutral
    
    # Ability score balance
    ability_scores = character_data.get("ability_scores", {})
    if ability_scores:
        ability_balance = assess_ability_score_balance(ability_scores)
        balance_score += ability_balance * 0.3
    
    # Level vs equipment balance
    level = character_data.get("level", 1)
    equipment = character_data.get("equipment", [])
    equipment_balance = assess_equipment_balance(level, equipment)
    balance_score += equipment_balance * 0.2
    
    # Class features balance
    character_class = character_data.get("class", "")
    class_balance = assess_class_balance(character_class, level)
    balance_score += class_balance * 0.2
    
    # Multiclass balance if applicable
    if "class_levels" in character_data:
        multiclass_balance = assess_multiclass_balance(character_data["class_levels"])
        balance_score += multiclass_balance * 0.2
    
    # Spell balance for casters
    spells = character_data.get("spells", [])
    if spells:
        spell_balance = assess_spell_balance(spells, level)
        balance_score += spell_balance * 0.1
    
    return max(0.0, min(1.0, balance_score))

def calculate_power_level(character_data: Dict[str, Any]) -> float:
    """Calculate character power level - crude_functional.py power assessment."""
    if not character_data:
        return 0.3  # Low power default
    
    power_score = 0.3  # Base power level
    
    # Ability score power contribution
    ability_scores = character_data.get("ability_scores", {})
    if ability_scores:
        ability_power = calculate_ability_power(ability_scores)
        power_score += ability_power * 0.4
    
    # Level-based power
    level = character_data.get("level", 1)
    level_power = min(1.0, level / 20.0)
    power_score += level_power * 0.3
    
    # Equipment power
    equipment = character_data.get("equipment", [])
    equipment_power = calculate_equipment_power(equipment)
    power_score += equipment_power * 0.2
    
    # Special features power
    features = character_data.get("features", [])
    feature_power = min(0.3, len(features) * 0.05)
    power_score += feature_power * 0.1
    
    return max(0.0, min(1.0, power_score))

def assess_character_viability(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Assess character viability - crude_functional.py viability check."""
    if not character_data:
        return {
            "viable": False,
            "viability_score": 0.0,
            "strengths": [],
            "weaknesses": ["No character data"],
            "recommendations": ["Create basic character"]
        }
    
    viability_score = 0.5
    strengths = []
    weaknesses = []
    recommendations = []
    
    # Check basic requirements
    required_fields = ["class", "race", "level"]
    missing_fields = [field for field in required_fields if field not in character_data]
    
    if missing_fields:
        viability_score -= 0.3
        weaknesses.extend([f"Missing {field}" for field in missing_fields])
        recommendations.extend([f"Add {field} to character" for field in missing_fields])
    else:
        strengths.append("Has basic character information")
    
    # Check ability scores
    ability_scores = character_data.get("ability_scores", {})
    if ability_scores:
        ability_viability = assess_ability_viability(ability_scores)
        viability_score += ability_viability["score_adjustment"]
        strengths.extend(ability_viability["strengths"])
        weaknesses.extend(ability_viability["weaknesses"])
        recommendations.extend(ability_viability["recommendations"])
    else:
        viability_score -= 0.2
        weaknesses.append("No ability scores")
        recommendations.append("Add ability scores")
    
    # Check class-level appropriateness
    character_class = character_data.get("class", "")
    level = character_data.get("level", 1)
    if character_class and level:
        class_viability = assess_class_viability(character_class, level)
        viability_score += class_viability["score_adjustment"]
        strengths.extend(class_viability["strengths"])
        recommendations.extend(class_viability["recommendations"])
    
    # Overall viability determination
    viable = viability_score >= 0.6 and len(missing_fields) == 0
    
    return {
        "viable": viable,
        "viability_score": max(0.0, min(1.0, viability_score)),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations
    }

def get_balance_recommendations(character_data: Dict[str, Any]) -> List[str]:
    """Get balance recommendations - crude_functional.py recommendation engine."""
    if not character_data:
        return ["Create a character with basic information"]
    
    recommendations = []
    
    # Calculate current balance
    balance_score = calculate_character_balance(character_data)
    power_level = calculate_power_level(character_data)
    
    # Balance-based recommendations
    if balance_score < 0.4:
        recommendations.append("Character appears underpowered - consider strengthening key abilities")
    elif balance_score > 0.8:
        recommendations.append("Character may be overpowered - consider reducing some advantages")
    
    # Power-based recommendations
    if power_level < 0.3:
        recommendations.append("Low power level - ensure character can contribute meaningfully")
    elif power_level > 0.9:
        recommendations.append("Very high power level - may overshadow other party members")
    
    # Specific recommendations based on character elements
    ability_recommendations = get_ability_recommendations(character_data.get("ability_scores", {}))
    recommendations.extend(ability_recommendations)
    
    equipment_recommendations = get_equipment_recommendations(character_data)
    recommendations.extend(equipment_recommendations)
    
    class_recommendations = get_class_recommendations(character_data)
    recommendations.extend(class_recommendations)
    
    # Remove duplicates
    return list(set(recommendations))

def calculate_combat_effectiveness(character_data: Dict[str, Any]) -> float:
    """Calculate combat effectiveness - crude_functional.py combat assessment."""
    if not character_data:
        return 0.2
    
    effectiveness = 0.3  # Base effectiveness
    
    # Ability score contribution to combat
    ability_scores = character_data.get("ability_scores", {})
    if ability_scores:
        combat_abilities = ["strength", "dexterity", "constitution"]
        combat_score = sum(ability_scores.get(ability, 10) for ability in combat_abilities) / 3
        ability_modifier = (combat_score - 10) / 2
        effectiveness += max(0, ability_modifier * 0.05)
    
    # Class combat effectiveness
    character_class = character_data.get("class", "")
    class_combat_rating = get_class_combat_rating(character_class)
    effectiveness += class_combat_rating * 0.3
    
    # Level scaling
    level = character_data.get("level", 1)
    level_bonus = min(0.4, level * 0.02)
    effectiveness += level_bonus
    
    # Equipment combat contribution
    equipment = character_data.get("equipment", [])
    equipment_combat = calculate_equipment_combat_value(equipment)
    effectiveness += equipment_combat * 0.2
    
    # Spells for combat (if applicable)
    spells = character_data.get("spells", [])
    if spells:
        combat_spells = count_combat_spells(spells)
        spell_bonus = min(0.2, combat_spells * 0.03)
        effectiveness += spell_bonus
    
    return max(0.0, min(1.0, effectiveness))

def validate_character_balance(character_data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
    """Validate character balance - crude_functional.py balance validation."""
    if not character_data:
        return False, ["No character data provided"], []
    
    violations = []
    warnings = []
    
    # Check balance score
    balance_score = calculate_character_balance(character_data)
    if balance_score < 0.2:
        violations.append("Character is severely underpowered")
    elif balance_score < 0.4:
        warnings.append("Character appears underpowered")
    elif balance_score > 0.9:
        violations.append("Character is overpowered")
    elif balance_score > 0.8:
        warnings.append("Character may be overpowered")
    
    # Check power level
    power_level = calculate_power_level(character_data)
    if power_level > 0.95:
        violations.append("Character power level too high")
    elif power_level < 0.15:
        violations.append("Character power level too low")
    
    # Check specific balance issues
    balance_issues = check_specific_balance_issues(character_data)
    violations.extend(balance_issues["violations"])
    warnings.extend(balance_issues["warnings"])
    
    is_balanced = len(violations) == 0
    return is_balanced, violations, warnings

# ============ SUPPORTING BALANCE FUNCTIONS ============

def assess_ability_score_balance(ability_scores: Dict[str, int]) -> float:
    """Assess ability score balance - crude_functional.py ability assessment."""
    if not ability_scores:
        return -0.2
    
    scores = list(ability_scores.values())
    if len(scores) != 6:
        return -0.1
    
    # Calculate balance metrics
    total = sum(scores)
    average = total / 6
    highest = max(scores)
    lowest = min(scores)
    
    # Standard array total is 72, average 12
    total_balance = 0.0
    if 70 <= total <= 78:  # Within reasonable range
        total_balance = 0.1
    elif total < 65 or total > 85:
        total_balance = -0.2
    
    # Check for extreme scores
    extreme_penalty = 0.0
    if highest > 18 or lowest < 6:
        extreme_penalty = -0.3
    elif highest > 16 or lowest < 8:
        extreme_penalty = -0.1
    
    return total_balance + extreme_penalty

def assess_equipment_balance(level: int, equipment: List[Any]) -> float:
    """Assess equipment balance - crude_functional.py equipment assessment."""
    if not equipment:
        return -0.1 if level > 1 else 0.0
    
    equipment_count = len(equipment)
    magic_items = count_magic_items(equipment)
    
    # Expected equipment for level
    expected_items = 3 + level // 2
    expected_magic = max(0, level - 2) // 3
    
    balance_score = 0.0
    
    # Equipment count balance
    if equipment_count < expected_items - 2:
        balance_score -= 0.1
    elif equipment_count > expected_items + 5:
        balance_score -= 0.1
    
    # Magic item balance
    if magic_items > expected_magic + 2:
        balance_score -= 0.2
    elif magic_items < expected_magic and level > 5:
        balance_score -= 0.05
    
    return balance_score

def assess_class_balance(character_class: str, level: int) -> float:
    """Assess class balance - crude_functional.py class assessment."""
    if not character_class:
        return -0.1
    
    # Simple class balance - all classes are generally balanced in 5e
    balance_score = 0.0
    
    # Level appropriateness
    if level < 1 or level > 20:
        balance_score -= 0.2
    
    return balance_score

def assess_multiclass_balance(class_levels: Dict[str, int]) -> float:
    """Assess multiclass balance - crude_functional.py multiclass assessment."""
    if not class_levels or len(class_levels) <= 1:
        return 0.0
    
    balance_score = 0.0
    total_levels = sum(class_levels.values())
    
    # Penalty for too many classes
    if len(class_levels) > 3:
        balance_score -= 0.2
    
    # Check for viable multiclass splits
    max_level = max(class_levels.values())
    if max_level < total_levels // 2:  # No dominant class
        balance_score -= 0.1
    
    return balance_score

def assess_spell_balance(spells: List[Any], level: int) -> float:
    """Assess spell balance - crude_functional.py spell assessment."""
    if not spells:
        return 0.0
    
    spell_count = len(spells)
    high_level_spells = count_high_level_spells(spells, level)
    
    balance_score = 0.0
    
    # Too many spells for level
    expected_spells = level * 2  # Rough estimate
    if spell_count > expected_spells + 5:
        balance_score -= 0.1
    
    # High level spells too early
    if high_level_spells > 0:
        balance_score -= 0.1
    
    return balance_score

def calculate_ability_power(ability_scores: Dict[str, int]) -> float:
    """Calculate ability score power contribution - crude_functional.py power calc."""
    if not ability_scores:
        return 0.0
    
    scores = list(ability_scores.values())
    total = sum(scores)
    highest = max(scores) if scores else 10
    
    # Power based on total and highest score
    power = 0.3  # Base power
    
    # Total score contribution
    if total > 78:
        power += 0.3
    elif total > 72:
        power += 0.1
    elif total < 65:
        power -= 0.2
    
    # Highest score contribution
    if highest >= 18:
        power += 0.2
    elif highest >= 16:
        power += 0.1
    elif highest < 13:
        power -= 0.1
    
    return max(0.0, min(1.0, power))

def calculate_equipment_power(equipment: List[Any]) -> float:
    """Calculate equipment power contribution - crude_functional.py equipment power."""
    if not equipment:
        return 0.0
    
    magic_items = count_magic_items(equipment)
    rare_items = count_rare_items(equipment)
    
    power = 0.0
    power += magic_items * 0.1
    power += rare_items * 0.2
    
    return min(0.5, power)  # Cap equipment power contribution

# ============ ASSESSMENT HELPER FUNCTIONS ============

def assess_ability_viability(ability_scores: Dict[str, int]) -> Dict[str, Any]:
    """Assess ability score viability - crude_functional.py ability viability."""
    result = {
        "score_adjustment": 0.0,
        "strengths": [],
        "weaknesses": [],
        "recommendations": []
    }
    
    if not ability_scores:
        result["score_adjustment"] = -0.3
        result["weaknesses"].append("No ability scores")
        result["recommendations"].append("Add ability scores")
        return result
    
    scores = list(ability_scores.values())
    highest = max(scores) if scores else 10
    lowest = min(scores) if scores else 10
    average = sum(scores) / len(scores) if scores else 10
    
    # Check for viable scores
    if highest >= 15:
        result["strengths"].append("Has strong primary ability")
        result["score_adjustment"] += 0.1
    elif highest < 13:
        result["weaknesses"].append("No strong abilities")
        result["recommendations"].append("Increase highest ability score")
        result["score_adjustment"] -= 0.1
    
    if lowest >= 8:
        result["strengths"].append("No weak dump stats")
    elif lowest < 6:
        result["weaknesses"].append("Extremely low ability score")
        result["recommendations"].append("Consider raising lowest ability score")
        result["score_adjustment"] -= 0.1
    
    if average >= 12:
        result["strengths"].append("Well-rounded ability scores")
        result["score_adjustment"] += 0.05
    elif average < 10:
        result["weaknesses"].append("Below average ability scores")
        result["score_adjustment"] -= 0.05
    
    return result

def assess_class_viability(character_class: str, level: int) -> Dict[str, Any]:
    """Assess class viability - crude_functional.py class viability."""
    result = {
        "score_adjustment": 0.0,
        "strengths": [],
        "recommendations": []
    }
    
    if not character_class:
        result["score_adjustment"] = -0.2
        result["recommendations"].append("Choose a character class")
        return result
    
    if 1 <= level <= 20:
        result["strengths"].append(f"Appropriate level {level} for play")
        result["score_adjustment"] += 0.1
    else:
        result["recommendations"].append("Set level between 1 and 20")
        result["score_adjustment"] -= 0.1
    
    # All 5e classes are viable
    result["strengths"].append(f"{character_class.title()} is a viable class choice")
    
    return result

def get_ability_recommendations(ability_scores: Dict[str, int]) -> List[str]:
    """Get ability score recommendations - crude_functional.py ability advice."""
    if not ability_scores:
        return ["Add ability scores to character"]
    
    recommendations = []
    scores = list(ability_scores.values())
    
    if not scores:
        return ["Add ability scores to character"]
    
    highest = max(scores)
    lowest = min(scores)
    total = sum(scores)
    
    if highest < 15:
        recommendations.append("Consider having at least one ability score of 15 or higher")
    
    if lowest < 8:
        recommendations.append("Very low ability scores may cause gameplay issues")
    
    if total < 70:
        recommendations.append("Consider increasing overall ability scores")
    elif total > 85:
        recommendations.append("Ability scores may be too high for balanced play")
    
    return recommendations

def get_equipment_recommendations(character_data: Dict[str, Any]) -> List[str]:
    """Get equipment recommendations - crude_functional.py equipment advice."""
    recommendations = []
    
    equipment = character_data.get("equipment", [])
    level = character_data.get("level", 1)
    
    if not equipment and level > 1:
        recommendations.append("Add equipment appropriate for character level")
    
    magic_items = count_magic_items(equipment)
    expected_magic = max(0, level - 2) // 3
    
    if magic_items > expected_magic + 3:
        recommendations.append("Consider reducing number of magic items")
    elif magic_items == 0 and level > 5:
        recommendations.append("Consider adding some magic items for higher level character")
    
    return recommendations

def get_class_recommendations(character_data: Dict[str, Any]) -> List[str]:
    """Get class-specific recommendations - crude_functional.py class advice."""
    recommendations = []
    
    character_class = character_data.get("class", "")
    ability_scores = character_data.get("ability_scores", {})
    level = character_data.get("level", 1)
    
    if not character_class:
        recommendations.append("Choose a character class")
        return recommendations
    
    # Class-specific ability recommendations
    class_abilities = {
        "barbarian": "strength",
        "bard": "charisma",
        "cleric": "wisdom",
        "druid": "wisdom",
        "fighter": "strength",
        "monk": "dexterity",
        "paladin": "strength",
        "ranger": "dexterity",
        "rogue": "dexterity",
        "sorcerer": "charisma",
        "warlock": "charisma",
        "wizard": "intelligence"
    }
    
    primary_ability = class_abilities.get(character_class.lower())
    if primary_ability and ability_scores:
        primary_score = ability_scores.get(primary_ability, 10)
        if primary_score < 13:
            recommendations.append(f"Consider increasing {primary_ability} for {character_class}")
    
    return recommendations

# ============ UTILITY HELPER FUNCTIONS ============

def count_magic_items(equipment: List[Any]) -> int:
    """Count magic items - crude_functional.py simple counting."""
    if not equipment:
        return 0
    
    magic_count = 0
    for item in equipment:
        if isinstance(item, dict):
            if item.get("magical", False) or item.get("rarity", "common") != "common":
                magic_count += 1
        elif isinstance(item, str):
            if "magic" in item.lower() or "+" in item:
                magic_count += 1
    
    return magic_count

def count_rare_items(equipment: List[Any]) -> int:
    """Count rare+ items - crude_functional.py rarity counting."""
    if not equipment:
        return 0
    
    rare_count = 0
    rare_rarities = ["rare", "very_rare", "legendary", "artifact"]
    
    for item in equipment:
        if isinstance(item, dict):
            rarity = item.get("rarity", "common").lower()
            if rarity in rare_rarities:
                rare_count += 1
    
    return rare_count

def count_combat_spells(spells: List[Any]) -> int:
    """Count combat spells - crude_functional.py combat spell counting."""
    if not spells:
        return 0
    
    combat_count = 0
    combat_keywords = ["damage", "attack", "fire", "lightning", "cold", "force", "weapon"]
    
    for spell in spells:
        if isinstance(spell, dict):
            name = spell.get("name", "").lower()
            description = spell.get("description", "").lower()
            if any(keyword in name or keyword in description for keyword in combat_keywords):
                combat_count += 1
        elif isinstance(spell, str):
            if any(keyword in spell.lower() for keyword in combat_keywords):
                combat_count += 1
    
    return combat_count

def count_high_level_spells(spells: List[Any], character_level: int) -> int:
    """Count high level spells - crude_functional.py spell level checking."""
    if not spells:
        return 0
    
    max_spell_level = min(9, (character_level + 1) // 2)  # Rough estimate
    high_level_count = 0
    
    for spell in spells:
        if isinstance(spell, dict):
            spell_level = spell.get("level", 0)
            if spell_level > max_spell_level:
                high_level_count += 1
    
    return high_level_count

def get_class_combat_rating(character_class: str) -> float:
    """Get class combat effectiveness rating - crude_functional.py class rating."""
    if not character_class:
        return 0.3
    
    # Simple combat effectiveness ratings
    combat_ratings = {
        "barbarian": 0.9,
        "fighter": 0.9,
        "paladin": 0.8,
        "ranger": 0.7,
        "monk": 0.7,
        "rogue": 0.6,
        "cleric": 0.6,
        "druid": 0.6,
        "warlock": 0.6,
        "bard": 0.5,
        "sorcerer": 0.5,
        "wizard": 0.5
    }
    
    return combat_ratings.get(character_class.lower(), 0.5)

def calculate_equipment_combat_value(equipment: List[Any]) -> float:
    """Calculate equipment combat value - crude_functional.py equipment combat value."""
    if not equipment:
        return 0.0
    
    combat_value = 0.0
    combat_keywords = ["sword", "bow", "armor", "shield", "weapon", "magic"]
    
    for item in equipment:
        if isinstance(item, dict):
            name = item.get("name", "").lower()
            item_type = item.get("type", "").lower()
            if any(keyword in name or keyword in item_type for keyword in combat_keywords):
                combat_value += 0.1
                if item.get("magical", False):
                    combat_value += 0.1
        elif isinstance(item, str):
            if any(keyword in item.lower() for keyword in combat_keywords):
                combat_value += 0.1
    
    return min(1.0, combat_value)

def check_specific_balance_issues(character_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Check specific balance issues - crude_functional.py issue detection."""
    violations = []
    warnings = []
    
    # Check for common balance problems
    level = character_data.get("level", 1)
    
    # Magic items vs level
    equipment = character_data.get("equipment", [])
    magic_items = count_magic_items(equipment)
    if magic_items > level // 2 + 2:
        warnings.append("High number of magic items for character level")
    
    # Ability scores vs level
    ability_scores = character_data.get("ability_scores", {})
    if ability_scores:
        scores = list(ability_scores.values())
        if max(scores) > 18 and level < 4:
            warnings.append("Very high ability score for low level character")
    
    # Multiclass issues
    if "class_levels" in character_data:
        class_levels = character_data["class_levels"]
        if len(class_levels) > 2 and sum(class_levels.values()) < 6:
            warnings.append("Too many multiclass levels too early")
    
    return {"violations": violations, "warnings": warnings}

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Core balance functions (required by __init__.py)
    'calculate_character_balance',
    'calculate_power_level',
    'assess_character_viability',
    'get_balance_recommendations',
    'calculate_combat_effectiveness',
    'validate_character_balance',
    
    # Supporting functions
    'assess_ability_score_balance',
    'assess_equipment_balance',
    'assess_class_balance',
    'assess_multiclass_balance',
    'assess_spell_balance',
    'calculate_ability_power',
    'calculate_equipment_power',
    
    # Assessment helpers
    'assess_ability_viability',
    'assess_class_viability',
    'get_ability_recommendations',
    'get_equipment_recommendations',
    'get_class_recommendations',
    
    # Utility helpers
    'count_magic_items',
    'count_rare_items',
    'count_combat_spells',
    'count_high_level_spells',
    'get_class_combat_rating',
    'calculate_equipment_combat_value',
    'check_specific_balance_issues',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D balance calculation utilities'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/utils",
    "focus": "balance_calculation_utilities",
    "line_target": 200,
    "dependencies": ["core.enums"],
    "philosophy": "crude_functional_inspired_essential_balance_calculations",
    "maintains_crude_functional_approach": True
}

# Balance Calculation Philosophy
BALANCE_PRINCIPLES = {
    "simple_assessments": "Use straightforward metrics for balance evaluation",
    "practical_recommendations": "Provide actionable advice for balance improvements",
    "flexible_scoring": "Balance scores guide rather than restrict character creation",
    "viability_focus": "Ensure characters are viable for gameplay",
    "fun_preservation": "Balance serves fun, engaging gameplay"
}