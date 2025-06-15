"""
Core Validation Utilities - Enhanced Creative Quality Assurance for Character Generation.

COMPLETELY REFACTORED: Full integration with enhanced culture_validator.py 
and complete culture_types enum system following CREATIVE_VALIDATION_APPROACH philosophy.

This module provides enhanced validation utilities focused on enabling creative freedom
and supporting character generation with complete enum integration. Follows Clean 
Architecture principles with pure functional validation and constructive enhancement suggestions.

Enhanced Creative Validation Philosophy:
- Enable and enhance creative character generation with enum-based optimization
- Provide supportive assessment with enum-based enhancement suggestions
- Focus on gaming usability and character background support with preset compatibility
- Maintain creative freedom while offering targeted quality improvements
- Almost all content is usable - validation suggests enum-based enhancements

Enhanced Features:
- Complete integration with enhanced culture_types enums
- Enhancement category targeting and priority assessment
- Gaming utility optimization throughout validation
- Preset-based validation support with CHARACTER_CULTURE_PRESETS
- Constructive validation with enum-based enhancement suggestions
- Creative freedom enablement with character generation focus
- Character readiness assessment with enum scoring

Usage:
    >>> from core.utils.validation import (
    ...     EnhancedCreativeCultureValidator, validate_culture_for_characters,
    ...     quick_culture_assessment, CultureEnhancementCategory
    ... )
    >>> 
    >>> # Enhanced validation for character creation
    >>> result = validate_culture_for_characters(
    ...     culture_data,
    ...     target_preset="gaming_optimized",
    ...     focus_areas=[CultureEnhancementCategory.CHARACTER_NAMES, CultureEnhancementCategory.GAMING_UTILITY]
    ... )
    >>> print(f"Character support: {result.character_support_score:.2f}")
    >>> print(f"Generation score: {result.calculated_generation_score:.2f}")
    >>> 
    >>> # Quick assessment with enum insights
    >>> assessment = quick_culture_assessment(culture_data)
    >>> print(f"Enhancement categories needed: {assessment['enhancement_categories_needed']}")
"""

from typing import Dict, List, Optional, Any

# ============================================================================
# ENHANCED CORE IMPORTS - Main Validation Classes and Functions
# ============================================================================

# Enhanced Creative Culture Validation with complete enum integration
from .culture_validator import (
    # Enhanced main validation class
    EnhancedCreativeCultureValidator,
    
    # Enhanced data structures
    EnhancedCreativeValidationResult,
    EnhancedCreativeValidationIssue,
    
    # Enhanced enums
    EnhancedValidationIssueType,
    EnhancedCreativeValidationFocus,
    
    # Enhanced utility functions
    validate_culture_for_characters,
    quick_culture_assessment,
    
    # Module metadata
    __version__ as validator_version
)

# Legacy support - map old imports to new enhanced versions
CreativeCultureValidator = EnhancedCreativeCultureValidator
CreativeValidationResult = EnhancedCreativeValidationResult
CreativeValidationIssue = EnhancedCreativeValidationIssue
ValidationIssueType = EnhancedValidationIssueType
CreativeValidationFocus = EnhancedCreativeValidationFocus

# ============================================================================
# ENHANCED ENUMS AND TYPES - Complete enum integration
# ============================================================================

from ...enums.culture_types import (
    # Core validation enums (enhanced)
    CultureValidationCategory,
    CultureValidationSeverity,
    
    # Core culture generation enums
    CultureGenerationType,
    CultureAuthenticityLevel,
    CultureCreativityLevel,
    CultureSourceType,
    CultureComplexityLevel,
    
    # Enhancement and status enums (NEW)
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
    
    # Preset configurations and compliance (NEW)
    CHARACTER_CULTURE_PRESETS,
    CREATIVE_VALIDATION_APPROACH_COMPLIANCE as ENUM_COMPLIANCE
)

# ============================================================================
# EXCEPTIONS - Re-export for convenience
# ============================================================================

from ...exceptions.culture import (
    CultureValidationError,
    CultureStructureError
)

# ============================================================================
# ENHANCED MODULE METADATA
# ============================================================================

__version__ = "3.0.0"  # Updated for enhanced enum integration
__author__ = "D&D Character Creator Team"
__description__ = "Enhanced Creative Validation Utilities for Character Generation with Complete Enum Integration"

# Enhanced Clean Architecture compliance
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/utils/validation",
    "description": "Enhanced creative quality assurance utilities with complete enum integration",
    "dependencies": {
        "internal": [
            "core.enums.culture_types",
            "core.exceptions.culture"
        ],
        "external": ["typing", "dataclasses", "enum", "re", "collections", "datetime"]
    },
    "dependents": [
        "domain.services.culture_service",
        "application.use_cases.culture_use_cases",
        "core.utils.cultures",
        "application.services.culture_orchestrator"
    ],
    "principles": {
        "infrastructure_independent": True,
        "pure_functions": True,
        "immutable_data": True,
        "no_side_effects": True,
        "stateless_operations": True,
        "creative_focused": True,
        "character_generation_optimized": True,
        "supportive_validation": True,
        "enum_integration_complete": True,  # NEW
        "preset_system_compatible": True,   # NEW
        "enhancement_category_aware": True  # NEW
    },
    "enhanced_features": {
        "enum_based_scoring": True,
        "preset_compatibility": True,
        "enhancement_prioritization": True,
        "character_generation_optimization": True,
        "gaming_utility_focus": True
    }
}

# Enhanced Creative Validation Approach with enum integration
CREATIVE_VALIDATION_APPROACH = {
    "philosophy": "Enable creativity rather than restrict it with enum-based enhancement targeting",
    "focus": "Character generation support and enhancement with complete enum integration",
    "validation_style": "Constructive suggestions with enum-based recommendations over rigid requirements",
    "usability_threshold": "Almost all cultures are usable for character generation",
    "enhancement_focus": [
        "Character background richness with enum targeting",
        "Gaming table usability with preset optimization",
        "Name generation quality with enum-based assessment",
        "Creative inspiration potential with enhancement categories",
        "Player experience optimization with priority-based suggestions",
        "Enum-based character generation scoring",  # NEW
        "Preset compatibility analysis",            # NEW
        "Enhancement category prioritization"       # NEW
    ],
    "quality_dimensions": {
        "creative_quality_score": "How well culture inspires character creation with enum assessment",
        "gaming_usability_score": "How practical culture is for table use with preset compatibility", 
        "character_support_score": "How well culture supports character backgrounds with enum categories",
        "name_generation_score": "Quality of names for character creation with enum optimization",
        "calculated_generation_score": "Enum-based character generation readiness score",  # NEW
        "enum_compatibility_score": "Culture compatibility with enum enhancement system"   # NEW
    },
    "enum_integration_features": [
        "Complete CultureEnhancementCategory targeting",
        "CultureEnhancementPriority assessment and recommendations",
        "CHARACTER_CULTURE_PRESETS compatibility analysis",
        "Enum-based character generation scoring",
        "Enhancement category identification and prioritization",
        "Preset-specific optimization suggestions"
    ]
}

# NEW: Creative Validation Philosophy with enum focus
CREATIVE_VALIDATION_PHILOSOPHY = {
    "core_principle": "Enhance creativity through intelligent enum-based suggestions",
    "approach": "constructive_enhancement_with_enum_targeting",
    "validation_goals": [
        "Enable rich character generation with enum optimization",
        "Provide actionable enhancement suggestions using categories",
        "Preserve creative freedom while offering targeted improvements",
        "Support diverse play styles through preset compatibility",
        "Optimize for gaming table usability with enum insights"
    ],
    "enum_enhancement_strategy": {
        "category_targeting": "Identify specific CultureEnhancementCategory opportunities",
        "priority_assessment": "Use CultureEnhancementPriority for suggestion ordering",
        "preset_optimization": "Leverage CHARACTER_CULTURE_PRESETS for compatibility",
        "character_focus": "Prioritize character generation readiness above all else"
    }
}

# ============================================================================
# ENHANCED CONVENIENCE VALIDATION FUNCTIONS
# ============================================================================

def validate_character_culture_enhanced(
    culture_data: Dict[str, Any],
    target_preset: Optional[str] = None,
    focus_areas: Optional[List[CultureEnhancementCategory]] = None
) -> EnhancedCreativeValidationResult:
    """
    Enhanced comprehensive culture validation for character generation.
    
    UPDATED: Convenience function with complete enum integration and preset support.
    
    Args:
        culture_data: Dictionary containing culture information
        target_preset: Optional preset name for compatibility assessment
        focus_areas: Optional list of specific enhancement categories to focus on
        
    Returns:
        EnhancedCreativeValidationResult with comprehensive enum-based assessment
        
    Example:
        >>> # Validate with preset targeting and enhancement focus
        >>> result = validate_character_culture_enhanced(
        ...     culture_data,
        ...     target_preset="gaming_optimized",
        ...     focus_areas=[CultureEnhancementCategory.CHARACTER_NAMES, CultureEnhancementCategory.GAMING_UTILITY]
        ... )
        >>> print(f"Character ready: {result.character_support_score >= 0.7}")
        >>> print(f"Critical enhancements: {result.get_critical_enhancements()}")
    """
    return EnhancedCreativeCultureValidator.validate_for_character_generation_enhanced(
        culture_data, target_preset, focus_areas
    )


def validate_culture_names_for_characters_enhanced(
    names_dict: Dict[str, List[str]],
    character_archetypes: Optional[List[str]] = None,
    gaming_focus: bool = True
) -> Dict[str, Any]:
    """
    Enhanced validation of name collections for character generation.
    
    UPDATED: Focused validation with enum-based name assessment and gaming optimization.
    
    Args:
        names_dict: Dictionary of name categories and name lists
        character_archetypes: Optional list of character archetypes to consider
        gaming_focus: Whether to prioritize gaming table usability
        
    Returns:
        Dictionary with enhanced name validation results including enum insights
        
    Example:
        >>> names = {
        ...     'male_names': ['Thorin', 'Balin', 'Dwalin'],
        ...     'female_names': ['Disa', 'Nala', 'Vera'],
        ...     'family_names': ['Ironforge', 'Stonebeard', 'Goldaxe']
        ... }
        >>> result = validate_culture_names_for_characters_enhanced(names, gaming_focus=True)
        >>> print(f"Gaming optimization: {result['gaming_table_usability']:.2f}")
    """
    # Create temporary culture data focused on names
    culture_data = names_dict.copy()
    culture_data['name'] = 'Enhanced Name Validation Culture'
    
    # Focus areas based on parameters
    focus_areas = [CultureEnhancementCategory.CHARACTER_NAMES]
    if gaming_focus:
        focus_areas.extend([
            CultureEnhancementCategory.GAMING_UTILITY,
            CultureEnhancementCategory.PRONUNCIATION
        ])
    
    # Assess enhanced name generation quality
    result = EnhancedCreativeCultureValidator.assess_name_generation_quality_enhanced(
        culture_data, focus_areas
    )
    
    return {
        'name_quality_score': result.name_generation_score,
        'character_fit_score': result.character_support_score,
        'gaming_usability_score': result.gaming_usability_score,
        'gaming_table_usability': result.name_analysis.get('gaming_table_usability', 0.5),
        'enum_compatibility_score': result.name_analysis.get('enum_compatibility_score', 0.5),
        'total_names': len([name for names in names_dict.values() for name in names if name]),
        'categories_available': list(names_dict.keys()),
        'enhancement_categories_needed': [cat.value for cat in result.identified_enhancement_categories],
        'prioritized_suggestions': [(sugg, priority.value) for sugg, priority in result.prioritized_enhancements],
        'enum_based_recommendations': result.enum_based_recommendations,
        'character_archetype_support': result.name_analysis.get('character_fit_potential', 0.5),
        'character_generation_readiness_percentage': result.get_character_generation_readiness_percentage()
    }


def get_culture_enhancement_suggestions_enhanced(
    culture_data: Dict[str, Any],
    target_score: float = 0.8,
    preset_focus: Optional[str] = None
) -> Dict[str, Any]:
    """
    Enhanced culture enhancement suggestions with enum targeting.
    
    UPDATED: Provides actionable enum-based suggestions to improve culture quality.
    
    Args:
        culture_data: Dictionary containing culture information
        target_score: Target quality score to achieve (0.0 to 1.0)
        preset_focus: Optional preset to optimize for
        
    Returns:
        Dictionary with enhanced suggestions and enum-based priorities
        
    Example:
        >>> suggestions = get_culture_enhancement_suggestions_enhanced(
        ...     culture_data, 
        ...     target_score=0.8,
        ...     preset_focus="gaming_optimized"
        ... )
        >>> print("Critical enhancements:")
        >>> for enhancement in suggestions['critical_enhancements']:
        ...     print(f"  • {enhancement}")
    """
    result = validate_culture_for_characters(culture_data, preset_focus)
    
    # Enhanced categorization with enum priorities
    critical_enhancements = result.get_critical_enhancements()
    priority_categories = result.get_top_enhancement_categories(limit=5)
    
    # Categorize suggestions by enhancement category and priority
    category_suggestions = {}
    for suggestion in result.suggestions:
        for category in suggestion.target_enhancement_categories:
            if category not in category_suggestions:
                category_suggestions[category] = []
            category_suggestions[category].append({
                'message': suggestion.message,
                'priority': suggestion.enhancement_priority.value,
                'character_impact': suggestion.character_impact,
                'enum_recommendations': suggestion.enum_based_recommendations
            })
    
    return {
        'current_scores': {
            'creative_quality': result.creative_quality_score,
            'gaming_usability': result.gaming_usability_score,
            'character_support': result.character_support_score,
            'name_generation': result.name_generation_score,
            'calculated_generation_score': result.calculated_generation_score
        },
        'enum_scoring_breakdown': result.enum_scoring_breakdown,
        'target_score': target_score,
        'needs_enhancement': max(
            result.creative_quality_score,
            result.gaming_usability_score, 
            result.character_support_score,
            result.name_generation_score
        ) < target_score,
        'critical_enhancements': critical_enhancements,
        'priority_enhancement_categories': [cat.value for cat in priority_categories],
        'category_specific_suggestions': {
            cat.value: suggestions for cat, suggestions in category_suggestions.items()
        },
        'enum_based_recommendations': result.enum_based_recommendations,
        'preset_compatibility': {
            'target_preset': preset_focus,
            'compatible': result.is_preset_compatible(preset_focus) if preset_focus else True,
            'preset_suggestions': result.preset_compatibility_analysis.get('preset_optimization_suggestions', [])
        },
        'character_generation_readiness': result.character_generation_readiness,
        'enhancement_opportunities': [opp.message for opp in result.creative_opportunities]
    }


def validate_multiple_cultures_enhanced(
    cultures_dict: Dict[str, Dict[str, Any]],
    comparison_preset: Optional[str] = None
) -> Dict[str, Any]:
    """
    Enhanced validation of multiple cultures with enum-based comparative analysis.
    
    UPDATED: Comparative analysis with enum insights and preset compatibility.
    
    Args:
        cultures_dict: Dictionary mapping culture names to culture data
        comparison_preset: Optional preset for standardized comparison
        
    Returns:
        Dictionary with enhanced comparative validation results
        
    Example:
        >>> cultures = {
        ...     'mountain_dwarves': dwarf_culture_data,
        ...     'forest_elves': elf_culture_data,
        ...     'desert_nomads': nomad_culture_data
        ... }
        >>> comparison = validate_multiple_cultures_enhanced(cultures, "gaming_optimized")
        >>> print(f"Best for preset: {comparison['best_for_preset']}")
    """
    results = {}
    scores = {}
    enum_insights = {}
    
    # Validate each culture with enhanced assessment
    for culture_name, culture_data in cultures_dict.items():
        try:
            result = validate_culture_for_characters(culture_data, comparison_preset)
            results[culture_name] = result
            scores[culture_name] = {
                'creative_quality': result.creative_quality_score,
                'gaming_usability': result.gaming_usability_score,
                'character_support': result.character_support_score,
                'name_generation': result.name_generation_score,
                'calculated_generation_score': result.calculated_generation_score or 0.5,
                'overall': (result.creative_quality_score + result.gaming_usability_score + 
                           result.character_support_score + result.name_generation_score) / 4,
                'character_readiness_percentage': result.get_character_generation_readiness_percentage()
            }
            enum_insights[culture_name] = {
                'top_enhancement_categories': [cat.value for cat in result.get_top_enhancement_categories()],
                'critical_enhancements_count': len(result.get_critical_enhancements()),
                'preset_compatible': result.is_preset_compatible(comparison_preset) if comparison_preset else True,
                'enum_scoring_breakdown': result.enum_scoring_breakdown
            }
        except Exception as e:
            results[culture_name] = None
            scores[culture_name] = {'error': str(e)}
            enum_insights[culture_name] = {'error': str(e)}
    
    # Enhanced analysis with enum insights
    valid_scores = {name: score for name, score in scores.items() if 'error' not in score}
    
    best_overall = max(valid_scores.items(), key=lambda x: x[1]['overall'])[0] if valid_scores else None
    best_for_characters = max(valid_scores.items(), key=lambda x: x[1]['character_support'])[0] if valid_scores else None
    best_for_gaming = max(valid_scores.items(), key=lambda x: x[1]['gaming_usability'])[0] if valid_scores else None
    best_generation_score = max(valid_scores.items(), key=lambda x: x[1]['calculated_generation_score'])[0] if valid_scores else None
    best_for_preset = max(
        ((name, score) for name, score in valid_scores.items() 
         if enum_insights[name].get('preset_compatible', True)),
        key=lambda x: x[1]['overall'],
        default=(None, None)
    )[0] if comparison_preset else None
    
    return {
        'total_cultures': len(cultures_dict),
        'successfully_validated': len(valid_scores),
        'validation_results': results,
        'comparative_scores': scores,
        'enum_insights': enum_insights,
        'recommendations': {
            'best_overall': best_overall,
            'best_for_characters': best_for_characters, 
            'best_for_gaming': best_for_gaming,
            'best_generation_score': best_generation_score,
            'best_for_preset': best_for_preset
        },
        'average_scores': {
            'creative_quality': sum(s['creative_quality'] for s in valid_scores.values()) / len(valid_scores) if valid_scores else 0,
            'gaming_usability': sum(s['gaming_usability'] for s in valid_scores.values()) / len(valid_scores) if valid_scores else 0,
            'character_support': sum(s['character_support'] for s in valid_scores.values()) / len(valid_scores) if valid_scores else 0,
            'name_generation': sum(s['name_generation'] for s in valid_scores.values()) / len(valid_scores) if valid_scores else 0,
            'calculated_generation_score': sum(s['calculated_generation_score'] for s in valid_scores.values()) / len(valid_scores) if valid_scores else 0,
            'character_readiness_percentage': sum(s['character_readiness_percentage'] for s in valid_scores.values()) / len(valid_scores) if valid_scores else 0
        },
        'preset_analysis': {
            'target_preset': comparison_preset,
            'preset_compatible_count': sum(1 for insight in enum_insights.values() 
                                         if insight.get('preset_compatible', True) and 'error' not in insight),
            'average_compatibility': sum(1 for insight in enum_insights.values() 
                                       if insight.get('preset_compatible', True) and 'error' not in insight) / len(valid_scores) if valid_scores else 0
        }
    }


# ============================================================================
# ENHANCED CREATIVE VALIDATION PRESETS
# ============================================================================

def validate_fantasy_culture_enhanced(
    culture_data: Dict[str, Any],
    creativity_focus: bool = True
) -> EnhancedCreativeValidationResult:
    """
    Enhanced validation for fantasy cultures with enum optimization.
    
    UPDATED: Preset validation with CultureSourceType.CREATIVE_MYTHOLOGICAL focus.
    
    Args:
        culture_data: Dictionary containing culture information
        creativity_focus: Whether to prioritize creative enhancement categories
        
    Returns:
        EnhancedCreativeValidationResult optimized for fantasy contexts
    """
    focus_areas = [CultureEnhancementCategory.CREATIVE_ELEMENTS, CultureEnhancementCategory.NARRATIVE_DEPTH]
    if creativity_focus:
        focus_areas.extend([
            CultureEnhancementCategory.CHARACTER_MOTIVATIONS,
            CultureEnhancementCategory.ROLEPLAY_ELEMENTS
        ])
    
    return EnhancedCreativeCultureValidator.validate_for_character_generation_enhanced(
        culture_data, target_preset="creative_focused", enhancement_focus=focus_areas
    )


def validate_historical_inspired_culture_enhanced(
    culture_data: Dict[str, Any],
    authenticity_balance: bool = True
) -> EnhancedCreativeValidationResult:
    """
    Enhanced validation for historically-inspired cultures.
    
    UPDATED: Preset validation with CultureAuthenticityLevel awareness.
    
    Args:
        culture_data: Dictionary containing culture information
        authenticity_balance: Whether to balance authenticity with creative freedom
        
    Returns:
        EnhancedCreativeValidationResult optimized for historical adaptation
    """
    focus_areas = [CultureEnhancementCategory.CULTURAL_TRAITS, CultureEnhancementCategory.BACKGROUND_HOOKS]
    if authenticity_balance:
        focus_areas.extend([
            CultureEnhancementCategory.CHARACTER_NAMES,
            CultureEnhancementCategory.GAMING_UTILITY
        ])
    
    return EnhancedCreativeCultureValidator.validate_for_character_generation_enhanced(
        culture_data, target_preset="character_rich", enhancement_focus=focus_areas
    )


def validate_original_culture_enhanced(
    culture_data: Dict[str, Any],
    gaming_optimization: bool = True
) -> EnhancedCreativeValidationResult:
    """
    Enhanced validation for completely original cultures.
    
    UPDATED: Preset validation with CultureSourceType.CREATIVE_ORIGINAL optimization.
    
    Args:
        culture_data: Dictionary containing culture information
        gaming_optimization: Whether to include gaming utility enhancements
        
    Returns:
        EnhancedCreativeValidationResult optimized for original creative cultures
    """
    focus_areas = [
        CultureEnhancementCategory.CREATIVE_ELEMENTS,
        CultureEnhancementCategory.CHARACTER_NAMES,
        CultureEnhancementCategory.NARRATIVE_DEPTH
    ]
    if gaming_optimization:
        focus_areas.extend([
            CultureEnhancementCategory.GAMING_UTILITY,
            CultureEnhancementCategory.PRONUNCIATION
        ])
    
    return EnhancedCreativeCultureValidator.validate_for_character_generation_enhanced(
        culture_data, target_preset="gaming_optimized", enhancement_focus=focus_areas
    )


def validate_gaming_optimized_culture(
    culture_data: Dict[str, Any]
) -> EnhancedCreativeValidationResult:
    """
    NEW: Enhanced validation specifically for gaming table optimization.
    
    Preset validation focusing on gaming utility and table-friendly features.
    
    Args:
        culture_data: Dictionary containing culture information
        
    Returns:
        EnhancedCreativeValidationResult optimized for gaming table use
    """
    focus_areas = [
        CultureEnhancementCategory.GAMING_UTILITY,
        CultureEnhancementCategory.PRONUNCIATION,
        CultureEnhancementCategory.CHARACTER_NAMES
    ]
    
    return EnhancedCreativeCultureValidator.validate_for_character_generation_enhanced(
        culture_data, target_preset="table_friendly", enhancement_focus=focus_areas
    )


# ============================================================================
# ENHANCED MODULE VALIDATION AND QUALITY ASSURANCE
# ============================================================================

def validate_enhanced_validation_module_integrity() -> Dict[str, Any]:
    """
    Enhanced validation of module integrity with enum integration assessment.
    
    UPDATED: Comprehensive check including enum integration and preset system.
    
    Returns:
        Dictionary with enhanced validation module integrity results
    """
    integrity_result = {
        "is_valid": True,
        "issues": [],
        "warnings": [],
        "compliance_score": 0.0,
        "feature_completeness": {},
        "enum_integration_status": {},
        "clean_architecture_compliance": CLEAN_ARCHITECTURE_COMPLIANCE,
        "creative_validation_approach": CREATIVE_VALIDATION_APPROACH,
        "creative_validation_philosophy": CREATIVE_VALIDATION_PHILOSOPHY
    }
    
    try:
        # Check enhanced core classes
        enhanced_classes = [
            EnhancedCreativeCultureValidator,
            EnhancedCreativeValidationResult,
            EnhancedCreativeValidationIssue
        ]
        
        for cls in enhanced_classes:
            if not hasattr(cls, '__name__'):
                integrity_result["issues"].append(f"Enhanced core class {cls} not properly defined")
        
        # Check enhanced utility functions
        enhanced_functions = [
            validate_culture_for_characters,
            quick_culture_assessment,
            validate_character_culture_enhanced,
            get_culture_enhancement_suggestions_enhanced,
            validate_multiple_cultures_enhanced
        ]
        
        for func in enhanced_functions:
            if not callable(func):
                integrity_result["issues"].append(f"Enhanced utility function {func.__name__} not callable")
        
        # Check enum integration
        required_enums = [
            CultureValidationCategory,
            CultureValidationSeverity,
            CultureEnhancementCategory,
            CultureEnhancementPriority,
            CultureGenerationStatus,
            CultureAuthenticityLevel,
            CultureComplexityLevel,
            CultureCreativityLevel
        ]
        
        enum_integration_status = {}
        for enum_class in required_enums:
            if hasattr(enum_class, '__members__'):
                enum_integration_status[enum_class.__name__] = {
                    'available': True,
                    'member_count': len(enum_class.__members__)
                }
            else:
                integrity_result["issues"].append(f"Enhanced enum {enum_class.__name__} not properly defined")
                enum_integration_status[enum_class.__name__] = {'available': False}
        
        integrity_result["enum_integration_status"] = enum_integration_status
        
        # Check enum utility functions
        enum_utilities = [
            suggest_creative_culture_enhancements,
            calculate_character_generation_score,
            get_character_generation_recommendations
        ]
        
        for util_func in enum_utilities:
            if not callable(util_func):
                integrity_result["issues"].append(f"Enum utility function {util_func.__name__} not callable")
        
        # Check preset system integration
        if CHARACTER_CULTURE_PRESETS:
            integrity_result["preset_system_available"] = True
            integrity_result["available_presets"] = list(CHARACTER_CULTURE_PRESETS.keys())
        else:
            integrity_result["warnings"].append("CHARACTER_CULTURE_PRESETS not available")
            integrity_result["preset_system_available"] = False
        
        # Calculate enhanced compliance score
        total_checks = (len(enhanced_classes) + len(enhanced_functions) + 
                       len(required_enums) + len(enum_utilities) + 1)  # +1 for preset system
        passed_checks = total_checks - len(integrity_result["issues"])
        integrity_result["compliance_score"] = passed_checks / total_checks
        
        # Enhanced feature completeness
        integrity_result["feature_completeness"] = {
            "enhanced_creative_culture_validation": True,
            "character_generation_support": True,
            "gaming_usability_assessment": True,
            "name_quality_validation": True,
            "enhancement_suggestions": True,
            "comparative_validation": True,
            "creative_freedom_preservation": True,
            "enum_integration_complete": len([s for s in enum_integration_status.values() if s.get('available')]) == len(required_enums),
            "preset_system_integration": integrity_result["preset_system_available"],
            "enhancement_category_targeting": True,
            "priority_based_suggestions": True,
            "character_generation_scoring": True
        }
        
        # Final validation
        integrity_result["is_valid"] = len(integrity_result["issues"]) == 0
        
        # Character generation readiness assessment
        integrity_result["character_generation_readiness"] = {
            "basic_validation": True,
            "enhanced_validation": integrity_result["is_valid"],
            "enum_support": integrity_result["feature_completeness"]["enum_integration_complete"],
            "preset_support": integrity_result["feature_completeness"]["preset_system_integration"],
            "overall_readiness": (
                integrity_result["compliance_score"] >= 0.9 and
                integrity_result["feature_completeness"]["enum_integration_complete"] and
                len(integrity_result["issues"]) == 0
            )
        }
        
    except Exception as e:
        integrity_result["is_valid"] = False
        integrity_result["issues"].append(f"Enhanced validation module integrity check error: {str(e)}")
    
    return integrity_result


# Legacy function name mapping
validate_validation_module_integrity = validate_enhanced_validation_module_integrity

# ============================================================================
# ENHANCED MODULE EXPORTS - Complete __all__ definition
# ============================================================================

__all__ = [
    # Enhanced Core Classes
    "EnhancedCreativeCultureValidator",
    "EnhancedCreativeValidationResult", 
    "EnhancedCreativeValidationIssue",
    
    # Legacy compatibility
    "CreativeCultureValidator",
    "CreativeValidationResult",
    "CreativeValidationIssue",
    
    # Enhanced Enums
    "EnhancedValidationIssueType",
    "EnhancedCreativeValidationFocus",
    
    # Legacy enum compatibility
    "ValidationIssueType",
    "CreativeValidationFocus",
    
    # Core Validation Enums
    "CultureValidationCategory",
    "CultureValidationSeverity",
    
    # Enhancement System Enums (NEW)
    "CultureEnhancementCategory",
    "CultureEnhancementPriority", 
    "CultureGenerationStatus",
    
    # Culture Generation Enums
    "CultureGenerationType",
    "CultureAuthenticityLevel",
    "CultureCreativityLevel",
    "CultureSourceType",
    "CultureComplexityLevel",
    
    # Cultural Structure Enums
    "CultureNamingStructure",
    "CultureGenderSystem",
    "CultureLinguisticFamily",
    "CultureTemporalPeriod",
    
    # Enhanced Core Validation Functions
    "validate_culture_for_characters",
    "quick_culture_assessment",
    
    # Enhanced Convenience Functions
    "validate_character_culture_enhanced",
    "validate_culture_names_for_characters_enhanced",
    "get_culture_enhancement_suggestions_enhanced",
    "validate_multiple_cultures_enhanced",
    
    # Enhanced Preset Validation Functions
    "validate_fantasy_culture_enhanced",
    "validate_historical_inspired_culture_enhanced", 
    "validate_original_culture_enhanced",
    "validate_gaming_optimized_culture",
    
    # Enum Utility Functions (NEW)
    "suggest_creative_culture_enhancements",
    "calculate_character_generation_score",
    "get_character_generation_recommendations",
    
    # Preset System (NEW)
    "CHARACTER_CULTURE_PRESETS",
    
    # Enhanced Module Validation
    "validate_enhanced_validation_module_integrity",
    "validate_validation_module_integrity",  # Legacy
    
    # Enhanced Module Metadata
    "__version__",
    "CLEAN_ARCHITECTURE_COMPLIANCE",
    "CREATIVE_VALIDATION_APPROACH", 
    "CREATIVE_VALIDATION_PHILOSOPHY",
    "ENUM_COMPLIANCE",
    
    # Re-exported Exceptions
    "CultureValidationError",
    "CultureStructureError"
]

# ============================================================================
# ENHANCED MODULE INITIALIZATION AND VALIDATION
# ============================================================================

# Validate enhanced module integrity on import
_module_validation = validate_enhanced_validation_module_integrity()
if not _module_validation["is_valid"]:
    import warnings
    warnings.warn(
        f"Enhanced validation module integrity issues: {_module_validation['issues']}", 
        ImportWarning
    )

# Enhanced creative validation banner for development
if __name__ == "__main__":
    print("=" * 80)
    print("D&D Character Creator - Enhanced Creative Validation Utilities")
    print("Character Generation Focused Quality Assurance with Complete Enum Integration")
    print("=" * 80)
    print(f"Module Version: {__version__}")
    print(f"Compliance Score: {_module_validation['compliance_score']:.2f}")
    print(f"Enum Integration: {_module_validation['feature_completeness']['enum_integration_complete']}")
    print(f"Preset System: {_module_validation['feature_completeness']['preset_system_integration']}")
    print(f"Character Generation Ready: {_module_validation['character_generation_readiness']['overall_readiness']}")
    print(f"Features Available: {list(_module_validation['feature_completeness'].keys())}")
    
    print("\nEnhanced Creative Validation Philosophy:")
    print(f"  • {CREATIVE_VALIDATION_APPROACH['philosophy']}")
    print(f"  • Focus: {CREATIVE_VALIDATION_APPROACH['focus']}")
    print(f"  • Style: {CREATIVE_VALIDATION_APPROACH['validation_style']}")
    
    print("\nEnum Integration Features:")
    for feature in CREATIVE_VALIDATION_APPROACH["enum_integration_features"]:
        print(f"  • {feature}")
    
    print("\nEnhancement Focus Areas:")
    for area in CREATIVE_VALIDATION_APPROACH["enhancement_focus"]:
        print(f"  • {area}")
    
    print("\nQuality Dimensions:")
    for dimension, description in CREATIVE_VALIDATION_APPROACH["quality_dimensions"].items():
        print(f"  • {dimension}: {description}")
    
    if _module_validation["preset_system_available"]:
        print(f"\nAvailable Presets: {', '.join(_module_validation['available_presets'])}")
    
    print("=" * 80)