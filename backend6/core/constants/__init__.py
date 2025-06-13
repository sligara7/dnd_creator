"""
Core Constants for the D&D Creative Content Framework.

This module provides all constant values used throughout the system,
organized by their domain purpose according to Clean Architecture principles.

These constants represent immutable business rules and game mechanics that
form the foundation of D&D 5e/2024 content generation and validation.
"""

# Balance and Power Level Constants
from .balance_thresholds import (
    DAMAGE_THRESHOLDS,
    ARMOR_CLASS_THRESHOLDS,
    HIT_POINT_THRESHOLDS,
    MECHANICAL_LIMITS,
    POWER_SCALING_FACTORS,
    POWER_BUDGET_BY_TIER,
    FEATURE_BASE_COSTS,
    REVIEW_THRESHOLDS,
    BALANCE_TOLERANCE,
    OFFICIAL_CONTENT_BENCHMARKS,
    get_power_threshold,
    calculate_feature_cost,
    is_within_balance_threshold
)

# Validation Rules and Requirements
from .validation_rules import (
    RULE_COMPLIANCE_DEFINITIONS,
    VALIDATION_SEVERITY_RULES,
    UNIVERSAL_MANDATORY_FIELDS,
    UNIVERSAL_OPTIONAL_FIELDS,
    CONTENT_VALIDATION_REQUIREMENTS,
    POWER_LEVEL_THRESHOLDS,
    VALIDATION_ERROR_TEMPLATES,
    VALIDATION_CATEGORY_WEIGHTS,
    GENERATION_LIMITS,
    OFFICIAL_BENCHMARKS,
    VALIDATION_TYPE_REQUIREMENTS,
    get_content_requirements,
    get_power_threshold,
    get_validation_weight,
    format_validation_error,
    get_benchmark_power_level,
    get_generation_limit
)

# D&D Core Mechanics Constants
from .dnd_mechanics import (
    ABILITY_SCORES,
    ABILITY_SCORE_RANGES,
    SKILLS_BY_ABILITY,
    ALL_SKILLS,
    SKILL_TO_ABILITY,
    SPELL_SCHOOLS,
    SPELL_LEVELS,
    DAMAGE_TYPES,
    CONDITIONS,
    WEAPON_PROPERTIES,
    CREATURE_SIZES,
    CURRENCY_CONVERSION,
    MULTICLASS_REQUIREMENTS,
    PROFICIENCY_BONUS_BY_LEVEL,
    POWER_TIERS,
    get_ability_modifier,
    is_valid_ability_score,
    get_proficiency_bonus,
    convert_currency,
    get_power_tier
)

# Character Progression Constants
from .progression import (
    LEVEL_RANGES,
    PROGRESSION_BREAKPOINTS,
    SCALING_PATTERNS,
    CANTRIP_DAMAGE_SCALING,
    THEMATIC_MILESTONES,
    POWER_PROGRESSION_CURVE,
    CUSTOMIZATION_BUDGET_BY_LEVEL,
    SIGNATURE_FEATURE_TIMING,
    get_cantrip_dice_count,
    get_expected_power_level,
    get_tier_from_level,
    calculate_multiclass_caster_level
)

# Content Generation Limits
from .generation_limits import (
    GENERATION_SESSION_LIMITS,
    CREATIVITY_LEVEL_LIMITS,
    COMPLEXITY_LIMITS,
    ABSOLUTE_POWER_LIMITS,
    CONTENT_DISTRIBUTION_REQUIREMENTS,
    THEMATIC_DEVIATION_LIMITS,
    NAMING_LIMITS,
    TIME_LIMITS,
    RESOURCE_LIMITS,
    get_generation_limit,
    get_complexity_limit,
    get_time_limit
)

# LLM Prompt Templates
from .llm_prompts import (
    CHARACTER_CONCEPT_PROMPTS,
    CONTENT_GENERATION_PROMPTS,
    CHARACTER_REFINEMENT_PROMPTS,
    PROGRESSION_PROMPTS,
    THEMATIC_TIER_PROMPTS,
    CONVERSATION_PROMPTS,
    BALANCE_ANALYSIS_PROMPTS,
    ERROR_HANDLING_PROMPTS,
    get_character_concept_prompt,
    get_content_generation_prompt,
    get_refinement_prompt,
    get_progression_prompt,
    get_thematic_tier_prompt,
    get_conversation_prompt,
    get_balance_analysis_prompt,
    get_error_handling_prompt,
    validate_prompt_parameters,
    get_prompt_metadata
)

# Export Templates and VTT Formats
from .export_templates import (
    UNIVERSAL_CHARACTER_TEMPLATE,
    DND_BEYOND_TEMPLATE,
    ROLL20_TEMPLATE,
    FANTASY_GROUNDS_TEMPLATE,
    FOUNDRY_VTT_TEMPLATE,
    PDF_CHARACTER_SHEET_TEMPLATE,
    JSON_EXPORT_TEMPLATE,
    LAYOUT_TEMPLATES,
    VTT_PLATFORM_SPECS,
    CUSTOM_CONTENT_TEMPLATES,
    PROGRESSION_EXPORT_TEMPLATE,
    get_export_template,
    get_layout_template,
    get_content_export_template,
    get_platform_specs,
    validate_export_data,
    format_template_string,
    get_supported_export_formats,
    get_export_requirements
)

# Export all public constants organized by architectural concern
__all__ = [
    # ============ BALANCE AND VALIDATION CONSTANTS ============
    'DAMAGE_THRESHOLDS',
    'ARMOR_CLASS_THRESHOLDS', 
    'HIT_POINT_THRESHOLDS',
    'MECHANICAL_LIMITS',
    'POWER_SCALING_FACTORS',
    'POWER_BUDGET_BY_TIER',
    'FEATURE_BASE_COSTS',
    'REVIEW_THRESHOLDS',
    'BALANCE_TOLERANCE',
    'OFFICIAL_CONTENT_BENCHMARKS',
    
    # ============ VALIDATION RULES CONSTANTS ============
    'RULE_COMPLIANCE_DEFINITIONS',
    'VALIDATION_SEVERITY_RULES',
    'UNIVERSAL_MANDATORY_FIELDS',
    'UNIVERSAL_OPTIONAL_FIELDS',
    'CONTENT_VALIDATION_REQUIREMENTS',
    'POWER_LEVEL_THRESHOLDS',
    'VALIDATION_ERROR_TEMPLATES',
    'VALIDATION_CATEGORY_WEIGHTS',
    'GENERATION_LIMITS',
    'OFFICIAL_BENCHMARKS',
    'VALIDATION_TYPE_REQUIREMENTS',
    
    # ============ D&D CORE MECHANICS CONSTANTS ============
    'ABILITY_SCORES',
    'ABILITY_SCORE_RANGES',
    'SKILLS_BY_ABILITY',
    'ALL_SKILLS',
    'SKILL_TO_ABILITY',
    'SPELL_SCHOOLS',
    'SPELL_LEVELS',
    'DAMAGE_TYPES',
    'CONDITIONS',
    'WEAPON_PROPERTIES',
    'CREATURE_SIZES',
    'CURRENCY_CONVERSION',
    'MULTICLASS_REQUIREMENTS',
    'PROFICIENCY_BONUS_BY_LEVEL',
    'POWER_TIERS',
    
    # ============ CHARACTER PROGRESSION CONSTANTS ============
    'LEVEL_RANGES',
    'PROGRESSION_BREAKPOINTS',
    'SCALING_PATTERNS',
    'CANTRIP_DAMAGE_SCALING',
    'THEMATIC_MILESTONES',
    'POWER_PROGRESSION_CURVE',
    'CUSTOMIZATION_BUDGET_BY_LEVEL',
    'SIGNATURE_FEATURE_TIMING',
    
    # ============ GENERATION LIMITS CONSTANTS ============
    'GENERATION_SESSION_LIMITS',
    'CREATIVITY_LEVEL_LIMITS',  
    'COMPLEXITY_LIMITS',
    'ABSOLUTE_POWER_LIMITS',
    'CONTENT_DISTRIBUTION_REQUIREMENTS',
    'THEMATIC_DEVIATION_LIMITS',
    'NAMING_LIMITS',
    'TIME_LIMITS',
    'RESOURCE_LIMITS',
    
    # ============ LLM PROMPT TEMPLATES ============
    'CHARACTER_CONCEPT_PROMPTS',
    'CONTENT_GENERATION_PROMPTS',
    'CHARACTER_REFINEMENT_PROMPTS',
    'PROGRESSION_PROMPTS',
    'THEMATIC_TIER_PROMPTS',
    'CONVERSATION_PROMPTS',
    'BALANCE_ANALYSIS_PROMPTS',
    'ERROR_HANDLING_PROMPTS',
    
    # ============ EXPORT TEMPLATES ============
    'UNIVERSAL_CHARACTER_TEMPLATE',
    'DND_BEYOND_TEMPLATE',
    'ROLL20_TEMPLATE',
    'FANTASY_GROUNDS_TEMPLATE',
    'FOUNDRY_VTT_TEMPLATE',
    'PDF_CHARACTER_SHEET_TEMPLATE',
    'JSON_EXPORT_TEMPLATE',
    'LAYOUT_TEMPLATES',
    'VTT_PLATFORM_SPECS',
    'CUSTOM_CONTENT_TEMPLATES',
    'PROGRESSION_EXPORT_TEMPLATE',
    
    # ============ UTILITY FUNCTIONS ============
    # Core Mechanics
    'get_ability_modifier',
    'is_valid_ability_score',
    'get_proficiency_bonus',
    'convert_currency',
    'get_power_tier',
    
    # Progression
    'get_cantrip_dice_count',
    'get_expected_power_level',
    'get_tier_from_level',
    'calculate_multiclass_caster_level',
    
    # Balance and Validation
    'get_power_threshold',
    'calculate_feature_cost',
    'is_within_balance_threshold',
    'get_content_requirements',
    'get_validation_weight',
    'format_validation_error',
    'get_benchmark_power_level',
    
    # Generation Limits
    'get_generation_limit',
    'get_complexity_limit', 
    'get_time_limit',
    
    # LLM Prompts
    'get_character_concept_prompt',
    'get_content_generation_prompt',
    'get_refinement_prompt',
    'get_progression_prompt',
    'get_thematic_tier_prompt',
    'get_conversation_prompt',
    'get_balance_analysis_prompt',
    'get_error_handling_prompt',
    'validate_prompt_parameters',
    'get_prompt_metadata',
    
    # Export Templates
    'get_export_template',
    'get_layout_template',
    'get_content_export_template',
    'get_platform_specs',
    'validate_export_data',
    'format_template_string',
    'get_supported_export_formats',
    'get_export_requirements',
]

# Constant registry organized by Clean Architecture concerns
CONSTANT_REGISTRY = {
    # ============ CORE LAYER CONSTANTS ============
    'core_mechanics': {
        'abilities': ABILITY_SCORES,
        'skills': ALL_SKILLS,
        'damage_types': DAMAGE_TYPES,
        'conditions': CONDITIONS,
        'spell_schools': SPELL_SCHOOLS,
        'power_tiers': POWER_TIERS,
        'currency_conversion': CURRENCY_CONVERSION,
        'multiclass_requirements': MULTICLASS_REQUIREMENTS
    },
    
    # ============ DOMAIN LAYER CONSTANTS ============
    'balance_validation': {
        'damage_thresholds': DAMAGE_THRESHOLDS,
        'mechanical_limits': MECHANICAL_LIMITS,
        'power_scaling': POWER_SCALING_FACTORS,
        'balance_tolerance': BALANCE_TOLERANCE,
        'rule_compliance': RULE_COMPLIANCE_DEFINITIONS,
        'validation_requirements': CONTENT_VALIDATION_REQUIREMENTS,
        'power_level_thresholds': POWER_LEVEL_THRESHOLDS,
        'official_benchmarks': OFFICIAL_BENCHMARKS
    },
    'character_progression': {
        'level_ranges': LEVEL_RANGES,
        'progression_breakpoints': PROGRESSION_BREAKPOINTS,
        'thematic_milestones': THEMATIC_MILESTONES,
        'power_curve': POWER_PROGRESSION_CURVE,
        'scaling_patterns': SCALING_PATTERNS,
        'cantrip_scaling': CANTRIP_DAMAGE_SCALING
    },
    'content_generation': {
        'character_prompts': CHARACTER_CONCEPT_PROMPTS,
        'content_prompts': CONTENT_GENERATION_PROMPTS,
        'refinement_prompts': CHARACTER_REFINEMENT_PROMPTS,
        'progression_prompts': PROGRESSION_PROMPTS,
        'conversation_prompts': CONVERSATION_PROMPTS,
        'error_prompts': ERROR_HANDLING_PROMPTS
    },
    
    # ============ APPLICATION LAYER CONSTANTS ============
    'generation_constraints': {
        'session_limits': GENERATION_SESSION_LIMITS,
        'complexity_limits': COMPLEXITY_LIMITS,
        'time_limits': TIME_LIMITS,
        'resource_limits': RESOURCE_LIMITS,
        'creativity_limits': CREATIVITY_LEVEL_LIMITS,
        'absolute_limits': ABSOLUTE_POWER_LIMITS
    },
    'export_formats': {
        'universal_template': UNIVERSAL_CHARACTER_TEMPLATE,
        'vtt_templates': {
            'dnd_beyond': DND_BEYOND_TEMPLATE,
            'roll20': ROLL20_TEMPLATE,
            'fantasy_grounds': FANTASY_GROUNDS_TEMPLATE,
            'foundry': FOUNDRY_VTT_TEMPLATE
        },
        'layout_templates': LAYOUT_TEMPLATES,
        'platform_specs': VTT_PLATFORM_SPECS,
        'custom_content': CUSTOM_CONTENT_TEMPLATES
    }
}

# Enhanced utility functions for constant management
def get_constants_by_category(category: str) -> dict:
    """
    Get constants for a specific category.
    
    Args:
        category: Category name (core_mechanics, balance_validation, etc.)
        
    Returns:
        Dictionary of constants for the category
    """
    return CONSTANT_REGISTRY.get(category, {})

def get_all_constant_categories() -> list[str]:
    """Get list of all available constant categories."""
    return list(CONSTANT_REGISTRY.keys())

def search_constants(search_term: str) -> dict[str, dict]:
    """
    Search for constants containing a specific term.
    
    Args:
        search_term: Term to search for
        
    Returns:
        Dictionary of matching constants by category
    """
    results = {}
    search_lower = search_term.lower()
    
    for category, constants in CONSTANT_REGISTRY.items():
        matching_constants = {}
        for const_name, const_value in constants.items():
            if search_lower in const_name.lower():
                matching_constants[const_name] = const_value
        
        if matching_constants:
            results[category] = matching_constants
    
    return results

def get_content_validation_constants() -> dict:
    """Get all constants related to content validation."""
    return {
        'rule_compliance': RULE_COMPLIANCE_DEFINITIONS,
        'validation_requirements': CONTENT_VALIDATION_REQUIREMENTS,
        'power_thresholds': POWER_LEVEL_THRESHOLDS,
        'error_templates': VALIDATION_ERROR_TEMPLATES,
        'category_weights': VALIDATION_CATEGORY_WEIGHTS,
        'generation_limits': GENERATION_LIMITS,
        'benchmarks': OFFICIAL_BENCHMARKS
    }

def get_llm_prompt_constants() -> dict:
    """Get all LLM prompt templates organized by purpose."""
    return {
        'character_concepts': CHARACTER_CONCEPT_PROMPTS,
        'content_generation': CONTENT_GENERATION_PROMPTS,
        'character_refinement': CHARACTER_REFINEMENT_PROMPTS,
        'progression': PROGRESSION_PROMPTS,
        'thematic_tiers': THEMATIC_TIER_PROMPTS,
        'conversation_flow': CONVERSATION_PROMPTS,
        'balance_analysis': BALANCE_ANALYSIS_PROMPTS,
        'error_handling': ERROR_HANDLING_PROMPTS
    }

def get_export_constants() -> dict:
    """Get all export template and VTT format constants."""
    return {
        'universal_template': UNIVERSAL_CHARACTER_TEMPLATE,
        'vtt_templates': {
            'dnd_beyond': DND_BEYOND_TEMPLATE,
            'roll20': ROLL20_TEMPLATE,
            'fantasy_grounds': FANTASY_GROUNDS_TEMPLATE,
            'foundry': FOUNDRY_VTT_TEMPLATE
        },
        'standard_formats': {
            'pdf': PDF_CHARACTER_SHEET_TEMPLATE,
            'json': JSON_EXPORT_TEMPLATE
        },
        'layouts': LAYOUT_TEMPLATES,
        'platform_specs': VTT_PLATFORM_SPECS,
        'custom_content': CUSTOM_CONTENT_TEMPLATES,
        'progression': PROGRESSION_EXPORT_TEMPLATE
    }

def validate_constant_integrity() -> list[str]:
    """
    Validate that all constants are properly defined and consistent.
    
    Returns:
        List of validation issues (empty if all constants are valid)
    """
    issues = []
    
    # Check that core mechanics constants are present
    required_core = ['abilities', 'skills', 'damage_types', 'spell_schools']
    core_constants = CONSTANT_REGISTRY.get('core_mechanics', {})
    for req in required_core:
        if req not in core_constants:
            issues.append(f"Missing required core mechanic constant: {req}")
    
    # Check that balance constants are reasonable
    if 'balance_validation' in CONSTANT_REGISTRY:
        balance_constants = CONSTANT_REGISTRY['balance_validation']
        
        # Validate balance tolerance values
        if 'balance_tolerance' in balance_constants:
            for mode, tolerance in balance_constants['balance_tolerance'].items():
                if not isinstance(tolerance, (int, float)) or tolerance < 0 or tolerance > 1:
                    issues.append(f"Invalid balance tolerance for {mode}: {tolerance}")
        
        # Check rule compliance definitions
        if 'rule_compliance' in balance_constants:
            for compliance_level, definition in balance_constants['rule_compliance'].items():
                if 'power_deviation_tolerance' not in definition:
                    issues.append(f"Missing power deviation tolerance for {compliance_level}")
    
    # Validate prompt templates have required structure
    if 'content_generation' in CONSTANT_REGISTRY:
        prompt_constants = CONSTANT_REGISTRY['content_generation']
        required_prompt_types = ['character_prompts', 'content_prompts', 'conversation_prompts']
        for req in required_prompt_types:
            if req not in prompt_constants:
                issues.append(f"Missing required prompt template category: {req}")
    
    # Validate export templates
    if 'export_formats' in CONSTANT_REGISTRY:
        export_constants = CONSTANT_REGISTRY['export_formats']
        if 'universal_template' not in export_constants:
            issues.append("Missing universal character template")
        
        if 'vtt_templates' in export_constants:
            required_vtt = ['dnd_beyond', 'roll20', 'foundry']
            vtt_templates = export_constants['vtt_templates']
            for req in required_vtt:
                if req not in vtt_templates:
                    issues.append(f"Missing VTT template for: {req}")
    
    return issues

def get_constant_statistics() -> dict:
    """Get statistics about the constant system."""
    stats = {
        'total_categories': len(CONSTANT_REGISTRY),
        'total_constants': 0,
        'category_breakdown': {}
    }
    
    for category, constants in CONSTANT_REGISTRY.items():
        count = len(constants)
        stats['category_breakdown'][category] = count
        stats['total_constants'] += count
    
    # Add specific statistics
    stats['prompt_templates'] = len(CHARACTER_CONCEPT_PROMPTS) + len(CONTENT_GENERATION_PROMPTS)
    stats['export_formats'] = len(VTT_PLATFORM_SPECS)
    stats['validation_rules'] = len(CONTENT_VALIDATION_REQUIREMENTS)
    stats['core_mechanics'] = len(ABILITY_SCORES) + len(ALL_SKILLS) + len(DAMAGE_TYPES)
    
    return stats

def print_constant_summary():
    """Print a summary of all available constants."""
    print("=== D&D Character Creator - Constants Summary ===\n")
    
    stats = get_constant_statistics()
    print(f"Total Categories: {stats['total_categories']}")
    print(f"Total Constants: {stats['total_constants']}\n")
    
    print("Category Breakdown:")
    for category, count in stats['category_breakdown'].items():
        print(f"  {category}: {count} constants")
    
    print(f"\nSpecialized Systems:")
    print(f"  LLM Prompt Templates: {stats['prompt_templates']}")
    print(f"  VTT Export Formats: {stats['export_formats']}")
    print(f"  Validation Rules: {stats['validation_rules']}")
    print(f"  Core D&D Mechanics: {stats['core_mechanics']}")
    
    # Check integrity
    issues = validate_constant_integrity()
    if issues:
        print(f"\n⚠️  Validation Issues Found: {len(issues)}")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print(f"\n✅ All constants validated successfully")

# Module metadata
__version__ = '2.0.0'  
__description__ = 'Clean Architecture constants for D&D Creative Content Framework'
__author__ = 'D&D Character Creator Backend6'

# Clean Architecture compliance metadata
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/constants",
    "dependencies": ["core/enums"],
    "dependents": ["domain/services", "application/use_cases", "infrastructure"],
    "immutable": True,
    "infrastructure_independent": True,
    "total_constants": len(__all__),
    "validation_status": "passed" if not validate_constant_integrity() else "issues_found"
}

# Validate constants on import
_VALIDATION_ISSUES = validate_constant_integrity()
if _VALIDATION_ISSUES:
    import warnings
    warnings.warn(f"Constant validation issues found: {_VALIDATION_ISSUES}")

# Optional: Print summary on import (can be disabled)
PRINT_SUMMARY_ON_IMPORT = False  # Set to True for debugging

if PRINT_SUMMARY_ON_IMPORT:
    import sys
    if not sys.flags.quiet:
        print_constant_summary()