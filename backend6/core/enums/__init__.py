"""
Core enumerations for the D&D Creative Content Framework.

This module provides all enumerated types used throughout the system,
organized by their primary purpose and domain according to Clean Architecture principles.
"""

# D&D Game Mechanics enums (Core business rules - immutable)
from .game_mechanics import (
    Ability,
    Skill,
    ProficiencyLevel,
    DamageType,
    ActionType,
    Condition,
    MagicSchool,
    SpellLevel,
    CastingTime,
    SpellRange,
    SpellDuration,
    AreaOfEffect,
    Currency,
    PowerTier
)

# Content Type enums (Creative content framework)
from .content_types import (
    ContentType,
    GenerationType,
    ContentRarity,
    ThemeCategory,
    CHARACTER_OPTIONS,
    EQUIPMENT_TYPES,
    SIGNATURE_CONTENT,
    get_content_types_by_category
)

# Creativity Level enums (Generation parameters)
from .creativity_levels import (
    CreativityLevel,
    GenerationMethod,
    ContentComplexity,
    ThematicConsistency
)

# Balance Level enums (Validation and power analysis)
from .balance_levels import (
    BalanceLevel,
    ValidationLevel,
    BalanceCategory,
    PowerBenchmark
)

# Validation Type enums (Content validation framework)
from .validation_types import (
    ValidationType,
    ValidationSeverity,
    ValidationStatus,
    ValidationScope,
    RuleCompliance
)

# Progression Type enums (Character development)
from .progression_types import (
    ProgressionType,
    MilestoneType,
    FeatureCategory,
    ScalingType,
    ThematicTier
)

# Export Format enums (Output and VTT compatibility)
from .export_formats import (
    ExportFormat,
    CharacterSheetType,
    OutputLayout,
    ContentInclusionLevel,
    get_supported_formats_for_vtt
)

# Export all public symbols organized by architectural layer
__all__ = [
    # ============ CORE LAYER ENUMS ============
    # D&D Game Mechanics (Immutable business rules)
    'Ability',
    'Skill', 
    'ProficiencyLevel',
    'DamageType',
    'ActionType',
    'Condition',
    'MagicSchool',
    'SpellLevel',
    'CastingTime',
    'SpellRange',
    'SpellDuration',
    'AreaOfEffect',
    'Currency',
    'PowerTier',
    
    # ============ DOMAIN LAYER ENUMS ============
    # Content Types (Business entities)
    'ContentType',
    'GenerationType',
    'ContentRarity',
    'ThemeCategory',
    
    # Content Type Collections
    'CHARACTER_OPTIONS',
    'EQUIPMENT_TYPES', 
    'SIGNATURE_CONTENT',
    
    # Creative Content Generation
    'CreativityLevel',
    'GenerationMethod',
    'ContentComplexity',
    'ThematicConsistency',
    
    # Balance Analysis
    'BalanceLevel',
    'ValidationLevel',
    'BalanceCategory',
    'PowerBenchmark',
    
    # Character Progression
    'ProgressionType',
    'MilestoneType',
    'FeatureCategory',
    'ScalingType',
    'ThematicTier',
    
    # ============ APPLICATION LAYER ENUMS ============
    # Validation Framework
    'ValidationType',
    'ValidationSeverity',
    'ValidationStatus',
    'ValidationScope',
    'RuleCompliance',
    
    # ============ INFRASTRUCTURE LAYER ENUMS ============
    # Export and Output
    'ExportFormat',
    'CharacterSheetType',
    'OutputLayout',
    'ContentInclusionLevel',
    
    # Helper Functions
    'get_content_types_by_category',
    'get_supported_formats_for_vtt'
]

# Comprehensive Enum Registry organized by Clean Architecture layers
ENUM_REGISTRY = {
    # ============ CORE LAYER ============
    'core': {
        # D&D Game Mechanics (immutable business rules)
        'ability': Ability,
        'skill': Skill,
        'proficiency_level': ProficiencyLevel,
        'damage_type': DamageType,
        'action_type': ActionType,
        'condition': Condition,
        'magic_school': MagicSchool,
        'spell_level': SpellLevel,
        'casting_time': CastingTime,
        'spell_range': SpellRange,
        'spell_duration': SpellDuration,
        'area_of_effect': AreaOfEffect,
        'currency': Currency,
        'power_tier': PowerTier,
    },
    
    # ============ DOMAIN LAYER ============
    'domain': {
        # Content Generation Business Logic
        'content_type': ContentType,
        'generation_type': GenerationType,
        'content_rarity': ContentRarity,
        'theme_category': ThemeCategory,
        'creativity_level': CreativityLevel,
        'generation_method': GenerationMethod,
        'content_complexity': ContentComplexity,
        'thematic_consistency': ThematicConsistency,
        'balance_level': BalanceLevel,
        'validation_level': ValidationLevel,
        'balance_category': BalanceCategory,
        'power_benchmark': PowerBenchmark,
        'progression_type': ProgressionType,
        'milestone_type': MilestoneType,
        'feature_category': FeatureCategory,
        'scaling_type': ScalingType,
        'thematic_tier': ThematicTier,
    },
    
    # ============ APPLICATION LAYER ============
    'application': {
        # Use Case Orchestration
        'validation_type': ValidationType,
        'validation_severity': ValidationSeverity,
        'validation_status': ValidationStatus,
        'validation_scope': ValidationScope,
        'rule_compliance': RuleCompliance,
    },
    
    # ============ INFRASTRUCTURE LAYER ============
    'infrastructure': {
        # External Systems and Export
        'export_format': ExportFormat,
        'character_sheet_type': CharacterSheetType,
        'output_layout': OutputLayout,
        'content_inclusion_level': ContentInclusionLevel,
    }
}

# Flattened registry for backward compatibility
FLAT_ENUM_REGISTRY = {}
for layer, enums in ENUM_REGISTRY.items():
    FLAT_ENUM_REGISTRY.update(enums)


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
    return FLAT_ENUM_REGISTRY.get(enum_type.lower())


def get_enums_by_layer(layer: str = None) -> dict:
    """
    Get enums organized by Clean Architecture layer.
    
    Args:
        layer: Specific layer ('core', 'domain', 'application', 'infrastructure')
               If None, returns all layers
        
    Returns:
        Dictionary of enums for the specified layer or all layers
        
    Example:
        >>> core_enums = get_enums_by_layer('core')
        >>> domain_enums = get_enums_by_layer('domain')
    """
    if layer:
        return ENUM_REGISTRY.get(layer.lower(), {})
    return ENUM_REGISTRY


def get_d3d_mechanics_enums() -> dict[str, type]:
    """
    Get all immutable D&D mechanics enums from core layer.
    
    Returns:
        Dictionary of D&D mechanics enum names to enum classes
        
    Example:
        >>> mechanics = get_d3d_mechanics_enums()
        >>> abilities = mechanics['ability']
    """
    return ENUM_REGISTRY['core']


def get_creative_content_enums() -> dict[str, type]:
    """
    Get all creative content generation enums from domain layer.
    
    Returns:
        Dictionary of creative content enum names to enum classes
        
    Example:
        >>> creative_enums = get_creative_content_enums()
        >>> content_types = creative_enums['content_type']
    """
    return ENUM_REGISTRY['domain']


def get_character_creation_enums() -> dict[str, type]:
    """
    Get enums specifically related to character creation workflow.
    
    Returns:
        Dictionary of character creation enum names to enum classes
        
    Example:
        >>> char_enums = get_character_creation_enums()
        >>> progression = char_enums['progression_type']
    """
    character_creation_enums = {}
    
    # Core D&D mechanics for characters
    core_char_enums = ['ability', 'skill', 'proficiency_level']
    for enum_name in core_char_enums:
        if enum_name in ENUM_REGISTRY['core']:
            character_creation_enums[enum_name] = ENUM_REGISTRY['core'][enum_name]
    
    # Domain character generation enums
    domain_char_enums = [
        'content_type', 'creativity_level', 'balance_level', 
        'progression_type', 'milestone_type', 'feature_category',
        'scaling_type', 'thematic_tier'
    ]
    for enum_name in domain_char_enums:
        if enum_name in ENUM_REGISTRY['domain']:
            character_creation_enums[enum_name] = ENUM_REGISTRY['domain'][enum_name]
    
    return character_creation_enums


def get_export_related_enums() -> dict[str, type]:
    """
    Get enums related to character sheet export and VTT compatibility.
    
    Returns:
        Dictionary of export-related enum names to enum classes
        
    Example:
        >>> export_enums = get_export_related_enums()
        >>> formats = export_enums['export_format']
    """
    return ENUM_REGISTRY['infrastructure']


def list_available_enums() -> list[str]:
    """
    Get list of all available enum types.
    
    Returns:
        List of enum type names
        
    Example:
        >>> enums = list_available_enums()
        >>> print(f"Available enums: {len(enums)}")
    """
    return list(FLAT_ENUM_REGISTRY.keys())


def get_enums_by_category() -> dict[str, list[str]]:
    """
    Get enums organized by their functional category within Clean Architecture.
    
    Returns:
        Dictionary of categories with their enum types
        
    Example:
        >>> categories = get_enums_by_category()
        >>> core_mechanics = categories['d3d_mechanics']
    """
    return {
        "d3d_mechanics": [
            "ability", "skill", "proficiency_level", "damage_type", "action_type",
            "condition", "magic_school", "spell_level", "casting_time", "spell_range", 
            "spell_duration", "area_of_effect", "currency", "power_tier"
        ],
        "content_generation": [
            "content_type", "generation_type", "content_rarity", "theme_category",
            "creativity_level", "generation_method", "content_complexity", "thematic_consistency"
        ],
        "balance_validation": [
            "balance_level", "validation_level", "balance_category", "power_benchmark",
            "validation_type", "validation_severity", "validation_status", "validation_scope",
            "rule_compliance"
        ],
        "character_progression": [
            "progression_type", "milestone_type", "feature_category", "scaling_type", "thematic_tier"
        ],
        "export_formats": [
            "export_format", "character_sheet_type", "output_layout", "content_inclusion_level"
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
        >>> creativity = get_enum_by_name('creativity_level', 'high')
        >>> print(creativity.name)
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


def search_enums(search_term: str) -> dict[str, dict[str, list[str]]]:
    """
    Search for enums containing a specific term, organized by architecture layer.
    
    Args:
        search_term: Term to search for in enum names or values
        
    Returns:
        Dictionary mapping layers to enum names to matching values
        
    Example:
        >>> results = search_enums('spell')
        >>> core_spell_enums = results.get('core', {})
    """
    results = {}
    search_lower = search_term.lower()
    
    for layer, layer_enums in ENUM_REGISTRY.items():
        layer_results = {}
        
        for enum_name, enum_class in layer_enums.items():
            # Check if enum name contains search term
            if search_lower in enum_name:
                layer_results[enum_name] = [e.value for e in enum_class]
                continue
                
            # Check if any enum values contain search term
            matching_values = [
                e.value for e in enum_class 
                if search_lower in e.value.lower()
            ]
            
            if matching_values:
                layer_results[enum_name] = matching_values
        
        if layer_results:
            results[layer] = layer_results
    
    return results


def get_content_creation_workflow_enums() -> dict[str, type]:
    """
    Get enums specifically for the interactive character creation workflow.
    
    Returns:
        Dictionary of workflow-related enum names to enum classes
        
    Example:
        >>> workflow_enums = get_content_creation_workflow_enums()
        >>> creativity = workflow_enums['creativity_level']
    """
    workflow_enums = {
        # User interaction and creativity
        'creativity_level': CreativityLevel,
        'generation_method': GenerationMethod,
        'content_complexity': ContentComplexity,
        'thematic_consistency': ThematicConsistency,
        
        # Content generation
        'content_type': ContentType,
        'generation_type': GenerationType,
        'theme_category': ThemeCategory,
        
        # Validation and balance
        'balance_level': BalanceLevel,
        'validation_level': ValidationLevel,
        'validation_type': ValidationType,
        'validation_status': ValidationStatus,
        
        # Character progression
        'progression_type': ProgressionType,
        'milestone_type': MilestoneType,
        'thematic_tier': ThematicTier,
        
        # Export
        'export_format': ExportFormat,
        'character_sheet_type': CharacterSheetType
    }
    
    return workflow_enums


def get_vtt_compatibility_enums() -> dict[str, type]:
    """
    Get enums related to Virtual Tabletop compatibility and export.
    
    Returns:
        Dictionary of VTT-related enum names to enum classes
        
    Example:
        >>> vtt_enums = get_vtt_compatibility_enums()
        >>> export_formats = vtt_enums['export_format']
    """
    return {
        'export_format': ExportFormat,
        'character_sheet_type': CharacterSheetType,
        'output_layout': OutputLayout,
        'content_inclusion_level': ContentInclusionLevel
    }


def validate_architecture_compliance() -> list[str]:
    """
    Validate that enum organization follows Clean Architecture principles.
    
    Returns:
        List of compliance issues (empty if compliant)
        
    Example:
        >>> issues = validate_architecture_compliance()
        >>> if not issues:
        ...     print("Architecture compliant!")
    """
    issues = []
    
    # Check that each layer has appropriate enums
    required_layers = ['core', 'domain', 'application', 'infrastructure']
    for layer in required_layers:
        if layer not in ENUM_REGISTRY:
            issues.append(f"Missing required architecture layer: {layer}")
    
    # Check that core layer only contains immutable D&D mechanics
    core_enums = ENUM_REGISTRY.get('core', {})
    if not core_enums:
        issues.append("Core layer is empty - should contain D&D mechanics")
    
    # Check that domain layer contains business logic enums
    domain_enums = ENUM_REGISTRY.get('domain', {})
    expected_domain_enums = ['content_type', 'creativity_level', 'balance_level']
    for enum_name in expected_domain_enums:
        if enum_name not in domain_enums:
            issues.append(f"Domain layer missing critical enum: {enum_name}")
    
    # Check that all enums are properly accessible
    for layer, enums in ENUM_REGISTRY.items():
        for enum_name, enum_class in enums.items():
            if enum_class is None:
                issues.append(f"Enum '{enum_name}' in layer '{layer}' is None")
            elif not hasattr(enum_class, '__members__'):
                issues.append(f"'{enum_name}' in layer '{layer}' is not a valid enum")
    
    return issues


# Module metadata
__version__ = '2.0.0'
__description__ = 'Clean Architecture-compliant enumerations for D&D Creative Content Framework'

# Configuration
ENABLE_ENUM_CACHING = True
STRICT_VALIDATION = True
ARCHITECTURE_COMPLIANCE_CHECK = True

# Architecture compliance validation on import
if ARCHITECTURE_COMPLIANCE_CHECK:
    _compliance_issues = validate_architecture_compliance()
    if _compliance_issues and STRICT_VALIDATION:
        import warnings
        warnings.warn(f"Architecture compliance issues: {_compliance_issues}")

# Usage examples in docstring
"""
Clean Architecture Usage Examples:

1. Core Layer (Immutable D&D mechanics):
   >>> from core.enums import Ability, Skill, DamageType
   >>> print(Ability.STRENGTH.value)
   
2. Domain Layer (Business logic):
   >>> from core.enums import ContentType, CreativityLevel, BalanceLevel
   >>> creativity = CreativityLevel.HIGH
   >>> print(f"Allows custom classes: {creativity.allows_custom_classes}")
   
3. Application Layer (Use case orchestration):
   >>> from core.enums import ValidationType, ValidationStatus
   >>> validation = ValidationType.BALANCE
   >>> print(f"Is blocking: {validation.is_blocking}")
   
4. Infrastructure Layer (External systems):
   >>> from core.enums import ExportFormat
   >>> formats = get_supported_formats_for_vtt('roll20')
   
5. Architecture-aware access:
   >>> core_enums = get_enums_by_layer('core')
   >>> domain_enums = get_enums_by_layer('domain')
   
6. Character creation workflow:
   >>> workflow_enums = get_content_creation_workflow_enums()
   >>> creativity_enum = workflow_enums['creativity_level']
   
7. VTT compatibility:
   >>> vtt_enums = get_vtt_compatibility_enums()
   >>> export_formats = vtt_enums['export_format']
   
8. Search by layer:
   >>> spell_results = search_enums('spell')
   >>> core_spell_enums = spell_results.get('core', {})
   
9. Architecture compliance:
   >>> issues = validate_architecture_compliance()
   >>> print(f"Compliance status: {'PASS' if not issues else 'FAIL'}")
"""