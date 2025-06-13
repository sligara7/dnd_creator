"""
Content Generation Limits Constants.

Defines boundaries and constraints for creative content generation,
ensuring generated content remains within acceptable parameters for
D&D gameplay while allowing creative freedom.
"""

from typing import Dict, List, Any, Tuple


# ============ GENERATION QUANTITY LIMITS ============

# Maximum number of items that can be generated per session
GENERATION_SESSION_LIMITS = {
    "character_concepts": 5,        # Max concepts per session
    "custom_species": 3,            # Max custom species per character
    "custom_classes": 2,            # Max custom classes per character  
    "custom_subclasses": 5,         # Max subclasses per custom class
    "signature_equipment": 10,      # Max signature items per character
    "custom_spells": 20,            # Max custom spells per character
    "custom_feats": 15,             # Max custom feats per character
    "background_variations": 8,     # Max background variants
    "total_custom_content": 50      # Total custom content per character
}

# Limits by creativity level
CREATIVITY_LEVEL_LIMITS = {
    "conservative": {
        "custom_content_multiplier": 0.3,  # 30% of base limits
        "complex_features_allowed": False,
        "homebrew_mechanics_allowed": False
    },
    "standard": {
        "custom_content_multiplier": 1.0,  # 100% of base limits
        "complex_features_allowed": True,
        "homebrew_mechanics_allowed": False
    },
    "high": {
        "custom_content_multiplier": 1.5,  # 150% of base limits
        "complex_features_allowed": True,
        "homebrew_mechanics_allowed": True
    },
    "maximum": {
        "custom_content_multiplier": 2.0,  # 200% of base limits
        "complex_features_allowed": True,
        "homebrew_mechanics_allowed": True
    }
}

# ============ CONTENT COMPLEXITY LIMITS ============

# Maximum complexity scores for different content types
COMPLEXITY_LIMITS = {
    "species": {
        "simple": 2.0,
        "moderate": 4.0,
        "complex": 6.0,
        "maximum": 8.0
    },
    "class": {
        "simple": 15.0,      # Classes are inherently complex
        "moderate": 25.0,
        "complex": 35.0,
        "maximum": 45.0
    },
    "subclass": {
        "simple": 8.0,
        "moderate": 12.0,
        "complex": 16.0,
        "maximum": 20.0
    },
    "spell": {
        "simple": 1.0,
        "moderate": 3.0,
        "complex": 5.0,
        "maximum": 8.0
    },
    "feat": {
        "simple": 2.0,
        "moderate": 4.0,
        "complex": 6.0,
        "maximum": 10.0
    },
    "equipment": {
        "simple": 1.0,
        "moderate": 3.0,
        "complex": 5.0,
        "maximum": 8.0
    }
}

# ============ MECHANICAL INTERACTION LIMITS ============

# Maximum number of mechanical interactions per content piece
INTERACTION_LIMITS = {
    "ability_score_interactions": 3,      # Max abilities affected
    "skill_interactions": 5,              # Max skills affected
    "spell_interactions": 4,              # Max spells that interact
    "condition_interactions": 3,          # Max conditions imposed/removed
    "damage_type_interactions": 4,        # Max damage types affected
    "action_economy_interactions": 2,     # Max action types affected
    "resource_interactions": 3            # Max resources (spell slots, etc.) affected
}

# Maximum feature depth (features that modify other features)
FEATURE_DEPTH_LIMITS = {
    "tier_1": 2,    # Features can modify features 2 levels deep
    "tier_2": 3,    # 3 levels deep
    "tier_3": 4,    # 4 levels deep  
    "tier_4": 5     # 5 levels deep (very complex interactions allowed)
}

# ============ POWER LEVEL CONSTRAINTS ============

# Absolute power limits that should never be exceeded
ABSOLUTE_POWER_LIMITS = {
    "damage_per_round": {
        "tier_1": 12,   # Never more than 12 damage per round at low levels
        "tier_2": 25,   # Never more than 25 damage per round at mid levels
        "tier_3": 40,   # Never more than 40 damage per round at high levels
        "tier_4": 60    # Never more than 60 damage per round at epic levels
    },
    "armor_class_bonus": {
        "natural_armor": 18,    # Natural AC should not exceed 18
        "magical_bonus": 3,     # Magical AC bonuses should not exceed +3
        "total_bonus": 5        # Total AC bonuses should not exceed +5
    },
    "ability_score_bonuses": {
        "single_bonus_max": 3,      # Never more than +3 to single ability
        "total_bonuses_max": 5,     # Never more than +5 total ability bonuses
        "penalty_limit": -2         # Never more than -2 penalty to ability
    },
    "saving_throw_bonuses": {
        "proficiency_grants_max": 2,    # Max 2 saving throw proficiencies
        "bonus_modifier_max": 3,        # Max +3 bonus to saves beyond proficiency
        "legendary_resistance_uses": 3   # Max 3 legendary resistance uses
    }
}

# ============ CONTENT DISTRIBUTION LIMITS ============

# Ensure balanced distribution of content types
CONTENT_DISTRIBUTION_REQUIREMENTS = {
    "combat_utility_ratio": {
        "combat_min": 0.3,      # At least 30% combat-related
        "utility_min": 0.3,     # At least 30% utility
        "social_min": 0.15,     # At least 15% social
        "exploration_min": 0.15  # At least 15% exploration
    },
    "power_level_distribution": {
        "low_power_min": 0.4,       # At least 40% low-power content
        "medium_power_max": 0.4,    # At most 40% medium-power content
        "high_power_max": 0.2       # At most 20% high-power content
    },
    "scaling_type_distribution": {
        "static_features": 0.3,     # 30% non-scaling features
        "linear_scaling": 0.4,      # 40% linear scaling
        "tier_based_scaling": 0.3   # 30% tier-based scaling
    }
}

# ============ THEMATIC CONSISTENCY LIMITS ============

# How much thematic deviation is allowed
THEMATIC_DEVIATION_LIMITS = {
    "strict_theme": {
        "primary_theme_weight": 0.8,    # 80% primary theme
        "secondary_theme_weight": 0.2,  # 20% secondary theme
        "conflicting_themes_allowed": False
    },
    "moderate_theme": {
        "primary_theme_weight": 0.6,    # 60% primary theme
        "secondary_theme_weight": 0.3,  # 30% secondary theme
        "tertiary_theme_weight": 0.1,   # 10% tertiary theme
        "conflicting_themes_allowed": False
    },
    "flexible_theme": {
        "primary_theme_weight": 0.5,    # 50% primary theme
        "secondary_theme_weight": 0.3,  # 30% secondary theme
        "tertiary_theme_weight": 0.2,   # 20% tertiary theme
        "conflicting_themes_allowed": True
    }
}

# Maximum number of different themes per content piece
THEME_COUNT_LIMITS = {
    "species": 3,           # Max 3 thematic elements
    "class": 2,             # Max 2 main themes (to maintain focus)
    "subclass": 2,          # Max 2 themes
    "spell": 2,             # Max 2 thematic elements
    "feat": 1,              # Max 1 primary theme (focused)
    "equipment": 2,         # Max 2 thematic elements
    "background": 3         # Max 3 thematic elements (backgrounds are broad)
}

# ============ NAMING AND LANGUAGE LIMITS ============

# Constraints on generated names and descriptions
NAMING_LIMITS = {
    "name_length": {
        "min_characters": 3,
        "max_characters": 30,
        "recommended_max": 20
    },
    "description_length": {
        "min_words": 10,
        "max_words": 500,
        "recommended_max": 200
    },
    "flavor_text_length": {
        "min_words": 5,
        "max_words": 100,
        "recommended_max": 50
    },
    "cultural_references": {
        "real_world_references_max": 2,     # Max 2 real-world cultural refs
        "fantasy_setting_refs_max": 5,      # Max 5 fantasy setting refs
        "original_elements_min": 3          # Min 3 original elements
    }
}

# ============ GENERATION TIME LIMITS ============

# Maximum time allowed for different generation tasks
TIME_LIMITS = {
    "character_concept": 30,        # 30 seconds max
    "full_character": 300,          # 5 minutes max
    "custom_species": 120,          # 2 minutes max
    "custom_class": 600,            # 10 minutes max
    "custom_subclass": 180,         # 3 minutes max
    "custom_spell": 60,             # 1 minute max
    "custom_feat": 90,              # 1.5 minutes max
    "signature_equipment": 120,     # 2 minutes max
    "complete_progression": 1800    # 30 minutes max
}

# ============ RESOURCE USAGE LIMITS ============

# Limits on computational resources for generation
RESOURCE_LIMITS = {
    "llm_tokens_per_request": {
        "simple_generation": 2000,
        "moderate_generation": 5000,
        "complex_generation": 10000,
        "maximum_generation": 15000
    },
    "llm_requests_per_minute": 20,      # Rate limiting
    "llm_requests_per_hour": 500,       # Hourly rate limiting
    "memory_usage_mb": 1000,            # Max memory per generation
    "concurrent_generations": 5          # Max simultaneous generations
}

# ============ VALIDATION INTENSITY LIMITS ============

# How thorough validation should be based on content complexity
VALIDATION_INTENSITY = {
    "simple_content": {
        "balance_checks": ["basic"],
        "rule_compliance_checks": ["mandatory_fields", "basic_rules"],
        "thematic_checks": ["primary_theme_consistency"]
    },
    "moderate_content": {
        "balance_checks": ["basic", "power_level", "comparative"],
        "rule_compliance_checks": ["mandatory_fields", "basic_rules", "interaction_rules"],
        "thematic_checks": ["primary_theme_consistency", "secondary_theme_compatibility"]
    },
    "complex_content": {
        "balance_checks": ["basic", "power_level", "comparative", "scaling_analysis"],
        "rule_compliance_checks": ["comprehensive"],
        "thematic_checks": ["comprehensive_theme_analysis"]
    },
    "maximum_content": {
        "balance_checks": ["comprehensive"],
        "rule_compliance_checks": ["comprehensive", "edge_case_analysis"],
        "thematic_checks": ["comprehensive_theme_analysis", "narrative_integration"]
    }
}

# ============ UTILITY FUNCTIONS ============

def get_generation_limit(content_type: str, creativity_level: str = "standard") -> int:
    """Get generation limit for content type and creativity level."""
    base_limit = GENERATION_SESSION_LIMITS.get(content_type, 1)
    multiplier = CREATIVITY_LEVEL_LIMITS.get(creativity_level, {}).get("custom_content_multiplier", 1.0)
    
    return int(base_limit * multiplier)

def get_complexity_limit(content_type: str, complexity_level: str = "moderate") -> float:
    """Get complexity limit for content type and complexity level."""
    return COMPLEXITY_LIMITS.get(content_type, {}).get(complexity_level, 5.0)

def is_within_power_limits(content_type: str, power_score: float, tier: str) -> bool:
    """Check if content is within absolute power limits."""
    # Implementation would check against ABSOLUTE_POWER_LIMITS
    return True  # Placeholder

def validate_content_distribution(content_list: List[Dict[str, Any]]) -> Dict[str, bool]:
    """Validate that content distribution meets requirements."""
    # Implementation would analyze content_list against CONTENT_DISTRIBUTION_REQUIREMENTS
    return {"combat_utility_ratio": True, "power_level_distribution": True}

def get_time_limit(generation_type: str) -> int:
    """Get time limit in seconds for generation type."""
    return TIME_LIMITS.get(generation_type, 60)

def check_resource_availability(generation_type: str) -> bool:
    """Check if resources are available for generation type."""
    # Implementation would check current resource usage against RESOURCE_LIMITS
    return True  # Placeholder

def get_validation_requirements(complexity_level: str) -> Dict[str, List[str]]:
    """Get validation requirements for complexity level."""
    return VALIDATION_INTENSITY.get(complexity_level, VALIDATION_INTENSITY["moderate_content"])