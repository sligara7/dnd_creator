"""
Enhanced Core Utilities for D&D Creative Content Framework.

COMPLETELY REFACTORED: Full integration with enhanced culture system, validation framework,
and LLM providers following CREATIVE_VALIDATION_APPROACH philosophy.

This module provides stateless, reusable functions for content processing,
validation, and analysis with complete enum integration. These utilities support 
the framework's core operations with enhanced character generation focus.

Enhanced with Complete Creative Culture Generation System:
- Enhanced culture generation with enum-based assessment
- Creative validation with constructive enhancement suggestions
- Character generation optimization with preset compatibility
- Gaming utility focus with table-friendly enhancements
- Text processing with cultural awareness and authenticity assessment
- LLM provider integration for enhanced content generation
"""

from typing import Dict, List, Optional, Any, Union

# ============================================================================
# CORE UTILITY IMPORTS
# ============================================================================

# Balance Calculator
from .balance_calculator import (
    calculate_overall_balance_score,
    calculate_power_level_score,
    calculate_utility_score,
    calculate_versatility_score,
    calculate_scaling_score,
    calculate_damage_per_round,
    parse_average_damage,
    calculate_survivability_score,
    calculate_resource_efficiency,
    create_balance_metrics,
)

# Content Utils
from .content_utils import (
    extract_themes_from_content,
    merge_content_themes,
    filter_content_by_theme,
    calculate_thematic_compatibility,
    group_content_by_theme,
    analyze_content_complexity,
    find_content_dependencies,
    suggest_complementary_content,
    serialize_content_collection,
    deserialize_content_collection,
    validate_content_structure,
    normalize_content_data,
)

# Naming Validator
from .naming_validator import (
    validate_content_name,
    suggest_name_improvements,
    generate_name_variations,
    validate_name_uniqueness,
    check_name_authenticity,
)

# Mechanical Parser
from .mechanical_parser import (
    MechanicalElement,
    extract_mechanical_elements,
    parse_damage_expression,
    analyze_mechanical_complexity,
    extract_spell_components,
    extract_scaling_information,
    validate_mechanical_consistency,
    get_category_patterns,
    get_category_keywords,
    get_all_mechanical_keywords,
    categorize_keyword,
    find_mechanical_keywords_in_text,
)

# Rule Checker
from .rule_checker import (
    validate_ability_scores,
    validate_character_level,
    validate_proficiency_bonus,
    validate_hit_points,
    validate_armor_class,
    validate_saving_throws,
    validate_spell_slots,
    validate_content_rarity_balance,
    validate_multiclass_prerequisites,
    calculate_proficiency_bonus,
    calculate_ability_modifier,
    get_spell_slots_by_level,
)

# ============================================================================
# ENHANCED CULTURE SYSTEM IMPORTS
# ============================================================================

# Enhanced Culture Generation System
from .cultures import (
    # Enhanced Core Classes
    EnhancedCreativeCultureGenerator,
    EnhancedCreativeCultureParser,
    EnhancedCreativePromptTemplates,
    CultureGenerationOrchestrator,
    
    # Enhanced Data Structures
    EnhancedCreativeCulture,
    EnhancedCreativeParsingResult,
    EnhancedCharacterPromptTemplate,
    EnhancedCreativeCultureSpec,
    CultureGenerationRequest,
    CultureGenerationResult,
    
    # Enhanced Core Functions
    get_culture_enhanced,
    list_cultures_enhanced,
    get_cultures_by_type_enhanced,
    generate_culture_content,
    
    # Enhanced Character Generation Functions
    create_character_culture_spec_enhanced,
    validate_creative_culture_spec_enhanced,
    parse_for_characters_enhanced,
    extract_character_names_enhanced,
    assess_character_readiness_enhanced,
    build_character_culture_prompt_enhanced,
    build_creative_enhancement_prompt_enhanced,
    build_gaming_validation_prompt_enhanced,
    get_character_prompt_recommendations_enhanced,
    
    # Enhanced Factory Functions
    create_sky_culture_spec_enhanced,
    create_mystical_culture_spec_enhanced,
    create_nomad_culture_spec_enhanced,
    
    # Enhanced Workflow Functions
    generate_character_culture_enhanced,
    parse_and_enhance_response_enhanced,
    enhance_culture_for_characters_enhanced,
    create_quick_character_culture_enhanced,
    
    # Enhanced Module Validation
    validate_enhanced_culture_module_integrity,
    
    # Enhanced Metadata
    ENHANCED_CREATIVE_VALIDATION_APPROACH_COMPLIANCE,
    ENHANCED_CHARACTER_GENERATION_GUIDELINES,
)

# ============================================================================
# ENHANCED VALIDATION SYSTEM IMPORTS
# ============================================================================

# Enhanced Validation System
from .validation import (
    # Enhanced Core Classes
    EnhancedCreativeCultureValidator,
    EnhancedCreativeValidationResult,
    EnhancedCreativeValidationIssue,
    
    # Enhanced Enums
    EnhancedValidationIssueType,
    EnhancedCreativeValidationFocus,
    
    # Enhanced Core Functions
    validate_culture_for_characters,
    quick_culture_assessment,
    get_culture_enhancement_suggestions,
    
    # Enhanced Convenience Functions
    validate_character_culture_enhanced,
    validate_culture_names_for_characters_enhanced,
    get_culture_enhancement_suggestions_enhanced,
    validate_multiple_cultures_enhanced,
    
    # Enhanced Preset Validation Functions
    validate_fantasy_culture_enhanced,
    validate_historical_inspired_culture_enhanced,
    validate_original_culture_enhanced,
    validate_gaming_optimized_culture,
    
    # Enhanced Module Validation
    validate_enhanced_validation_module_integrity,
    
    # Enhanced Metadata
    CREATIVE_VALIDATION_APPROACH,
    CREATIVE_VALIDATION_PHILOSOPHY,
)

# ============================================================================
# ENHANCED TEXT PROCESSING IMPORTS
# ============================================================================

# Enhanced Text Processing System
from .text_processing import (
    # Enhanced Type Definitions
    EnhancedTextStyle,
    EnhancedContentType,
    EnhancedNameComponents,
    EnhancedTextAnalysis,
    EnhancedValidationResult,
    
    # Enhanced Core Functions
    format_text_enhanced,
    sanitize_text_input_enhanced,
    validate_character_sheet_text_enhanced,
    analyze_text_content_enhanced,
    
    # Enhanced Analysis Functions
    calculate_reading_level_enhanced,
    count_syllables_enhanced,
    calculate_text_complexity_enhanced,
    extract_fantasy_terms_enhanced,
    detect_sentiment_enhanced,
    extract_keywords_enhanced,
    detect_language_enhanced,
    extract_cultural_references_enhanced,
)

# ============================================================================
# ENHANCED ENUM IMPORTS
# ============================================================================

# Enhanced Culture Type Enums
from ..enums.culture_types import (
    # Core generation and validation enums
    CultureGenerationType,
    CultureAuthenticityLevel,
    CultureCreativityLevel,
    CultureSourceType,
    CultureComplexityLevel,
    CultureValidationCategory,
    CultureValidationSeverity,
    
    # Enhancement system enums (NEW)
    CultureEnhancementCategory,
    CultureEnhancementPriority,
    CultureGenerationStatus,
    
    # Cultural structure enums
    CultureNamingStructure,
    CultureGenderSystem,
    CultureLinguisticFamily,
    CultureTemporalPeriod,
    
    # Enhanced utility functions (NEW)
    suggest_creative_culture_enhancements,
    calculate_character_generation_score,
    get_character_generation_recommendations,
    
    # Preset system (NEW)
    CHARACTER_CULTURE_PRESETS,
    CREATIVE_VALIDATION_APPROACH_COMPLIANCE,
)

# Legacy compatibility mappings
CreativeCultureGenerator = EnhancedCreativeCultureGenerator
CreativeCultureParser = EnhancedCreativeCultureParser
CreativePromptTemplates = EnhancedCreativePromptTemplates
CreativeCulture = EnhancedCreativeCulture
CreativeParsingResult = EnhancedCreativeParsingResult
CharacterPromptTemplate = EnhancedCharacterPromptTemplate
CreativeCultureSpec = EnhancedCreativeCultureSpec

# ============================================================================
# ENHANCED MODULE EXPORTS
# ============================================================================

__all__ = [
    # Balance Calculator
    'calculate_overall_balance_score',
    'calculate_power_level_score',
    'calculate_utility_score',
    'calculate_versatility_score',
    'calculate_scaling_score',
    'calculate_damage_per_round',
    'parse_average_damage',
    'calculate_survivability_score',
    'calculate_resource_efficiency',
    'create_balance_metrics',
    
    # Content Utils
    'extract_themes_from_content',
    'merge_content_themes',
    'filter_content_by_theme',
    'calculate_thematic_compatibility',
    'group_content_by_theme',
    'analyze_content_complexity',
    'find_content_dependencies',
    'suggest_complementary_content',
    'serialize_content_collection',
    'deserialize_content_collection',
    'validate_content_structure',
    'normalize_content_data',
    
    # Naming Validator
    'validate_content_name',
    'suggest_name_improvements',
    'generate_name_variations',
    'validate_name_uniqueness',
    'check_name_authenticity',
    
    # Mechanical Parser
    'MechanicalElement',
    'extract_mechanical_elements',
    'parse_damage_expression',
    'analyze_mechanical_complexity',
    'extract_spell_components',
    'extract_scaling_information',
    'validate_mechanical_consistency',
    'get_category_patterns',
    'get_category_keywords',
    'get_all_mechanical_keywords',
    'categorize_keyword',
    'find_mechanical_keywords_in_text',
    
    # Rule Checker
    'validate_ability_scores',
    'validate_character_level',
    'validate_proficiency_bonus',
    'validate_hit_points',
    'validate_armor_class',
    'validate_saving_throws',
    'validate_spell_slots',
    'validate_content_rarity_balance',
    'validate_multiclass_prerequisites',
    'calculate_proficiency_bonus',
    'calculate_ability_modifier',
    'get_spell_slots_by_level',
    
    # Enhanced Culture Generation System
    'EnhancedCreativeCultureGenerator',
    'EnhancedCreativeCultureParser',
    'EnhancedCreativePromptTemplates',
    'CultureGenerationOrchestrator',
    'EnhancedCreativeCulture',
    'EnhancedCreativeParsingResult',
    'EnhancedCharacterPromptTemplate',
    'EnhancedCreativeCultureSpec',
    'CultureGenerationRequest',
    'CultureGenerationResult',
    
    # Legacy compatibility
    'CreativeCultureGenerator',
    'CreativeCultureParser',
    'CreativePromptTemplates',
    'CreativeCulture',
    'CreativeParsingResult',
    'CharacterPromptTemplate',
    'CreativeCultureSpec',
    
    # Enhanced Culture Functions
    'get_culture_enhanced',
    'list_cultures_enhanced',
    'get_cultures_by_type_enhanced',
    'generate_culture_content',
    
    # Enhanced Character Generation Functions
    'create_character_culture_spec_enhanced',
    'validate_creative_culture_spec_enhanced',
    'parse_for_characters_enhanced',
    'extract_character_names_enhanced',
    'assess_character_readiness_enhanced',
    'build_character_culture_prompt_enhanced',
    'build_creative_enhancement_prompt_enhanced',
    'build_gaming_validation_prompt_enhanced',
    'get_character_prompt_recommendations_enhanced',
    
    # Enhanced Factory Functions
    'create_sky_culture_spec_enhanced',
    'create_mystical_culture_spec_enhanced',
    'create_nomad_culture_spec_enhanced',
    
    # Enhanced Workflow Functions
    'generate_character_culture_enhanced',
    'parse_and_enhance_response_enhanced',
    'enhance_culture_for_characters_enhanced',
    'create_quick_character_culture_enhanced',
    
    # Enhanced Validation System
    'EnhancedCreativeCultureValidator',
    'EnhancedCreativeValidationResult',
    'EnhancedCreativeValidationIssue',
    'EnhancedValidationIssueType',
    'EnhancedCreativeValidationFocus',
    'validate_culture_for_characters',
    'quick_culture_assessment',
    'get_culture_enhancement_suggestions',
    'validate_character_culture_enhanced',
    'validate_culture_names_for_characters_enhanced',
    'get_culture_enhancement_suggestions_enhanced',
    'validate_multiple_cultures_enhanced',
    'validate_fantasy_culture_enhanced',
    'validate_historical_inspired_culture_enhanced',
    'validate_original_culture_enhanced',
    'validate_gaming_optimized_culture',
    
    # Enhanced Text Processing System
    'EnhancedTextStyle',
    'EnhancedContentType',
    'EnhancedNameComponents',
    'EnhancedTextAnalysis',
    'EnhancedValidationResult',
    'format_text_enhanced',
    'sanitize_text_input_enhanced',
    'validate_character_sheet_text_enhanced',
    'analyze_text_content_enhanced',
    'calculate_reading_level_enhanced',
    'count_syllables_enhanced',
    'calculate_text_complexity_enhanced',
    'extract_fantasy_terms_enhanced',
    'detect_sentiment_enhanced',
    'extract_keywords_enhanced',
    'detect_language_enhanced',
    'extract_cultural_references_enhanced',
    
    # Enhanced Culture Type Enums
    'CultureGenerationType',
    'CultureAuthenticityLevel',
    'CultureCreativityLevel',
    'CultureSourceType',
    'CultureComplexityLevel',
    'CultureValidationCategory',
    'CultureValidationSeverity',
    'CultureEnhancementCategory',
    'CultureEnhancementPriority',
    'CultureGenerationStatus',
    'CultureNamingStructure',
    'CultureGenderSystem',
    'CultureLinguisticFamily',
    'CultureTemporalPeriod',
    
    # Enhanced Enum Utility Functions
    'suggest_creative_culture_enhancements',
    'calculate_character_generation_score',
    'get_character_generation_recommendations',
    
    # Enhanced System Components
    'CHARACTER_CULTURE_PRESETS',
    'CREATIVE_VALIDATION_APPROACH_COMPLIANCE',
    'ENHANCED_CREATIVE_VALIDATION_APPROACH_COMPLIANCE',
    'ENHANCED_CHARACTER_GENERATION_GUIDELINES',
    'CREATIVE_VALIDATION_APPROACH',
    'CREATIVE_VALIDATION_PHILOSOPHY',
    
    # Enhanced Module Validation
    'validate_enhanced_culture_module_integrity',
    'validate_enhanced_validation_module_integrity',
]

# ============================================================================
# ENHANCED UTILITY FUNCTION REGISTRY
# ============================================================================

ENHANCED_UTILITY_REGISTRY = {
    # Balance functions
    'balance_overall': calculate_overall_balance_score,
    'balance_power': calculate_power_level_score,
    'balance_utility': calculate_utility_score,
    'balance_versatility': calculate_versatility_score,
    'balance_scaling': calculate_scaling_score,
    'balance_damage_per_round': calculate_damage_per_round,
    'balance_survivability': calculate_survivability_score,
    'balance_resource_efficiency': calculate_resource_efficiency,
    
    # Content analysis
    'content_themes': extract_themes_from_content,
    'content_compatibility': calculate_thematic_compatibility,
    'content_complexity': analyze_content_complexity,
    'content_dependencies': find_content_dependencies,
    'content_validate_structure': validate_content_structure,
    'content_normalize': normalize_content_data,
    
    # Naming validation
    'naming_validate': validate_content_name,
    'naming_suggest': suggest_name_improvements,
    'naming_generate_variants': generate_name_variations,
    'naming_check_uniqueness': validate_name_uniqueness,
    'naming_check_authenticity': check_name_authenticity,
    
    # Mechanical parsing  
    'mechanical_extract': extract_mechanical_elements,
    'mechanical_parse_damage': parse_damage_expression,
    'mechanical_complexity': analyze_mechanical_complexity,
    'mechanical_spell_components': extract_spell_components,
    'mechanical_scaling': extract_scaling_information,
    'mechanical_validate': validate_mechanical_consistency,
    
    # Rule validation
    'rules_ability_scores': validate_ability_scores,
    'rules_character_level': validate_character_level,
    'rules_hit_points': validate_hit_points,
    'rules_armor_class': validate_armor_class,
    'rules_saving_throws': validate_saving_throws,
    'rules_spell_slots': validate_spell_slots,
    'rules_rarity_balance': validate_content_rarity_balance,
    'rules_multiclass': validate_multiclass_prerequisites,
    
    # Enhanced Culture Generation System
    'culture_generate_character_enhanced': generate_character_culture_enhanced,
    'culture_create_quick_enhanced': create_quick_character_culture_enhanced,
    'culture_parse_response_enhanced': parse_for_characters_enhanced,
    'culture_extract_names_enhanced': extract_character_names_enhanced,
    'culture_assess_readiness_enhanced': assess_character_readiness_enhanced,
    'culture_enhance_for_characters_enhanced': enhance_culture_for_characters_enhanced,
    'culture_create_spec_enhanced': create_character_culture_spec_enhanced,
    'culture_validate_spec_enhanced': validate_creative_culture_spec_enhanced,
    'culture_build_prompt_enhanced': build_character_culture_prompt_enhanced,
    'culture_build_enhancement_prompt_enhanced': build_creative_enhancement_prompt_enhanced,
    'culture_sky_spec_enhanced': create_sky_culture_spec_enhanced,
    'culture_mystical_spec_enhanced': create_mystical_culture_spec_enhanced,
    'culture_nomad_spec_enhanced': create_nomad_culture_spec_enhanced,
    
    # Enhanced Validation Functions
    'validation_character_culture_enhanced': validate_character_culture_enhanced,
    'validation_culture_names_enhanced': validate_culture_names_for_characters_enhanced,
    'validation_enhancement_suggestions_enhanced': get_culture_enhancement_suggestions_enhanced,
    'validation_multiple_cultures_enhanced': validate_multiple_cultures_enhanced,
    'validation_fantasy_culture_enhanced': validate_fantasy_culture_enhanced,
    'validation_historical_culture_enhanced': validate_historical_inspired_culture_enhanced,
    'validation_original_culture_enhanced': validate_original_culture_enhanced,
    'validation_gaming_optimized_culture': validate_gaming_optimized_culture,
    'validation_quick_assessment': quick_culture_assessment,
    'validation_culture_for_characters': validate_culture_for_characters,
    
    # Enhanced Text Processing Functions
    'text_format_enhanced': format_text_enhanced,
    'text_sanitize_enhanced': sanitize_text_input_enhanced,
    'text_validate_character_sheet_enhanced': validate_character_sheet_text_enhanced,
    'text_analyze_content_enhanced': analyze_text_content_enhanced,
    'text_reading_level_enhanced': calculate_reading_level_enhanced,
    'text_syllables_enhanced': count_syllables_enhanced,
    'text_complexity_enhanced': calculate_text_complexity_enhanced,
    'text_fantasy_terms_enhanced': extract_fantasy_terms_enhanced,
    'text_sentiment_enhanced': detect_sentiment_enhanced,
    'text_keywords_enhanced': extract_keywords_enhanced,
    'text_language_enhanced': detect_language_enhanced,
    'text_cultural_references_enhanced': extract_cultural_references_enhanced,
    
    # Enhanced Module Validation
    'validate_culture_module_enhanced': validate_enhanced_culture_module_integrity,
    'validate_validation_module_enhanced': validate_enhanced_validation_module_integrity,
    
    # Enhanced Enum Utilities
    'enum_suggest_enhancements': suggest_creative_culture_enhancements,
    'enum_calculate_generation_score': calculate_character_generation_score,
    'enum_get_recommendations': get_character_generation_recommendations,
}

# Legacy registry mapping for backward compatibility
UTILITY_REGISTRY = ENHANCED_UTILITY_REGISTRY.copy()

# ============================================================================
# ENHANCED UTILITY ACCESS FUNCTIONS
# ============================================================================

def get_utility_function_enhanced(function_name: str):
    """
    Get enhanced utility function by name for dynamic access.
    
    Args:
        function_name: Name of the utility function
        
    Returns:
        Function object or None if not found
    """
    return ENHANCED_UTILITY_REGISTRY.get(function_name)


def list_available_utilities_enhanced() -> Dict[str, List[str]]:
    """
    Get organized list of enhanced utility functions.
    
    Returns:
        Dictionary organized by utility category with enhanced functions
    """
    return {
        "balance": [name for name in ENHANCED_UTILITY_REGISTRY if name.startswith('balance_')],
        "content": [name for name in ENHANCED_UTILITY_REGISTRY if name.startswith('content_')],
        "naming": [name for name in ENHANCED_UTILITY_REGISTRY if name.startswith('naming_')],
        "mechanical": [name for name in ENHANCED_UTILITY_REGISTRY if name.startswith('mechanical_')],
        "rules": [name for name in ENHANCED_UTILITY_REGISTRY if name.startswith('rules_')],
        "culture": [name for name in ENHANCED_UTILITY_REGISTRY if name.startswith('culture_')],
        "validation": [name for name in ENHANCED_UTILITY_REGISTRY if name.startswith('validation_')],
        "text_processing": [name for name in ENHANCED_UTILITY_REGISTRY if name.startswith('text_')],
        "enum_utilities": [name for name in ENHANCED_UTILITY_REGISTRY if name.startswith('enum_')]
    }


def get_utilities_by_category_enhanced(category: str) -> List[str]:
    """
    Get enhanced utility functions for a specific category.
    
    Args:
        category: Category name (balance, content, naming, mechanical, rules, culture, validation, text_processing, enum_utilities)
        
    Returns:
        List of function names in that category
    """
    all_utilities = list_available_utilities_enhanced()
    return all_utilities.get(category, [])


def validate_utility_availability_enhanced() -> Dict[str, Any]:
    """
    Enhanced validation of utility module availability and health.
    
    Returns:
        Dictionary showing availability and health of each utility category
    """
    availability = {}
    
    # Core utilities
    try:
        from . import balance_calculator
        availability['balance_calculator'] = {'available': True, 'enhanced': False}
    except ImportError:
        availability['balance_calculator'] = {'available': False, 'enhanced': False}
    
    try:
        from . import content_utils
        availability['content_utils'] = {'available': True, 'enhanced': False}
    except ImportError:
        availability['content_utils'] = {'available': False, 'enhanced': False}
    
    try:
        from . import naming_validator
        availability['naming_validator'] = {'available': True, 'enhanced': False}
    except ImportError:
        availability['naming_validator'] = {'available': False, 'enhanced': False}
    
    try:
        from . import mechanical_parser
        availability['mechanical_parser'] = {'available': True, 'enhanced': False}
    except ImportError:
        availability['mechanical_parser'] = {'available': False, 'enhanced': False}
    
    try:
        from . import rule_checker
        availability['rule_checker'] = {'available': True, 'enhanced': False}
    except ImportError:
        availability['rule_checker'] = {'available': False, 'enhanced': False}
    
    # Enhanced Culture System
    try:
        from . import cultures
        culture_integrity = validate_enhanced_culture_module_integrity()
        availability['cultures'] = {
            'available': True,
            'enhanced': True,
            'character_generation_ready': culture_integrity.get('character_generation_ready', False),
            'creative_support_score': culture_integrity.get('creative_support_score', 0.0),
            'enum_integration_complete': culture_integrity.get('enum_integration_complete', False),
            'preset_system_available': culture_integrity.get('preset_system_available', False),
            'enhancement_categories_supported': culture_integrity.get('enhancement_categories_supported', 0)
        }
    except ImportError:
        availability['cultures'] = {
            'available': False,
            'enhanced': False,
            'character_generation_ready': False,
            'creative_support_score': 0.0
        }
    
    # Enhanced Validation System
    try:
        from . import validation
        validation_integrity = validate_enhanced_validation_module_integrity()
        availability['validation'] = {
            'available': True,
            'enhanced': True,
            'validation_approach_compliant': validation_integrity.get('is_valid', False),
            'enhancement_categories_supported': validation_integrity.get('feature_completeness', {}).get('enhancement_category_targeting', False),
            'preset_compatibility_supported': validation_integrity.get('feature_completeness', {}).get('preset_system_integration', False),
            'character_generation_optimized': validation_integrity.get('character_generation_readiness', {}).get('overall_readiness', False)
        }
    except ImportError:
        availability['validation'] = {
            'available': False,
            'enhanced': False,
            'validation_approach_compliant': False
        }
    
    # Enhanced Text Processing System
    try:
        from . import text_processing
        availability['text_processing'] = {
            'available': True,
            'enhanced': True,
            'cultural_awareness': True,
            'character_generation_support': True,
            'gaming_utility_optimization': True
        }
    except ImportError:
        availability['text_processing'] = {
            'available': False,
            'enhanced': False,
            'cultural_awareness': False
        }
    
    # Enhanced Enum System
    try:
        from ..enums import culture_types
        availability['culture_enums'] = {
            'available': True,
            'enhanced': True,
            'enhancement_categories_available': hasattr(culture_types, 'CultureEnhancementCategory'),
            'preset_system_available': hasattr(culture_types, 'CHARACTER_CULTURE_PRESETS'),
            'utility_functions_available': hasattr(culture_types, 'suggest_creative_culture_enhancements')
        }
    except ImportError:
        availability['culture_enums'] = {
            'available': False,
            'enhanced': False
        }
    
    return availability


# ============================================================================
# ENHANCED CREATIVE CULTURE UTILITIES
# ============================================================================

def get_enhanced_creative_culture_utilities() -> Dict[str, str]:
    """
    Get enhanced creative culture utilities with detailed descriptions.
    
    Returns:
        Dictionary mapping enhanced culture utility names to their descriptions
    """
    return {
        'culture_generate_character_enhanced': 'Complete enhanced workflow for character-focused culture generation with enum integration',
        'culture_create_quick_enhanced': 'Quick enhanced culture creation for immediate character use with preset optimization',
        'culture_parse_response_enhanced': 'Parse LLM responses for character-ready cultures with validation and enhancement',
        'culture_extract_names_enhanced': 'Extract character names from any text with cultural authenticity assessment',
        'culture_assess_readiness_enhanced': 'Assess culture readiness for character creation with enum-based scoring',
        'culture_enhance_for_characters_enhanced': 'Enhance existing cultures for character use with targeted improvements',
        'culture_create_spec_enhanced': 'Create enhanced character-focused culture specifications with preset targeting',
        'culture_validate_spec_enhanced': 'Validate culture specs with constructive enhancement suggestions',
        'culture_build_prompt_enhanced': 'Build enhanced character-focused culture prompts with cultural authenticity',
        'culture_build_enhancement_prompt_enhanced': 'Build enhancement prompts for existing cultures with category targeting',
        'culture_sky_spec_enhanced': 'Create enhanced sky/aerial themed culture specifications',
        'culture_mystical_spec_enhanced': 'Create enhanced mystical/magical culture specifications',
        'culture_nomad_spec_enhanced': 'Create enhanced nomadic/traveling culture specifications',
        'validation_character_culture_enhanced': 'Enhanced character culture validation with enum-based assessment',
        'validation_culture_names_enhanced': 'Enhanced name validation for character generation optimization',
        'validation_enhancement_suggestions_enhanced': 'Get targeted enhancement suggestions with priority assessment',
        'validation_multiple_cultures_enhanced': 'Enhanced comparative analysis of multiple cultures',
        'validation_quick_assessment': 'Quick culture assessment with character generation focus',
        'text_analyze_content_enhanced': 'Enhanced text analysis with cultural awareness and authenticity assessment',
        'text_cultural_references_enhanced': 'Extract cultural references with authenticity level assessment',
        'enum_suggest_enhancements': 'Get enum-based enhancement suggestions for cultures',
        'enum_calculate_generation_score': 'Calculate character generation readiness score using enums',
        'enum_get_recommendations': 'Get character generation recommendations based on enum assessment'
    }


def get_enhanced_character_culture_workflow() -> Dict[str, str]:
    """
    Get enhanced workflow for character culture generation with enum integration.
    
    Returns:
        Dictionary with step-by-step enhanced character culture workflow
    """
    return {
        "step_1": "Create enhanced culture spec with create_character_culture_spec_enhanced()",
        "step_2": "Generate culture with generate_character_culture_enhanced()",
        "step_3": "Parse LLM response with parse_for_characters_enhanced()",
        "step_4": "Assess readiness with assess_character_readiness_enhanced()",
        "step_5": "Validate with validate_character_culture_enhanced()",
        "step_6": "Enhance with enhance_culture_for_characters_enhanced()",
        "quick_option": "Use create_quick_character_culture_enhanced() for immediate results",
        "validation": "Use validate_enhanced_culture_module_integrity() to check system health",
        "enhancement_suggestions": "Use get_culture_enhancement_suggestions_enhanced() for improvements",
        "preset_optimization": "Use CHARACTER_CULTURE_PRESETS for preset-specific optimization",
        "enum_insights": "Use enum utility functions for deeper cultural analysis"
    }


def create_character_culture_quick_enhanced(cultural_concept: str, 
                                          target_preset: Optional[str] = None,
                                          focus_areas: Optional[List[CultureEnhancementCategory]] = None) -> 'EnhancedCreativeCulture':
    """
    Enhanced quick access function for creating character-ready cultures.
    
    Convenience wrapper around the enhanced culture generation system with
    complete enum integration and preset optimization.
    
    Args:
        cultural_concept: Any description of desired culture
        target_preset: Optional preset to optimize for
        focus_areas: Optional enhancement categories to focus on
        
    Returns:
        EnhancedCreativeCulture ready for character generation
        
    Example:
        >>> culture = create_character_culture_quick_enhanced(
        ...     "Storm-riding sky pirates",
        ...     target_preset="gaming_optimized",
        ...     focus_areas=[CultureEnhancementCategory.CHARACTER_NAMES, CultureEnhancementCategory.GAMING_UTILITY]
        ... )
        >>> print(f"Character support: {culture.character_support_score:.2f}")
        >>> print(f"Enhancement categories: {culture.identified_enhancement_categories}")
    """
    return create_quick_character_culture_enhanced(cultural_concept, target_preset, focus_areas)


def parse_culture_response_quick_enhanced(llm_response: str,
                                        target_preset: Optional[str] = None) -> 'EnhancedCreativeParsingResult':
    """
    Enhanced quick access function for parsing culture responses.
    
    Convenience wrapper around the enhanced creative parsing system with
    complete validation and enhancement suggestions.
    
    Args:
        llm_response: Raw LLM response to parse
        target_preset: Optional preset to optimize for
        
    Returns:
        EnhancedCreativeParsingResult with character-focused data and enhancements
        
    Example:
        >>> result = parse_culture_response_quick_enhanced(response, "gaming_optimized")
        >>> print(f"Character ready: {result.character_support_score > 0.3}")
        >>> print(f"Enhancement categories: {result.identified_enhancement_categories}")
        >>> print(f"Preset compatibility: {result.preset_compatibility_score}")
    """
    return parse_for_characters_enhanced(llm_response, target_preset)


def validate_culture_quick_enhanced(culture_data: Dict[str, Any],
                                  target_preset: Optional[str] = None) -> Dict[str, Any]:
    """
    Enhanced quick culture validation with comprehensive assessment.
    
    Args:
        culture_data: Culture data to validate
        target_preset: Optional preset to optimize for
        
    Returns:
        Dictionary with enhanced validation results and suggestions
    """
    validation_result = validate_culture_for_characters(culture_data, target_preset)
    
    return {
        'is_usable': validation_result.is_usable,
        'character_generation_readiness': validation_result.get_character_generation_readiness_percentage(),
        'creative_quality': validation_result.creative_quality_score,
        'gaming_usability': validation_result.gaming_usability_score,
        'character_support': validation_result.character_support_score,
        'name_generation': validation_result.name_generation_score,
        'calculated_generation_score': validation_result.calculated_generation_score,
        'enhancement_categories_needed': [cat.value for cat in validation_result.identified_enhancement_categories],
        'critical_enhancements': validation_result.get_critical_enhancements(),
        'top_suggestions': [sugg.message for sugg in validation_result.suggestions[:3]],
        'preset_compatible': validation_result.is_preset_compatible(target_preset) if target_preset else True,
        'enum_based_recommendations': validation_result.enum_based_recommendations,
        'validation_compliant': validation_result.creative_validation_approach_compliant
    }


# ============================================================================
# ENHANCED CREATIVE CULTURE MODULE INFORMATION
# ============================================================================

ENHANCED_CREATIVE_CULTURE_INFO = {
    "version": "3.0.0",
    "description": "Enhanced Creative Culture Generation for Character Creation with Complete Enum Integration",
    "philosophy": "Enable creativity rather than restrict it with intelligent enum-based enhancement targeting",
    "focus": "Character generation support and enhancement with preset compatibility",
    "validation_style": "Constructive suggestions with enum-based recommendations over rigid requirements",
    "usability_threshold": "Almost all cultures are usable for character generation",
    "enhanced_features": [
        "Complete enum integration with CultureEnhancementCategory targeting",
        "Preset compatibility system with CHARACTER_CULTURE_PRESETS",
        "Enhancement priority assessment with CultureEnhancementPriority",
        "Cultural authenticity evaluation with CultureAuthenticityLevel",
        "Character generation scoring with calculate_character_generation_score",
        "Text processing with cultural awareness and gaming utility optimization",
        "Constructive validation with enhancement suggestions rather than errors",
        "Always produces usable cultures with creative fallback systems"
    ],
    "key_benefits": [
        "Always produces usable cultures for character creation",
        "Enhanced creative fallback systems prevent complete failures",
        "Enum-based enhancement suggestions instead of error messages",
        "Gaming utility optimization for table use with preset targeting",
        "Flexible name extraction with cultural authenticity assessment",
        "Character background hooks for player inspiration with enhancement categories",
        "Preset compatibility analysis for different play styles",
        "Text processing with cultural awareness and authenticity evaluation"
    ],
    "quick_start": {
        "create_culture": "create_character_culture_quick_enhanced('your concept here', 'gaming_optimized')",
        "parse_response": "parse_culture_response_quick_enhanced('llm response here', 'creative_focused')",
        "validate_culture": "validate_culture_quick_enhanced(culture_data, 'character_rich')",
        "get_workflow": "get_enhanced_character_culture_workflow()",
        "check_utilities": "get_enhanced_creative_culture_utilities()",
        "check_presets": "list(CHARACTER_CULTURE_PRESETS.keys())",
        "get_enhancements": "suggest_creative_culture_enhancements(culture_data)"
    },
    "enum_integration_features": [
        "CultureEnhancementCategory for targeted improvements",
        "CultureEnhancementPriority for suggestion ordering",
        "CultureAuthenticityLevel for cultural assessment",
        "CultureComplexityLevel for character generation optimization",
        "CHARACTER_CULTURE_PRESETS for preset compatibility",
        "Enhancement utility functions for deep cultural analysis"
    ]
}


def get_enhanced_creative_culture_info() -> Dict[str, Any]:
    """
    Get comprehensive information about the enhanced creative culture generation system.
    
    Returns:
        Dictionary with enhanced system information and usage guidelines
    """
    return ENHANCED_CREATIVE_CULTURE_INFO


def validate_all_utilities_enhanced() -> Dict[str, Any]:
    """
    Comprehensive enhanced validation of all utility systems.
    
    Returns:
        Dictionary with complete enhanced utility system health check
    """
    availability = validate_utility_availability_enhanced()
    
    # Enhanced culture system assessment
    culture_system = availability.get('cultures', {})
    validation_system = availability.get('validation', {})
    text_processing_system = availability.get('text_processing', {})
    enum_system = availability.get('culture_enums', {})
    
    # Calculate overall system health
    systems_available = sum(1 for system in availability.values() if system.get('available', False))
    enhanced_systems = sum(1 for system in availability.values() if system.get('enhanced', False))
    total_systems = len(availability)
    
    system_health = systems_available / total_systems
    enhancement_level = enhanced_systems / total_systems if enhanced_systems > 0 else 0
    
    # Character generation readiness assessment
    character_generation_ready = (
        culture_system.get('character_generation_ready', False) and
        validation_system.get('character_generation_optimized', False) and
        text_processing_system.get('character_generation_support', False) and
        enum_system.get('enhancement_categories_available', False)
    )
    
    return {
        'system_availability': availability,
        'enhanced_utility_registry_size': len(ENHANCED_UTILITY_REGISTRY),
        'culture_utilities_count': len([k for k in ENHANCED_UTILITY_REGISTRY.keys() if k.startswith('culture_')]),
        'validation_utilities_count': len([k for k in ENHANCED_UTILITY_REGISTRY.keys() if k.startswith('validation_')]),
        'text_processing_utilities_count': len([k for k in ENHANCED_UTILITY_REGISTRY.keys() if k.startswith('text_')]),
        'enum_utilities_count': len([k for k in ENHANCED_UTILITY_REGISTRY.keys() if k.startswith('enum_')]),
        'system_health_score': system_health,
        'enhancement_level_score': enhancement_level,
        'character_generation_ready': character_generation_ready,
        'enhanced_creative_culture_info': ENHANCED_CREATIVE_CULTURE_INFO,
        'recommendations': {
            'enhanced_character_culture_workflow': get_enhanced_character_culture_workflow(),
            'enhanced_creative_utilities': get_enhanced_creative_culture_utilities(),
            'available_presets': list(CHARACTER_CULTURE_PRESETS.keys()) if CHARACTER_CULTURE_PRESETS else [],
            'enhancement_categories': [cat.value for cat in CultureEnhancementCategory] if CultureEnhancementCategory else []
        },
        'integration_status': {
            'enum_integration_complete': enum_system.get('enhanced', False),
            'preset_system_available': enum_system.get('preset_system_available', False),
            'enhancement_categories_operational': enum_system.get('enhancement_categories_available', False),
            'cultural_authenticity_assessment_available': culture_system.get('enhanced', False),
            'text_cultural_awareness_available': text_processing_system.get('cultural_awareness', False)
        }
    }


# ============================================================================
# ENHANCED MODULE INITIALIZATION
# ============================================================================

def _initialize_enhanced_utility_systems():
    """Initialize and validate all enhanced utility systems."""
    try:
        validation_results = validate_all_utilities_enhanced()
        
        # Check if enhanced systems are ready for character generation
        character_ready = validation_results.get('character_generation_ready', False)
        enhancement_level = validation_results.get('enhancement_level_score', 0.0)
        
        if not character_ready:
            import warnings
            warnings.warn(
                "Enhanced creative culture system has optimization opportunities. "
                "Use validate_all_utilities_enhanced() for details.",
                ImportWarning
            )
        
        if enhancement_level < 0.8:
            import warnings
            warnings.warn(
                f"System enhancement level at {enhancement_level:.1%}. "
                "Some enhanced features may not be available.",
                ImportWarning
            )
        
        return validation_results
    except Exception as e:
        import warnings
        warnings.warn(f"Enhanced utility system initialization encountered issues: {e}", ImportWarning)
        return {'initialization_error': str(e)}


# Legacy function mappings for backward compatibility
get_utility_function = get_utility_function_enhanced
list_available_utilities = list_available_utilities_enhanced
get_utilities_by_category = get_utilities_by_category_enhanced
validate_utility_availability = validate_utility_availability_enhanced
get_creative_culture_utilities = get_enhanced_creative_culture_utilities
get_character_culture_workflow = get_enhanced_character_culture_workflow
create_character_culture_quick = create_character_culture_quick_enhanced
parse_culture_response_quick = parse_culture_response_quick_enhanced
get_creative_culture_info = get_enhanced_creative_culture_info
validate_all_utilities = validate_all_utilities_enhanced

# Initialize enhanced systems on import
_enhanced_system_validation = _initialize_enhanced_utility_systems()

# ============================================================================
# ENHANCED MODULE METADATA
# ============================================================================

__version__ = "3.0.0"
__author__ = "D&D Character Creator Team"
__description__ = "Enhanced Core Utilities with Complete Culture System Integration"

# Enhanced Clean Architecture compliance
ENHANCED_CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/utils",
    "description": "Enhanced stateless utilities with complete culture system integration",
    "dependencies": {
        "internal": [
            "core.enums.culture_types",
            "core.abstractions.culture_llm_providers"
        ],
        "external": ["typing", "dataclasses", "enum", "re", "collections", "datetime"]
    },
    "principles": {
        "infrastructure_independent": True,
        "pure_functions": True,
        "immutable_data": True,
        "stateless_operations": True,
        "enhanced_culture_integration": True,
        "character_generation_optimized": True,
        "creative_validation_compliant": True,
        "enum_based_enhancement": True,
        "preset_system_compatible": True
    },
    "enhanced_features": {
        "complete_enum_integration": True,
        "preset_compatibility_system": True,
        "enhancement_category_targeting": True,
        "cultural_authenticity_assessment": True,
        "text_cultural_awareness": True,
        "character_generation_optimization": True,
        "gaming_utility_focus": True,
        "constructive_validation_approach": True
    }
}

# ============================================================================
# ENHANCED MODULE MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("D&D Character Creator - Enhanced Core Utilities")
    print("Complete Culture System with Enum Integration")
    print("=" * 80)
    
    validation = validate_all_utilities_enhanced()
    print(f"Total Enhanced Utilities Available: {validation['enhanced_utility_registry_size']}")
    print(f"Culture Utilities Available: {validation['culture_utilities_count']}")
    print(f"Validation Utilities Available: {validation['validation_utilities_count']}")
    print(f"Text Processing Utilities Available: {validation['text_processing_utilities_count']}")
    print(f"Enum Utilities Available: {validation['enum_utilities_count']}")
    
    character_ready = validation.get('character_generation_ready', False)
    system_health = validation.get('system_health_score', 0.0) 
    enhancement_level = validation.get('enhancement_level_score', 0.0)
    
    print(f"\nSystem Health Score: {system_health:.1%}")
    print(f"Enhancement Level: {enhancement_level:.1%}")
    print(f"Character Generation Ready: {character_ready}")
    
    print("\nAvailable Enhanced Utility Categories:")
    categories = list_available_utilities_enhanced()
    for category, utilities in categories.items():
        print(f"  {category.title()}: {len(utilities)} utilities")
    
    print("\nIntegration Status:")
    integration = validation.get('integration_status', {})
    for feature, status in integration.items():
        print(f"  {feature.replace('_', ' ').title()}: {'✓' if status else '✗'}")
    
    print("\nQuick Start for Enhanced Character Cultures:")
    quick_start = ENHANCED_CREATIVE_CULTURE_INFO['quick_start']
    for action, code in quick_start.items():
        print(f"  {action.replace('_', ' ').title()}: {code}")
    
    if validation.get('recommendations', {}).get('available_presets'):
        print(f"\nAvailable Presets: {', '.join(validation['recommendations']['available_presets'])}")
    
    print("\n🎨 Enhanced Creative Culture Generation Ready!")
    print("🎲 Complete enum integration with preset compatibility!")
    print("🔍 Cultural authenticity assessment with enhancement targeting!")
    print("=" * 80)