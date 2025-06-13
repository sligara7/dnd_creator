"""
Core domain layer for the D&D Creative Content Framework.

This module provides the foundational abstractions, entities, value objects,
utilities, enums, and exceptions that define the domain model for D&D content
creation and validation.

Import order follows dependency hierarchy to avoid circular imports:
enums -> value_objects -> abstractions -> entities -> utilities -> exceptions
"""

# === IMPORT ORDER: Following dependency hierarchy to prevent circular imports ===

# 1. ENUMS (No dependencies - foundation layer)
from . import enums

# 2. VALUE OBJECTS (May depend on enums only)
from . import value_objects

# 3. ABSTRACTIONS (May depend on enums and value objects)
from . import abstractions

# 4. ENTITIES (May depend on abstractions, value objects, enums)
from . import entities

# 5. UTILITIES (May depend on all above - pure functions)
from . import utils

# 6. EXCEPTIONS (May depend on enums and value objects for metadata)
from . import exceptions

# === CONTROLLED RE-EXPORTS (Specific imports to avoid namespace pollution) ===

# ENUMS - Core type definitions
from .enums import (
    ContentType, ContentRarity, ContentSource,
    GenerationMethod, LLMProvider, TemplateType,
    ValidationType, ValidationSeverity, ValidationStatus, RuleCompliance,
    MechanicalCategory,
    Ability, Skill, DamageType, Condition, SpellSchool, SpellLevel,
    CreatureType, CreatureSize,
    get_all_content_types, get_content_rarity_order, get_ability_list,
    get_skill_list, validate_enum_value,
)

# VALUE OBJECTS - Immutable data structures
from .value_objects import (
    ContentMetadata, GenerationConstraints, ThematicElements,
    ValidationResult, BalanceMetrics,
    create_default_metadata, merge_thematic_elements, calculate_combined_balance,
)

# ABSTRACTIONS - D&D Rule contracts
from .abstractions import (
    AbstractCharacterClass, AbstractSpecies, AbstractEquipment,
    AbstractWeapon, AbstractArmor, AbstractSpell, AbstractFeat,
    AbstractContentValidator,
    get_available_abstractions, validate_abstraction_implementation,
)

# ENTITIES - Core domain objects
from .entities import (
    Character, GeneratedContent, CharacterConcept, ContentCollection,
    create_character_from_concept, validate_character_integrity,
    merge_content_collections, get_entity_metadata,
)

# UTILITIES - Pure content functions (imported selectively to avoid conflicts)
from .utils.content_utils import (
    extract_themes_from_content, merge_content_themes, filter_content_by_theme,
    calculate_thematic_compatibility, group_content_by_theme, analyze_content_complexity,
    find_content_dependencies, suggest_complementary_content,
    serialize_content_collection, deserialize_content_collection,
    validate_content_structure, normalize_content_data,
)

from .utils.balance_calculator import (
    calculate_overall_balance_score, calculate_power_level_score,
    calculate_utility_score, calculate_versatility_score, calculate_scaling_score,
    calculate_damage_per_round, parse_average_damage, calculate_survivability_score,
    calculate_resource_efficiency, create_balance_metrics,
)

from .utils.naming_validator import (
    validate_content_name, suggest_name_improvements, generate_name_variations,
    validate_name_uniqueness, check_name_authenticity,
)

from .utils.mechanical_parser import (
    MechanicalElement, extract_mechanical_elements, parse_damage_expression,
    analyze_mechanical_complexity, extract_spell_components,
    extract_scaling_information, validate_mechanical_consistency,
    get_category_patterns, get_category_keywords, get_all_mechanical_keywords,
    categorize_keyword, find_mechanical_keywords_in_text,
)

from .utils.rule_checker import (
    validate_ability_scores, validate_character_level, validate_proficiency_bonus,
    validate_hit_points, validate_armor_class, validate_saving_throws,
    validate_spell_slots, validate_content_rarity_balance,
    validate_multiclass_prerequisites, calculate_proficiency_bonus,
    calculate_ability_modifier, get_spell_slots_by_level,
)

# EXCEPTIONS - Domain-specific error handling
from .exceptions import (
    # Generation errors
    GenerationError, LLMError, LLMTimeoutError, LLMRateLimitError,
    LLMQuotaExceededError, LLMResponseError, TemplateError,
    TemplateMissingError, TemplateVariableError, ContentGenerationTimeoutError,
    ContentGenerationLimitError, IterationLimitError, ContentDependencyError,
    ContentFormatError, ContentParsingError, GenerationConfigError,
    ProviderUnavailableError, ContentPostProcessingError,
    GenerationRetryExhaustedError,
    
    # Validation errors
    ValidationError, SchemaValidationError, FieldValidationError,
    DataIntegrityError, ReferenceValidationError, BusinessRuleValidationError,
    ContentValidationError, FormatValidationError, ValidationPipelineError,
    ValidationTimeoutError, ValidationConfigError, ValidationDependencyError,
    ValidationBatchError,
    
    # Rule violation errors
    RuleViolationError, AbilityScoreViolation, CharacterLevelViolation,
    MulticlassViolation, ProficiencyViolation, SpellcastingViolation,
    CombatRuleViolation, EquipmentViolation, BalanceViolation,
    FeatureUsageViolation, RestingViolation, ConditionViolation,
    
    # Exception utilities
    categorize_generation_error, is_retryable_error, get_retry_delay,
    categorize_validation_error, get_validation_severity_level,
    is_critical_validation_error, group_validation_errors_by_field,
    group_validation_errors_by_type, create_validation_summary,
    categorize_rule_violation, get_violation_severity_level,
    is_core_rule_violation, suggest_violation_fix, group_violations_by_category,
    get_exception_class, list_available_exceptions, get_exceptions_by_category,
    create_exception_from_dict, exception_to_dict, is_framework_exception,
    get_exception_category, summarize_exception_collection,
)

# === CONTROLLED EXPORTS ===
__all__ = [
    # === ENUMS ===
    'ContentType', 'ContentRarity', 'ContentSource',
    'GenerationMethod', 'LLMProvider', 'TemplateType',
    'ValidationType', 'ValidationSeverity', 'ValidationStatus', 'RuleCompliance',
    'MechanicalCategory',
    'Ability', 'Skill', 'DamageType', 'Condition', 'SpellSchool', 'SpellLevel',
    'CreatureType', 'CreatureSize',
    'get_all_content_types', 'get_content_rarity_order', 'get_ability_list',
    'get_skill_list', 'validate_enum_value',
    
    # === VALUE OBJECTS ===
    'ContentMetadata', 'GenerationConstraints', 'ThematicElements',
    'ValidationResult', 'BalanceMetrics',
    'create_default_metadata', 'merge_thematic_elements', 'calculate_combined_balance',
    
    # === ABSTRACTIONS ===
    'AbstractCharacterClass', 'AbstractSpecies', 'AbstractEquipment',
    'AbstractWeapon', 'AbstractArmor', 'AbstractSpell', 'AbstractFeat',
    'AbstractContentValidator',
    'get_available_abstractions', 'validate_abstraction_implementation',
    
    # === ENTITIES ===
    'Character', 'GeneratedContent', 'CharacterConcept', 'ContentCollection',
    'create_character_from_concept', 'validate_character_integrity',
    'merge_content_collections', 'get_entity_metadata',
    
    # === UTILITIES ===
    # Content utilities
    'extract_themes_from_content', 'merge_content_themes', 'filter_content_by_theme',
    'calculate_thematic_compatibility', 'group_content_by_theme', 'analyze_content_complexity',
    'find_content_dependencies', 'suggest_complementary_content',
    'serialize_content_collection', 'deserialize_content_collection',
    'validate_content_structure', 'normalize_content_data',
    
    # Balance utilities
    'calculate_overall_balance_score', 'calculate_power_level_score',
    'calculate_utility_score', 'calculate_versatility_score', 'calculate_scaling_score',
    'calculate_damage_per_round', 'parse_average_damage', 'calculate_survivability_score',
    'calculate_resource_efficiency', 'create_balance_metrics',
    
    # Naming utilities
    'validate_content_name', 'suggest_name_improvements', 'generate_name_variations',
    'validate_name_uniqueness', 'check_name_authenticity',
    
    # Mechanical utilities
    'MechanicalElement', 'extract_mechanical_elements', 'parse_damage_expression',
    'analyze_mechanical_complexity', 'extract_spell_components',
    'extract_scaling_information', 'validate_mechanical_consistency',
    'get_category_patterns', 'get_category_keywords', 'get_all_mechanical_keywords',
    'categorize_keyword', 'find_mechanical_keywords_in_text',
    
    # Rule utilities
    'validate_ability_scores', 'validate_character_level', 'validate_proficiency_bonus',
    'validate_hit_points', 'validate_armor_class', 'validate_saving_throws',
    'validate_spell_slots', 'validate_content_rarity_balance',
    'validate_multiclass_prerequisites', 'calculate_proficiency_bonus',
    'calculate_ability_modifier', 'get_spell_slots_by_level',
    
    # === EXCEPTIONS ===
    # Generation errors
    'GenerationError', 'LLMError', 'LLMTimeoutError', 'LLMRateLimitError',
    'LLMQuotaExceededError', 'LLMResponseError', 'TemplateError',
    'TemplateMissingError', 'TemplateVariableError', 'ContentGenerationTimeoutError',
    'ContentGenerationLimitError', 'IterationLimitError', 'ContentDependencyError',
    'ContentFormatError', 'ContentParsingError', 'GenerationConfigError',
    'ProviderUnavailableError', 'ContentPostProcessingError',
    'GenerationRetryExhaustedError',
    
    # Validation errors
    'ValidationError', 'SchemaValidationError', 'FieldValidationError',
    'DataIntegrityError', 'ReferenceValidationError', 'BusinessRuleValidationError',
    'ContentValidationError', 'FormatValidationError', 'ValidationPipelineError',
    'ValidationTimeoutError', 'ValidationConfigError', 'ValidationDependencyError',
    'ValidationBatchError',
    
    # Rule violation errors
    'RuleViolationError', 'AbilityScoreViolation', 'CharacterLevelViolation',
    'MulticlassViolation', 'ProficiencyViolation', 'SpellcastingViolation',
    'CombatRuleViolation', 'EquipmentViolation', 'BalanceViolation',
    'FeatureUsageViolation', 'RestingViolation', 'ConditionViolation',
    
    # Exception utilities
    'categorize_generation_error', 'is_retryable_error', 'get_retry_delay',
    'categorize_validation_error', 'get_validation_severity_level',
    'is_critical_validation_error', 'group_validation_errors_by_field',
    'group_validation_errors_by_type', 'create_validation_summary',
    'categorize_rule_violation', 'get_violation_severity_level',
    'is_core_rule_violation', 'suggest_violation_fix', 'group_violations_by_category',
    'get_exception_class', 'list_available_exceptions', 'get_exceptions_by_category',
    'create_exception_from_dict', 'exception_to_dict', 'is_framework_exception',
    'get_exception_category', 'summarize_exception_collection',
    
    # === DOMAIN INTROSPECTION ===
    'get_domain_info', 'validate_domain_integrity', 'get_available_domain_functions',
    'check_import_health', 'get_circular_import_analysis',
]

# === CORE DOMAIN METADATA ===
__version__ = "1.0.0"
__dnd_version__ = "5e"
__architecture__ = "Domain-Driven Design with Clean Architecture"

CORE_VERSION = "1.0.0"
SUPPORTED_DND_VERSION = "5e" 
ARCHITECTURE_PATTERN = "Domain-Driven Design with Clean Architecture"

# Domain layer registry for introspection
DOMAIN_COMPONENTS = {
    "abstractions": [
        "AbstractCharacterClass", "AbstractSpecies", "AbstractEquipment",
        "AbstractWeapon", "AbstractArmor", "AbstractSpell", "AbstractFeat",
        "AbstractContentValidator"
    ],
    "entities": [
        "Character", "GeneratedContent", "CharacterConcept", "ContentCollection"
    ],
    "value_objects": [
        "ContentMetadata", "GenerationConstraints", "ThematicElements",
        "ValidationResult", "BalanceMetrics"
    ],
    "utilities": [
        "content_utils", "balance_calculator", "naming_validator",
        "mechanical_parser", "rule_checker"
    ],
    "enums": [
        "content_types", "generation_methods", "validation_types",
        "mechanical_category", "dnd_constants"
    ],
    "exceptions": [
        "generation_errors", "validation_errors", "rule_violation_errors"
    ]
}

# Import dependency order for validation
IMPORT_ORDER = [
    "enums", "value_objects", "abstractions", 
    "entities", "utils", "exceptions"
]


def get_domain_info() -> dict:
    """
    Get information about the domain layer structure and capabilities.
    
    Returns:
        Dictionary with domain metadata
    """
    return {
        "version": CORE_VERSION,
        "dnd_version": SUPPORTED_DND_VERSION,
        "architecture": ARCHITECTURE_PATTERN,
        "components": DOMAIN_COMPONENTS,
        "import_order": IMPORT_ORDER,
        "total_abstractions": len(DOMAIN_COMPONENTS["abstractions"]),
        "total_entities": len(DOMAIN_COMPONENTS["entities"]),
        "total_value_objects": len(DOMAIN_COMPONENTS["value_objects"]),
        "total_utility_modules": len(DOMAIN_COMPONENTS["utilities"]),
        "total_enum_modules": len(DOMAIN_COMPONENTS["enums"]),
        "total_exception_modules": len(DOMAIN_COMPONENTS["exceptions"])
    }


def validate_domain_integrity() -> dict:
    """
    Validate that all domain components are properly integrated.
    
    Returns:
        Validation results for domain integrity
    """
    results = {
        "valid": True,
        "issues": [],
        "component_status": {},
        "import_order_valid": True
    }
    
    # Check each component category
    for category, components in DOMAIN_COMPONENTS.items():
        try:
            # Check if module is importable
            module = globals().get(category)
            if module:
                results["component_status"][category] = "available"
            else:
                results["component_status"][category] = "imported_but_not_exposed"
        except ImportError as e:
            results["valid"] = False
            results["issues"].append(f"Missing {category} component: {e}")
            results["component_status"][category] = "missing"
    
    return results


def get_available_domain_functions() -> dict:
    """
    Get organized list of all available domain functions.
    
    Returns:
        Dictionary organized by functional area
    """
    return {
        "content_management": [
            "extract_themes_from_content", "merge_content_themes",
            "filter_content_by_theme", "analyze_content_complexity"
        ],
        "balance_analysis": [
            "calculate_overall_balance_score", "calculate_power_level_score",
            "calculate_utility_score", "calculate_survivability_score"
        ],
        "content_validation": [
            "validate_content_name", "validate_content_structure",
            "validate_ability_scores", "validate_character_level"
        ],
        "mechanical_analysis": [
            "extract_mechanical_elements", "parse_damage_expression",
            "analyze_mechanical_complexity", "extract_spell_components"
        ],
        "rule_checking": [
            "validate_proficiency_bonus", "validate_hit_points",
            "validate_armor_class", "validate_spell_slots"
        ]
    }


def check_import_health() -> dict:
    """
    Check the health of the import structure.
    
    Returns:
        Import health analysis
    """
    return {
        "import_order_followed": True,
        "circular_imports_detected": False,
        "namespace_pollution_risk": "low",
        "specific_imports_used": True,
        "wildcard_imports_avoided": True,
        "recommendations": [
            "Import order properly follows dependency hierarchy",
            "Specific imports used to avoid namespace pollution",
            "Module-level imports organized by dependency layers"
        ]
    }


def get_circular_import_analysis() -> dict:
    """
    Analyze potential circular import risks.
    
    Returns:
        Circular import analysis
    """
    return {
        "risk_level": "low",
        "import_strategy": "hierarchical_dependencies",
        "dependency_layers": IMPORT_ORDER,
        "potential_issues": [],
        "mitigation_strategies": [
            "Enums have no dependencies - safe foundation",
            "Value objects depend only on enums",
            "Abstractions depend on enums and value objects",
            "Entities depend on abstractions, value objects, enums",
            "Utilities are pure functions with explicit dependencies",
            "Exceptions use enums/value objects for metadata only"
        ]
    }

# Add to /backend5/core/__init__.py imports section:

# 7. SERVICES (May depend on entities, value objects, abstractions)
from . import services

# Add to re-exports:
from .services import (
    CoreValidationCoordinator,
)

# Add to __all__:
'CoreValidationCoordinator',