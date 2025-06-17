"""
Essential D&D Enums Package

Streamlined enums package following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
Unified access to all D&D 5e/2024 enumeration types.
"""

# ============ CORE GAME MECHANICS ============

from .game_mechanics import (
    # Abilities and skills
    AbilityScore,
    SavingThrow,
    SkillType,
    
    # Combat mechanics
    ActionEconomy,
    AttackType,
    DamageType,
    Condition,
    
    # Magic mechanics
    SpellSchool,
    SpellLevel,
    CastingTime,
    SpellRange,
    
    # Dice and advantage
    DiceType,
    AdvantageType,
    
    # Mappings and utilities
    ABILITY_SKILLS,
    get_ability_modifier,
    get_proficiency_bonus,
    is_physical_ability,
    is_mental_ability,
    get_skill_ability,
    is_damaging_spell_school,
    is_control_spell_school,
)

# ============ CONTENT CLASSIFICATION ============

from .content_types import (
    # Character content
    CharacterElement,
    SourceType,
    ContentRarity,
    
    # Game mechanics
    MechanicType,
    ActionType,
    DurationType,
    
    # Equipment
    EquipmentCategory,
    WeaponType,
    ArmorType,
    
    # Spells
    SpellComponent,
    SpellTarget,
    AreaType,
    
    # Validation
    ValidationLevel,
    ContentStatus,
    
    # Mappings and utilities
    CONTENT_CATEGORIES,
    ACTION_PRIORITY,
    is_official_content,
    requires_approval,
    get_spell_components,
    is_combat_relevant,
)

# ============ CULTURE AND WORLD BUILDING ============

from .culture_types import (
    # Core culture types
    CultureType,
    SettlementType,
    SocialStructure,
    
    # Cultural characteristics
    CulturalValue,
    Worldview,
    ReligiousPractice,
    ArtisticTradition,
    
    # Language and communication
    LanguageFamily,
    CommunicationStyle,
    
    # Mappings and utilities
    CULTURE_DEFAULTS,
    get_culture_defaults,
    is_urban_culture,
    is_hierarchical,
    values_tradition,
    is_nature_focused,
    uses_formal_communication,
)

# ============ CREATIVITY AND GENERATION ============

from .creativity_levels import (
    # Core creativity levels
    CreativityLevel,
    CustomizationScope,
    HomebrewLevel,
    
    # Generation creativity
    GenerationStyle,
    NameCreativity,
    BackstoryDepth,
    
    # Rule interpretation
    RuleFlexibility,
    OptionalRules,
    
    # Profiles and utilities
    CREATIVITY_PROFILES,
    get_creativity_profile,
    allows_homebrew,
    allows_customization,
    is_conservative_approach,
    requires_approval as requires_creativity_approval,
    get_backstory_complexity,
    is_rules_flexible,
)

# ============ BALANCE AND DIFFICULTY ============

from .balance_levels import (
    # Power balance
    PowerLevel,
    BalanceTier,
    CampaignStyle,
    
    # Mechanical balance
    StatGenMethod,
    WealthLevel,
    MagicItemRarity,
    
    # Encounter balance
    DifficultyScale,
    RestFrequency,
    
    # Configuration and utilities
    BALANCE_PROFILES,
    get_balance_profile,
    get_tier_for_level,
    is_balanced_combination,
)

# ============ VALIDATION FRAMEWORK ============

from .validation_types import (
    # Validation results
    ValidationResult,
    ValidationSeverity,
    ValidationScope,
    
    # Character validation
    CharacterValidation,
    RuleCompliance,
    ContentValidation,
    
    # Input validation
    InputType,
    DataFormat,
    
    # Validation strategies
    ValidationStrategy,
    ErrorHandling,
    
    # Mappings and utilities
    VALIDATION_PRIORITIES,
    COMPLIANCE_STRICTNESS,
    VALIDATION_SCOPES,
    is_blocking_issue,
    requires_user_attention,
    get_validation_priority,
    is_strict_validation,
    get_compliance_threshold,
    supports_deferred_validation,
    is_creation_validation,
    continues_on_error,
)

# ============ CHARACTER PROGRESSION ============

from .progression_types import (
    # Progression types
    ProgressionType,
    LevelTier,
    AdvancementRate,
    
    # Ability progression
    ASIType,
    StatProgression,
    
    # Skill progression
    ProficiencyGrowth,
    LanguageProgression,
    
    # Spell progression
    SpellProgression,
    SpellKnownType,
    
    # Feature progression
    FeatureType,
    ScalingType,
    
    # Mappings and utilities
    TIER_LEVEL_RANGES,
    ASI_LEVELS,
    SPELL_SLOT_PROGRESSION,
    get_tier_for_level as get_progression_tier,
    get_asi_levels,
    has_asi_at_level,
    get_spell_slot_multiplier,
    is_caster,
    requires_spell_preparation,
    scales_with_level,
)

# ============ EXPORT AND FORMATTING ============

from .export_formats import (
    # Core format types
    ExportFormat,
    OutputTarget,
    CompressionLevel,
    
    # Content options
    DetailLevel,
    IncludeOptions,
    
    # Format-specific options
    PDFLayout,
    HTMLTheme,
    TextFormat,
    
    # Configuration and utilities
    EXPORT_PRESETS,
    FORMAT_EXTENSIONS,
    get_export_preset,
    get_file_extension,
    supports_compression,
    is_binary_format,
    requires_styling,
    is_structured_data,
    get_mime_type,
)

# ============ CONVERSATION AND WORKFLOW ============

from .conversation_states import (
    # Core states
    CreationState,
    InputState,
    ValidationState,
    
    # Flow control
    FlowDirection,
    UserIntent,
    ResponseType,
    
    # Modification
    ModificationState,
    EditMode,
    
    # Error handling
    ErrorLevel,
    HelpContext,
    
    # Flow mappings and utilities
    CREATION_FLOW,
    VALID_BACK_STATES,
    get_next_state,
    get_previous_state,
    can_go_back,
    is_creation_complete,
    requires_user_input,
    is_error_state,
    get_help_for_state,
)

# ============ TEXT PROCESSING ============

from .text_types import (
    # Content types
    TextContentType,
    DescriptiveText,
    NarrativeText,
    
    # Formatting
    TextFormat as TextFormatType,
    TextLength,
    TextStyle,
    
    # Language and tone
    LanguageStyle,
    ToneType,
    
    # Generation
    GenerationStyle as TextGenerationStyle,
    ContentDepth,
    ValidationLevel as TextValidationLevel,
    
    # Mappings and utilities
    CONTENT_CATEGORIES as TEXT_CONTENT_CATEGORIES,
    STYLE_COMPATIBILITY,
    get_max_length,
    is_formatted_text,
    requires_processing,
    is_creative_content,
    get_appropriate_length,
    supports_rich_formatting,
)

# ============ CONVENIENCE GROUPINGS ============

# Core D&D mechanics for character creation
CORE_MECHANICS = {
    'abilities': AbilityScore,
    'skills': SkillType,
    'damage_types': DamageType,
    'conditions': Condition,
    'spell_schools': SpellSchool,
    'dice_types': DiceType,
}

# Character creation workflow enums
CHARACTER_CREATION = {
    'states': CreationState,
    'validation': ValidationResult,
    'progression': ProgressionType,
    'content': CharacterElement,
    'balance': PowerLevel,
}

# Content generation and creativity
CONTENT_GENERATION = {
    'creativity': CreativityLevel,
    'generation': GenerationStyle,
    'culture': CultureType,
    'text_style': TextStyle,
    'balance': BalanceTier,
}

# Validation and compliance
VALIDATION_FRAMEWORK = {
    'results': ValidationResult,
    'severity': ValidationSeverity,
    'compliance': RuleCompliance,
    'strategies': ValidationStrategy,
    'content': ContentValidation,
}

# Export and output
EXPORT_SYSTEM = {
    'formats': ExportFormat,
    'targets': OutputTarget,
    'detail': DetailLevel,
    'layouts': PDFLayout,
    'themes': HTMLTheme,
}

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Core game mechanics
    'AbilityScore', 'SavingThrow', 'SkillType', 'ActionEconomy', 'AttackType',
    'DamageType', 'Condition', 'SpellSchool', 'SpellLevel', 'CastingTime',
    'SpellRange', 'DiceType', 'AdvantageType',
    
    # Content classification
    'CharacterElement', 'SourceType', 'ContentRarity', 'MechanicType',
    'ActionType', 'DurationType', 'EquipmentCategory', 'WeaponType',
    'ArmorType', 'SpellComponent', 'SpellTarget', 'AreaType',
    
    # Culture and world building
    'CultureType', 'SettlementType', 'SocialStructure', 'CulturalValue',
    'Worldview', 'ReligiousPractice', 'ArtisticTradition', 'LanguageFamily',
    'CommunicationStyle',
    
    # Creativity and generation
    'CreativityLevel', 'CustomizationScope', 'HomebrewLevel', 'GenerationStyle',
    'NameCreativity', 'BackstoryDepth', 'RuleFlexibility', 'OptionalRules',
    
    # Balance and difficulty
    'PowerLevel', 'BalanceTier', 'CampaignStyle', 'StatGenMethod',
    'WealthLevel', 'MagicItemRarity', 'DifficultyScale', 'RestFrequency',
    
    # Validation framework
    'ValidationResult', 'ValidationSeverity', 'ValidationScope',
    'CharacterValidation', 'RuleCompliance', 'ContentValidation',
    'InputType', 'DataFormat', 'ValidationStrategy', 'ErrorHandling',
    
    # Character progression
    'ProgressionType', 'LevelTier', 'AdvancementRate', 'ASIType',
    'StatProgression', 'ProficiencyGrowth', 'LanguageProgression',
    'SpellProgression', 'SpellKnownType', 'FeatureType', 'ScalingType',
    
    # Export and formatting
    'ExportFormat', 'OutputTarget', 'CompressionLevel', 'DetailLevel',
    'IncludeOptions', 'PDFLayout', 'HTMLTheme', 'TextFormat',
    
    # Conversation and workflow
    'CreationState', 'InputState', 'ValidationState', 'FlowDirection',
    'UserIntent', 'ResponseType', 'ModificationState', 'EditMode',
    'ErrorLevel', 'HelpContext',
    
    # Text processing
    'TextContentType', 'DescriptiveText', 'NarrativeText', 'TextFormatType',
    'TextLength', 'TextStyle', 'LanguageStyle', 'ToneType',
    'TextGenerationStyle', 'ContentDepth', 'TextValidationLevel',
    
    # Convenience groupings
    'CORE_MECHANICS', 'CHARACTER_CREATION', 'CONTENT_GENERATION',
    'VALIDATION_FRAMEWORK', 'EXPORT_SYSTEM',
    
    # Essential utility functions (most commonly used)
    'get_ability_modifier', 'get_proficiency_bonus', 'get_tier_for_level',
    'is_blocking_issue', 'requires_user_attention', 'get_next_state',
    'get_previous_state', 'is_creation_complete',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D 5e/2024 enums package'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/enums",
    "purpose": "unified_enum_access",
    "line_target": 400,
    "simplified_imports": True,
    "convenience_groupings": True,
    "essential_utilities": True,
    "dependencies": [
        "game_mechanics", "content_types", "culture_types", "creativity_levels",
        "balance_levels", "validation_types", "progression_types", 
        "export_formats", "conversation_states", "text_types"
    ],
    "philosophy": "crude_functional_inspired_simplicity"
}