"""
Essential Character Creation Limits

Streamlined character creation boundaries following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
"""

# ============ ABILITY SCORE LIMITS ============

ABILITY_SCORE_LIMITS = {
    "absolute_minimum": 1,
    "absolute_maximum": 30,
    "standard_minimum": 8,
    "standard_maximum": 15,
    "racial_bonus_maximum": 2,
    "starting_maximum": 20,
    "epic_maximum": 30
}

ABILITY_SCORE_METHODS = {
    "standard_array": [15, 14, 13, 12, 10, 8],
    "point_buy_total": 27,
    "point_buy_costs": {
        8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9
    },
    "rolling_method": "4d6_drop_lowest"
}

# ============ CHARACTER LEVEL LIMITS ============

LEVEL_LIMITS = {
    "minimum_level": 1,
    "maximum_level": 20,
    "starting_level": 1,
    "multiclass_minimum": 2,
    "epic_threshold": 20
}

PROFICIENCY_BONUS_LIMITS = {
    "minimum": 2,
    "maximum": 6,
    "progression": {
        range(1, 5): 2,
        range(5, 9): 3,
        range(9, 13): 4,
        range(13, 17): 5,
        range(17, 21): 6
    }
}

# ============ SKILL PROFICIENCY LIMITS ============

SKILL_PROFICIENCY_LIMITS = {
    "maximum_proficiencies": 18,  # All skills
    "typical_starting_count": 4,
    "background_skills": 2,
    "class_skill_ranges": {
        "minimum": 2,
        "maximum": 4
    },
    "expertise_maximum": 4
}

LANGUAGE_LIMITS = {
    "standard_languages": 8,
    "exotic_languages": 8,
    "maximum_languages": 16,
    "typical_starting": 2
}

# ============ COMBAT LIMITS ============

HIT_POINT_LIMITS = {
    "minimum_per_level": 1,
    "constitution_modifier_applies": True,
    "negative_con_minimum": 1,
    "maximum_theoretical": 1000  # Practical upper bound
}

ARMOR_CLASS_LIMITS = {
    "absolute_minimum": 10,
    "practical_maximum": 25,
    "typical_range": (10, 20),
    "unarmored_base": 10
}

ATTACK_BONUS_LIMITS = {
    "minimum": 0,
    "maximum_theoretical": 20,
    "typical_range": (0, 15)
}

# ============ SPELLCASTING LIMITS ============

SPELL_LIMITS = {
    "cantrips_maximum": 10,
    "spells_known_maximum": 100,  # Theoretical
    "metamagic_maximum": 4,
    "spell_attack_bonus_maximum": 17,
    "spell_save_dc_maximum": 25
}

SPELL_SLOT_LIMITS = {
    "level_1_maximum": 4,
    "level_2_maximum": 3,
    "level_3_maximum": 3,
    "level_4_maximum": 3,
    "level_5_maximum": 3,
    "level_6_maximum": 1,
    "level_7_maximum": 1,
    "level_8_maximum": 1,
    "level_9_maximum": 1
}

# ============ EQUIPMENT LIMITS ============

EQUIPMENT_LIMITS = {
    "carrying_capacity_multiplier": 15,  # STR × 15
    "encumbrance_thresholds": {
        "normal": 1.0,
        "encumbered": 2.0,
        "heavily_encumbered": 3.0
    },
    "attunement_maximum": 3,
    "coin_weight_per_50": 1  # 50 coins = 1 pound
}

MAGIC_ITEM_LIMITS = {
    "attunement_slots": 3,
    "same_item_maximum": 1,  # Most magic items don't stack
    "artifact_maximum": 1
}

# ============ MULTICLASSING LIMITS ============

MULTICLASS_LIMITS = {
    "minimum_ability_scores": 13,
    "maximum_classes": 13,  # Theoretical (all classes)
    "practical_maximum": 3,
    "caster_level_calculation": "multiclass_spellcaster_table"
}

# ============ PROGRESSION LIMITS ============

FEAT_LIMITS = {
    "maximum_feats": 10,  # ASI opportunities
    "prerequisite_enforced": True,
    "stacking_allowed": False
}

ASI_LIMITS = {
    "ability_increase_maximum": 2,
    "total_increases_per_asi": 2,
    "or_feat_instead": True
}

# ============ CHARACTER CREATION VALIDATION ============

def validate_ability_scores(scores: list) -> bool:
    """Validate ability score array."""
    if len(scores) != 6:
        return False
    
    for score in scores:
        if not (ABILITY_SCORE_LIMITS["absolute_minimum"] <= score <= ABILITY_SCORE_LIMITS["absolute_maximum"]):
            return False
    
    return True

def validate_character_level(level: int) -> bool:
    """Validate character level."""
    return LEVEL_LIMITS["minimum_level"] <= level <= LEVEL_LIMITS["maximum_level"]

def calculate_point_buy_cost(score: int) -> int:
    """Calculate point buy cost for ability score."""
    return ABILITY_SCORE_METHODS["point_buy_costs"].get(score, 0)

def validate_point_buy_array(scores: list) -> bool:
    """Validate point buy ability score array."""
    total_cost = sum(calculate_point_buy_cost(score) for score in scores)
    return total_cost == ABILITY_SCORE_METHODS["point_buy_total"]

def get_proficiency_bonus_for_level(level: int) -> int:
    """Get proficiency bonus for character level."""
    for level_range, bonus in PROFICIENCY_BONUS_LIMITS["progression"].items():
        if level in level_range:
            return bonus
    return PROFICIENCY_BONUS_LIMITS["minimum"]

def validate_multiclass_requirements(class_name: str, ability_scores: dict) -> bool:
    """Validate multiclass ability score requirements."""
    # This would need the actual multiclass requirements
    # Simplified for essential-only approach
    return max(ability_scores.values()) >= MULTICLASS_LIMITS["minimum_ability_scores"]

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Limits constants
    'ABILITY_SCORE_LIMITS',
    'ABILITY_SCORE_METHODS',
    'LEVEL_LIMITS',
    'PROFICIENCY_BONUS_LIMITS',
    'SKILL_PROFICIENCY_LIMITS',
    'LANGUAGE_LIMITS',
    'HIT_POINT_LIMITS',
    'ARMOR_CLASS_LIMITS',
    'ATTACK_BONUS_LIMITS',
    'SPELL_LIMITS',
    'SPELL_SLOT_LIMITS',
    'EQUIPMENT_LIMITS',
    'MAGIC_ITEM_LIMITS',
    'MULTICLASS_LIMITS',
    'FEAT_LIMITS',
    'ASI_LIMITS',
    
    # Validation functions
    'validate_ability_scores',
    'validate_character_level',
    'calculate_point_buy_cost',
    'validate_point_buy_array',
    'get_proficiency_bonus_for_level',
    'validate_multiclass_requirements',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential character creation limits and validation'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/constants",
    "focus": "character_creation_limits_only",
    "line_target": 150,
    "dependencies": [],
    "philosophy": "crude_functional_inspired_essential_limits"
}