"""
Core enumerations for the D&D Creative Content Framework.

This module provides all enumerated types used throughout the system,
organized by their primary purpose and domain.
"""

# Application enums
from .environment import Environment
from .application import (
    LogLevel,
    SecurityAlgorithm,
    CacheBackend,
    DatabaseType
)

# Content type enums
from .content_types import (
    ContentType,
    GenerationMethod,
    ValidationSeverity,
    BalanceLevel,
    ContentRarity,
    ContentSource,
    QualityLevel,
    ComplexityLevel,
    ThemeCategory,
    PowerTier,
    ContentStatus,
    # Content type groupings
    CHARACTER_OPTIONS,
    ITEM_TYPES,
    MECHANICAL_CONTENT,
    NARRATIVE_CONTENT,
    # Helper functions
    get_content_types_by_category,
    get_compatible_themes
)

# D&D mechanics enums
from .game_mechanics import (
    AbilityScore,
    Skill,
    DamageType,
    CreatureSize,
    SpellSchool,
    ArmorType,
    WeaponProperty,
    WeaponType,
    EquipmentCategory,
    Condition,
    SpellLevel,
    CastingTime,
    SpellRange,
    SpellDuration,
    SpellComponent,
    ProficiencyLevel,
    Currency,
    LanguageType,
    SenseType
)

# Generation-specific enums
from .generation import (
    LLMProvider,
    TemplateType,
    GenerationComplexity,
    IterationMethod,
    GenerationPriority,
    OptimizationStrategy
)

# Validation and analysis enums
from .validation import (
    ValidationType,
    ValidationStatus,
    BalanceCategory,
    RuleCompliance,
    ComplianceLevel,
    AnalysisType
)

# Character creation enums
from .character import (
    FeatCategory,
    SpeciesSize,
    BackgroundType,
    ClassResource,
    SubclassType,
    SpellcastingType,
    AlignmentAxis,
    AlignmentTendency
)

# Export all public symbols
__all__ = [
    # Application
    'Environment',
    'LogLevel',
    'SecurityAlgorithm', 
    'CacheBackend',
    'DatabaseType',
    
    # Content Types
    'ContentType',
    'GenerationMethod',
    'ValidationSeverity',
    'BalanceLevel',
    'ContentRarity',
    'ContentSource',
    'QualityLevel',
    'ComplexityLevel',
    'ThemeCategory',
    'PowerTier',
    'ContentStatus',
    
    # Content type collections
    'CHARACTER_OPTIONS',
    'ITEM_TYPES',
    'MECHANICAL_CONTENT',
    'NARRATIVE_CONTENT',
    
    # Helper functions
    'get_content_types_by_category',
    'get_compatible_themes',
    
    # Game Mechanics
    'AbilityScore',
    'Skill',
    'DamageType',
    'CreatureSize',
    'SpellSchool',
    'ArmorType',
    'WeaponProperty',
    'WeaponType',
    'EquipmentCategory',
    'Condition',
    'SpellLevel',
    'CastingTime',
    'SpellRange',
    'SpellDuration',
    'SpellComponent',
    'ProficiencyLevel',
    'Currency',
    'LanguageType',
    'SenseType',
    
    # Generation
    'LLMProvider',
    'TemplateType',
    'GenerationComplexity',
    'IterationMethod',
    'GenerationPriority',
    'OptimizationStrategy',
    
    # Validation
    'ValidationType',
    'ValidationStatus',
    'BalanceCategory',
    'RuleCompliance',
    'ComplianceLevel',
    'AnalysisType',
    
    # Character Creation
    'FeatCategory',
    'SpeciesSize',
    'BackgroundType',
    'ClassResource',
    'SubclassType',
    'SpellcastingType',
    'AlignmentAxis',
    'AlignmentTendency'
]

# Comprehensive Enum Registry for dynamic loading and introspection
ENUM_REGISTRY = {
    # Application
    'environment': Environment,
    'log_level': LogLevel,
    'security_algorithm': SecurityAlgorithm,
    'cache_backend': CacheBackend,
    'database_type': DatabaseType,
    
    # Content Types
    'content_type': ContentType,
    'generation_method': GenerationMethod,
    'validation_severity': ValidationSeverity,
    'balance_level': BalanceLevel,
    'content_rarity': ContentRarity,
    'content_source': ContentSource,
    'quality_level': QualityLevel,
    'complexity_level': ComplexityLevel,
    'theme_category': ThemeCategory,
    'power_tier': PowerTier,
    'content_status': ContentStatus,
    
    # Game Mechanics
    'ability_score': AbilityScore,
    'skill': Skill,
    'damage_type': DamageType,
    'creature_size': CreatureSize,
    'spell_school': SpellSchool,
    'armor_type': ArmorType,
    'weapon_property': WeaponProperty,
    'weapon_type': WeaponType,
    'equipment_category': EquipmentCategory,
    'condition': Condition,
    'spell_level': SpellLevel,
    'casting_time': CastingTime,
    'spell_range': SpellRange,
    'spell_duration': SpellDuration,
    'spell_component': SpellComponent,
    'proficiency_level': ProficiencyLevel,
    'currency': Currency,
    'language_type': LanguageType,
    'sense_type': SenseType,
    
    # Generation
    'llm_provider': LLMProvider,
    'template_type': TemplateType,
    'generation_complexity': GenerationComplexity,
    'iteration_method': IterationMethod,
    'generation_priority': GenerationPriority,
    'optimization_strategy': OptimizationStrategy,
    
    # Validation
    'validation_type': ValidationType,
    'validation_status': ValidationStatus,
    'balance_category': BalanceCategory,
    'rule_compliance': RuleCompliance,
    'compliance_level': ComplianceLevel,
    'analysis_type': AnalysisType,
    
    # Character Creation
    'feat_category': FeatCategory,
    'species_size': SpeciesSize,
    'background_type': BackgroundType,
    'class_resource': ClassResource,
    'subclass_type': SubclassType,
    'spellcasting_type': SpellcastingType,
    'alignment_axis': AlignmentAxis,
    'alignment_tendency': AlignmentTendency
}


def get_enum_class(enum_type: str):
    """
    Get enum class by type name.
    
    Args:
        enum_type: String identifier for the enum type
        
    Returns:
        Enum class or None if not found
        
    Example:
        >>> content_enum = get_enum_class('content_type')
        >>> print(list(content_enum))
    """
    return ENUM_REGISTRY.get(enum_type.lower())


def list_available_enums() -> list[str]:
    """
    Get list of all available enum types.
    
    Returns:
        List of enum type names
        
    Example:
        >>> enums = list_available_enums()
        >>> print(f"Available enums: {len(enums)}")
    """
    return list(ENUM_REGISTRY.keys())


def get_enums_by_category() -> dict[str, list[str]]:
    """
    Get enums organized by their functional category.
    
    Returns:
        Dictionary of categories with their enum types
        
    Example:
        >>> categories = get_enums_by_category()
        >>> content_enums = categories['content_types']
    """
    return {
        "application": [
            "environment", "log_level", "security_algorithm", 
            "cache_backend", "database_type"
        ],
        "content_types": [
            "content_type", "generation_method", "validation_severity", "balance_level",
            "content_rarity", "content_source", "quality_level", "complexity_level",
            "theme_category", "power_tier", "content_status"
        ],
        "game_mechanics": [
            "ability_score", "skill", "damage_type", "creature_size", "spell_school",
            "armor_type", "weapon_property", "weapon_type", "equipment_category",
            "condition", "spell_level", "casting_time", "spell_range", "spell_duration",
            "spell_component", "proficiency_level", "currency", "language_type", "sense_type"
        ],
        "generation": [
            "llm_provider", "template_type", "generation_complexity", "iteration_method",
            "generation_priority", "optimization_strategy"
        ],
        "validation": [
            "validation_type", "validation_status", "balance_category", "rule_compliance",
            "compliance_level", "analysis_type"
        ],
        "character_creation": [
            "feat_category", "species_size", "background_type", "class_resource",
            "subclass_type", "spellcasting_type", "alignment_axis", "alignment_tendency"
        ]
    }


def get_enum_by_name(enum_name: str, value: str):
    """
    Get specific enum value by enum name and value.
    
    Args:
        enum_name: Name of the enum type
        value: String value to look up
        
    Returns:
        Enum value or None if not found
        
    Example:
        >>> species_size = get_enum_by_name('creature_size', 'medium')
        >>> print(species_size.name)
    """
    enum_class = get_enum_class(enum_name)
    if enum_class:
        try:
            return enum_class(value.lower())
        except ValueError:
            return None
    return None


def validate_enum_value(enum_name: str, value: str) -> bool:
    """
    Validate that a value is valid for a given enum.
    
    Args:
        enum_name: Name of the enum type
        value: Value to validate
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> is_valid = validate_enum_value('content_type', 'species')
        >>> print(f"Valid: {is_valid}")
    """
    return get_enum_by_name(enum_name, value) is not None


def get_enum_values(enum_name: str) -> list[str]:
    """
    Get all possible values for an enum.
    
    Args:
        enum_name: Name of the enum type
        
    Returns:
        List of enum values or empty list if enum not found
        
    Example:
        >>> content_types = get_enum_values('content_type')
        >>> print(f"Content types: {content_types}")
    """
    enum_class = get_enum_class(enum_name)
    if enum_class:
        return [e.value for e in enum_class]
    return []


def search_enums(search_term: str) -> dict[str, list[str]]:
    """
    Search for enums containing a specific term.
    
    Args:
        search_term: Term to search for in enum names or values
        
    Returns:
        Dictionary mapping enum names to matching values
        
    Example:
        >>> results = search_enums('spell')
        >>> print(f"Found enums with 'spell': {list(results.keys())}")
    """
    results = {}
    search_lower = search_term.lower()
    
    for enum_name, enum_class in ENUM_REGISTRY.items():
        # Check if enum name contains search term
        if search_lower in enum_name:
            results[enum_name] = [e.value for e in enum_class]
            continue
            
        # Check if any enum values contain search term
        matching_values = [
            e.value for e in enum_class 
            if search_lower in e.value.lower()
        ]
        
        if matching_values:
            results[enum_name] = matching_values
    
    return results


def get_related_enums(content_type: str) -> dict[str, list]:
    """
    Get enums that are commonly used with a specific content type.
    
    Args:
        content_type: The content type to find related enums for
        
    Returns:
        Dictionary of related enum categories and their values
        
    Example:
        >>> related = get_related_enums('spell')
        >>> print(f"Spell-related enums: {list(related.keys())}")
    """
    content_type_lower = content_type.lower()
    
    # Define relationships between content types and relevant enums
    relationships = {
        'spell': [
            'spell_school', 'spell_level', 'casting_time', 'spell_range',
            'spell_duration', 'spell_component', 'damage_type'
        ],
        'species': [
            'creature_size', 'ability_score', 'skill', 'language_type',
            'sense_type', 'damage_type'
        ],
        'character_class': [
            'ability_score', 'skill', 'class_resource', 'spellcasting_type',
            'proficiency_level'
        ],
        'equipment': [
            'equipment_category', 'weapon_type', 'armor_type', 'weapon_property',
            'damage_type', 'currency'
        ],
        'feat': [
            'feat_category', 'ability_score', 'skill', 'proficiency_level'
        ],
        'background': [
            'background_type', 'skill', 'language_type', 'equipment_category'
        ]
    }
    
    related_enum_names = relationships.get(content_type_lower, [])
    
    result = {}
    for enum_name in related_enum_names:
        enum_class = get_enum_class(enum_name)
        if enum_class:
            result[enum_name] = list(enum_class)
    
    return result


def get_application_enums() -> dict[str, type]:
    """
    Get all application-level enums.
    
    Returns:
        Dictionary of application enum names to enum classes
    """
    app_categories = get_enums_by_category()["application"]
    return {name: ENUM_REGISTRY[name] for name in app_categories}


def get_domain_enums() -> dict[str, type]:
    """
    Get all domain-specific enums (non-application).
    
    Returns:
        Dictionary of domain enum names to enum classes
    """
    categories = get_enums_by_category()
    domain_enums = {}
    
    for category, enum_names in categories.items():
        if category != "application":
            for enum_name in enum_names:
                domain_enums[enum_name] = ENUM_REGISTRY[enum_name]
    
    return domain_enums


def validate_enum_relationships() -> list[str]:
    """
    Validate that all enum relationships are properly defined.
    
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Check that all enums in registry are properly imported
    for enum_name, enum_class in ENUM_REGISTRY.items():
        if enum_class is None:
            errors.append(f"Enum '{enum_name}' is None in registry")
            continue
            
        # Check that enum has expected properties
        if not hasattr(enum_class, '__members__'):
            errors.append(f"'{enum_name}' is not a valid enum class")
            
        # Check that enum has at least one member
        if not list(enum_class):
            errors.append(f"Enum '{enum_name}' has no members")
    
    # Check categories contain valid enums
    categories = get_enums_by_category()
    for category, enum_names in categories.items():
        for enum_name in enum_names:
            if enum_name not in ENUM_REGISTRY:
                errors.append(f"Category '{category}' references unknown enum '{enum_name}'")
    
    return errors


# Module metadata
__version__ = '1.1.0'
__description__ = 'Core enumerations for D&D Creative Content Framework'

# Configuration
ENABLE_ENUM_CACHING = True
STRICT_VALIDATION = True

# Validation on import
_validation_errors = validate_enum_relationships()
if _validation_errors and STRICT_VALIDATION:
    import warnings
    warnings.warn(f"Enum validation errors: {_validation_errors}")

# Usage examples in docstring
"""
Usage Examples:

1. Basic enum access:
   >>> from core.enums import ContentType, ValidationSeverity
   >>> print(ContentType.SPECIES.value)
   
2. Dynamic enum loading:
   >>> content_enum = get_enum_class('content_type')
   >>> all_types = list(content_enum)
   
3. Validation:
   >>> is_valid = validate_enum_value('balance_level', 'balanced')
   
4. Search functionality:
   >>> spell_enums = search_enums('spell')
   
5. Related enums:
   >>> spell_related = get_related_enums('spell')
   
6. Category browsing:
   >>> categories = get_enums_by_category()
   >>> game_mechanics = categories['game_mechanics']
   
7. Application vs Domain enums:
   >>> app_enums = get_application_enums()
   >>> domain_enums = get_domain_enums()
"""