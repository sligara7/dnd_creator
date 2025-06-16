"""
Core enumerations for the D&D Creative Content Framework.

This module provides all enumerated types used throughout the system,
organized by their primary purpose and domain according to Clean Architecture principles.
SIMPLIFIED with minimal culture enums that support character creation without complexity.

Follows CREATIVE_VALIDATION_APPROACH philosophy:
- Enable creativity rather than restrict it
- Character generation support and enhancement focus
- Simple, supportive culture features
- Creative freedom is paramount
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

# Text processing enums
from .text_types import (
    EnhancedTextStyle,
    EnhancedContentType,
    TextAnalysisCategory,
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

# 🆕 SIMPLIFIED Culture Generation enums (Character creation focus)
from .culture_types import (
    # Simple core culture enums
    CultureAuthenticityLevel,
    CultureType,
    
    # Simple utility functions
    get_default_authenticity_level,
    is_gaming_optimized,
    get_available_culture_types,
    get_available_authenticity_levels
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
    
    # 🆕 SIMPLIFIED Culture Generation System (Character creation focus)
    'CultureAuthenticityLevel',
    'CultureType',
    
    # Text Processing
    'EnhancedTextStyle',
    'EnhancedContentType', 
    'TextAnalysisCategory',
    
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
    
    # 🆕 SIMPLIFIED Culture Generation Utilities (Character creation focus)
    'get_default_authenticity_level',
    'is_gaming_optimized',
    'get_available_culture_types',
    'get_available_authenticity_levels'
]

# SIMPLIFIED Enum Registry organized by Clean Architecture layers
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
        # Text processing enums
        'enhanced_text_style': EnhancedTextStyle,
        'enhanced_content_type': EnhancedContentType,
        'text_analysis_category': TextAnalysisCategory,

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
        
        # 🆕 SIMPLIFIED Culture Generation System (Character creation focus)
        'culture_authenticity_level': CultureAuthenticityLevel,
        'culture_type': CultureType,
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
        >>> culture_auth = get_enum_class('culture_authenticity_level')
        >>> culture_type = get_enum_class('culture_type')
        >>> print(list(culture_auth))
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
        >>> culture_enums = domain_enums  # Simple culture enums are in domain layer
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
        >>> culture_auth = creative_enums['culture_authenticity_level']
        >>> culture_type = creative_enums['culture_type']
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
        >>> culture_type = char_enums['culture_type']
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
        # 🆕 SIMPLIFIED Culture generation enums for character creation
        'culture_authenticity_level', 'culture_type'
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


def get_simple_culture_generation_enums() -> dict[str, type]:
    """
    Get simple culture enums for character creation.
    
    Returns:
        Dictionary of simple culture enum names to enum classes
        
    Example:
        >>> culture_enums = get_simple_culture_generation_enums()
        >>> auth_levels = culture_enums['culture_authenticity_level']
        >>> culture_types = culture_enums['culture_type']
    """
    culture_enums = {}
    culture_enum_names = ['culture_authenticity_level', 'culture_type']
    
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
    Get list of all available enum types.
    
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
        >>> simple_culture = categories['simple_culture_generation']
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
        "simple_culture_generation": [
            "culture_authenticity_level", "culture_type"
        ],
        "text_processing": [
            "enhanced_text_style", "enhanced_content_type", "text_analysis_category"
        ],
        "export_formats": [
            "export_format", "character_sheet_type", "output_layout", "content_inclusion_level"
        ]
    }


def get_text_processing_enums() -> dict[str, type]:
    """
    Get enums specifically for text processing and formatting.
    
    Returns:
        Dictionary of text processing enum names to enum classes
        
    Example:
        >>> text_enums = get_text_processing_enums()
        >>> text_styles = text_enums['enhanced_text_style']
        >>> content_types = text_enums['enhanced_content_type']
    """
    return {
        'enhanced_text_style': EnhancedTextStyle,
        'enhanced_content_type': EnhancedContentType,
        'text_analysis_category': TextAnalysisCategory
    }


def get_gaming_friendly_text_styles() -> list[str]:
    """
    Get text styles optimized for gaming utility.
    
    Returns:
        List of gaming-friendly text style names
        
    Example:
        >>> gaming_styles = get_gaming_friendly_text_styles()
        >>> print(f"Gaming text styles: {gaming_styles}")
    """
    try:
        return [style.value for style in EnhancedTextStyle if hasattr(style, 'gaming_friendliness') and style.gaming_friendliness >= 0.8]
    except (NameError, AttributeError):
        return ['title_case', 'plain', 'gaming_friendly']


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
        >>> culture_auth = get_enum_by_name('culture_authenticity_level', 'gaming')
        >>> culture_type = get_enum_by_name('culture_type', 'fantasy')
        >>> print(culture_auth.description if culture_auth else "Not found")
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
        >>> is_culture_auth_valid = validate_enum_value('culture_authenticity_level', 'gaming')
        >>> is_culture_type_valid = validate_enum_value('culture_type', 'fantasy')
        >>> print(f"Valid: {is_valid}, Culture auth valid: {is_culture_auth_valid}")
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
        >>> culture_types = get_enum_values('culture_type')
        >>> print(f"Available culture types: {culture_types}")
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
        >>> text_results = search_enums('enhanced')
        >>> enhanced_enums = text_results.get('domain', {})
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
        >>> culture_auth = workflow_enums['culture_authenticity_level']
        >>> culture_type = workflow_enums['culture_type']
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
        
        # 🆕 SIMPLIFIED Culture generation workflow (Character creation focus)
        'culture_authenticity_level': CultureAuthenticityLevel,
        'culture_type': CultureType,
        
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


def get_simple_culture_generation_utilities() -> dict[str, callable]:
    """
    Get simple culture generation utility functions.
    
    Returns:
        Dictionary of utility function names to function objects
        
    Example:
        >>> utilities = get_simple_culture_generation_utilities()
        >>> get_default_auth = utilities['get_default_authenticity_level']
        >>> is_gaming = utilities['is_gaming_optimized']
    """
    return {
        'get_default_authenticity_level': get_default_authenticity_level,
        'is_gaming_optimized': is_gaming_optimized,
        'get_available_culture_types': get_available_culture_types,
        'get_available_authenticity_levels': get_available_authenticity_levels
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


def get_simple_culture_configuration(authenticity: str = "gaming", 
                                   culture_type: str = "fantasy") -> dict:
    """
    Get simple culture configuration for character creation.
    
    Args:
        authenticity: Authenticity level as string
        culture_type: Culture type as string
        
    Returns:
        Dictionary with culture configuration
        
    Example:
        >>> config = get_simple_culture_configuration('gaming', 'fantasy')
        >>> print(f"Gaming optimized: {config['gaming_optimized']}")
        >>> print(f"Description: {config['description']}")
    """
    try:
        auth_level = CultureAuthenticityLevel(authenticity.lower())
        culture_type_enum = CultureType(culture_type.lower())
        
        return {
            'authenticity_level': auth_level.value,
            'culture_type': culture_type_enum.value,
            'gaming_optimized': auth_level.is_gaming_friendly,
            'description': auth_level.description,
            'culture_description': culture_type_enum.description,
            'character_ready': True,
            'suggestions': [
                f"Configuration ready for character creation",
                f"Using {auth_level.description.lower()}",
                f"Culture type: {culture_type_enum.description.lower()}"
            ]
        }
    except ValueError as e:
        # Fallback configuration
        return {
            'authenticity_level': authenticity,
            'culture_type': culture_type,
            'gaming_optimized': True,
            'description': "Gaming table optimized - easy to pronounce and use during play",
            'culture_description': "Generic fantasy culture suitable for any campaign",
            'character_ready': True,
            'suggestions': [
                f"Configuration needs attention ({str(e)}) but is still usable",
                "Try 'gaming' authenticity with 'fantasy' type for optimal results",
                "Culture features are optional - continue with character creation"
            ]
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


def validate_simple_culture_architecture_compliance() -> dict[str, any]:
    """
    Validate that simple culture enum organization supports character creation.
    
    Returns:
        Dictionary with simple culture compliance assessment
        
    Example:
        >>> compliance = validate_simple_culture_architecture_compliance()
        >>> print(f"Character creation ready: {compliance['character_generation_ready']}")
        >>> print(f"Simple culture available: {compliance['simple_culture_available']}")
    """
    compliance_assessment = {
        'character_generation_ready': True,  # Always ready approach
        'simple_culture_available': False,
        'culture_support_score': 0.0,
        'enhancement_opportunities': [],
        'culture_features_available': {},
        'architecture_alignment': True
    }
    
    try:
        # Check simple culture enum availability
        culture_enums = get_simple_culture_generation_enums()
        expected_culture_enums = ['culture_authenticity_level', 'culture_type']
        
        available_enums = 0
        for enum_name in expected_culture_enums:
            if enum_name in culture_enums:
                available_enums += 1
            else:
                compliance_assessment['enhancement_opportunities'].append(
                    f"Consider adding {enum_name} for character creation support"
                )
        
        # Check if both essential enums are available
        simple_culture_available = (
            'culture_authenticity_level' in culture_enums and
            'culture_type' in culture_enums
        )
        compliance_assessment['simple_culture_available'] = simple_culture_available
        
        # Calculate culture support score
        compliance_assessment['culture_support_score'] = available_enums / len(expected_culture_enums)
        
        # Check simple utility functions
        culture_utilities = get_simple_culture_generation_utilities()
        expected_utilities = [
            'get_default_authenticity_level',
            'is_gaming_optimized',
            'get_available_culture_types',
            'get_available_authenticity_levels'
        ]
        
        for utility_name in expected_utilities:
            if utility_name in culture_utilities:
                compliance_assessment['culture_features_available'][utility_name] = True
            else:
                compliance_assessment['culture_features_available'][utility_name] = False
                compliance_assessment['enhancement_opportunities'].append(
                    f"Consider implementing {utility_name} for better character support"
                )
        
        # Always provide encouragement
        if compliance_assessment['culture_support_score'] >= 0.8 and simple_culture_available:
            compliance_assessment['enhancement_opportunities'].append(
                "Excellent simple culture system - ready for character creation!"
            )
        elif compliance_assessment['culture_support_score'] >= 0.5:
            compliance_assessment['enhancement_opportunities'].append(
                "Good simple culture foundation - supports character creation"
            )
        else:
            compliance_assessment['enhancement_opportunities'].append(
                "Simple culture system has potential - basic features will help character creation"
            )
            
    except Exception as e:
        # Even errors are constructive
        compliance_assessment['enhancement_opportunities'].append(
            f"Simple culture system assessment encountered minor issues ({str(e)}) but system is still usable"
        )
    
    return compliance_assessment


# Module metadata - SIMPLIFIED for simple culture approach
__version__ = '1.0.0'  # SIMPLIFIED: Version reset for simple culture approach
__description__ = 'Clean Architecture-compliant enumerations for D&D Creative Content Framework with simple culture support focused on character creation'

# SIMPLIFIED Configuration
ENABLE_ENUM_CACHING = True
STRICT_VALIDATION = False  # Creative approach is permissive
SIMPLE_CULTURE_COMPLIANCE_CHECK = True  # Simple culture compliance

# Simple culture compliance validation on import
if SIMPLE_CULTURE_COMPLIANCE_CHECK:
    _culture_compliance = validate_simple_culture_architecture_compliance()
    if _culture_compliance['culture_support_score'] < 0.5:
        import warnings
        warnings.warn(
            f"Simple culture system enhancement opportunities: {_culture_compliance['enhancement_opportunities'][:2]}", 
            ImportWarning
        )

# SIMPLIFIED Usage examples in docstring
"""
Clean Architecture Usage Examples with Simple Culture Generation:

1. Core Layer (Immutable D&D mechanics):
   >>> from core.enums import Ability, Skill, DamageType
   >>> print(Ability.STRENGTH.value)
   
2. Domain Layer (Business logic with simple culture generation):
   >>> from core.enums import ContentType, CreativityLevel, BalanceLevel
   >>> from core.enums import CultureAuthenticityLevel, CultureType
   >>> creativity = CreativityLevel.HIGH
   >>> culture_auth = CultureAuthenticityLevel.GAMING
   >>> culture_type = CultureType.FANTASY
   >>> print(f"Gaming friendly: {culture_auth.is_gaming_friendly}")
   >>> print(f"Description: {culture_type.description}")
   
3. Simple culture configuration:
   >>> config = get_simple_culture_configuration('gaming', 'fantasy')
   >>> print(f"Gaming optimized: {config['gaming_optimized']}")
   >>> print(f"Character ready: {config['character_ready']}")
   
4. Character creation workflow:
   >>> workflow_enums = get_content_creation_workflow_enums()
   >>> culture_auth = workflow_enums['culture_authenticity_level']
   >>> culture_type = workflow_enums['culture_type']
   
5. Simple culture utilities:
   >>> utilities = get_simple_culture_generation_utilities()
   >>> default_auth = utilities['get_default_authenticity_level']()
   >>> print(f"Default authenticity: {default_auth.value}")
   
6. Available culture options:
   >>> auth_levels = get_available_authenticity_levels()
   >>> culture_types = get_available_culture_types()
   >>> print(f"Available auth levels: {[a.value for a in auth_levels]}")
   >>> print(f"Available culture types: {[c.value for c in culture_types]}")
   
7. Gaming optimization check:
   >>> auth_level = CultureAuthenticityLevel.GAMING
   >>> is_optimized = is_gaming_optimized(auth_level)
   >>> print(f"Gaming optimized: {is_optimized}")
   
8. Simple culture enum validation:
   >>> is_valid_auth = validate_enum_value('culture_authenticity_level', 'gaming')
   >>> is_valid_type = validate_enum_value('culture_type', 'fantasy')
   >>> print(f"Valid auth: {is_valid_auth}, Valid type: {is_valid_type}")
   
9. Culture enum discovery:
   >>> culture_enums = get_simple_culture_generation_enums()
   >>> print(f"Available culture enums: {list(culture_enums.keys())}")
   
10. System compliance check:
    >>> compliance = validate_simple_culture_architecture_compliance()
    >>> print(f"System ready: {compliance['character_generation_ready']}")
    >>> print(f"Culture support: {compliance['culture_support_score']:.2f}")
"""