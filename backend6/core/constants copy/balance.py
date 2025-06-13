"""
Game Balance Constants

Constants used for maintaining game balance in generated content.
"""

# Balance thresholds for different content types
BALANCE_THRESHOLDS = {
    "damage_per_round": {
        "level_1_5": {"min": 2, "max": 8, "average": 5},
        "level_6_10": {"min": 6, "max": 15, "average": 10},
        "level_11_15": {"min": 12, "max": 25, "average": 18},
        "level_16_20": {"min": 20, "max": 35, "average": 27}
    },
    "armor_class": {
        "light": {"min": 11, "max": 14},
        "medium": {"min": 13, "max": 17},
        "heavy": {"min": 14, "max": 20}
    },
    "hit_points": {
        "level_1": {"min": 6, "max": 12},
        "per_level": {"min": 1, "max": 8}
    }
}

# Power scaling factors
POWER_SCALING_FACTORS = {
    "linear": 1.0,
    "moderate": 1.2,
    "significant": 1.5,
    "exponential": 2.0
}

# Mechanical limits
MECHANICAL_LIMITS = {
    "ability_score_bonus": {"max": 2, "total_max": 3},
    "skill_proficiencies": {"max": 4, "expertise_max": 2},
    "resistance_immunities": {"resistance_max": 3, "immunity_max": 1},
    "spell_level_access": {"early_max": 2, "standard_progression": True}
}

# Feature costs (for balance calculations)
FEATURE_COSTS = {
    "ability_score_increase": 1.0,
    "skill_proficiency": 0.5,
    "damage_resistance": 0.5,
    "damage_immunity": 1.5,
    "condition_immunity": 1.0,
    "spell_like_ability": 1.0,
    "extra_language": 0.25,
    "tool_proficiency": 0.25
}

# Progression benchmarks
PROGRESSION_BENCHMARKS = {
    "tier_1": {"levels": "1-4", "power_budget": 2.0},
    "tier_2": {"levels": "5-10", "power_budget": 4.0},
    "tier_3": {"levels": "11-16", "power_budget": 6.0},
    "tier_4": {"levels": "17-20", "power_budget": 8.0}
}