"""
Essential D&D Exceptions Package

Streamlined exceptions package following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
Unified access to all D&D character creator exception types.
"""

# ============ BASE EXCEPTIONS ============

from .base import (
    # Base exception class
    DnDCharacterCreatorError,
    
    # Validation exceptions
    ValidationError,
    RuleViolationError,
    CompatibilityError,
    
    # Data exceptions
    DataNotFoundError,
    DataCorruptionError,
    
    # Character creation exceptions
    CharacterCreationError,
    InvalidChoiceError,
    
    # System exceptions
    ConfigurationError,
    ResourceError,
    
    # Utility functions
    create_validation_error,
    create_rule_violation,
    create_data_not_found,
    is_recoverable_error,
    get_error_severity,
)

# ============ BALANCE EXCEPTIONS ============

from .balance import (
    # Power balance exceptions
    PowerLevelError,
    StatArrayError, 
    PointBuyError,
    
    # Campaign balance exceptions
    DifficultyMismatchError,
    TierImbalanceError,
    
    # Equipment balance exceptions
    WealthImbalanceError,
    MagicItemImbalanceError,
    
    # Multiclass balance exceptions
    MulticlassImbalanceError,
    
    # Utility functions
    create_power_level_error,
    create_stat_array_error,
    create_point_buy_error,
    is_balance_critical,
    get_balance_severity,
    requires_dm_approval,
)

# ============ CULTURAL EXCEPTIONS ============

from .culture import (
    # Cultural compatibility exceptions
    CulturalMismatchError,
    LanguageConflictError, 
    SocialStructureError,
    
    # Cultural values exceptions
    ValueSystemError,
    WorldviewConflictError,
    
    # Religious practice exceptions
    ReligiousConflictError,
    
    # Artistic tradition exceptions
    ArtisticTraditionError,
    
    # Settlement type exceptions
    SettlementMismatchError,
    
    # Utility functions
    create_cultural_mismatch,
    create_language_conflict,
    create_value_system_error,
    is_cultural_flexibility_allowed,
    requires_cultural_explanation,
    get_cultural_severity,
)

# ============ EXPORT EXCEPTIONS ============

from .export import (
    # Format exceptions
    UnsupportedFormatError,
    FormatCorruptionError,
    
    # Content exceptions
    IncompleteDataError,
    ContentFilterError,
    
    # Output exceptions
    OutputGenerationError,
    FileWriteError,
    
    # Template exceptions
    TemplateError,
    LayoutError,
    
    # Compression exceptions
    CompressionError,
    
    # Utility functions
    create_unsupported_format_error,
    create_incomplete_data_error,
    create_output_generation_error,
    is_recoverable_export_error,
    requires_user_intervention,
    get_export_error_severity,
)

# ============ GENERATION EXCEPTIONS ============

from .generation import (
    # Content generation exceptions
    GenerationFailureError,
    CreativityConstraintError,
    InsufficientDataError,
    
    # Template generation exceptions
    TemplateProcessingError,
    VariableSubstitutionError,
    
    # Name generation exceptions
    NameGenerationError,
    NameConflictError,
    
    # Backstory generation exceptions
    BackstoryGenerationError,
    InconsistentBackstoryError,
    
    # Random generation exceptions
    RandomSeedError,
    
    # Utility functions
    create_generation_failure,
    create_creativity_constraint,
    create_insufficient_data_error,
    is_retryable_generation_error,
    requires_manual_intervention,
    get_generation_error_severity,
)

# ============ INTEGRATION EXCEPTIONS ============

from .integration import (
    # System integration exceptions
    ServiceIntegrationError,
    APIConnectionError,
    AuthenticationError,
    
    # Data integration exceptions
    DataSyncError,
    DataFormatMismatchError,
    VersionMismatchError,
    
    # Workflow integration exceptions
    WorkflowInterruptionError,
    StateTransitionError,
    
    # Dependency integration exceptions
    DependencyError,
    ModuleImportError,
    
    # Utility functions
    create_service_integration_error,
    create_api_connection_error,
    create_data_sync_error,
    is_retryable_integration_error,
    requires_system_admin,
    get_integration_error_severity,
    is_configuration_issue,
)

# ============ PERSISTENCE EXCEPTIONS ============

from .persistence import (
    # Data persistence exceptions
    SaveError,
    LoadError,
    DeleteError,
    
    # Storage system exceptions
    StorageConnectionError,
    StorageCapacityError,
    StoragePermissionError,
    
    # Data integrity exceptions
    # DataCorruptionError - imported from base to avoid conflict
    VersionConflictError,
    TransactionError,
    
    # Cache exceptions
    CacheError,
    
    # Utility functions
    create_save_error,
    create_load_error,
    create_storage_connection_error,
    is_retryable_persistence_error,
    is_data_integrity_issue,
    requires_admin_intervention,
    get_persistence_error_severity,
)

# ============ WORKFLOW EXCEPTIONS ============

from .workflow import (
    # Character creation workflow exceptions
    WorkflowStateError,
    InvalidTransitionError,
    # WorkflowInterruptionError - imported from integration to avoid conflict
    
    # Step validation exceptions
    StepValidationError,
    IncompleteStepError,
    PrerequisiteError,
    
    # User input exceptions
    UserInputError,
    TimeoutError,
    
    # Completion exceptions
    WorkflowCompletionError,
    FinalValidationError,
    
    # Utility functions
    create_workflow_state_error,
    create_invalid_transition_error,
    create_step_validation_error,
    is_recoverable_workflow_error,
    requires_workflow_restart,
    can_continue_workflow,
    get_workflow_error_severity,
)

# ============ CONVENIENCE GROUPINGS ============

# Character creation specific exceptions
CHARACTER_CREATION_ERRORS = {
    'validation': [ValidationError, StepValidationError, FinalValidationError],
    'rules': [RuleViolationError, CompatibilityError, PrerequisiteError],
    'balance': [PowerLevelError, StatArrayError, PointBuyError],
    'culture': [CulturalMismatchError, LanguageConflictError, ValueSystemError],
    'workflow': [WorkflowStateError, InvalidTransitionError, IncompleteStepError],
}

# System operation exceptions
SYSTEM_OPERATION_ERRORS = {
    'persistence': [SaveError, LoadError, StorageConnectionError],
    'integration': [ServiceIntegrationError, APIConnectionError, DataSyncError],
    'generation': [GenerationFailureError, NameGenerationError, BackstoryGenerationError],
    'export': [UnsupportedFormatError, OutputGenerationError, FileWriteError],
}

# Error severity classifications
ERROR_SEVERITY_LEVELS = {
    'critical': [
        DataCorruptionError, StorageConnectionError, AuthenticationError,
        DependencyError, ModuleImportError, StorageCapacityError
    ],
    'error': [
        PowerLevelError, RuleViolationError, WorkflowStateError,
        GenerationFailureError, SaveError, LoadError
    ],
    'warning': [
        ValidationError, CulturalMismatchError, StepValidationError,
        BackstoryGenerationError, VersionConflictError
    ],
    'info': [
        NameConflictError, UserInputError, ContentFilterError,
        LanguageConflictError, ValueSystemError
    ]
}

# Recoverable vs non-recoverable errors
RECOVERABLE_ERRORS = [
    ValidationError, InvalidChoiceError, CompatibilityError,
    StepValidationError, IncompleteStepError, UserInputError,
    NameGenerationError, BackstoryGenerationError, CulturalMismatchError
]

NON_RECOVERABLE_ERRORS = [
    DataCorruptionError, StorageConnectionError, DependencyError,
    ModuleImportError, AuthenticationError, ConfigurationError
]

# ============ UTILITY FUNCTIONS ============

def get_error_category(error: DnDCharacterCreatorError) -> str:
    """Get the category of an exception."""
    for category, error_types in CHARACTER_CREATION_ERRORS.items():
        if any(isinstance(error, error_type) for error_type in error_types):
            return f"character_creation.{category}"
    
    for category, error_types in SYSTEM_OPERATION_ERRORS.items():
        if any(isinstance(error, error_type) for error_type in error_types):
            return f"system_operation.{category}"
    
    return "unknown"

def get_unified_error_severity(error: DnDCharacterCreatorError) -> str:
    """Get unified error severity across all exception types."""
    for severity, error_types in ERROR_SEVERITY_LEVELS.items():
        if any(isinstance(error, error_type) for error_type in error_types):
            return severity
    return "error"

def is_user_actionable(error: DnDCharacterCreatorError) -> bool:
    """Check if error can be resolved by user action."""
    return any(isinstance(error, error_type) for error_type in RECOVERABLE_ERRORS)

def requires_technical_support(error: DnDCharacterCreatorError) -> bool:
    """Check if error requires technical support intervention."""
    return any(isinstance(error, error_type) for error_type in NON_RECOVERABLE_ERRORS)

def format_error_for_user(error: DnDCharacterCreatorError) -> Dict[str, Any]:
    """Format error for user-friendly display."""
    return {
        "type": error.__class__.__name__,
        "message": error.message,
        "category": get_error_category(error),
        "severity": get_unified_error_severity(error),
        "recoverable": is_user_actionable(error),
        "requires_support": requires_technical_support(error),
        "details": error.details
    }

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Base exceptions
    'DnDCharacterCreatorError', 'ValidationError', 'RuleViolationError',
    'CompatibilityError', 'DataNotFoundError', 'DataCorruptionError',
    'CharacterCreationError', 'InvalidChoiceError', 'ConfigurationError',
    'ResourceError',
    
    # Balance exceptions
    'PowerLevelError', 'StatArrayError', 'PointBuyError',
    'DifficultyMismatchError', 'TierImbalanceError', 'WealthImbalanceError',
    'MagicItemImbalanceError', 'MulticlassImbalanceError',
    
    # Cultural exceptions
    'CulturalMismatchError', 'LanguageConflictError', 'SocialStructureError',
    'ValueSystemError', 'WorldviewConflictError', 'ReligiousConflictError',
    'ArtisticTraditionError', 'SettlementMismatchError',
    
    # Export exceptions
    'UnsupportedFormatError', 'FormatCorruptionError', 'IncompleteDataError',
    'ContentFilterError', 'OutputGenerationError', 'FileWriteError',
    'TemplateError', 'LayoutError', 'CompressionError',
    
    # Generation exceptions
    'GenerationFailureError', 'CreativityConstraintError', 'InsufficientDataError',
    'TemplateProcessingError', 'VariableSubstitutionError', 'NameGenerationError',
    'NameConflictError', 'BackstoryGenerationError', 'InconsistentBackstoryError',
    'RandomSeedError',
    
    # Integration exceptions
    'ServiceIntegrationError', 'APIConnectionError', 'AuthenticationError',
    'DataSyncError', 'DataFormatMismatchError', 'VersionMismatchError',
    'WorkflowInterruptionError', 'StateTransitionError', 'DependencyError',
    'ModuleImportError',
    
    # Persistence exceptions
    'SaveError', 'LoadError', 'DeleteError', 'StorageConnectionError',
    'StorageCapacityError', 'StoragePermissionError', 'VersionConflictError',
    'TransactionError', 'CacheError',
    
    # Workflow exceptions
    'WorkflowStateError', 'InvalidTransitionError', 'StepValidationError',
    'IncompleteStepError', 'PrerequisiteError', 'UserInputError',
    'TimeoutError', 'WorkflowCompletionError', 'FinalValidationError',
    
    # Convenience groupings
    'CHARACTER_CREATION_ERRORS', 'SYSTEM_OPERATION_ERRORS',
    'ERROR_SEVERITY_LEVELS', 'RECOVERABLE_ERRORS', 'NON_RECOVERABLE_ERRORS',
    
    # Utility functions (most commonly used)
    'get_error_category', 'get_unified_error_severity', 'is_user_actionable',
    'requires_technical_support', 'format_error_for_user',
    'create_validation_error', 'create_rule_violation', 'is_recoverable_error',
    'get_error_severity',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D character creator exceptions package'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/exceptions",
    "purpose": "unified_exception_access",
    "line_target": 300,
    "simplified_imports": True,
    "convenience_groupings": True,
    "essential_utilities": True,
    "dependencies": [
        "base", "balance", "culture", "export", "generation",
        "integration", "persistence", "workflow"
    ],
    "philosophy": "crude_functional_inspired_simplicity"
}