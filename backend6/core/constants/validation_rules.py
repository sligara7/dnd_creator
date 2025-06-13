"""
D&D 5e/2024 Validation Rule Constants.

This module defines the fundamental validation rules and requirements for D&D content
generation and validation. These constants represent immutable business rules that
enforce D&D 5e/2024 compliance across all generated content.

Following Clean Architecture principles, these constants are:
- Infrastructure-independent
- Focused on D&D business rules
- Immutable and well-defined
- Used by validation services in the domain layer
"""

from typing import Dict, List, Set, Any, Union
from ..enums.validation_types import ValidationSeverity, RuleCompliance, ValidationType
from ..enums.content_types import ContentType
from ..enums.balance_levels import BalanceLevel


# ============ D&D 5e/2024 CORE VALIDATION RULES ============

# Rule compliance strictness definitions
RULE_COMPLIANCE_DEFINITIONS: Dict[RuleCompliance, Dict[str, Union[str, float]]] = {
    RuleCompliance.STRICT: {
        "description": "Must follow all official D&D 5e/2024 rules exactly",
        "power_deviation_tolerance": 0.05,  # 5% deviation allowed
        "allows_custom_mechanics": False,
        "requires_official_precedent": True
    },
    RuleCompliance.STANDARD: {
        "description": "Follows core rules with minor acceptable variations",
        "power_deviation_tolerance": 0.15,  # 15% deviation allowed
        "allows_custom_mechanics": True,
        "requires_official_precedent": False
    },
    RuleCompliance.VARIANT: {
        "description": "Uses official variant rules and interpretations",
        "power_deviation_tolerance": 0.25,  # 25% deviation allowed
        "allows_custom_mechanics": True,
        "requires_official_precedent": False
    },
    RuleCompliance.HOMEBREW: {
        "description": "Custom rules allowed with clear documentation and balance",
        "power_deviation_tolerance": 0.35,  # 35% deviation allowed
        "allows_custom_mechanics": True,
        "requires_official_precedent": False
    },
    RuleCompliance.EXPERIMENTAL: {
        "description": "Untested or edge-case rules for creative exploration",
        "power_deviation_tolerance": 0.50,  # 50% deviation allowed
        "allows_custom_mechanics": True,
        "requires_official_precedent": False
    }
}

# Validation severity impact on content generation
VALIDATION_SEVERITY_RULES: Dict[ValidationSeverity, Dict[str, Any]] = {
    ValidationSeverity.INFO: {
        "blocks_generation": False,
        "requires_user_acknowledgment": False,
        "auto_fix_attempts": 0,
        "logging_level": "info"
    },
    ValidationSeverity.WARNING: {
        "blocks_generation": False,
        "requires_user_acknowledgment": True,
        "auto_fix_attempts": 1,
        "logging_level": "warning"
    },
    ValidationSeverity.ERROR: {
        "blocks_generation": True,
        "requires_user_acknowledgment": True,
        "auto_fix_attempts": 3,
        "logging_level": "error"
    },
    ValidationSeverity.CRITICAL: {
        "blocks_generation": True,
        "requires_user_acknowledgment": True,
        "auto_fix_attempts": 0,  # No auto-fix for critical issues
        "logging_level": "critical"
    }
}

# ============ CONTENT TYPE VALIDATION REQUIREMENTS ============

# Mandatory fields that every D&D content type must have
UNIVERSAL_MANDATORY_FIELDS: Set[str] = {
    "name",           # Content name (must be unique within type)
    "description",    # Clear description of what this content does
    "type",          # Content type (species, class, spell, etc.)
    "source",        # Source of the content (official, homebrew, generated)
    "version"        # Content version for tracking changes
}

# Optional but highly recommended fields for all content
UNIVERSAL_OPTIONAL_FIELDS: Set[str] = {
    "flavor_text",       # Thematic description and lore
    "example_usage",     # Examples of how to use this content
    "design_notes",      # Designer's notes and reasoning
    "balance_notes",     # Balance considerations and testing notes
    "prerequisite_notes", # Any prerequisite explanations
    "interaction_notes"  # How this interacts with other content
}

# Content-specific validation requirements following D&D 5e/2024 structure
CONTENT_VALIDATION_REQUIREMENTS: Dict[ContentType, Dict[str, Set[str]]] = {
    # Species (Races) - D&D 2024 structure
    ContentType.SPECIES: {
        "mandatory": {
            "creature_type",      # Humanoid, Fey, etc.
            "size",              # Size category
            "speed",             # Base walking speed
            "languages",         # Known languages
            "life_span",         # Typical lifespan
            "alignment_tendency"  # Typical alignment (not restrictive)
        },
        "optional": {
            "ability_score_increase",  # ASI or flexible ASI
            "darkvision",             # Darkvision range if applicable
            "special_senses",         # Other special senses
            "resistances",            # Damage resistances
            "immunities",            # Damage immunities
            "vulnerabilities",       # Damage vulnerabilities
            "natural_weapons",       # Natural attacks
            "proficiencies"          # Skill/tool/weapon proficiencies
        },
        "mechanical": {
            "traits",               # Species traits with mechanics
            "size_category",        # Mechanical size implications
            "base_speed_type",      # Walking, flying, swimming, etc.
            "language_mechanics"    # How language selection works
        }
    },
    
    # Character Classes - D&D 2024 structure
    ContentType.CHARACTER_CLASS: {
        "mandatory": {
            "hit_die",              # Hit die type (d6, d8, d10, d12)
            "primary_ability",      # Primary ability score(s)
            "saving_throw_proficiencies",  # Two saving throw proficiencies
            "armor_proficiencies",  # Armor proficiency list
            "weapon_proficiencies", # Weapon proficiency list
            "tool_proficiencies",   # Tool proficiency options
            "skill_proficiencies"   # Skill proficiency options and count
        },
        "optional": {
            "multiclass_requirements",     # Ability score requirements
            "spellcasting_ability",        # If spellcaster, which ability
            "spell_list_source",           # Which spell list to use
            "ritual_casting",              # Can cast rituals
            "spellcasting_focus",          # Spellcasting focus requirements
            "cantrips_known",              # Cantrip progression
            "spells_known",                # Spell known progression
            "spell_slots"                  # Spell slot progression
        },
        "mechanical": {
            "class_features",              # Level-by-level features
            "subclass_selection_level",    # When subclass is chosen
            "asi_levels",                  # Ability Score Improvement levels
            "proficiency_bonus_progression", # Usually standard
            "hit_point_progression",       # HP calculation rules
            "equipment_starting"           # Starting equipment
        }
    },
    
    # Subclasses - D&D 2024 structure  
    ContentType.SUBCLASS: {
        "mandatory": {
            "parent_class",         # Which class this belongs to
            "selection_level",      # Level when chosen (usually 3)
            "subclass_features",    # Level-specific features
            "thematic_identity"     # Core theme and concept
        },
        "optional": {
            "additional_spells",    # Subclass-specific spells
            "expanded_spell_list",  # Additional spell options
            "tool_proficiencies",   # Additional tool proficiencies
            "skill_proficiencies",  # Additional skill options
            "equipment_proficiencies" # Additional equipment proficiencies
        },
        "mechanical": {
            "feature_progression",  # Mechanical progression by level
            "resource_management",  # Any subclass-specific resources
            "interaction_rules"     # How features interact with base class
        }
    },
    
    # Spells - D&D 2024 structure
    ContentType.SPELL: {
        "mandatory": {
            "level",               # Spell level (0-9)
            "school",              # School of magic
            "casting_time",        # Action, bonus action, etc.
            "range",               # Range in feet or special
            "duration",            # Duration or instantaneous
            "components"           # V, S, M components
        },
        "optional": {
            "material_components",  # Specific material component
            "component_cost",       # GP cost if expensive component
            "component_consumed",   # Whether component is consumed
            "ritual",              # Can be cast as ritual
            "concentration",       # Requires concentration
            "damage_type",         # Type of damage dealt
            "save_type",           # Saving throw type
            "spell_attack",        # Spell attack roll required
            "area_of_effect",      # AOE shape and size
            "target_type",         # What can be targeted
            "upcast_effects"       # Effects when cast at higher levels
        },
        "mechanical": {
            "spell_effects",       # Detailed mechanical effects
            "scaling_formula",     # How damage/effects scale
            "save_mechanics",      # Save for half, negates, etc.
            "spell_lists"          # Which classes can learn this
        }
    },
    
    # Feats - D&D 2024 structure
    ContentType.FEAT: {
        "mandatory": {
            "feat_type",           # General, Fighting Style, etc.
            "mechanical_benefit",  # Clear mechanical benefit
            "thematic_identity"    # What this feat represents
        },
        "optional": {
            "prerequisites",       # Ability scores, level, other feats
            "ability_score_increase", # ASI component if applicable
            "repeatable",          # Can be taken multiple times
            "choice_options",      # If feat offers choices
            "tool_proficiencies",  # Tool proficiencies granted
            "skill_proficiencies", # Skill proficiencies granted
            "language_proficiencies" # Language proficiencies granted
        },
        "mechanical": {
            "feat_features",       # Detailed mechanical features
            "resource_costs",      # Any resource expenditure
            "usage_limitations",   # Per rest, per turn, etc.
            "stacking_rules"       # How multiple instances interact
        }
    },
    
    # Weapons - D&D 2024 structure
    ContentType.WEAPON: {
        "mandatory": {
            "weapon_category",     # Simple, Martial, Improvised
            "weapon_type",         # Melee, Ranged
            "damage_die",          # Damage dice (1d8, 2d6, etc.)
            "damage_type",         # Slashing, piercing, bludgeoning
            "weight",              # Weight in pounds
            "cost"                 # Cost in GP
        },
        "optional": {
            "weapon_properties",   # Finesse, heavy, light, etc.
            "range_normal",        # Normal range for ranged weapons
            "range_long",          # Long range for ranged weapons
            "ammunition_type",     # Type of ammunition required
            "versatile_damage",    # Damage when used two-handed
            "special_properties",  # Unique weapon properties
            "magic_bonus",         # Enhancement bonus if magical
            "magic_properties"     # Magical properties and effects
        },
        "mechanical": {
            "attack_mechanics",    # How attacks are resolved
            "proficiency_requirements", # Who can use effectively
            "interaction_rules",   # Special combat interactions
            "crafting_requirements" # If craftable, what's needed
        }
    },
    
    # Armor - D&D 2024 structure
    ContentType.ARMOR: {
        "mandatory": {
            "armor_category",      # Light, Medium, Heavy, Shield
            "armor_class_base",    # Base AC provided
            "weight",              # Weight in pounds
            "cost"                 # Cost in GP
        },
        "optional": {
            "max_dex_bonus",       # Dexterity modifier limit
            "strength_requirement", # Minimum Strength needed
            "stealth_disadvantage", # Imposes stealth disadvantage
            "don_time",            # Time to put on
            "doff_time",           # Time to take off
            "magic_bonus",         # Enhancement bonus if magical
            "magic_properties",    # Magical properties and effects
            "special_materials"    # Special material properties
        },
        "mechanical": {
            "ac_calculation",      # How final AC is calculated
            "proficiency_requirements", # Who can wear effectively
            "interaction_rules",   # Special mechanical interactions
            "maintenance_requirements" # Upkeep and repair needs
        }
    },
    
    # Magic Items - D&D 2024 structure
    ContentType.MAGIC_ITEM: {
        "mandatory": {
            "item_type",           # Weapon, armor, wondrous item, etc.
            "rarity",              # Common, uncommon, rare, etc.
            "attunement_required", # Requires attunement
            "magical_properties"   # What the item does
        },
        "optional": {
            "activation_method",   # How to activate (command, use, etc.)
            "charges_max",         # Maximum charges if applicable
            "charges_regain",      # How charges are regained
            "curse_properties",    # If cursed, what's the curse
            "destruction_method",  # How item can be destroyed
            "creation_requirements", # What's needed to create
            "historical_significance", # Lore and background
            "variant_properties"   # Alternative versions
        },
        "mechanical": {
            "usage_mechanics",     # Detailed usage rules
            "attunement_effects",  # What happens when attuned
            "resource_costs",      # Any costs to use
            "interaction_with_other_magic" # How it interacts with other magic
        }
    },
    
    # Backgrounds - D&D 2024 structure
    ContentType.BACKGROUND: {
        "mandatory": {
            "skill_proficiencies", # Two skill proficiencies
            "background_feature",  # Special background feature
            "starting_equipment",  # Equipment provided
            "thematic_identity"    # What this background represents
        },
        "optional": {
            "tool_proficiencies",  # Tool proficiency options
            "language_proficiencies", # Language options
            "equipment_alternatives", # Alternative starting equipment
            "personality_traits",  # Suggested personality traits
            "ideals",              # Suggested ideals
            "bonds",               # Suggested bonds
            "flaws",               # Suggested flaws
            "variant_features"     # Alternative background features
        },
        "mechanical": {
            "feature_mechanics",   # How background feature works
            "proficiency_choices", # How to select proficiencies
            "equipment_rules",     # Equipment selection rules
            "customization_options" # How to customize background
        }
    }
}

# ============ BALANCE VALIDATION THRESHOLDS ============

# Power level thresholds for different content types at different levels
POWER_LEVEL_THRESHOLDS: Dict[ContentType, Dict[str, Dict[int, float]]] = {
    ContentType.SPECIES: {
        "combat_power": {1: 0.8, 5: 0.9, 10: 1.0, 15: 1.0, 20: 1.0},
        "utility_power": {1: 1.2, 5: 1.1, 10: 1.0, 15: 0.9, 20: 0.8},
        "total_power": {1: 1.0, 5: 1.0, 10: 1.0, 15: 0.95, 20: 0.9}
    },
    ContentType.CHARACTER_CLASS: {
        "combat_power": {1: 1.0, 5: 1.0, 10: 1.0, 15: 1.0, 20: 1.0},
        "utility_power": {1: 1.0, 5: 1.0, 10: 1.0, 15: 1.0, 20: 1.0},
        "total_power": {1: 1.0, 5: 1.0, 10: 1.0, 15: 1.0, 20: 1.0}
    },
    ContentType.FEAT: {
        "combat_power": {1: 0.5, 4: 0.7, 8: 0.9, 12: 1.0, 16: 1.1, 19: 1.2},
        "utility_power": {1: 0.7, 4: 0.8, 8: 0.9, 12: 1.0, 16: 1.0, 19: 1.0},
        "total_power": {1: 0.6, 4: 0.75, 8: 0.9, 12: 1.0, 16: 1.05, 19: 1.1}
    },
    ContentType.SPELL: {
        "damage_per_level": {
            0: 5.5,   # Cantrips: ~1d10 damage
            1: 10.5,  # 1st level: ~3d6 damage  
            2: 16.5,  # 2nd level: ~3d10 damage
            3: 24.5,  # 3rd level: ~7d6 damage
            4: 32.5,  # 4th level: ~7d8 damage
            5: 45.5,  # 5th level: ~10d8 damage
            6: 52.5,  # 6th level: ~15d6 damage
            7: 63.0,  # 7th level: ~18d6 damage
            8: 73.5,  # 8th level: ~21d6 damage
            9: 84.0   # 9th level: ~24d6 damage
        },
        "save_or_suck_power": {
            1: 0.3, 2: 0.4, 3: 0.5, 4: 0.6, 5: 0.7,
            6: 0.8, 7: 0.9, 8: 1.0, 9: 1.1
        }
    }
}

# ============ VALIDATION ERROR TEMPLATES ============

# Standard validation error messages for consistency
VALIDATION_ERROR_TEMPLATES: Dict[str, str] = {
    "missing_mandatory_field": "Missing mandatory field '{field}' for {content_type}",
    "invalid_field_type": "Field '{field}' must be of type {expected_type}, got {actual_type}",
    "invalid_field_value": "Field '{field}' has invalid value '{value}'. Expected: {expected_values}",
    "power_level_exceeded": "{content_type} power level {actual_level} exceeds threshold {threshold}",
    "missing_prerequisites": "Prerequisites not met: {missing_prerequisites}",
    "rule_compliance_violation": "Violates {compliance_level} rule compliance: {violation_details}",
    "balance_concern": "Balance concern in {category}: {issue_description}",
    "mechanical_inconsistency": "Mechanical inconsistency: {inconsistency_description}",
    "thematic_mismatch": "Thematic inconsistency: {mismatch_description}",
    "naming_convention_violation": "Name '{name}' violates D&D naming conventions: {violation_reason}"
}

# ============ CONTENT VALIDATION WEIGHTS ============

# Weights for different aspects of content validation
VALIDATION_CATEGORY_WEIGHTS: Dict[str, float] = {
    "rule_compliance": 0.25,      # 25% - Following D&D rules
    "mechanical_balance": 0.30,   # 30% - Power level appropriateness  
    "thematic_consistency": 0.20, # 20% - Theme and flavor consistency
    "usability": 0.15,           # 15% - Practical usability
    "integration": 0.10          # 10% - Integration with existing content
}

# ============ GENERATION CONSTRAINT CONSTANTS ============

# Maximum values for various content aspects to prevent abuse
GENERATION_LIMITS: Dict[str, Dict[str, Any]] = {
    "species_traits": {
        "max_count": 4,              # Maximum number of species traits
        "max_power_budget": 1.0,     # Total power budget for traits
        "required_ribbon_traits": 1   # Minimum "ribbon" (flavor) traits
    },
    "class_features": {
        "max_per_level": 2,          # Maximum features per level
        "max_total": 25,             # Maximum total features 1-20
        "asi_levels": [4, 8, 12, 16, 19], # Standard ASI levels
        "subclass_levels": [3, 7, 15, 18]  # Typical subclass feature levels
    },
    "spell_parameters": {
        "max_damage_dice": 20,       # Maximum damage dice for a spell
        "max_range_feet": 1000,      # Maximum spell range in feet
        "max_duration_hours": 24,    # Maximum spell duration in hours
        "max_targets": 20            # Maximum number of targets
    },
    "feat_limitations": {
        "max_asi_bonus": 2,          # Maximum ASI bonus from a feat
        "max_skill_proficiencies": 3, # Maximum skill proficiencies
        "max_features": 3            # Maximum distinct features per feat
    }
}

# ============ OFFICIAL BENCHMARK DATA ============

# Reference power levels from official content for comparison
OFFICIAL_BENCHMARKS: Dict[ContentType, Dict[str, float]] = {
    ContentType.SPECIES: {
        "human_variant": 1.0,        # Baseline comparison
        "half_elf": 1.1,            # Slightly above baseline
        "tiefling": 0.95,           # Slightly below baseline
        "dragonborn": 0.9,          # Below baseline (pre-2024)
        "dwarf_mountain": 1.05      # Slightly above baseline
    },
    ContentType.CHARACTER_CLASS: {
        "fighter": 1.0,             # Baseline martial class
        "wizard": 1.0,              # Baseline full caster
        "rogue": 0.95,              # Slightly below baseline
        "paladin": 1.05,            # Slightly above baseline
        "ranger": 0.9               # Below baseline (known weak class)
    },
    ContentType.FEAT: {
        "great_weapon_master": 1.2,  # High-power combat feat
        "sharpshooter": 1.2,        # High-power ranged feat
        "alert": 0.8,               # Utility feat
        "lucky": 1.1,               # Powerful utility feat
        "magic_initiate": 0.9       # Moderate power feat
    }
}

# ============ VALIDATION FUNCTION MAPPINGS ============

# Maps validation types to their required validation functions
VALIDATION_TYPE_REQUIREMENTS: Dict[ValidationType, Set[str]] = {
    ValidationType.MECHANICAL: {
        "validate_mandatory_fields",
        "validate_field_types", 
        "validate_mechanical_consistency",
        "validate_rule_compliance"
    },
    ValidationType.BALANCE: {
        "calculate_power_level",
        "compare_to_benchmarks",
        "validate_power_scaling",
        "check_balance_thresholds"
    },
    ValidationType.THEMATIC: {
        "validate_theme_consistency",
        "check_naming_conventions",
        "validate_flavor_appropriateness"
    },
    ValidationType.INTEGRATION: {
        "check_content_compatibility",
        "validate_prerequisites",
        "check_interaction_rules"
    },
    ValidationType.PROGRESSION: {
        "validate_level_scaling",
        "check_milestone_appropriateness",
        "validate_tier_progression"
    },
    ValidationType.MULTICLASS: {
        "validate_multiclass_requirements",
        "check_multiclass_interactions",
        "validate_progression_stacking"
    }
}

# ============ HELPER FUNCTIONS FOR CONSTANTS ============

def get_content_requirements(content_type: ContentType) -> Dict[str, Set[str]]:
    """
    Get validation requirements for a specific content type.
    
    Args:
        content_type: The type of content to get requirements for
        
    Returns:
        Dictionary with mandatory, optional, and mechanical requirements
    """
    requirements = CONTENT_VALIDATION_REQUIREMENTS.get(content_type, {})
    
    # Add universal requirements
    if "mandatory" in requirements:
        requirements["mandatory"] = requirements["mandatory"].union(UNIVERSAL_MANDATORY_FIELDS)
    else:
        requirements["mandatory"] = UNIVERSAL_MANDATORY_FIELDS.copy()
    
    if "optional" in requirements:
        requirements["optional"] = requirements["optional"].union(UNIVERSAL_OPTIONAL_FIELDS)
    else:
        requirements["optional"] = UNIVERSAL_OPTIONAL_FIELDS.copy()
    
    return requirements

def get_power_threshold(content_type: ContentType, category: str, level: int) -> float:
    """
    Get power level threshold for content type at specific level.
    
    Args:
        content_type: Type of content
        category: Power category (combat_power, utility_power, etc.)
        level: Character level context
        
    Returns:
        Power threshold value (1.0 = balanced baseline)
    """
    thresholds = POWER_LEVEL_THRESHOLDS.get(content_type, {}).get(category, {})
    
    if not thresholds:
        return 1.0  # Default to balanced baseline
    
    # Find closest level threshold
    closest_level = min(thresholds.keys(), key=lambda x: abs(x - level))
    return thresholds[closest_level]

def get_validation_weight(category: str) -> float:
    """Get validation weight for a specific category."""
    return VALIDATION_CATEGORY_WEIGHTS.get(category, 0.1)  # Default 10% weight

def format_validation_error(error_type: str, **kwargs) -> str:
    """
    Format a validation error message using templates.
    
    Args:
        error_type: Type of error from VALIDATION_ERROR_TEMPLATES
        **kwargs: Template parameters
        
    Returns:
        Formatted error message
    """
    template = VALIDATION_ERROR_TEMPLATES.get(error_type, "Unknown validation error: {error_type}")
    try:
        return template.format(error_type=error_type, **kwargs)
    except KeyError as e:
        return f"Error formatting validation message: missing parameter {e}"

def get_benchmark_power_level(content_type: ContentType, benchmark_name: str) -> float:
    """
    Get official benchmark power level for comparison.
    
    Args:
        content_type: Type of content
        benchmark_name: Name of benchmark content
        
    Returns:
        Power level of benchmark content (1.0 = baseline)
    """
    benchmarks = OFFICIAL_BENCHMARKS.get(content_type, {})
    return benchmarks.get(benchmark_name, 1.0)  # Default to baseline if not found

def get_generation_limit(content_category: str, limit_type: str) -> Any:
    """
    Get generation limit for specific content category and limit type.
    
    Args:
        content_category: Category of content (species_traits, class_features, etc.)
        limit_type: Type of limit (max_count, max_power_budget, etc.)
        
    Returns:
        Limit value or None if not found
    """
    return GENERATION_LIMITS.get(content_category, {}).get(limit_type)

# ============ VALIDATION RULE CONSTANTS METADATA ============

__version__ = '2.0.0'
__description__ = 'D&D 5e/2024 validation rule constants for Clean Architecture content framework'
__author__ = 'D&D Character Creator Backend6'

# Export validation for Clean Architecture compliance
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/constants",
    "dependencies": ["core/enums"],
    "dependents": ["domain/services", "application/use_cases"],
    "immutable": True,
    "infrastructure_independent": True
}