"""
Balance Threshold Constants.

Defines power level thresholds, balance limits, and mechanical constraints
for validating generated D&D content. These constants ensure all custom
content maintains appropriate power levels relative to official D&D content.
"""

from typing import Dict, Any, Tuple


# ============ POWER LEVEL THRESHOLDS ============

# Damage output thresholds by level tier
DAMAGE_THRESHOLDS = {
    "tier_1": {  # Levels 1-4
        "single_target": {"min": 2, "max": 8, "average": 5},
        "multi_target": {"min": 1, "max": 5, "average": 3},
        "sustained": {"min": 1, "max": 4, "average": 2.5}
    },
    "tier_2": {  # Levels 5-10
        "single_target": {"min": 6, "max": 15, "average": 10},
        "multi_target": {"min": 3, "max": 10, "average": 6},
        "sustained": {"min": 3, "max": 8, "average": 5.5}
    },
    "tier_3": {  # Levels 11-16
        "single_target": {"min": 12, "max": 25, "average": 18},
        "multi_target": {"min": 6, "max": 15, "average": 10},
        "sustained": {"min": 6, "max": 12, "average": 9}
    },
    "tier_4": {  # Levels 17-20
        "single_target": {"min": 20, "max": 35, "average": 27},
        "multi_target": {"min": 10, "max": 20, "average": 15},
        "sustained": {"min": 10, "max": 18, "average": 14}
    }
}

# Armor Class thresholds by armor type
ARMOR_CLASS_THRESHOLDS = {
    "light_armor": {"min": 11, "max": 14, "dex_cap": None},
    "medium_armor": {"min": 13, "max": 17, "dex_cap": 2},
    "heavy_armor": {"min": 14, "max": 20, "dex_cap": 0},
    "natural_armor": {"min": 10, "max": 18, "special": True},
    "magical_bonus": {"min": 1, "max": 3, "rarity_dependent": True}
}

# Hit Point thresholds by character level
HIT_POINT_THRESHOLDS = {
    "level_1": {"min": 6, "max": 12, "average": 9},
    "per_level_after_1": {"min": 1, "max": 8, "average": 4.5},
    "constitution_modifier": {"applies": True, "per_level": True},
    "racial_bonus": {"max": 1, "per_level": False}
}

# Spell save DC and attack bonus thresholds
SPELL_POWER_THRESHOLDS = {
    "save_dc_bonus": {"min": 0, "max": 6, "proficiency_based": True},
    "spell_attack_bonus": {"min": 0, "max": 11, "proficiency_based": True},
    "spell_damage_multiplier": {"cantrip": 1.0, "leveled": 1.2}
}

# ============ MECHANICAL LIMITS ============

# Maximum bonuses and penalties
MECHANICAL_LIMITS = {
    "ability_score_bonus": {
        "single_ability": {"max": 2, "rare_max": 3},
        "total_bonuses": {"max": 3, "legendary_max": 4},
        "penalty_max": 1  # Negative bonuses should be rare
    },
    "skill_proficiencies": {
        "granted_max": 4,
        "expertise_max": 2,
        "double_proficiency_equivalent": True
    },
    "saving_throw_proficiencies": {
        "granted_max": 2,
        "strong_saves": ["dexterity", "constitution", "wisdom"],
        "weak_saves": ["strength", "intelligence", "charisma"]
    },
    "resistance_immunities": {
        "damage_resistance_max": 3,  # Per character
        "damage_immunity_max": 1,    # Very rare
        "condition_immunity_max": 2  # Situational
    },
    "spell_access": {
        "early_access_penalty": 2,  # Levels behind normal progression
        "spell_level_max": 9,
        "cantrips_known_max": 4     # From racial traits
    }
}

# Resource limitations
RESOURCE_LIMITS = {
    "uses_per_rest": {
        "short_rest_max": 3,
        "long_rest_max": 1,
        "unlimited_uses": False  # Should have some limitation
    },
    "spell_slots": {
        "bonus_slots_max": 1,   # Additional spell slots per long rest
        "slot_level_max": 5     # From racial/feat sources
    },
    "action_economy": {
        "bonus_action_features_max": 2,
        "reaction_features_max": 3,
        "free_action_features_max": 1
    }
}

# ============ POWER SCALING FACTORS ============

# How features should scale with level
POWER_SCALING_FACTORS = {
    "linear": 1.0,      # Scales directly with level/proficiency
    "moderate": 1.2,    # Slightly better than linear
    "significant": 1.5, # Notably better scaling
    "exponential": 2.0, # Should be rare, high-level only
    "static": 0.0       # Doesn't scale (utility features)
}

# Tier-based power budgets
POWER_BUDGET_BY_TIER = {
    "tier_1": {"total_budget": 2.0, "feature_max": 0.5},
    "tier_2": {"total_budget": 4.0, "feature_max": 1.0},
    "tier_3": {"total_budget": 6.0, "feature_max": 1.5},
    "tier_4": {"total_budget": 8.0, "feature_max": 2.0}
}

# ============ FEATURE COST CALCULATIONS ============

# Base costs for common features (for balance calculations)
FEATURE_BASE_COSTS = {
    # Ability improvements
    "ability_score_increase_1": 1.0,
    "ability_score_increase_2": 1.8,  # Not quite double due to diminishing returns
    
    # Proficiencies
    "skill_proficiency": 0.5,
    "skill_expertise": 0.75,
    "tool_proficiency": 0.25,
    "language": 0.1,
    
    # Combat features
    "damage_resistance": 0.5,
    "damage_immunity": 1.5,
    "condition_immunity": 1.0,
    "extra_attack": 2.0,  # Very powerful
    
    # Spellcasting
    "cantrip": 0.5,
    "1st_level_spell": 1.0,
    "spell_slot_bonus": 0.75,
    
    # Utility
    "darkvision": 0.25,
    "telepathy": 0.5,
    "flight": 2.0,  # Extremely powerful
    "teleportation": 1.5
}

# Multipliers based on usage frequency
USAGE_FREQUENCY_MULTIPLIERS = {
    "at_will": 1.0,
    "per_short_rest": 0.8,
    "per_long_rest": 0.6,
    "once_per_day": 0.4,
    "limited_uses": 0.3
}

# ============ VALIDATION THRESHOLDS ============

# When to flag content for review
REVIEW_THRESHOLDS = {
    "power_score": {
        "auto_approve": 1.2,    # Below this is automatically approved
        "needs_review": 1.5,    # Above this needs manual review
        "likely_overpowered": 2.0,  # Above this is likely too powerful
        "definitely_broken": 3.0    # Above this is definitely broken
    },
    "complexity_score": {
        "simple": 1.0,
        "moderate": 2.0,
        "complex": 3.0,
        "too_complex": 4.0  # Should be simplified
    }
}

# Acceptable deviation from baseline
BALANCE_TOLERANCE = {
    "strict_mode": 0.1,      # 10% deviation allowed
    "standard_mode": 0.2,    # 20% deviation allowed
    "permissive_mode": 0.3,  # 30% deviation allowed
    "homebrew_mode": 0.5     # 50% deviation allowed
}

# ============ COMPARATIVE BENCHMARKS ============

# Power levels of official content for comparison
OFFICIAL_CONTENT_BENCHMARKS = {
    "species": {
        "variant_human": 1.0,    # Baseline
        "half_elf": 0.9,
        "dragonborn": 0.8,
        "tiefling": 0.85
    },
    "feats": {
        "great_weapon_master": 1.2,  # High power
        "lucky": 1.1,
        "alert": 0.8,
        "actor": 0.4   # Low power, mostly utility
    },
    "spells": {
        "fireball": 1.0,    # The baseline for 3rd level damage
        "healing_word": 0.8,
        "counterspell": 1.1,
        "wish": 2.0     # Extremely powerful
    }
}

def get_power_threshold(content_type: str, level_range: str) -> Dict[str, float]:
    """
    Get power thresholds for specific content type and level range.
    
    Args:
        content_type: Type of content (species, feat, spell, etc.)
        level_range: Level range (tier_1, tier_2, etc.)
        
    Returns:
        Dictionary with min, max, and average power thresholds
    """
    if content_type == "damage_dealing" and level_range in DAMAGE_THRESHOLDS:
        return DAMAGE_THRESHOLDS[level_range]["single_target"]
    
    # Default thresholds
    return {"min": 0.5, "max": 1.5, "average": 1.0}

def calculate_feature_cost(feature_type: str, usage_frequency: str = "at_will") -> float:
    """
    Calculate the power cost of a feature for balance purposes.
    
    Args:
        feature_type: Type of feature
        usage_frequency: How often it can be used
        
    Returns:
        Power cost value
    """
    base_cost = FEATURE_BASE_COSTS.get(feature_type, 0.5)
    frequency_multiplier = USAGE_FREQUENCY_MULTIPLIERS.get(usage_frequency, 1.0)
    
    return base_cost * frequency_multiplier

def is_within_balance_threshold(power_score: float, tolerance_mode: str = "standard_mode") -> bool:
    """
    Check if a power score is within acceptable balance thresholds.
    
    Args:
        power_score: Calculated power score
        tolerance_mode: Balance tolerance level
        
    Returns:
        True if within acceptable range
    """
    tolerance = BALANCE_TOLERANCE.get(tolerance_mode, 0.2)
    ideal_power = 1.0
    
    return abs(power_score - ideal_power) <= tolerance