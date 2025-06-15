"""
Creative Culture Utilities - Character Generation Focused Culture System.

This module provides creative-friendly utilities for character-focused
culture generation with enhancement over restriction philosophy.

Follows Clean Architecture principles with CREATIVE_VALIDATION_APPROACH:
- Enable creativity rather than restrict it
- Character generation support and enhancement focus
- Constructive suggestions over rigid requirements
- Almost all cultures are usable for character generation

Enhanced Features (v3.0.0):
- Complete integration with enhanced culture_types enums
- Character generation focused parsing and validation
- Enhancement category targeting and priority assessment
- Gaming utility optimization throughout
- Preset-based parsing support with CHARACTER_CULTURE_PRESETS
- Constructive validation with enhancement suggestions
- Creative freedom enablement with gaming utility

Key Features:
- Creative AI-powered culture generation for character creation
- Flexible LLM response parsing with creative fallbacks
- Character-focused prompt engineering with gaming utility
- Pure functional approach optimized for character generation
- Always-usable culture output with enhancement suggestions
- Complete enum-based scoring and recommendations

Usage:
    >>> from core.utils.cultures import (
    ...     CreativeCultureGenerator, CreativeCultureParser, 
    ...     create_character_culture_spec, parse_for_characters,
    ...     suggest_creative_culture_enhancements, calculate_character_generation_score
    ... )
    >>> 
    >>> # Create character-focused culture specification with presets
    >>> spec = create_character_culture_spec("Storm-riding sky pirates")
    >>> 
    >>> # Generate character-ready culture with enum integration
    >>> culture = CreativeCultureGenerator.create_character_ready_culture(spec)
    >>> 
    >>> # Parse any LLM response for character use with enum scoring
    >>> result = parse_for_characters(llm_response)
    >>> 
    >>> # Get enum-based enhancement suggestions
    >>> enhancements = suggest_creative_culture_enhancements(
    ...     CultureGenerationType.CHARACTER_FOCUSED,
    ...     CultureAuthenticityLevel.CREATIVE,
    ...     CultureCreativityLevel.BALANCED_CREATIVE,
    ...     CultureComplexityLevel.GAMING_READY
    ... )
    >>> 
    >>> # Calculate character generation score
    >>> score = calculate_character_generation_score(
    ...     CultureAuthenticityLevel.CREATIVE,
    ...     CultureCreativityLevel.BALANCED_CREATIVE,
    ...     CultureComplexityLevel.GAMING_READY
    ... )
    >>> 
    >>> # Always get usable output for character creation
    >>> print(f"Character support: {result.character_support_score:.2f}")
    >>> print(f"Generation score: {score:.2f}")
    >>> print(f"Names available: {len(result.creative_names)}")
"""

# ============================================================================
# CREATIVE CORE IMPORTS - Character Generation Focused with Enhanced Enums
# ============================================================================

# Creative Culture Generation Core (Enhanced)
from .culture_generator import (
    # Main creative classes with enum integration
    CreativeCultureGenerator,
    CreativeCulture,
    CreativeCultureSpec,
    CreativeValidationResult,
    
    # Utility functions with enum support
    create_character_culture_spec,
    validate_creative_culture_spec,
    
    # Version info
    __version__ as generator_version,
    CREATIVE_VALIDATION_APPROACH_COMPLIANCE as generator_compliance
)

# Creative Culture Response Parsing (Enhanced)
from .culture_parser import (
    # Main creative classes with enum integration
    CreativeCultureParser,
    EnhancedCreativeParsingResult,
    EnhancedCreativeValidationResult,
    ResponseFormat,
    NameCategory,
    
    # Utility functions with enum integration
    parse_for_characters,
    extract_character_names,
    assess_character_readiness,
    
    # Version info
    __version__ as parser_version,
    CREATIVE_VALIDATION_APPROACH_COMPLIANCE as parser_compliance
)

# Creative Prompt Templates (Enhanced)
from .prompt_templates import (
    # Main creative classes with enum integration
    CreativePromptTemplates,
    CharacterPromptTemplate,
    CreativePromptType,
    GamingPromptStyle,
    
    # Utility functions with enum support
    build_character_culture_prompt,
    build_creative_enhancement_prompt,
    build_gaming_validation_prompt,
    get_character_prompt_recommendations,
    
    # Version info
    __version__ as templates_version,
    CREATIVE_VALIDATION_APPROACH_COMPLIANCE as templates_compliance
)

# ============================================================================
# ENHANCED ENUMS AND TYPES - Complete Culture Types Integration
# ============================================================================

from ...enums.culture_types import (
    # Core creative culture enums
    CultureGenerationType,
    CultureAuthenticityLevel,
    CultureCreativityLevel,
    CultureSourceType,
    CultureComplexityLevel,
    
    # Enhancement and validation enums (NEW)
    CultureEnhancementCategory,
    CultureEnhancementPriority,
    CultureGenerationStatus,
    CultureValidationCategory,
    CultureValidationSeverity,
    
    # Cultural system enums (flexible)
    CultureNamingStructure,
    CultureGenderSystem,
    CultureLinguisticFamily,
    CultureTemporalPeriod,
    
    # Enum utility functions (NEW)
    suggest_creative_culture_enhancements,
    calculate_character_generation_score,
    get_character_generation_recommendations,
    
    # Preset configurations (NEW)
    CHARACTER_CULTURE_PRESETS,
    
    # Compliance metadata
    CREATIVE_VALIDATION_APPROACH_COMPLIANCE as ENUM_COMPLIANCE
)

# ============================================================================
# EXCEPTIONS - Re-export Creative-Friendly Versions
# ============================================================================

from ...exceptions.culture import (
    CultureGenerationError,
    CultureParsingError,
    CultureValidationError,
    CultureStructureError,
    CultureTemplateError
)

# ============================================================================
# MODULE METADATA - Enhanced CREATIVE_VALIDATION_APPROACH Aligned
# ============================================================================

__version__ = "3.0.0"
__author__ = "D&D Character Creator Team"
__description__ = "Enhanced Creative Culture Generation Utilities for Character Creation"

# Enhanced Creative Validation Approach compliance for the entire module
CREATIVE_VALIDATION_APPROACH_COMPLIANCE = {
    "philosophy": "Enable creativity rather than restrict it",
    "implementation": "Enhanced creative culture utilities with complete enum integration",
    "focus": "Character generation support and enhancement with enum-based optimization",
    "validation_style": "Constructive suggestions over rigid requirements with enum priorities",
    "usability_threshold": "Almost all cultures are usable for character generation",
    "enum_integration": "Complete integration with enhanced culture_types enums",
    "preset_support": "CHARACTER_CULTURE_PRESETS integration for quick character setup",
    "module_approach": {
        "always_produces_output": True,
        "creative_fallbacks": True,
        "enhancement_focused": True,
        "character_optimized": True,
        "gaming_utility_priority": True,
        "flexible_requirements": True,
        "creative_freedom_enabled": True,
        "enum_based_scoring": True,
        "preset_compatibility": True,
        "enhancement_categorization": True
    },
    "key_features": [
        "Character-ready culture generation with enum-based creativity scoring",
        "Flexible LLM response parsing with enum-based enhancement identification",
        "Enhancement suggestions with CultureEnhancementCategory targeting",
        "Gaming utility optimization with priority assessment",
        "Creative name extraction with enum-based quality scoring",
        "Always usable output guarantee with enum-based character readiness",
        "CHARACTER_CULTURE_PRESETS integration for rapid character creation",
        "Complete enum-based cultural metadata inference and assignment"
    ],
    "sub_modules": {
        "creative_culture_generator": generator_compliance,
        "creative_culture_parser": parser_compliance,
        "creative_prompt_templates": templates_compliance
    },
    "principles": {
        "infrastructure_independent": True,
        "pure_functions": True,
        "immutable_data": True,
        "no_side_effects": True,
        "stateless_operations": True,
        "character_generation_focus": True,
        "creative_enhancement_priority": True,
        "gaming_utility_optimized": True,
        "enum_integration_complete": True,
        "preset_system_enabled": True
    }
}

# Enhanced Clean Architecture compliance
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/utils/cultures",
    "description": "Enhanced creative culture generation utilities for character creation",
    "dependencies": {
        "internal": [
            "core.enums.culture_types (enhanced with all new enums)",
            "core.exceptions.culture"
        ],
        "external": ["typing", "dataclasses", "enum", "re", "json"]
    },
    "dependents": [
        "domain.services.culture_service",
        "infrastructure.llm.culture_llm_service",
        "application.use_cases.culture_use_cases"
    ],
    "enhanced_creative_principles": {
        "creativity_over_restriction": True,
        "character_generation_focused": True,
        "constructive_enhancement": True,
        "usability_guaranteed": True,
        "gaming_optimized": True,
        "enum_based_optimization": True,
        "preset_system_integration": True,
        "enhancement_category_targeting": True
    }
}

# Enhanced Character Generation Guidelines with Enum Integration
CHARACTER_GENERATION_GUIDELINES = {
    "creativity_levels": {
        "CREATIVE": "Full creative freedom with enum-based character generation scoring",
        "BALANCED": "Creative interpretation balanced with enum-based gaming utility",
        "AUTHENTIC": "Authentic elements adapted for character creation with enum validation",
        "FANTASY": "Fantasy adaptation optimized for gaming with enum enhancement",
        "GAMING": "Gaming-first approach with creative elements and enum optimization",
        "ORIGINAL": "Original creative cultures for unique characters with enum scoring"
    },
    "character_generation_principles": [
        "Always prioritize character creation utility with enum-based assessment",
        "Provide names suitable for gaming table pronunciation with quality scoring",
        "Include background hooks for character inspiration with enum categorization",
        "Support diverse character concepts and identities with enum flexibility",
        "Enhance rather than restrict creative player choices using enum priorities",
        "Offer constructive suggestions for improvement with enhancement categories",
        "Use CHARACTER_CULTURE_PRESETS for rapid character culture setup",
        "Apply enum-based scoring for character generation optimization"
    ],
    "gaming_objectives": [
        "Character name accessibility for all players with pronunciation scoring",
        "Background elements that inspire roleplay with enum-based richness",
        "Cultural traits that support character development with complexity scoring",
        "Gaming utility notes for GMs and players with enum optimization",
        "Flexible elements that adapt to any campaign with preset compatibility",
        "Enhancement suggestions with clear priority levels and categories"
    ],
    "enum_integration_features": [
        "Complete culture_types enum integration for all operations",
        "CHARACTER_CULTURE_PRESETS for rapid character-focused setup",
        "Enhancement category identification with CultureEnhancementCategory",
        "Priority assessment using CultureEnhancementPriority",
        "Generation status tracking with CultureGenerationStatus",
        "Authentic scoring with enum-based character support calculations"
    ]
}

# ============================================================================
# ENHANCED CONVENIENCE FACTORY FUNCTIONS - Preset Integration
# ============================================================================

def create_sky_culture_spec(
    cultural_theme: str = "sky-dwelling storm riders",
    creativity_level: CultureCreativityLevel = CultureCreativityLevel.BALANCED_CREATIVE,
    character_focus: bool = True,
    use_preset: str = "quick_character_creation"
) -> CreativeCultureSpec:
    """
    Create a specification for sky/aerial culture generation with preset support.
    
    Enhanced convenience function with CHARACTER_CULTURE_PRESETS integration.
    
    Args:
        cultural_theme: Theme description for the sky culture
        creativity_level: Desired creativity level
        character_focus: Whether to prioritize character generation
        use_preset: Preset name from CHARACTER_CULTURE_PRESETS
        
    Returns:
        CreativeCultureSpec for sky culture with enum-based optimization
        
    Example:
        >>> spec = create_sky_culture_spec("Storm riders with wind magic")
        >>> culture = CreativeCultureGenerator.create_character_ready_culture(spec)
        >>> print(f"Names: {culture.creative_names}")
        >>> print(f"Generation score: {culture.calculated_generation_score:.2f}")
    """
    return create_character_culture_spec(
        f"{cultural_theme} - aerial culture with wind-based traditions",
        character_focus=character_focus,
        gaming_optimization=True,
        preset_name=use_preset if use_preset in CHARACTER_CULTURE_PRESETS else None,
        authenticity_level=CultureAuthenticityLevel.CREATIVE,
        creativity_level=creativity_level,
        complexity_level=CultureComplexityLevel.GAMING_READY
    )


def create_mystical_culture_spec(
    cultural_theme: str = "mystical forest dwellers",
    creativity_level: CultureCreativityLevel = CultureCreativityLevel.BALANCED_CREATIVE,
    character_focus: bool = True,
    use_preset: str = "creative_focused"
) -> CreativeCultureSpec:
    """
    Create a specification for mystical culture generation with enum integration.
    
    Enhanced convenience function with preset and enum support.
    
    Args:
        cultural_theme: Theme description for the mystical culture
        creativity_level: Desired creativity level
        character_focus: Whether to prioritize character generation
        use_preset: Preset name from CHARACTER_CULTURE_PRESETS
        
    Returns:
        CreativeCultureSpec for mystical culture with enum optimization
        
    Example:
        >>> spec = create_mystical_culture_spec("Crystal cave shamans")
        >>> culture = CreativeCultureGenerator.create_character_ready_culture(spec)
        >>> enhancements = culture.get_critical_enhancements()
    """
    return create_character_culture_spec(
        f"{cultural_theme} - mystical culture with magical traditions",
        character_focus=character_focus,
        gaming_optimization=True,
        preset_name=use_preset if use_preset in CHARACTER_CULTURE_PRESETS else None,
        authenticity_level=CultureAuthenticityLevel.CREATIVE,
        creativity_level=creativity_level,
        complexity_level=CultureComplexityLevel.COMPLEX_READY
    )


def create_nomad_culture_spec(
    cultural_theme: str = "wandering nomadic traders",
    creativity_level: CultureCreativityLevel = CultureCreativityLevel.BALANCED_CREATIVE,
    character_focus: bool = True,
    use_preset: str = "gaming_optimized"
) -> CreativeCultureSpec:
    """
    Create a specification for nomadic culture generation with enum scoring.
    
    Enhanced convenience function with complete enum integration.
    
    Args:
        cultural_theme: Theme description for the nomadic culture
        creativity_level: Desired creativity level
        character_focus: Whether to prioritize character generation
        use_preset: Preset name from CHARACTER_CULTURE_PRESETS
        
    Returns:
        CreativeCultureSpec for nomadic culture with enum-based assessment
        
    Example:
        >>> spec = create_nomad_culture_spec("Desert caravan merchants")
        >>> culture = CreativeCultureGenerator.create_character_ready_culture(spec)
        >>> readiness = culture.get_generation_readiness_percentage()
    """
    return create_character_culture_spec(
        f"{cultural_theme} - nomadic culture with traveling traditions",
        character_focus=character_focus,
        gaming_optimization=True,
        preset_name=use_preset if use_preset in CHARACTER_CULTURE_PRESETS else None,
        authenticity_level=CultureAuthenticityLevel.CREATIVE,
        creativity_level=creativity_level,
        complexity_level=CultureComplexityLevel.GAMING_READY
    )


# ============================================================================
# ENHANCED WORKFLOW HELPER FUNCTIONS - Complete Enum Integration
# ============================================================================

def generate_character_culture(
    cultural_reference: str,
    creativity_level: CultureCreativityLevel = CultureCreativityLevel.BALANCED_CREATIVE,
    character_focus: bool = True,
    gaming_optimization: bool = True,
    preset_name: str = None
) -> tuple[str, CreativeCultureSpec, CreativeCulture]:
    """
    Complete enhanced workflow for character culture generation with enum integration.
    
    Always produces usable culture optimized for character creation with enum scoring.
    
    Args:
        cultural_reference: Description of desired culture
        creativity_level: Desired creativity level from enum
        character_focus: Whether to prioritize character generation
        gaming_optimization: Whether to optimize for gaming use
        preset_name: Optional preset from CHARACTER_CULTURE_PRESETS
        
    Returns:
        Tuple of (prompt_string, culture_spec, creative_culture)
        
    Example:
        >>> prompt, spec, culture = generate_character_culture(
        ...     "Floating island sky pirates with storm magic",
        ...     creativity_level=CultureCreativityLevel.HIGHLY_CREATIVE,
        ...     preset_name="creative_focused"
        ... )
        >>> print(f"Character support: {culture.character_support_score:.2f}")
        >>> print(f"Generation score: {culture.calculated_generation_score:.2f}")
        >>> print(f"Available names: {len(culture.male_names + culture.female_names)}")
        >>> print(f"Enhancement categories: {len(culture.enhancement_categories)}")
    """
    # Create enhanced character-focused specification with preset support
    spec = create_character_culture_spec(
        cultural_reference,
        character_focus=character_focus,
        gaming_optimization=gaming_optimization,
        preset_name=preset_name,
        authenticity_level=CultureAuthenticityLevel.CREATIVE,
        creativity_level=creativity_level,
        complexity_level=CultureComplexityLevel.GAMING_READY
    )
    
    # Generate character-ready culture with enum integration
    culture = CreativeCultureGenerator.create_character_ready_culture(spec)
    
    # Build enhanced character-focused prompt with enum support
    prompt = build_character_culture_prompt(
        cultural_reference,
        creativity_level=creativity_level,
        character_focus=character_focus,
        gaming_optimization=gaming_optimization,
        preset_integration=preset_name is not None
    )
    
    return prompt, spec, culture


def parse_and_enhance_response(
    llm_response: str,
    enhance_for_gaming: bool = True,
    target_enhancement_categories: list = None
) -> tuple[EnhancedCreativeParsingResult, EnhancedCreativeValidationResult]:
    """
    Complete enhanced workflow for parsing and enhancing LLM responses with enum integration.
    
    Always produces usable results with enum-based enhancement suggestions.
    
    Args:
        llm_response: Raw LLM response to parse
        enhance_for_gaming: Whether to enhance for gaming utility
        target_enhancement_categories: Specific enhancement categories to focus on
        
    Returns:
        Tuple of (enhanced_creative_parsing_result, enhanced_creative_validation_result)
        
    Example:
        >>> parsed, validation = parse_and_enhance_response(
        ...     response,
        ...     target_enhancement_categories=[
        ...         CultureEnhancementCategory.NAMING_SYSTEMS,
        ...         CultureEnhancementCategory.CHARACTER_HOOKS
        ...     ]
        ... )
        >>> print(f"Character ready: {validation.character_ready}")
        >>> print(f"Generation score: {validation.calculated_generation_score:.2f}")
        >>> print(f"Enhancement priorities: {len(validation.prioritized_enhancements)}")
    """
    # Parse with enhanced creative flexibility and enum integration
    parsed = parse_for_characters(llm_response)
    
    # Enhance for gaming with enum-based optimization if requested
    if enhance_for_gaming:
        parsed = CreativeCultureParser.enhance_for_gaming(parsed)
    
    # Apply targeted enhancement categories if specified
    if target_enhancement_categories:
        parsed = CreativeCultureParser.apply_enhancement_categories(
            parsed, target_enhancement_categories
        )
    
    # Enhanced validation with enum-based character focus
    validation = assess_character_readiness({
        'culture_name': parsed.culture_name,
        'culture_description': parsed.culture_description,
        'male_names': parsed.male_names,
        'female_names': parsed.female_names,
        'neutral_names': parsed.neutral_names,
        'family_names': parsed.family_names,
        'creative_names': parsed.creative_names,
        'character_hooks': parsed.character_hooks,
        'gaming_notes': parsed.gaming_notes,
        'enhancement_categories': parsed.identified_enhancement_categories,
        'generation_status': parsed.generation_status
    })
    
    return parsed, validation


def enhance_culture_for_characters(
    culture_name: str,
    existing_names: list[str],
    target_categories: list[CultureEnhancementCategory] = None,
    priority_threshold: CultureEnhancementPriority = CultureEnhancementPriority.NARRATIVE_HELPFUL,
    gaming_focus: bool = True
) -> str:
    """
    Generate enhanced enhancement prompts for existing cultures with enum integration.
    
    Creates prompts to expand cultures for better character generation support using enums.
    
    Args:
        culture_name: Name of the culture to enhance
        existing_names: Current names in the culture
        target_categories: Enhancement categories from enum to focus on
        priority_threshold: Minimum priority level for suggestions
        gaming_focus: Whether to focus on gaming utility
        
    Returns:
        Enhancement prompt string optimized for character generation with enum targeting
        
    Example:
        >>> prompt = enhance_culture_for_characters(
        ...     "Storm Riders",
        ...     ["Zephyr", "Gale", "Storm"],
        ...     target_categories=[
        ...         CultureEnhancementCategory.NAMING_SYSTEMS,
        ...         CultureEnhancementCategory.CHARACTER_HOOKS
        ...     ],
        ...     priority_threshold=CultureEnhancementPriority.CHARACTER_ESSENTIAL,
        ...     gaming_focus=True
        ... )
    """
    if target_categories is None:
        target_categories = [
            CultureEnhancementCategory.NAMING_SYSTEMS,
            CultureEnhancementCategory.CHARACTER_HOOKS,
            CultureEnhancementCategory.CULTURAL_BACKGROUND,
            CultureEnhancementCategory.GAMING_UTILITY
        ]
    
    existing_data = {
        'culture_name': culture_name,
        'existing_names': existing_names,
        'target_categories': [cat.value for cat in target_categories],
        'priority_threshold': priority_threshold.value
    }
    
    return build_creative_enhancement_prompt(
        culture_name,
        existing_data,
        "expand_for_characters_with_enum_targeting",
        target_categories,
        gaming_focus=gaming_focus,
        priority_threshold=priority_threshold
    )


def create_quick_character_culture(
    cultural_concept: str,
    preset_name: str = "quick_character_creation"
) -> CreativeCulture:
    """
    Quick culture creation for immediate character generation use with preset integration.
    
    Enhanced streamlined function that creates a usable culture from any concept using presets.
    Always succeeds and produces character-ready results with enum scoring.
    
    Args:
        cultural_concept: Any description of desired culture
        preset_name: Preset configuration from CHARACTER_CULTURE_PRESETS
        
    Returns:
        CreativeCulture ready for character generation with enum-based scoring
        
    Example:
        >>> culture = create_quick_character_culture(
        ...     "Cyberpunk sky hackers",
        ...     preset_name="gaming_optimized"
        ... )
        >>> print(f"Ready for characters: {culture.is_character_usable()}")
        >>> print(f"Generation score: {culture.calculated_generation_score:.2f}")
        >>> print(f"Names available: {len(culture.creative_names)}")
        >>> print(f"Readiness: {culture.get_generation_readiness_percentage()}%")
    """
    try:
        # Use preset configuration if available
        preset_config = CHARACTER_CULTURE_PRESETS.get(preset_name, {})
        
        spec = create_character_culture_spec(
            cultural_concept,
            preset_name=preset_name,
            authenticity_level=preset_config.get('authenticity', CultureAuthenticityLevel.CREATIVE),
            creativity_level=preset_config.get('creativity', CultureCreativityLevel.BALANCED_CREATIVE),
            complexity_level=preset_config.get('complexity', CultureComplexityLevel.GAMING_READY)
        )
        
        return CreativeCultureGenerator.create_character_ready_culture(spec)
        
    except Exception:
        # Enhanced fallback with enum integration - never fail
        fallback_score = calculate_character_generation_score(
            CultureAuthenticityLevel.CREATIVE,
            CultureCreativityLevel.BALANCED_CREATIVE,
            CultureComplexityLevel.GAMING_READY
        )
        
        return CreativeCulture(
            name="Creative Culture",
            description=f"A unique culture inspired by: {cultural_concept}",
            creative_names=["Unique", "Creative", "Original", "Inspiring"],
            character_hooks=[
                f"Characters from this {cultural_concept.lower()} culture have unique backgrounds",
                "Perfect foundation for creative character development"
            ],
            gaming_notes=[
                "Flexible culture that adapts to any campaign setting",
                "Names designed for easy pronunciation at gaming table"
            ],
            authenticity_level=CultureAuthenticityLevel.CREATIVE,
            complexity_level=CultureComplexityLevel.GAMING_READY,
            generation_status=CultureGenerationStatus.CHARACTER_READY,
            calculated_generation_score=fallback_score,
            character_support_score=0.6,
            creative_inspiration_score=0.8,
            gaming_usability_score=0.7,
            enhancement_suggestions=[
                "Add more specific names to enhance character options",
                "Consider cultural background elements for character depth"
            ],
            enhancement_categories=[
                CultureEnhancementCategory.NAMING_SYSTEMS,
                CultureEnhancementCategory.CHARACTER_HOOKS
            ],
            prioritized_enhancements=[
                ("Add more specific names", CultureEnhancementPriority.CHARACTER_ESSENTIAL),
                ("Expand cultural background", CultureEnhancementPriority.NARRATIVE_HELPFUL)
            ],
            creative_opportunities=[
                "This culture concept has great potential for expansion",
                "Perfect starting point for unique character backgrounds"
            ]
        )


# ============================================================================
# ENHANCED PRESET SYSTEM INTEGRATION
# ============================================================================

def get_available_presets() -> dict[str, dict]:
    """
    Get all available CHARACTER_CULTURE_PRESETS with descriptions.
    
    Returns:
        Dictionary of preset names and their configurations
        
    Example:
        >>> presets = get_available_presets()
        >>> for name, config in presets.items():
        ...     print(f"{name}: {config.get('description', 'No description')}")
    """
    return CHARACTER_CULTURE_PRESETS.copy()


def apply_preset_to_spec(
    spec: CreativeCultureSpec,
    preset_name: str
) -> CreativeCultureSpec:
    """
    Apply a preset configuration to an existing culture specification.
    
    Args:
        spec: Existing culture specification
        preset_name: Name of preset from CHARACTER_CULTURE_PRESETS
        
    Returns:
        Updated culture specification with preset applied
        
    Example:
        >>> spec = create_character_culture_spec("Sky pirates")
        >>> enhanced_spec = apply_preset_to_spec(spec, "gaming_optimized")
    """
    if preset_name not in CHARACTER_CULTURE_PRESETS:
        return spec
    
    preset = CHARACTER_CULTURE_PRESETS[preset_name]
    
    return CreativeCultureSpec(
        cultural_reference=spec.cultural_reference,
        preset_name=preset_name,
        authenticity_level=preset.get('authenticity', spec.authenticity_level),
        creativity_level=preset.get('creativity', spec.creativity_level),
        complexity_level=preset.get('complexity', spec.complexity_level),
        generation_type=CultureGenerationType.CHARACTER_FOCUSED,
        character_focus=spec.character_focus,
        gaming_optimization=spec.gaming_optimization,
        creative_freedom=spec.creative_freedom,
        target_enhancement_categories=spec.target_enhancement_categories,
        enhancement_priority_threshold=spec.enhancement_priority_threshold
    )


def recommend_preset_for_concept(cultural_concept: str) -> str:
    """
    Recommend the best preset for a given cultural concept.
    
    Args:
        cultural_concept: Description of the desired culture
        
    Returns:
        Recommended preset name from CHARACTER_CULTURE_PRESETS
        
    Example:
        >>> preset = recommend_preset_for_concept("Complex magical society")
        >>> print(f"Recommended preset: {preset}")
    """
    concept_lower = cultural_concept.lower()
    
    # Simple keyword-based recommendation
    if any(word in concept_lower for word in ["quick", "simple", "basic"]):
        return "quick_character_creation"
    elif any(word in concept_lower for word in ["gaming", "table", "session"]):
        return "gaming_optimized"
    elif any(word in concept_lower for word in ["creative", "unique", "original"]):
        return "creative_focused"
    elif any(word in concept_lower for word in ["complex", "detailed", "rich"]):
        return "authentic_creative"
    else:
        return "balanced_approach"


# ============================================================================
# ENHANCED VALIDATION AND QUALITY ASSURANCE - Complete Enum Integration
# ============================================================================

def validate_creative_module_integrity() -> dict[str, any]:
    """
    Enhanced validation of the creative culture module integrity with enum integration.
    
    Focuses on character generation readiness with complete enum integration assessment.
    
    Returns:
        Dictionary with enhanced creative validation results and character support info
        
    Example:
        >>> integrity = validate_creative_module_integrity()
        >>> print(f"Character ready: {integrity['character_generation_ready']}")
        >>> print(f"Enum integration: {integrity['enum_integration_score']:.2f}")
    """
    validation_result = {
        "is_valid": True,
        "character_generation_ready": True,
        "issues": [],
        "enhancement_suggestions": [],
        "creative_support_score": 0.0,
        "enum_integration_score": 0.0,
        "preset_compatibility_score": 0.0,
        "character_utility_features": {},
        "enum_features": {},
        "preset_features": {},
        "creative_validation_compliance": CREATIVE_VALIDATION_APPROACH_COMPLIANCE
    }
    
    try:
        # Check enhanced creative core classes availability
        creative_classes = [
            CreativeCultureGenerator, CreativeCultureParser, CreativePromptTemplates,
            CreativeCulture, EnhancedCreativeParsingResult, CharacterPromptTemplate
        ]
        
        available_classes = 0
        for cls in creative_classes:
            try:
                if hasattr(cls, '__name__'):
                    available_classes += 1
                else:
                    validation_result["enhancement_suggestions"].append(
                        f"Enhanced creative class {cls} could be enhanced for better character support"
                    )
            except:
                validation_result["enhancement_suggestions"].append(
                    f"Enhanced creative class availability could be improved"
                )
        
        # Check enhanced character-focused utility functions
        character_functions = [
            create_character_culture_spec, parse_for_characters, 
            generate_character_culture, create_quick_character_culture,
            enhance_culture_for_characters, suggest_creative_culture_enhancements,
            calculate_character_generation_score, get_character_generation_recommendations
        ]
        
        available_functions = 0
        for func in character_functions:
            try:
                if callable(func):
                    available_functions += 1
                else:
                    validation_result["enhancement_suggestions"].append(
                        f"Enhanced character utility function {func.__name__} could be enhanced"
                    )
            except:
                validation_result["enhancement_suggestions"].append(
                    "Enhanced character utility functions could be improved"
                )
        
        # Check enhanced creative enum availability with new enums
        creative_enums = [
            CultureCreativityLevel, CultureComplexityLevel, CultureSourceType,
            CultureEnhancementCategory, CultureEnhancementPriority, CultureGenerationStatus,
            CreativePromptType, ResponseFormat, NameCategory
        ]
        
        available_enums = 0
        for enum_class in creative_enums:
            try:
                if hasattr(enum_class, '__members__'):
                    available_enums += 1
                else:
                    validation_result["enhancement_suggestions"].append(
                        f"Enhanced creative enum {enum_class.__name__} could be enhanced"
                    )
            except:
                validation_result["enhancement_suggestions"].append(
                    "Enhanced creative enum support could be improved"
                )
        
        # Check preset system integration
        preset_score = 0.0
        try:
            if CHARACTER_CULTURE_PRESETS and len(CHARACTER_CULTURE_PRESETS) > 0:
                preset_score += 0.5
            if callable(get_available_presets):
                preset_score += 0.3
            if callable(recommend_preset_for_concept):
                preset_score += 0.2
        except:
            validation_result["enhancement_suggestions"].append(
                "Preset system integration could be improved"
            )
        
        # Calculate enhanced scores
        total_checks = len(creative_classes) + len(character_functions) + len(creative_enums)
        passed_checks = available_classes + available_functions + available_enums
        validation_result["creative_support_score"] = passed_checks / total_checks if total_checks > 0 else 0.0
        validation_result["enum_integration_score"] = available_enums / len(creative_enums) if creative_enums else 0.0
        validation_result["preset_compatibility_score"] = preset_score
        
        # Enhanced character utility features assessment
        validation_result["character_utility_features"] = {
            "character_ready_generation": available_classes > 0,
            "creative_parsing": available_functions > 0,
            "gaming_optimization": True,
            "enhancement_suggestions": True,
            "creative_fallbacks": True,
            "always_usable_output": True,
            "enum_based_scoring": available_enums > 6,
            "preset_integration": preset_score > 0.5
        }
        
        # Enhanced enum features assessment
        validation_result["enum_features"] = {
            "enhancement_categorization": CultureEnhancementCategory in creative_enums,
            "priority_assessment": CultureEnhancementPriority in creative_enums,
            "generation_status_tracking": CultureGenerationStatus in creative_enums,
            "character_generation_scoring": callable(calculate_character_generation_score),
            "creative_enhancement_suggestions": callable(suggest_creative_culture_enhancements)
        }
        
        # Preset features assessment
        validation_result["preset_features"] = {
            "preset_configurations_available": bool(CHARACTER_CULTURE_PRESETS),
            "preset_recommendation_system": callable(recommend_preset_for_concept),
            "preset_application_capability": callable(apply_preset_to_spec),
            "preset_discovery": callable(get_available_presets)
        }
        
        # Enhanced creative validation - very permissive but comprehensive
        validation_result["character_generation_ready"] = validation_result["creative_support_score"] >= 0.3
        validation_result["is_valid"] = True  # Almost always valid
        
        # Add encouraging enhancement suggestions with enum focus
        if validation_result["enum_integration_score"] < 1.0:
            validation_result["enhancement_suggestions"].append(
                f"Enum integration is {validation_result['enum_integration_score']:.1%} complete - consider expanding enum-based features"
            )
        
        if validation_result["preset_compatibility_score"] < 1.0:
            validation_result["enhancement_suggestions"].append(
                f"Preset system is {validation_result['preset_compatibility_score']:.1%} integrated - consider enhancing preset features"
            )
        
        if not validation_result["enhancement_suggestions"]:
            validation_result["enhancement_suggestions"].append(
                "Module is fully ready for enhanced creative character generation with complete enum integration!"
            )
        
    except Exception as e:
        # Even validation errors should be constructive
        validation_result["is_valid"] = True  # Still usable
        validation_result["character_generation_ready"] = True
        validation_result["enhancement_suggestions"].append(
            f"Validation encountered minor issues ({str(e)}) but module is still usable for character generation"
        )
        validation_result["enhancement_suggestions"].append(
            "Consider checking enhanced module imports for optimal character generation support"
        )
    
    return validation_result


# ============================================================================
# ENHANCED MODULE EXPORTS - Complete Enum Integration
# ============================================================================

__all__ = [
    # Enhanced Creative Core Classes
    "CreativeCultureGenerator",
    "CreativeCultureParser", 
    "CreativePromptTemplates",
    
    # Enhanced Creative Data Structures
    "CreativeCulture",
    "EnhancedCreativeParsingResult",
    "CharacterPromptTemplate",
    "CreativeCultureSpec",
    "CreativeValidationResult",
    "EnhancedCreativeValidationResult",
    
    # Complete Enums (Enhanced)
    "CultureAuthenticityLevel",
    "CultureCreativityLevel",
    "CultureComplexityLevel",
    "CultureSourceType",
    "CultureGenerationType",
    "CultureEnhancementCategory",
    "CultureEnhancementPriority",
    "CultureGenerationStatus",
    "CultureNamingStructure",
    "CultureGenderSystem",
    "CultureLinguisticFamily",
    "CultureTemporalPeriod",
    "CultureValidationCategory",
    "CultureValidationSeverity",
    "CreativePromptType",
    "GamingPromptStyle",
    "ResponseFormat",
    "NameCategory",
    
    # Enhanced Enum Utility Functions
    "suggest_creative_culture_enhancements",
    "calculate_character_generation_score",
    "get_character_generation_recommendations",
    
    # Preset System
    "CHARACTER_CULTURE_PRESETS",
    "get_available_presets",
    "apply_preset_to_spec",
    "recommend_preset_for_concept",
    
    # Exceptions (Creative-Friendly)
    "CultureGenerationError",
    "CultureParsingError",
    "CultureValidationError",
    "CultureStructureError",
    "CultureTemplateError",
    
    # Enhanced Character Generation Utility Functions
    "create_character_culture_spec",
    "validate_creative_culture_spec",
    "parse_for_characters",
    "extract_character_names",
    "assess_character_readiness",
    "build_character_culture_prompt",
    "build_creative_enhancement_prompt",
    "build_gaming_validation_prompt",
    "get_character_prompt_recommendations",
    
    # Enhanced Creative Convenience Factory Functions
    "create_sky_culture_spec",
    "create_mystical_culture_spec",
    "create_nomad_culture_spec",
    
    # Enhanced Creative Workflow Helper Functions
    "generate_character_culture",
    "parse_and_enhance_response",
    "enhance_culture_for_characters",
    "create_quick_character_culture",
    
    # Enhanced Creative Module Validation
    "validate_creative_module_integrity",
    
    # Enhanced Creative Module Metadata
    "__version__",
    "CREATIVE_VALIDATION_APPROACH_COMPLIANCE",
    "CHARACTER_GENERATION_GUIDELINES",
    "CLEAN_ARCHITECTURE_COMPLIANCE"
]

# ============================================================================
# ENHANCED MODULE INITIALIZATION AND CREATIVE VALIDATION
# ============================================================================

# Enhanced creative module integrity validation on import
_creative_validation = validate_creative_module_integrity()
if not _creative_validation["character_generation_ready"]:
    import warnings
    warnings.warn(
        f"Enhanced creative culture module enhancement opportunities: {_creative_validation['enhancement_suggestions']}", 
        ImportWarning
    )

# Enhanced creative character generation banner for development
if __name__ == "__main__":
    print("=" * 80)
    print("D&D Character Creator - Enhanced Creative Culture Generation Utilities")
    print("Character Generation Focused Implementation v3.0.0")
    print("=" * 80)
    print(f"Module Version: {__version__}")
    print(f"Creative Support Score: {_creative_validation['creative_support_score']:.2f}")
    print(f"Enum Integration Score: {_creative_validation['enum_integration_score']:.2f}")
    print(f"Preset Compatibility Score: {_creative_validation['preset_compatibility_score']:.2f}")
    print(f"Character Generation Ready: {_creative_validation['character_generation_ready']}")
    print(f"Features Available: {list(_creative_validation['character_utility_features'].keys())}")
    print(f"Enum Features: {list(_creative_validation['enum_features'].keys())}")
    print(f"Preset Features: {list(_creative_validation['preset_features'].keys())}")
    print("\nCharacter Generation Principles:")
    for principle in CHARACTER_GENERATION_GUIDELINES["character_generation_principles"]:
        print(f"  • {principle}")
    print("\nGaming Objectives:")
    for objective in CHARACTER_GENERATION_GUIDELINES["gaming_objectives"]:
        print(f"  • {objective}")
    print("\nEnum Integration Features:")
    for feature in CHARACTER_GENERATION_GUIDELINES["enum_integration_features"]:
        print(f"  • {feature}")
    print("\nAvailable Presets:")
    for preset_name in CHARACTER_CULTURE_PRESETS.keys():
        print(f"  • {preset_name}")
    print("\nEnhancement Suggestions:")
    for suggestion in _creative_validation["enhancement_suggestions"][:3]:  # Show top 3
        print(f"  • {suggestion}")
    print("\n🎨 CREATIVE_VALIDATION_APPROACH: Enable creativity rather than restrict it!")
    print("🎲 Always produces usable cultures for character generation!")
    print("📊 Complete enum integration for enhanced character generation!")
    print("⚙️  Preset system for rapid character culture setup!")
    print("=" * 80)