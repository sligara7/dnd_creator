"""
Core enumerations for the D&D Creative Content Framework.

This module provides all enumerated types used throughout the system,
organized by their primary purpose and domain according to Clean Architecture principles.
Enhanced with AI-powered culture generation enums for authentic cultural naming systems.
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

# Conversation State enums (Interactive workflow management)
from .conversation_states import (
    ConversationState,
    ConversationSubState,
    ConversationPhase,
    UserInteractionType,
    ConversationTrigger,
    ConversationContext,
    ResponseTone,
    ConversationPriority,
    # Utility functions
    is_valid_transition,
    get_valid_transitions,
    get_conversation_phase,
    get_expected_interactions,
    get_state_timeout,
    is_terminal_state,
    is_processing_state,
    is_user_input_state,
    get_states_in_phase,
    calculate_progress_percentage,
    get_next_recommended_state,
    # State metadata
    STATE_DESCRIPTIONS,
    STATE_DISPLAY_NAMES,
    VALID_TRANSITIONS,
    STATE_PHASES,
    STATE_INTERACTIONS,
    STATE_TIMEOUTS
)

# 🆕 Culture Generation enums (AI-powered culture system)
from .culture_types import (
    CultureGenerationType,
    CultureAuthenticityLevel,
    CultureCreativityLevel,
    CultureSourceType,
    CultureComplexityLevel,
    CultureValidationCategory,
    CultureValidationSeverity,
    CultureGenerationStatus,
    CultureNamingStructure,
    CultureGenderSystem,
    CultureLinguisticFamily,
    CultureTemporalPeriod,
    # Utility functions
    get_default_authenticity_for_source,
    get_complexity_for_authenticity,
    validate_culture_configuration,
    # Configuration presets
    CULTURE_GENERATION_PRESETS
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
    
    # Conversation Workflow Management
    'ConversationState',
    'ConversationSubState',
    'ConversationPhase',
    'UserInteractionType',
    'ConversationTrigger',
    'ConversationContext',
    'ResponseTone',
    'ConversationPriority',
    
    # 🆕 Culture Generation System
    'CultureGenerationType',
    'CultureAuthenticityLevel',
    'CultureCreativityLevel',
    'CultureSourceType',
    'CultureComplexityLevel',
    'CultureValidationCategory',
    'CultureValidationSeverity',
    'CultureGenerationStatus',
    'CultureNamingStructure',
    'CultureGenderSystem',
    'CultureLinguisticFamily',
    'CultureTemporalPeriod',
    
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
    'get_supported_formats_for_vtt',
    
    # Conversation State Utilities
    'is_valid_transition',
    'get_valid_transitions',
    'get_conversation_phase',
    'get_expected_interactions',
    'get_state_timeout',
    'is_terminal_state',
    'is_processing_state',
    'is_user_input_state',
    'get_states_in_phase',
    'calculate_progress_percentage',
    'get_next_recommended_state',
    
    # State Metadata
    'STATE_DESCRIPTIONS',
    'STATE_DISPLAY_NAMES',
    'VALID_TRANSITIONS',
    'STATE_PHASES',
    'STATE_INTERACTIONS',
    'STATE_TIMEOUTS',
    
    # 🆕 Culture Generation Utilities
    'get_default_authenticity_for_source',
    'get_complexity_for_authenticity',
    'validate_culture_configuration',
    'CULTURE_GENERATION_PRESETS'
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
        
        # Interactive Conversation Workflow
        'conversation_state': ConversationState,
        'conversation_substate': ConversationSubState,
        'conversation_phase': ConversationPhase,
        'user_interaction_type': UserInteractionType,
        'conversation_trigger': ConversationTrigger,
        'conversation_context': ConversationContext,
        'response_tone': ResponseTone,
        'conversation_priority': ConversationPriority,
        
        # 🆕 Culture Generation System
        'culture_generation_type': CultureGenerationType,
        'culture_authenticity_level': CultureAuthenticityLevel,
        'culture_creativity_level': CultureCreativityLevel,
        'culture_source_type': CultureSourceType,
        'culture_complexity_level': CultureComplexityLevel,
        'culture_validation_category': CultureValidationCategory,
        'culture_validation_severity': CultureValidationSeverity,
        'culture_generation_status': CultureGenerationStatus,
        'culture_naming_structure': CultureNamingStructure,
        'culture_gender_system': CultureGenderSystem,
        'culture_linguistic_family': CultureLinguisticFamily,
        'culture_temporal_period': CultureTemporalPeriod,
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
        >>> culture_enum = get_enum_class('culture_generation_type')
        >>> print(list(culture_enum))
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
        >>> culture_enums = domain_enums  # Culture enums are in domain layer
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
        >>> culture_types = creative_enums['culture_generation_type']
    """
    # Filter out conversation-specific enums for creative content focus
    domain_enums = ENUM_REGISTRY['domain'].copy()
    conversation_enum_names = [
        'conversation_state', 'conversation_substate', 'conversation_phase',
        'user_interaction_type', 'conversation_trigger', 'conversation_context',
        'response_tone', 'conversation_priority'
    ]
    
    for enum_name in conversation_enum_names:
        domain_enums.pop(enum_name, None)
    
    return domain_enums


def get_character_creation_enums() -> dict[str, type]:
    """
    Get enums specifically related to character creation workflow.
    
    Returns:
        Dictionary of character creation enum names to enum classes
        
    Example:
        >>> char_enums = get_character_creation_enums()
        >>> progression = char_enums['progression_type']
        >>> culture_auth = char_enums['culture_authenticity_level']
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
        'scaling_type', 'thematic_tier',
        # 🆕 Culture generation enums for character creation
        'culture_generation_type', 'culture_authenticity_level', 
        'culture_creativity_level', 'culture_source_type',
        'culture_naming_structure', 'culture_gender_system'
    ]
    for enum_name in domain_char_enums:
        if enum_name in ENUM_REGISTRY['domain']:
            character_creation_enums[enum_name] = ENUM_REGISTRY['domain'][enum_name]
    
    return character_creation_enums


def get_conversation_workflow_enums() -> dict[str, type]:
    """
    Get enums specifically related to interactive conversation workflow.
    
    Returns:
        Dictionary of conversation workflow enum names to enum classes
        
    Example:
        >>> workflow_enums = get_conversation_workflow_enums()
        >>> states = workflow_enums['conversation_state']
    """
    conversation_enums = {}
    conversation_enum_names = [
        'conversation_state', 'conversation_substate', 'conversation_phase',
        'user_interaction_type', 'conversation_trigger', 'conversation_context',
        'response_tone', 'conversation_priority'
    ]
    
    for enum_name in conversation_enum_names:
        if enum_name in ENUM_REGISTRY['domain']:
            conversation_enums[enum_name] = ENUM_REGISTRY['domain'][enum_name]
    
    return conversation_enums


def get_culture_generation_enums() -> dict[str, type]:
    """
    Get enums specifically related to AI-powered culture generation.
    
    Returns:
        Dictionary of culture generation enum names to enum classes
        
    Example:
        >>> culture_enums = get_culture_generation_enums()
        >>> auth_levels = culture_enums['culture_authenticity_level']
        >>> generation_types = culture_enums['culture_generation_type']
    """
    culture_enums = {}
    culture_enum_names = [
        'culture_generation_type', 'culture_authenticity_level', 
        'culture_creativity_level', 'culture_source_type',
        'culture_complexity_level', 'culture_validation_category',
        'culture_validation_severity', 'culture_generation_status',
        'culture_naming_structure', 'culture_gender_system',
        'culture_linguistic_family', 'culture_temporal_period'
    ]
    
    for enum_name in culture_enum_names:
        if enum_name in ENUM_REGISTRY['domain']:
            culture_enums[enum_name] = ENUM_REGISTRY['domain'][enum_name]
    
    return culture_enums


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
    Get list of all available enum types including culture generation.
    
    Returns:
        List of enum type names
        
    Example:
        >>> enums = list_available_enums()
        >>> culture_enums = [e for e in enums if 'culture' in e]
        >>> print(f"Culture enums: {culture_enums}")
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
        >>> culture_system = categories['culture_generation']
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
        "conversation_workflow": [
            "conversation_state", "conversation_substate", "conversation_phase",
            "user_interaction_type", "conversation_trigger", "conversation_context",
            "response_tone", "conversation_priority"
        ],
        "culture_generation": [  # 🆕 New category for culture generation
            "culture_generation_type", "culture_authenticity_level", "culture_creativity_level",
            "culture_source_type", "culture_complexity_level", "culture_validation_category",
            "culture_validation_severity", "culture_generation_status", "culture_naming_structure",
            "culture_gender_system", "culture_linguistic_family", "culture_temporal_period"
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
        >>> culture_auth = get_enum_by_name('culture_authenticity_level', 'academic')
        >>> print(culture_auth.description)
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
        >>> is_culture_valid = validate_enum_value('culture_source_type', 'historical')
        >>> print(f"Valid: {is_valid}, Culture valid: {is_culture_valid}")
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
        >>> culture_auth_levels = get_enum_values('culture_authenticity_level')
        >>> print(f"Culture authenticity levels: {culture_auth_levels}")
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
        >>> results = search_enums('culture')
        >>> domain_culture_enums = results.get('domain', {})
        >>> spell_results = search_enums('spell')
        >>> core_spell_enums = spell_results.get('core', {})
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
        >>> culture_creativity = workflow_enums['culture_creativity_level']
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
        
        # Conversation workflow
        'conversation_state': ConversationState,
        'conversation_phase': ConversationPhase,
        'user_interaction_type': UserInteractionType,
        'conversation_context': ConversationContext,
        'response_tone': ResponseTone,
        
        # 🆕 Culture generation workflow
        'culture_generation_type': CultureGenerationType,
        'culture_authenticity_level': CultureAuthenticityLevel,
        'culture_creativity_level': CultureCreativityLevel,
        'culture_source_type': CultureSourceType,
        'culture_complexity_level': CultureComplexityLevel,
        'culture_generation_status': CultureGenerationStatus,
        'culture_naming_structure': CultureNamingStructure,
        'culture_gender_system': CultureGenderSystem,
        
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


def get_conversation_state_utilities() -> dict[str, callable]:
    """
    Get all conversation state utility functions.
    
    Returns:
        Dictionary of utility function names to function objects
        
    Example:
        >>> utilities = get_conversation_state_utilities()
        >>> is_valid = utilities['is_valid_transition']
    """
    return {
        'is_valid_transition': is_valid_transition,
        'get_valid_transitions': get_valid_transitions,
        'get_conversation_phase': get_conversation_phase,
        'get_expected_interactions': get_expected_interactions,
        'get_state_timeout': get_state_timeout,
        'is_terminal_state': is_terminal_state,
        'is_processing_state': is_processing_state,
        'is_user_input_state': is_user_input_state,
        'get_states_in_phase': get_states_in_phase,
        'calculate_progress_percentage': calculate_progress_percentage,
        'get_next_recommended_state': get_next_recommended_state
    }


def get_culture_generation_utilities() -> dict[str, callable]:
    """
    Get all culture generation utility functions.
    
    Returns:
        Dictionary of utility function names to function objects
        
    Example:
        >>> utilities = get_culture_generation_utilities()
        >>> get_default_auth = utilities['get_default_authenticity_for_source']
        >>> validate_config = utilities['validate_culture_configuration']
    """
    return {
        'get_default_authenticity_for_source': get_default_authenticity_for_source,
        'get_complexity_for_authenticity': get_complexity_for_authenticity,
        'validate_culture_configuration': validate_culture_configuration
    }


def validate_conversation_transition(from_state: str, to_state: str) -> bool:
    """
    Validate a conversation state transition using string values.
    
    Args:
        from_state: Current state as string
        to_state: Target state as string
        
    Returns:
        True if transition is valid
        
    Example:
        >>> valid = validate_conversation_transition('greeting', 'concept_gathering')
        >>> print(f"Valid transition: {valid}")
    """
    try:
        from_enum = ConversationState(from_state.lower())
        to_enum = ConversationState(to_state.lower())
        return is_valid_transition(from_enum, to_enum)
    except ValueError:
        return False


def validate_culture_generation_config(
    generation_type: str,
    authenticity: str,
    creativity: str,
    complexity: str
) -> dict:
    """
    Validate culture generation configuration using string values.
    
    Args:
        generation_type: Culture generation type as string
        authenticity: Authenticity level as string
        creativity: Creativity level as string
        complexity: Complexity level as string
        
    Returns:
        Dictionary with validation results
        
    Example:
        >>> result = validate_culture_generation_config(
        ...     'custom', 'academic', 'unrestricted', 'simple'
        ... )
        >>> print(f"Valid: {result['valid']}, Issues: {result['issues']}")
    """
    try:
        gen_type = CultureGenerationType(generation_type.lower())
        auth_level = CultureAuthenticityLevel(authenticity.lower())
        creativity_level = CultureCreativityLevel(creativity.lower())
        complexity_level = CultureComplexityLevel(complexity.lower())
        
        issues = validate_culture_configuration(
            gen_type, auth_level, creativity_level, complexity_level
        )
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'generation_type': gen_type.name,
            'authenticity_level': auth_level.name,
            'creativity_level': creativity_level.name,
            'complexity_level': complexity_level.name
        }
    except ValueError as e:
        return {
            'valid': False,
            'issues': [f"Invalid enum value: {str(e)}"],
            'generation_type': generation_type,
            'authenticity_level': authenticity,
            'creativity_level': creativity,
            'complexity_level': complexity
        }


def get_conversation_progress(current_state: str) -> dict:
    """
    Get conversation progress information for a state.
    
    Args:
        current_state: Current conversation state as string
        
    Returns:
        Dictionary with progress information
        
    Example:
        >>> progress = get_conversation_progress('concept_gathering')
        >>> print(f"Progress: {progress['percentage']}%")
    """
    try:
        state_enum = ConversationState(current_state.lower())
        return {
            'percentage': calculate_progress_percentage(state_enum),
            'phase': get_conversation_phase(state_enum).value,
            'display_name': STATE_DISPLAY_NAMES.get(state_enum, current_state),
            'description': STATE_DESCRIPTIONS.get(state_enum, ''),
            'is_terminal': is_terminal_state(state_enum),
            'is_processing': is_processing_state(state_enum),
            'timeout_minutes': get_state_timeout(state_enum)
        }
    except ValueError:
        return {
            'percentage': 0.0,
            'phase': 'unknown',
            'display_name': current_state,
            'description': 'Unknown state',
            'is_terminal': False,
            'is_processing': False,
            'timeout_minutes': None
        }


def get_culture_generation_preset(preset_name: str) -> dict:
    """
    Get culture generation configuration preset.
    
    Args:
        preset_name: Name of the preset configuration
        
    Returns:
        Dictionary with preset configuration or empty dict if not found
        
    Example:
        >>> preset = get_culture_generation_preset('academic_research')
        >>> print(f"Authenticity: {preset['authenticity'].name}")
        >>> educational_preset = get_culture_generation_preset('educational_gaming')
    """
    return CULTURE_GENERATION_PRESETS.get(preset_name.lower(), {})


def list_culture_generation_presets() -> list[str]:
    """
    Get list of available culture generation presets.
    
    Returns:
        List of preset names
        
    Example:
        >>> presets = list_culture_generation_presets()
        >>> print(f"Available presets: {presets}")
    """
    return list(CULTURE_GENERATION_PRESETS.keys())


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
    expected_domain_enums = [
        'content_type', 'creativity_level', 'balance_level', 'conversation_state',
        'culture_generation_type', 'culture_authenticity_level'  # Culture enums
    ]
    for enum_name in expected_domain_enums:
        if enum_name not in domain_enums:
            issues.append(f"Domain layer missing critical enum: {enum_name}")
    
    # Check that conversation workflow is properly integrated
    conversation_enums = get_conversation_workflow_enums()
    if not conversation_enums:
        issues.append("Conversation workflow enums not properly integrated")
    
    # 🆕 Check that culture generation system is properly integrated
    culture_enums = get_culture_generation_enums()
    if not culture_enums:
        issues.append("Culture generation enums not properly integrated")
    
    expected_culture_enums = [
        'culture_generation_type', 'culture_authenticity_level',
        'culture_source_type', 'culture_generation_status'
    ]
    for enum_name in expected_culture_enums:
        if enum_name not in culture_enums:
            issues.append(f"Missing critical culture generation enum: {enum_name}")
    
    # Check that all enums are properly accessible
    for layer, enums in ENUM_REGISTRY.items():
        for enum_name, enum_class in enums.items():
            if enum_class is None:
                issues.append(f"Enum '{enum_name}' in layer '{layer}' is None")
            elif not hasattr(enum_class, '__members__'):
                issues.append(f"'{enum_name}' in layer '{layer}' is not a valid enum")
    
    return issues


# Module metadata
__version__ = '2.2.0'
__description__ = 'Clean Architecture-compliant enumerations for D&D Creative Content Framework with conversation workflow and AI-powered culture generation'

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
Clean Architecture Usage Examples with Culture Generation:

1. Core Layer (Immutable D&D mechanics):
   >>> from core.enums import Ability, Skill, DamageType
   >>> print(Ability.STRENGTH.value)
   
2. Domain Layer (Business logic with culture generation):
   >>> from core.enums import ContentType, CreativityLevel, BalanceLevel
   >>> from core.enums import CultureGenerationType, CultureAuthenticityLevel
   >>> creativity = CreativityLevel.HIGH
   >>> culture_auth = CultureAuthenticityLevel.ACADEMIC
   >>> print(f"Culture description: {culture_auth.description}")
   
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
   >>> culture_enums = get_culture_generation_enums()
   
6. Character creation workflow with culture:
   >>> workflow_enums = get_content_creation_workflow_enums()
   >>> creativity_enum = workflow_enums['creativity_level']
   >>> culture_creativity = workflow_enums['culture_creativity_level']
   
7. Conversation workflow:
   >>> conversation_enums = get_conversation_workflow_enums()
   >>> states = conversation_enums['conversation_state']
   >>> print(f"Available states: {len(states)}")
   
8. Culture generation workflow:
   >>> culture_enums = get_culture_generation_enums()
   >>> generation_types = culture_enums['culture_generation_type']
   >>> print(f"Generation types: {[t.name for t in generation_types]}")
   
9. VTT compatibility:
   >>> vtt_enums = get_vtt_compatibility_enums()
   >>> export_formats = vtt_enums['export_format']
   
10. Conversation state validation:
    >>> valid = validate_conversation_transition('greeting', 'concept_gathering')
    >>> progress = get_conversation_progress('concept_gathering')
    
11. Culture generation configuration:
    >>> config_result = validate_culture_generation_config(
    ...     'custom', 'academic', 'conservative', 'scholarly'
    ... )
    >>> print(f"Valid config: {config_result['valid']}")
    
12. Culture generation presets:
    >>> preset = get_culture_generation_preset('academic_research')
    >>> presets = list_culture_generation_presets()
    >>> print(f"Available presets: {presets}")
   
13. Search by layer including culture:
    >>> culture_results = search_enums('culture')
    >>> domain_culture_enums = culture_results.get('domain', {})
    >>> spell_results = search_enums('spell')
    >>> core_spell_enums = spell_results.get('core', {})
   
14. Architecture compliance with culture system:
    >>> issues = validate_architecture_compliance()
    >>> print(f"Compliance status: {'PASS' if not issues else 'FAIL'}")
    
15. Culture-specific utilities:
    >>> culture_utils = get_culture_generation_utilities()
    >>> default_auth = culture_utils['get_default_authenticity_for_source']
    >>> recommended_complexity = culture_utils['get_complexity_for_authenticity']
"""