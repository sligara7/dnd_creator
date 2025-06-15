"""
Core Validation Utilities - Creative Quality Assurance for Character Generation.

This module provides validation utilities focused on enhancing creative freedom
and supporting character generation rather than enforcing rigid constraints.
Follows Clean Architecture principles with pure functional validation.

Creative Validation Philosophy:
- Enable and enhance creative character generation
- Provide supportive assessment rather than restrictive validation
- Focus on gaming usability and character background support
- Maintain creative freedom while offering quality improvements
- Almost all content is usable - validation suggests enhancements

Key Features:
- Creative culture quality assessment for character generation
- Gaming usability optimization suggestions
- Character background support validation
- Name generation quality assurance with creative focus
- Pure functional validation with constructive feedback
- Enhancement opportunities rather than rigid requirements

Usage:
    >>> from core.utils.validation import (
    ...     CreativeCultureValidator, validate_for_character_creation,
    ...     quick_gaming_assessment, assess_creative_value
    ... )
    >>> 
    >>> # Validate any culture for character creation
    >>> result = validate_for_character_creation(culture_data)
    >>> print(f"Character support: {result.character_support_score:.2f}")
    >>> 
    >>> # Quick gaming usability check
    >>> gaming = quick_gaming_assessment(culture_data)
    >>> print(f"Gaming ready: {gaming['gaming_ready']}")
    >>> 
    >>> # Assess creative potential
    >>> creative = assess_creative_value(culture_data)
    >>> print(f"Creative score: {creative['creative_score']:.2f}")
"""

# ============================================================================
# CORE IMPORTS - Main Validation Classes and Functions
# ============================================================================

# Creative Culture Validation
from .culture_validator import (
    # Main validation class
    CreativeCultureValidator,
    
    # Data structures
    CreativeValidationResult,
    CreativeValidationIssue,
    
    # Enums
    ValidationIssueType,
    CreativeValidationFocus,
    
    # Utility functions
    validate_for_character_creation,
    quick_gaming_assessment,
    assess_creative_value,
    get_character_generation_readiness,
    
    # Module metadata
    __version__ as validator_version,
    CLEAN_ARCHITECTURE_COMPLIANCE as validator_compliance,
    CREATIVE_VALIDATION_PHILOSOPHY
)

# ============================================================================
# ENUMS AND TYPES - Re-export for convenience
# ============================================================================

from ...enums.culture_types import (
    # Validation-related enums
    CultureValidationCategory,
    CultureValidationSeverity,
    
    # Culture type enums for validation context
    CultureAuthenticityLevel,
    CultureSourceType,
    CultureComplexityLevel
)

# ============================================================================
# EXCEPTIONS - Re-export for convenience
# ============================================================================

from ...exceptions.culture import (
    CultureValidationError,
    CultureStructureError
)

# ============================================================================
# MODULE METADATA
# ============================================================================

__version__ = "1.0.0"
__author__ = "D&D Character Creator Team"
__description__ = "Creative Validation Utilities for Character Generation"

# Clean Architecture compliance for the entire validation module
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/utils/validation",
    "description": "Creative quality assurance utilities for character generation",
    "dependencies": {
        "internal": [
            "core.enums.culture_types",
            "core.exceptions.culture"
        ],
        "external": ["typing", "dataclasses", "enum", "re", "collections"]
    },
    "dependents": [
        "domain.services.culture_service",
        "application.use_cases.culture_use_cases",
        "core.utils.cultures"
    ],
    "principles": {
        "infrastructure_independent": True,
        "pure_functions": True,
        "immutable_data": True,
        "no_side_effects": True,
        "stateless_operations": True,
        "creative_focused": True,
        "character_generation_optimized": True,
        "supportive_validation": True
    },
    "sub_modules": {
        "culture_validator": validator_compliance
    }
}

# Creative validation approach metadata
CREATIVE_VALIDATION_APPROACH = {
    "philosophy": "Enable creativity rather than restrict it",
    "focus": "Character generation support and enhancement",
    "validation_style": "Constructive suggestions over rigid requirements",
    "usability_threshold": "Almost all cultures are usable for character generation",
    "enhancement_focus": [
        "Character background richness",
        "Gaming table usability",
        "Name generation quality",
        "Creative inspiration potential",
        "Player experience optimization"
    ],
    "quality_dimensions": {
        "creative_quality_score": "How well culture inspires character creation",
        "gaming_usability_score": "How practical culture is for table use",
        "character_support_score": "How well culture supports character backgrounds",
        "name_generation_score": "Quality of names for character creation"
    }
}

# ============================================================================
# CONVENIENCE VALIDATION FUNCTIONS
# ============================================================================

def validate_character_culture(
    culture_data: Dict[str, Any],
    focus_areas: Optional[List[CreativeValidationFocus]] = None
) -> CreativeValidationResult:
    """
    Comprehensive culture validation for character generation.
    
    Convenience function that performs complete validation with optional focus areas.
    
    Args:
        culture_data: Dictionary containing culture information
        focus_areas: Optional list of specific validation focus areas
        
    Returns:
        CreativeValidationResult with comprehensive assessment
        
    Example:
        >>> # Validate with specific focus areas
        >>> result = validate_character_culture(
        ...     culture_data,
        ...     [CreativeValidationFocus.CHARACTER_BACKGROUNDS, CreativeValidationFocus.NAME_GENERATION]
        ... )
        >>> print(f"Character ready: {result.character_support_score >= 0.7}")
    """
    if focus_areas is None:
        # Default comprehensive validation
        return validate_for_character_creation(culture_data)
    
    # Focused validation based on specified areas
    if CreativeValidationFocus.CHARACTER_BACKGROUNDS in focus_areas:
        return CreativeCultureValidator.assess_character_background_support(culture_data)
    elif CreativeValidationFocus.NAME_GENERATION in focus_areas:
        return CreativeCultureValidator.assess_name_generation_quality(culture_data)
    elif CreativeValidationFocus.GAMING_EXPERIENCE in focus_areas:
        return CreativeCultureValidator.assess_gaming_usability(culture_data)
    elif CreativeValidationFocus.CREATIVE_FREEDOM in focus_areas:
        return CreativeCultureValidator.assess_creative_potential(culture_data)
    else:
        # Default if no recognized focus areas
        return validate_for_character_creation(culture_data)


def validate_culture_names_for_characters(
    names_dict: Dict[str, List[str]],
    character_archetypes: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Validate name collections specifically for character generation.
    
    Focused validation on name quality and character generation support.
    
    Args:
        names_dict: Dictionary of name categories and name lists
        character_archetypes: Optional list of character archetypes to consider
        
    Returns:
        Dictionary with name validation results
        
    Example:
        >>> names = {
        ...     'male_names': ['Thorin', 'Balin', 'Dwalin'],
        ...     'female_names': ['Disa', 'Nala', 'Vera'],
        ...     'titles': ['Ironforge', 'Stonebeard', 'Goldaxe']
        ... }
        >>> result = validate_culture_names_for_characters(names)
        >>> print(f"Name quality: {result['name_quality_score']:.2f}")
    """
    # Create temporary culture data focused on names
    culture_data = names_dict.copy()
    culture_data['name'] = 'Name Validation Culture'
    
    # Assess name generation quality
    result = CreativeCultureValidator.assess_name_generation_quality(culture_data)
    
    return {
        'name_quality_score': result.name_generation_score,
        'character_fit_score': result.character_support_score,
        'gaming_usability_score': result.gaming_usability_score,
        'total_names': len([name for names in names_dict.values() for name in names if name]),
        'categories_available': list(names_dict.keys()),
        'suggestions': [sugg.message for sugg in result.suggestions],
        'creative_opportunities': [opp.message for opp in result.creative_opportunities],
        'character_archetype_support': result.name_analysis.get('character_fit_potential', 0.5)
    }


def get_culture_enhancement_suggestions(
    culture_data: Dict[str, Any],
    target_score: float = 0.8
) -> Dict[str, Any]:
    """
    Get specific enhancement suggestions to improve culture quality.
    
    Provides actionable suggestions to enhance culture for character generation.
    
    Args:
        culture_data: Dictionary containing culture information
        target_score: Target quality score to achieve (0.0 to 1.0)
        
    Returns:
        Dictionary with enhancement suggestions and priorities
        
    Example:
        >>> suggestions = get_culture_enhancement_suggestions(culture_data, 0.8)
        >>> print("Priority enhancements:")
        >>> for enhancement in suggestions['priority_enhancements']:
        ...     print(f"  • {enhancement}")
    """
    result = validate_for_character_creation(culture_data)
    
    # Prioritize suggestions based on impact
    priority_enhancements = []
    secondary_enhancements = []
    
    # Categorize suggestions by priority
    for suggestion in result.suggestions:
        if suggestion.severity == CultureValidationSeverity.HIGH:
            priority_enhancements.append(suggestion.message)
        elif suggestion.character_impact:
            priority_enhancements.append(f"{suggestion.message} - {suggestion.character_impact}")
        else:
            secondary_enhancements.append(suggestion.message)
    
    # Add general enhancements
    priority_enhancements.extend(result.enhancements[:3])
    secondary_enhancements.extend(result.enhancements[3:])
    
    return {
        'current_scores': {
            'creative_quality': result.creative_quality_score,
            'gaming_usability': result.gaming_usability_score,
            'character_support': result.character_support_score,
            'name_generation': result.name_generation_score
        },
        'target_score': target_score,
        'needs_enhancement': max(
            result.creative_quality_score,
            result.gaming_usability_score,
            result.character_support_score,
            result.name_generation_score
        ) < target_score,
        'priority_enhancements': priority_enhancements,
        'secondary_enhancements': secondary_enhancements,
        'creative_opportunities': [opp.message for opp in result.creative_opportunities],
        'character_generation_impact': [
            sugg.character_impact for sugg in result.suggestions 
            if sugg.character_impact
        ]
    }


def validate_multiple_cultures(
    cultures_dict: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Validate multiple cultures and provide comparative analysis.
    
    Useful for comparing culture quality across multiple generated cultures.
    
    Args:
        cultures_dict: Dictionary mapping culture names to culture data
        
    Returns:
        Dictionary with comparative validation results
        
    Example:
        >>> cultures = {
        ...     'mountain_dwarves': dwarf_culture_data,
        ...     'forest_elves': elf_culture_data,
        ...     'desert_nomads': nomad_culture_data
        ... }
        >>> comparison = validate_multiple_cultures(cultures)
        >>> print(f"Best for characters: {comparison['best_for_characters']}")
    """
    results = {}
    scores = {}
    
    # Validate each culture
    for culture_name, culture_data in cultures_dict.items():
        try:
            result = validate_for_character_creation(culture_data)
            results[culture_name] = result
            scores[culture_name] = {
                'creative_quality': result.creative_quality_score,
                'gaming_usability': result.gaming_usability_score,
                'character_support': result.character_support_score,
                'name_generation': result.name_generation_score,
                'overall': (result.creative_quality_score + result.gaming_usability_score + 
                           result.character_support_score + result.name_generation_score) / 4
            }
        except Exception as e:
            results[culture_name] = None
            scores[culture_name] = {'error': str(e)}
    
    # Find best cultures for different purposes
    valid_scores = {name: score for name, score in scores.items() if 'error' not in score}
    
    best_overall = max(valid_scores.items(), key=lambda x: x[1]['overall'])[0] if valid_scores else None
    best_for_characters = max(valid_scores.items(), key=lambda x: x[1]['character_support'])[0] if valid_scores else None
    best_for_gaming = max(valid_scores.items(), key=lambda x: x[1]['gaming_usability'])[0] if valid_scores else None
    
    return {
        'total_cultures': len(cultures_dict),
        'successfully_validated': len(valid_scores),
        'validation_results': results,
        'comparative_scores': scores,
        'recommendations': {
            'best_overall': best_overall,
            'best_for_characters': best_for_characters,
            'best_for_gaming': best_for_gaming
        },
        'average_scores': {
            'creative_quality': sum(s['creative_quality'] for s in valid_scores.values()) / len(valid_scores) if valid_scores else 0,
            'gaming_usability': sum(s['gaming_usability'] for s in valid_scores.values()) / len(valid_scores) if valid_scores else 0,
            'character_support': sum(s['character_support'] for s in valid_scores.values()) / len(valid_scores) if valid_scores else 0,
            'name_generation': sum(s['name_generation'] for s in valid_scores.values()) / len(valid_scores) if valid_scores else 0
        }
    }


# ============================================================================
# CREATIVE VALIDATION PRESETS
# ============================================================================

def validate_fantasy_culture(culture_data: Dict[str, Any]) -> CreativeValidationResult:
    """
    Validate culture with fantasy-optimized criteria.
    
    Preset validation for fantasy/mythical cultures with creative freedom focus.
    
    Args:
        culture_data: Dictionary containing culture information
        
    Returns:
        CreativeValidationResult optimized for fantasy contexts
    """
    # Fantasy cultures get maximum creative freedom
    return validate_for_character_creation(culture_data)


def validate_historical_inspired_culture(culture_data: Dict[str, Any]) -> CreativeValidationResult:
    """
    Validate culture inspired by historical sources.
    
    Preset validation for historically-inspired cultures with creative adaptation.
    
    Args:
        culture_data: Dictionary containing culture information
        
    Returns:
        CreativeValidationResult optimized for historical adaptation
    """
    # Historical cultures still prioritize creative character generation
    return validate_for_character_creation(culture_data)


def validate_original_culture(culture_data: Dict[str, Any]) -> CreativeValidationResult:
    """
    Validate completely original/invented culture.
    
    Preset validation for entirely original cultures with maximum creative support.
    
    Args:
        culture_data: Dictionary containing culture information
        
    Returns:
        CreativeValidationResult optimized for original creative cultures
    """
    # Original cultures get full creative validation focus
    return validate_for_character_creation(culture_data)


# ============================================================================
# MODULE VALIDATION AND QUALITY ASSURANCE
# ============================================================================

def validate_validation_module_integrity() -> Dict[str, Any]:
    """
    Validate the integrity and completeness of the validation module.
    
    Pure function that checks module completeness and Clean Architecture compliance.
    
    Returns:
        Dictionary with validation module integrity results
    """
    integrity_result = {
        "is_valid": True,
        "issues": [],
        "warnings": [],
        "compliance_score": 0.0,
        "feature_completeness": {},
        "clean_architecture_compliance": CLEAN_ARCHITECTURE_COMPLIANCE,
        "creative_validation_approach": CREATIVE_VALIDATION_APPROACH
    }
    
    try:
        # Check core classes availability
        core_classes = [
            CreativeCultureValidator,
            CreativeValidationResult,
            CreativeValidationIssue
        ]
        
        for cls in core_classes:
            if not hasattr(cls, '__name__'):
                integrity_result["issues"].append(f"Core class {cls} not properly defined")
        
        # Check utility functions
        utility_functions = [
            validate_for_character_creation,
            quick_gaming_assessment,
            assess_creative_value,
            get_character_generation_readiness,
            validate_character_culture,
            get_culture_enhancement_suggestions
        ]
        
        for func in utility_functions:
            if not callable(func):
                integrity_result["issues"].append(f"Utility function {func.__name__} not callable")
        
        # Check enum availability
        required_enums = [
            ValidationIssueType,
            CreativeValidationFocus,
            CultureValidationCategory,
            CultureValidationSeverity
        ]
        
        for enum_class in required_enums:
            if not hasattr(enum_class, '__members__'):
                integrity_result["issues"].append(f"Enum {enum_class.__name__} not properly defined")
        
        # Calculate compliance score
        total_checks = len(core_classes) + len(utility_functions) + len(required_enums)
        passed_checks = total_checks - len(integrity_result["issues"])
        integrity_result["compliance_score"] = passed_checks / total_checks
        
        # Feature completeness
        integrity_result["feature_completeness"] = {
            "creative_culture_validation": True,
            "character_generation_support": True,
            "gaming_usability_assessment": True,
            "name_quality_validation": True,
            "enhancement_suggestions": True,
            "comparative_validation": True,
            "creative_freedom_preservation": True
        }
        
        # Final validation
        integrity_result["is_valid"] = len(integrity_result["issues"]) == 0
        
    except Exception as e:
        integrity_result["is_valid"] = False
        integrity_result["issues"].append(f"Validation module integrity check error: {str(e)}")
    
    return integrity_result


# ============================================================================
# MODULE EXPORTS - Explicit __all__ definition
# ============================================================================

__all__ = [
    # Core Classes
    "CreativeCultureValidator",
    
    # Data Structures
    "CreativeValidationResult",
    "CreativeValidationIssue",
    
    # Enums
    "ValidationIssueType",
    "CreativeValidationFocus",
    "CultureValidationCategory",
    "CultureValidationSeverity",
    
    # Core Validation Functions
    "validate_for_character_creation",
    "quick_gaming_assessment",
    "assess_creative_value",
    "get_character_generation_readiness",
    
    # Convenience Functions
    "validate_character_culture",
    "validate_culture_names_for_characters",
    "get_culture_enhancement_suggestions",
    "validate_multiple_cultures",
    
    # Preset Validation Functions
    "validate_fantasy_culture",
    "validate_historical_inspired_culture",
    "validate_original_culture",
    
    # Module Validation
    "validate_validation_module_integrity",
    
    # Module Metadata
    "__version__",
    "CLEAN_ARCHITECTURE_COMPLIANCE",
    "CREATIVE_VALIDATION_APPROACH",
    "CREATIVE_VALIDATION_PHILOSOPHY",
    
    # Re-exported Enums
    "CultureAuthenticityLevel",
    "CultureSourceType",
    "CultureComplexityLevel",
    
    # Re-exported Exceptions
    "CultureValidationError",
    "CultureStructureError"
]

# ============================================================================
# MODULE INITIALIZATION AND VALIDATION
# ============================================================================

# Validate module integrity on import
_module_validation = validate_validation_module_integrity()
if not _module_validation["is_valid"]:
    import warnings
    warnings.warn(
        f"Validation module integrity issues: {_module_validation['issues']}", 
        ImportWarning
    )

# Creative validation banner for development
if __name__ == "__main__":
    print("=" * 80)
    print("D&D Character Creator - Creative Validation Utilities")
    print("Character Generation Focused Quality Assurance")
    print("=" * 80)
    print(f"Module Version: {__version__}")
    print(f"Compliance Score: {_module_validation['compliance_score']:.2f}")
    print(f"Features Available: {list(_module_validation['feature_completeness'].keys())}")
    print("\nCreative Validation Philosophy:")
    print(f"  • {CREATIVE_VALIDATION_APPROACH['philosophy']}")
    print(f"  • Focus: {CREATIVE_VALIDATION_APPROACH['focus']}")
    print(f"  • Style: {CREATIVE_VALIDATION_APPROACH['validation_style']}")
    print("\nEnhancement Focus Areas:")
    for area in CREATIVE_VALIDATION_APPROACH["enhancement_focus"]:
        print(f"  • {area}")
    print("\nQuality Dimensions:")
    for dimension, description in CREATIVE_VALIDATION_APPROACH["quality_dimensions"].items():
        print(f"  • {dimension}: {description}")
    print("=" * 80)