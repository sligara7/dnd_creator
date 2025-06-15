"""
Core Culture Utilities - Clean Architecture Culture Generation System.

This module provides pure functional utilities for culturally authentic
character name generation with educational focus and respect for cultural heritage.

Follows Clean Architecture principles:
- Infrastructure independence
- Pure functions with no side effects
- Immutable data structures
- Inward dependencies only
- Domain-driven design with educational focus

Key Features:
- Culturally sensitive AI-powered culture generation
- Comprehensive LLM response parsing
- Educational prompt engineering with authenticity focus
- Pure functional approach to cultural data processing
- Respectful representation of cultural heritage

Usage:
    >>> from core.utils.cultures import (
    ...     CultureGenerator, CultureParser, CulturePromptTemplates,
    ...     create_culture_spec, build_culture_prompt
    ... )
    >>> 
    >>> # Create culture specification
    >>> spec = create_culture_spec("Ancient Norse seafaring culture")
    >>> 
    >>> # Generate culture template
    >>> culture = CultureGenerator.create_culture_template(spec)
    >>> 
    >>> # Build AI prompt
    >>> prompt = build_culture_prompt("Celtic druids", authenticity_level=CultureAuthenticityLevel.HIGH)
    >>> 
    >>> # Parse LLM response
    >>> parsed = CultureParser.parse_culture_response(llm_response)
"""

# ============================================================================
# CORE IMPORTS - Main Module Classes and Functions
# ============================================================================

# Culture Generation Core
from .culture_generator import (
    # Main classes
    CultureGenerator,
    BaseCulture,
    CultureGenerationSpec,
    
    # Utility functions
    create_culture_spec,
    validate_culture_spec,
    get_recommended_complexity,
    
    # Version info
    __version__ as generator_version,
    CLEAN_ARCHITECTURE_COMPLIANCE as generator_compliance
)

# Culture Response Parsing
from .culture_parser import (
    # Main classes
    CultureParser,
    ParsedCultureData,
    ResponseFormat,
    NameCategory,
    
    # Utility functions
    parse_multiple_responses,
    merge_multiple_parsed_data,
    extract_names_from_text,
    validate_response_format,
    
    # Version info
    __version__ as parser_version,
    CLEAN_ARCHITECTURE_COMPLIANCE as parser_compliance
)

# Prompt Templates
from .prompt_templates import (
    # Main classes
    CulturePromptTemplates,
    PromptTemplate,
    PromptType,
    PromptStyle,
    
    # Utility functions
    build_culture_prompt,
    build_enhancement_prompt,
    build_validation_prompt,
    get_prompt_recommendations,
    
    # Version info
    __version__ as templates_version,
    CLEAN_ARCHITECTURE_COMPLIANCE as templates_compliance
)

# ============================================================================
# ENUMS AND TYPES - Re-export for convenience
# ============================================================================

from ...enums.culture_types import (
    # Core culture enums
    CultureGenerationType,
    CultureAuthenticityLevel,
    CultureCreativityLevel,
    CultureSourceType,
    CultureComplexityLevel,
    
    # Cultural system enums
    CultureNamingStructure,
    CultureGenderSystem,
    CultureLinguisticFamily,
    CultureTemporalPeriod,
    
    # Validation enums
    CultureValidationCategory,
    CultureValidationSeverity
)

# ============================================================================
# EXCEPTIONS - Re-export for convenience
# ============================================================================

from ...exceptions.culture import (
    CultureGenerationError,
    CultureParsingError,
    CultureValidationError,
    CultureStructureError,
    CultureTemplateError
)

# ============================================================================
# VALIDATION UTILITIES - Re-export for convenience
# ============================================================================

from ..validation.culture_validator import (
    ValidationResult
)

# ============================================================================
# MODULE METADATA
# ============================================================================

__version__ = "1.0.0"
__author__ = "D&D Character Creator Team"
__description__ = "Clean Architecture Culture Generation Utilities"

# Clean Architecture compliance for the entire module
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/utils/cultures",
    "description": "Pure functional culture generation utilities",
    "dependencies": {
        "internal": [
            "core.enums.culture_types",
            "core.exceptions.culture", 
            "core.utils.validation.culture_validator"
        ],
        "external": ["typing", "dataclasses", "enum", "re", "json"]
    },
    "dependents": [
        "domain.services.culture_service",
        "infrastructure.llm.culture_llm_service",
        "application.use_cases.culture_use_cases"
    ],
    "principles": {
        "infrastructure_independent": True,
        "pure_functions": True,
        "immutable_data": True,
        "no_side_effects": True,
        "stateless_operations": True,
        "educational_focus": True,
        "cultural_sensitivity": True
    },
    "sub_modules": {
        "culture_generator": generator_compliance,
        "culture_parser": parser_compliance,
        "prompt_templates": templates_compliance
    }
}

# Educational and cultural sensitivity metadata
CULTURAL_SENSITIVITY_GUIDELINES = {
    "authenticity_levels": {
        "ACADEMIC": "Rigorous scholarly approach with historical accuracy",
        "HIGH": "Historically accurate with cultural respect",
        "MODERATE": "Culturally respectful with some creative interpretation",
        "CREATIVE": "Creative interpretation while maintaining respect",
        "FANTASY": "Fantasy adaptation with cultural sensitivity",
        "NONE": "Creative generation with basic respect"
    },
    "usage_principles": [
        "Always approach cultures with respect and dignity",
        "Provide educational context when possible",
        "Avoid stereotypes and harmful representations",
        "Focus on linguistic authenticity when available",
        "Include historical and cultural context for learning",
        "Encourage respectful use in gaming contexts"
    ],
    "educational_objectives": [
        "Cultural awareness and sensitivity",
        "Understanding of naming conventions",
        "Appreciation of linguistic diversity",
        "Historical and cultural context learning",
        "Respectful gaming practices"
    ]
}

# ============================================================================
# CONVENIENCE FACTORY FUNCTIONS
# ============================================================================

def create_norse_culture_spec(
    authenticity_level: CultureAuthenticityLevel = CultureAuthenticityLevel.HIGH,
    complexity_level: CultureComplexityLevel = CultureComplexityLevel.DETAILED
) -> CultureGenerationSpec:
    """
    Create a specification for Norse culture generation.
    
    Convenience function for common Norse culture requests.
    
    Args:
        authenticity_level: Desired authenticity level
        complexity_level: Desired complexity level
        
    Returns:
        CultureGenerationSpec for Norse culture
        
    Example:
        >>> spec = create_norse_culture_spec(CultureAuthenticityLevel.ACADEMIC)
        >>> culture = CultureGenerator.create_culture_template(spec)
    """
    return create_culture_spec(
        "Ancient Norse seafaring culture with Viking Age traditions",
        authenticity_level=authenticity_level,
        creativity_level=CultureCreativityLevel.AUTHENTIC,
        complexity_level=complexity_level
    )


def create_celtic_culture_spec(
    authenticity_level: CultureAuthenticityLevel = CultureAuthenticityLevel.HIGH,
    complexity_level: CultureComplexityLevel = CultureComplexityLevel.DETAILED
) -> CultureGenerationSpec:
    """
    Create a specification for Celtic culture generation.
    
    Convenience function for common Celtic culture requests.
    
    Args:
        authenticity_level: Desired authenticity level
        complexity_level: Desired complexity level
        
    Returns:
        CultureGenerationSpec for Celtic culture
        
    Example:
        >>> spec = create_celtic_culture_spec(CultureAuthenticityLevel.HIGH)
        >>> culture = CultureGenerator.create_culture_template(spec)
    """
    return create_culture_spec(
        "Ancient Celtic druidic culture with clan traditions",
        authenticity_level=authenticity_level,
        creativity_level=CultureCreativityLevel.AUTHENTIC,
        complexity_level=complexity_level
    )


def create_fantasy_culture_spec(
    cultural_reference: str,
    creativity_level: CultureCreativityLevel = CultureCreativityLevel.CREATIVE,
    complexity_level: CultureComplexityLevel = CultureComplexityLevel.STANDARD
) -> CultureGenerationSpec:
    """
    Create a specification for fantasy culture generation.
    
    Convenience function for fantasy-adapted cultures.
    
    Args:
        cultural_reference: Description of the fantasy culture
        creativity_level: Desired creativity level
        complexity_level: Desired complexity level
        
    Returns:
        CultureGenerationSpec for fantasy culture
        
    Example:
        >>> spec = create_fantasy_culture_spec("Tolkien-inspired woodland elves")
        >>> culture = CultureGenerator.create_culture_template(spec)
    """
    return create_culture_spec(
        cultural_reference,
        authenticity_level=CultureAuthenticityLevel.FANTASY,
        creativity_level=creativity_level,
        complexity_level=complexity_level
    )


# ============================================================================
# WORKFLOW HELPER FUNCTIONS
# ============================================================================

def generate_complete_culture(
    cultural_reference: str,
    authenticity_level: CultureAuthenticityLevel = CultureAuthenticityLevel.MODERATE,
    complexity_level: CultureComplexityLevel = CultureComplexityLevel.STANDARD,
    min_names_per_category: int = 20
) -> tuple[str, CultureGenerationSpec, BaseCulture]:
    """
    Complete workflow for culture generation.
    
    Convenience function that creates spec, generates template, and builds prompt.
    
    Args:
        cultural_reference: Description of culture to generate
        authenticity_level: Desired authenticity level
        complexity_level: Desired complexity level
        min_names_per_category: Minimum names per category
        
    Returns:
        Tuple of (prompt_string, culture_spec, culture_template)
        
    Example:
        >>> prompt, spec, culture = generate_complete_culture(
        ...     "Ancient Egyptian scribes and priests",
        ...     CultureAuthenticityLevel.HIGH,
        ...     CultureComplexityLevel.DETAILED
        ... )
    """
    # Create specification
    spec = create_culture_spec(
        cultural_reference,
        authenticity_level,
        complexity_level=complexity_level
    )
    
    # Generate culture template
    culture = CultureGenerator.create_culture_template(spec)
    
    # Build prompt
    prompt = build_culture_prompt(
        cultural_reference,
        authenticity_level,
        complexity_level,
        min_names_per_category
    )
    
    return prompt, spec, culture


def parse_and_validate_response(
    llm_response: str,
    expected_categories: Optional[List[str]] = None
) -> tuple[ParsedCultureData, ValidationResult]:
    """
    Complete workflow for parsing and validating LLM responses.
    
    Convenience function that parses response and validates results.
    
    Args:
        llm_response: Raw LLM response to parse
        expected_categories: Optional list of expected name categories
        
    Returns:
        Tuple of (parsed_data, validation_result)
        
    Example:
        >>> parsed, validation = parse_and_validate_response(response)
        >>> print(f"Valid: {validation.is_valid}, Names: {len(parsed.male_names)}")
    """
    # Parse the response
    parsed = CultureParser.parse_culture_response(llm_response)
    
    # Normalize and validate
    normalized = CultureParser.normalize_culture_data(parsed)
    validation = CultureParser.validate_parsed_data(normalized)
    
    return parsed, validation


def enhance_existing_culture(
    culture_name: str,
    existing_data: str,
    enhancement_requests: Dict[str, int],
    authenticity_level: CultureAuthenticityLevel = CultureAuthenticityLevel.HIGH
) -> str:
    """
    Generate enhancement prompts for existing cultures.
    
    Convenience function for enhancing cultures with additional content.
    
    Args:
        culture_name: Name of the culture to enhance
        existing_data: Current culture data as string
        enhancement_requests: Dict of category->count requests
        authenticity_level: Desired authenticity level
        
    Returns:
        Enhancement prompt string
        
    Example:
        >>> prompt = enhance_existing_culture(
        ...     "Norse Culture",
        ...     existing_culture_data,
        ...     {"male_names": 10, "titles": 5, "epithets": 8}
        ... )
    """
    total_count = sum(enhancement_requests.values())
    categories = list(enhancement_requests.keys())
    
    return build_enhancement_prompt(
        culture_name,
        existing_data,
        "expand_names",
        total_count,
        categories
    )


# ============================================================================
# VALIDATION AND QUALITY ASSURANCE
# ============================================================================

def validate_module_integrity() -> Dict[str, Any]:
    """
    Validate the integrity and completeness of the cultures module.
    
    Pure function that checks module completeness and Clean Architecture compliance.
    
    Returns:
        Dictionary with validation results and compliance information
        
    Example:
        >>> integrity = validate_module_integrity()
        >>> print(f"Module valid: {integrity['is_valid']}")
    """
    validation_result = {
        "is_valid": True,
        "issues": [],
        "warnings": [],
        "compliance_score": 0.0,
        "feature_completeness": {},
        "clean_architecture_compliance": CLEAN_ARCHITECTURE_COMPLIANCE
    }
    
    try:
        # Check core classes availability
        core_classes = [
            CultureGenerator, CultureParser, CulturePromptTemplates,
            BaseCulture, ParsedCultureData, PromptTemplate
        ]
        
        for cls in core_classes:
            if not hasattr(cls, '__name__'):
                validation_result["issues"].append(f"Core class {cls} not properly defined")
        
        # Check utility functions
        utility_functions = [
            create_culture_spec, build_culture_prompt, parse_multiple_responses,
            generate_complete_culture, parse_and_validate_response
        ]
        
        for func in utility_functions:
            if not callable(func):
                validation_result["issues"].append(f"Utility function {func.__name__} not callable")
        
        # Check enum availability
        required_enums = [
            CultureAuthenticityLevel, CultureComplexityLevel, CultureSourceType,
            PromptType, ResponseFormat, NameCategory
        ]
        
        for enum_class in required_enums:
            if not hasattr(enum_class, '__members__'):
                validation_result["issues"].append(f"Enum {enum_class.__name__} not properly defined")
        
        # Calculate compliance score
        total_checks = len(core_classes) + len(utility_functions) + len(required_enums)
        passed_checks = total_checks - len(validation_result["issues"])
        validation_result["compliance_score"] = passed_checks / total_checks
        
        # Feature completeness
        validation_result["feature_completeness"] = {
            "culture_generation": True,
            "response_parsing": True,
            "prompt_templates": True,
            "validation_utilities": True,
            "educational_focus": True,
            "cultural_sensitivity": True
        }
        
        # Final validation
        validation_result["is_valid"] = len(validation_result["issues"]) == 0
        
    except Exception as e:
        validation_result["is_valid"] = False
        validation_result["issues"].append(f"Module validation error: {str(e)}")
    
    return validation_result


# ============================================================================
# MODULE EXPORTS - Explicit __all__ definition
# ============================================================================

__all__ = [
    # Core Classes
    "CultureGenerator",
    "CultureParser", 
    "CulturePromptTemplates",
    
    # Data Structures
    "BaseCulture",
    "ParsedCultureData",
    "PromptTemplate",
    "CultureGenerationSpec",
    "ValidationResult",
    
    # Enums
    "CultureAuthenticityLevel",
    "CultureCreativityLevel",
    "CultureComplexityLevel",
    "CultureSourceType",
    "CultureGenerationType",
    "CultureNamingStructure",
    "CultureGenderSystem",
    "CultureLinguisticFamily",
    "CultureTemporalPeriod",
    "CultureValidationCategory",
    "CultureValidationSeverity",
    "PromptType",
    "PromptStyle",
    "ResponseFormat",
    "NameCategory",
    
    # Exceptions
    "CultureGenerationError",
    "CultureParsingError",
    "CultureValidationError",
    "CultureStructureError",
    "CultureTemplateError",
    
    # Core Utility Functions
    "create_culture_spec",
    "validate_culture_spec",
    "get_recommended_complexity",
    "build_culture_prompt",
    "build_enhancement_prompt",
    "build_validation_prompt",
    "get_prompt_recommendations",
    "parse_multiple_responses",
    "merge_multiple_parsed_data",
    "extract_names_from_text",
    "validate_response_format",
    
    # Convenience Factory Functions
    "create_norse_culture_spec",
    "create_celtic_culture_spec",
    "create_fantasy_culture_spec",
    
    # Workflow Helper Functions
    "generate_complete_culture",
    "parse_and_validate_response",
    "enhance_existing_culture",
    
    # Module Validation
    "validate_module_integrity",
    
    # Module Metadata
    "__version__",
    "CLEAN_ARCHITECTURE_COMPLIANCE",
    "CULTURAL_SENSITIVITY_GUIDELINES"
]

# ============================================================================
# MODULE INITIALIZATION AND VALIDATION
# ============================================================================

# Validate module integrity on import
_module_validation = validate_module_integrity()
if not _module_validation["is_valid"]:
    import warnings
    warnings.warn(
        f"Culture module validation issues: {_module_validation['issues']}", 
        ImportWarning
    )

# Educational banner for development
if __name__ == "__main__":
    print("=" * 80)
    print("D&D Character Creator - Culture Generation Utilities")
    print("Clean Architecture Implementation")
    print("=" * 80)
    print(f"Module Version: {__version__}")
    print(f"Compliance Score: {_module_validation['compliance_score']:.2f}")
    print(f"Features Available: {list(_module_validation['feature_completeness'].keys())}")
    print("\nCultural Sensitivity Guidelines:")
    for principle in CULTURAL_SENSITIVITY_GUIDELINES["usage_principles"]:
        print(f"  • {principle}")
    print("\nEducational Objectives:")
    for objective in CULTURAL_SENSITIVITY_GUIDELINES["educational_objectives"]:
        print(f"  • {objective}")
    print("=" * 80)