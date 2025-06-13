"""
Character Progression Constants.

Defines constants for character level progression, milestone tracking,
and feature scaling across levels 1-20 in D&D 5e/2024.
"""

from typing import Dict, List, Tuple, Any


# ============ LEVEL PROGRESSION STRUCTURE ============

LEVEL_RANGES = {
    "low_levels": (1, 4),      # Tier 1
    "mid_levels": (5, 10),     # Tier 2
    "high_levels": (11, 16),   # Tier 3
    "epic_levels": (17, 20)    # Tier 4
}

MAJOR_MILESTONE_LEVELS = [1, 3, 5, 11, 17, 20]

# Key progression breakpoints
PROGRESSION_BREAKPOINTS = {
    1: "Character creation",
    2: "First advancement",
    3: "Subclass/archetype choice",
    4: "First ability score improvement",
    5: "Tier 2 begins, proficiency bonus increases",
    6: "Class-specific power spike",
    9: "Proficiency bonus increases",
    11: "Tier 3 begins, major power increase",
    13: "Proficiency bonus increases",
    17: "Tier 4 begins, legendary capabilities",
    20: "Capstone abilities"
}

# ============ FEATURE ACQUISITION PATTERNS ============

# Common levels when classes gain new features
COMMON_FEATURE_LEVELS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 17, 18, 20]

# Levels that typically don't have major new features (ASI levels)
ASI_LEVELS = [4, 8, 12, 16, 19]

# Subclass feature levels (most classes)
SUBCLASS_FEATURE_LEVELS = [3, 7, 15, 20]

# ============ SCALING MECHANISMS ============

# How different types of features typically scale
SCALING_PATTERNS = {
    "proficiency_based": {
        "description": "Scales with proficiency bonus",
        "formula": "base + proficiency_bonus",
        "examples": ["spell attack bonus", "skill checks"]
    },
    "level_based": {
        "description": "Scales directly with character level",
        "formula": "base + (level // divisor)",
        "examples": ["hit points", "some class features"]
    },
    "tier_based": {
        "description": "Scales at tier boundaries",
        "breakpoints": [1, 5, 11, 17],
        "examples": ["cantrip damage", "some racial features"]
    },
    "spell_level_based": {
        "description": "Scales with highest spell level available",
        "examples": ["spell damage", "spell save DC"]
    },
    "static": {
        "description": "Does not scale with level",
        "examples": ["fixed bonuses", "utility features"]
    }
}

# Cantrip damage scaling (official pattern)
CANTRIP_DAMAGE_SCALING = {
    1: 1,   # 1d10, 1d8, etc.
    5: 2,   # 2d10, 2d8, etc.
    11: 3,  # 3d10, 3d8, etc.
    17: 4   # 4d10, 4d8, etc.
}

def get_cantrip_dice_count(character_level: int) -> int:
    """Get number of damage dice for cantrips at given level."""
    for level in sorted(CANTRIP_DAMAGE_SCALING.keys(), reverse=True):
        if character_level >= level:
            return CANTRIP_DAMAGE_SCALING[level]
    return 1

# ============ MULTICLASS PROGRESSION ============

# Spell slot progression for multiclass characters
MULTICLASS_SPELL_SLOT_LEVELS = {
    "full_caster": 1.0,     # Wizard, Cleric, etc.
    "half_caster": 0.5,     # Paladin, Ranger
    "third_caster": 0.33,   # Eldritch Knight, Arcane Trickster
    "warlock": "special"    # Warlock uses different progression
}

# Classes that contribute to multiclass spell slot calculation
SPELLCASTING_CLASSES = {
    "Bard": "full_caster",
    "Cleric": "full_caster", 
    "Druid": "full_caster",
    "Sorcerer": "full_caster",
    "Wizard": "full_caster",
    "Paladin": "half_caster",
    "Ranger": "half_caster",
    "Eldritch Knight": "third_caster",  # Fighter subclass
    "Arcane Trickster": "third_caster", # Rogue subclass
    "Warlock": "warlock"
}

# ============ PROGRESSION MILESTONES ============

# Thematic progression milestones
THEMATIC_MILESTONES = {
    "apprentice_phase": {
        "levels": (1, 4),
        "themes": [
            "Learning the basics",
            "First adventures", 
            "Establishing identity",
            "Local recognition"
        ]
    },
    "journeyman_phase": {
        "levels": (5, 10),
        "themes": [
            "Growing reputation",
            "Regional adventures",
            "Mastering core abilities",
            "Leadership opportunities"
        ]
    },
    "expert_phase": {
        "levels": (11, 16), 
        "themes": [
            "National recognition",
            "Confronting major threats",
            "Legendary deeds",
            "Transformative experiences"
        ]
    },
    "legend_phase": {
        "levels": (17, 20),
        "themes": [
            "World-shaping events",
            "Mythic enemies",
            "Planar adventures", 
            "Legacy establishment"
        ]
    }
}

# ============ POWER PROGRESSION CURVES ============

# Expected power progression by level (baseline = 1.0 at level 1)
POWER_PROGRESSION_CURVE = {
    1: 1.0,    # Baseline
    2: 1.2,    # 20% increase
    3: 1.5,    # Subclass features
    4: 1.6,    # ASI boost
    5: 2.0,    # Major power spike (Extra Attack, 3rd level spells, etc.)
    6: 2.2,
    7: 2.4,
    8: 2.5,    # Another ASI
    9: 2.7,
    10: 2.9,
    11: 3.5,   # Another major spike
    12: 3.6,   # ASI
    13: 3.8,
    14: 4.0,
    15: 4.2,
    16: 4.3,   # ASI
    17: 5.0,   # Tier 4 begins
    18: 5.2,
    19: 5.4,   # Final ASI
    20: 6.0    # Capstone abilities
}

def get_expected_power_level(character_level: int) -> float:
    """Get expected power level for character level."""
    return POWER_PROGRESSION_CURVE.get(character_level, 1.0)

# ============ FEATURE COMPLEXITY PROGRESSION ============

# How complex features should be at different levels
FEATURE_COMPLEXITY_BY_LEVEL = {
    "tier_1": {
        "simple_features": 0.8,      # 80% should be simple
        "moderate_features": 0.2,    # 20% can be moderate
        "complex_features": 0.0      # No complex features
    },
    "tier_2": {
        "simple_features": 0.5,
        "moderate_features": 0.4,
        "complex_features": 0.1
    },
    "tier_3": {
        "simple_features": 0.3,
        "moderate_features": 0.5,
        "complex_features": 0.2
    },
    "tier_4": {
        "simple_features": 0.2,
        "moderate_features": 0.4,
        "complex_features": 0.4      # High-level features can be complex
    }
}

# ============ CUSTOMIZATION POINTS ============

# "Budget" for customization at different levels
CUSTOMIZATION_BUDGET_BY_LEVEL = {
    1: {"points": 2, "description": "Basic customization"},
    3: {"points": 3, "description": "Subclass choice adds options"},
    5: {"points": 4, "description": "More significant choices"},
    11: {"points": 6, "description": "High-level customization"},
    17: {"points": 8, "description": "Near-legendary customization"},
    20: {"points": 10, "description": "Legendary customization"}
}

# ============ PROGRESSION VALIDATION RULES ============

# Rules for validating character progression
PROGRESSION_VALIDATION_RULES = {
    "power_spike_limits": {
        "max_increase_per_level": 0.3,  # 30% power increase per level max
        "tier_transition_allowed": 0.5   # 50% increase at tier transitions
    },
    "feature_distribution": {
        "combat_features_max_ratio": 0.6,    # Max 60% combat features
        "utility_features_min_ratio": 0.2,   # Min 20% utility features
        "social_features_min_ratio": 0.1     # Min 10% social features
    },
    "complexity_limits": {
        "interactions_per_feature": {
            "tier_1": 1, "tier_2": 2, "tier_3": 3, "tier_4": 4
        },
        "total_complexity_budget": {
            "tier_1": 5, "tier_2": 10, "tier_3": 15, "tier_4": 20
        }
    }
}

# ============ SIGNATURE FEATURE TIMING ============

# When characters should gain their "signature" abilities
SIGNATURE_FEATURE_TIMING = {
    "identity_establishing": (1, 3),   # Features that define character concept
    "power_defining": (5, 11),         # Features that define combat role
    "legendary_defining": (17, 20)     # Features that make character legendary
}

# ============ UTILITY FUNCTIONS ============

def get_tier_from_level(level: int) -> str:
    """Get tier name from character level."""
    if 1 <= level <= 4:
        return "tier_1"
    elif 5 <= level <= 10:
        return "tier_2"
    elif 11 <= level <= 16:
        return "tier_3"
    elif 17 <= level <= 20:
        return "tier_4"
    else:
        return "invalid"

def get_milestone_type(level: int) -> str:
    """Determine if level is a major milestone."""
    if level in MAJOR_MILESTONE_LEVELS:
        return "major"
    elif level in ASI_LEVELS:
        return "asi"
    elif level in SUBCLASS_FEATURE_LEVELS:
        return "subclass"
    else:
        return "minor"

def calculate_multiclass_caster_level(class_levels: Dict[str, int]) -> int:
    """Calculate effective caster level for multiclass character."""
    total_caster_level = 0
    
    for class_name, class_level in class_levels.items():
        if class_name in SPELLCASTING_CLASSES:
            caster_type = SPELLCASTING_CLASSES[class_name]
            if caster_type == "full_caster":
                total_caster_level += class_level
            elif caster_type == "half_caster":
                total_caster_level += class_level // 2
            elif caster_type == "third_caster":
                total_caster_level += class_level // 3
            # Warlock doesn't contribute to multiclass spell slots
    
    return total_caster_level

def is_appropriate_complexity_for_level(complexity_score: float, level: int) -> bool:
    """Check if feature complexity is appropriate for character level."""
    tier = get_tier_from_level(level)
    max_complexity = PROGRESSION_VALIDATION_RULES["complexity_limits"]["total_complexity_budget"][tier]
    
    return complexity_score <= max_complexity

def get_recommended_power_increase(current_level: int, new_level: int) -> float:
    """Get recommended power increase between levels."""
    current_power = get_expected_power_level(current_level)
    new_power = get_expected_power_level(new_level)
    
    return new_power - current_power