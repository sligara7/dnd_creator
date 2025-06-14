"""Centralized exception imports and utilities."""
# - Import all exception types
# - Exception factory functions
# - Common error handling utilities
# - Exception categorization helpers

"""
Core domain exceptions for the D&D Creative Content Framework.

This module provides a comprehensive set of exceptions for content generation,
validation failures, and D&D rule violations, supporting robust error handling
and debugging throughout the framework.
"""

# Base Exceptions
from .base import (
    BaseFrameworkError,
    DnDFrameworkError,
    ValidationError,
    SchemaValidationError,
    FieldValidationError,
    DataIntegrityError,
    ReferenceValidationError,
    BusinessRuleValidationError,
    ContentValidationError,
    FormatValidationError,
    ValidationPipelineError,
    ValidationTimeoutError,
    ValidationConfigError,
    ValidationDependencyError,
    ValidationBatchError,
    ValidationResult,
    categorize_validation_error,
    get_validation_severity_level,
    is_critical_validation_error,
    group_validation_errors_by_field,
    group_validation_errors_by_type,
    create_validation_summary,
)

# Generation Errors
from .generation import (
    GenerationError,
    GenerationWorkflowError,
    LLMProviderError,
    LLMConnectionError,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMQuotaExceededError,
    LLMResponseError,
    LLMContentFilterError,
    CharacterGenerationError,
    CharacterConceptError,
    CharacterBuildError,
    CharacterProgressionError,
    CustomContentError,
    ContentBalanceError,
    ContentThemeError,
    ContentComplexityError,
    TemplateError,
    TemplateMissingError,
    TemplateVariableError,
    PromptProcessingError,
    GenerationConstraintError,
    CreativityLimitError,
    BalanceLimitError,
    ContentGenerationTimeoutError,
    ContentGenerationLimitError,
    IterationLimitError,
    ContentDependencyError,
    ConversationFlowError,
    ConversationStateError,
    ConversationContextError,
    categorize_generation_error,
    is_retryable_generation_error,
    get_retry_delay_for_error,
    extract_recovery_suggestions,
    create_generation_error_context,
    should_fail_fast,
)

# Balance and Rule Violation Errors
from .balance import (
    BalanceError,
    ValidationError as BalanceValidationError,  # Alias to avoid conflict
    RuleViolationError,
    AbilityScoreViolation,
    CharacterLevelViolation,
    MulticlassViolation,
    ProficiencyViolation,
    SpellcastingViolation,
    ContentBalanceError as BalanceContentError,  # Alias to avoid conflict
    PowerLevelViolation,
    RarityMismatchError,
    ThemeConsistencyError,
    MechanicalComplexityError,
    ValidationPipelineError as BalanceValidationPipelineError,  # Alias
    SchemaValidationError as BalanceSchemaValidationError,  # Alias
    FieldValidationError as BalanceFieldValidationError,  # Alias
    DataIntegrityError as BalanceDataIntegrityError,  # Alias
    ReferenceValidationError as BalanceReferenceValidationError,  # Alias
    ValidationResult as BalanceValidationResult,  # Alias
    BalanceAnalysisResult,
    categorize_balance_error,
    get_validation_severity_level as get_balance_validation_severity_level,
    is_critical_validation_error as is_critical_balance_error,
    is_core_rule_violation,
    suggest_balance_fix,
    group_validation_errors_by_field as group_balance_errors_by_field,
    group_validation_errors_by_type as group_balance_errors_by_type,
    group_balance_errors_by_category,
    create_validation_summary as create_balance_summary,
    validate_content_balance,
)

# Workflow and Use Case Errors
from .workflow import (
    WorkflowError,
    UseCaseError,
    UseCaseExecutionError,
    UseCaseValidationError,
    UseCasePreconditionError,
    UseCasePostconditionError,
    UseCaseTimeoutError,
    UseCaseDependencyError,
    CharacterWorkflowError,
    CharacterCreationWorkflowError,
    CharacterUpdateWorkflowError,
    CharacterLevelUpWorkflowError,
    CharacterValidationWorkflowError,
    CampaignWorkflowError,
    CampaignCreationWorkflowError,
    PlayerInvitationWorkflowError,
    CampaignSessionWorkflowError,
    BusinessProcessError,
    CharacterBusinessRuleError,
    CampaignBusinessRuleError,
    ApplicationServiceError,
    WorkflowStateError,
    WorkflowTimeoutError,
    InvalidWorkflowTransitionError,
    WorkflowOrchestrationError,
    WorkflowDependencyError,
    ParallelWorkflowError,
    WorkflowCompensationError,
    categorize_workflow_error,
    is_retryable_workflow_error,
    get_workflow_retry_delay,
    get_workflow_recovery_suggestions,
    create_workflow_error_context,
    validate_workflow_preconditions,
)

# Export and Format Conversion Errors
from .export import (
    ExportError,
    VTTExportError,
    DNDBeyondExportError,
    Roll20ExportError,
    FantasyGroundsExportError,
    FoundryVTTExportError,
    EncounterPlusExportError,
    FormatConversionError,
    JSONExportError,
    XMLExportError,
    PDFExportError,
    CSVExportError,
    TemplateRenderingError,
    TemplateMissingError as ExportTemplateMissingError,  # Alias
    TemplateVariableError as ExportTemplateVariableError,  # Alias
    TemplateSyntaxError,
    CharacterSheetExportError,
    CharacterDataIncompleteError,
    CharacterSheetLayoutError,
    CustomContentExportError,
    ContentTypeNotSupportedError,
    UnsupportedContentError,
    ContentComplexityExportError,
    ExportQualityError,
    ExportValidationError,
    ExportTimeoutError,
    ExportResourceError,
    ExportFileSizeError,
    categorize_export_error,
    is_retryable_export_error,
    get_export_retry_delay,
    get_export_recovery_suggestions,
    get_export_format_alternatives,
    create_export_error_context,
    validate_export_requirements,
)

# Persistence and Repository Errors
from .persistence import (
    PersistenceError,
    RepositoryError,
    DatabaseConnectionError,
    DatabaseUnavailableError,
    ConnectionPoolExhaustedError,
    EntityNotFoundError,
    CharacterNotFoundError,
    CampaignNotFoundError,
    UserNotFoundError,
    ContentNotFoundError,
    PersistenceDataIntegrityError,
    ForeignKeyViolationError,
    UniqueConstraintViolationError,
    CheckConstraintViolationError,
    OptimisticLockingError,
    RepositoryOperationError,
    CreateOperationError,
    UpdateOperationError,
    DeleteOperationError,
    QueryOperationError,
    BulkOperationError,
    TransactionError,
    TransactionRollbackError,
    TransactionTimeoutError,
    DeadlockError,
    RepositoryConfigurationError,
    RepositoryInitializationError,
    DataMigrationError,
    MigrationRollbackError,
    categorize_persistence_error,
    is_retryable_persistence_error,
    get_persistence_retry_delay,
    get_persistence_recovery_suggestions,
    analyze_constraint_violation,
)

# Integration and External Service Errors
from .integration import (
    IntegrationError,
    ExternalServiceError,
    APIIntegrationError,
    APIConnectionError,
    APITimeoutError,
    APIRateLimitError,
    APIAuthenticationError,
    APIResponseError,
    ServiceProviderError,
    LLMProviderError as IntegrationLLMProviderError,  # Alias
    VTTProviderError,
    ContentProviderError,
    DataSynchronizationError,
    SyncConflictError,
    SyncTimeoutError,
    WebhookError,
    WebhookValidationError,
    RealTimeUpdateError,
    ThirdPartyServiceError,
    ServiceUnavailableError,
    ServiceConfigurationError,
    IntegrationConfigError,
    ServiceProviderConfigError,
    IntegrationPerformanceError,
    IntegrationTimeoutError,
    IntegrationResourceError,
    DataTransformationError,
    DataMappingError,
    DataValidationError as IntegrationDataValidationError,  # Alias
    categorize_integration_error,
    is_retryable_integration_error,
    get_integration_retry_delay,
    get_integration_recovery_suggestions,
    create_integration_error_context,
    validate_integration_requirements,
)

__all__ = [
    # Base Exceptions
    'BaseFrameworkError',
    'DnDFrameworkError',
    'ValidationError',
    'SchemaValidationError',
    'FieldValidationError',
    'DataIntegrityError',
    'ReferenceValidationError',
    'BusinessRuleValidationError',
    'ContentValidationError',
    'FormatValidationError',
    'ValidationPipelineError',
    'ValidationTimeoutError',
    'ValidationConfigError',
    'ValidationDependencyError',
    'ValidationBatchError',
    'ValidationResult',
    'categorize_validation_error',
    'get_validation_severity_level',
    'is_critical_validation_error',
    'group_validation_errors_by_field',
    'group_validation_errors_by_type',
    'create_validation_summary',
    
    # Generation Errors
    'GenerationError',
    'GenerationWorkflowError',
    'LLMProviderError',
    'LLMConnectionError',
    'LLMTimeoutError',
    'LLMRateLimitError',
    'LLMQuotaExceededError',
    'LLMResponseError',
    'LLMContentFilterError',
    'CharacterGenerationError',
    'CharacterConceptError',
    'CharacterBuildError',
    'CharacterProgressionError',
    'CustomContentError',
    'ContentBalanceError',
    'ContentThemeError',
    'ContentComplexityError',
    'TemplateError',
    'TemplateMissingError',
    'TemplateVariableError',
    'PromptProcessingError',
    'GenerationConstraintError',
    'CreativityLimitError',
    'BalanceLimitError',
    'ContentGenerationTimeoutError',
    'ContentGenerationLimitError',
    'IterationLimitError',
    'ContentDependencyError',
    'ConversationFlowError',
    'ConversationStateError',
    'ConversationContextError',
    'categorize_generation_error',
    'is_retryable_generation_error',
    'get_retry_delay_for_error',
    'extract_recovery_suggestions',
    'create_generation_error_context',
    'should_fail_fast',
    
    # Balance and Rule Violation Errors
    'BalanceError',
    'BalanceValidationError',
    'RuleViolationError',
    'AbilityScoreViolation',
    'CharacterLevelViolation',
    'MulticlassViolation',
    'ProficiencyViolation',
    'SpellcastingViolation',
    'BalanceContentError',
    'PowerLevelViolation',
    'RarityMismatchError',
    'ThemeConsistencyError',
    'MechanicalComplexityError',
    'BalanceValidationPipelineError',
    'BalanceSchemaValidationError',
    'BalanceFieldValidationError',
    'BalanceDataIntegrityError',
    'BalanceReferenceValidationError',
    'BalanceValidationResult',
    'BalanceAnalysisResult',
    'categorize_balance_error',
    'get_balance_validation_severity_level',
    'is_critical_balance_error',
    'is_core_rule_violation',
    'suggest_balance_fix',
    'group_balance_errors_by_field',
    'group_balance_errors_by_type',
    'group_balance_errors_by_category',
    'create_balance_summary',
    'validate_content_balance',
    
    # Workflow and Use Case Errors
    'WorkflowError',
    'UseCaseError',
    'UseCaseExecutionError',
    'UseCaseValidationError',
    'UseCasePreconditionError',
    'UseCasePostconditionError',
    'UseCaseTimeoutError',
    'UseCaseDependencyError',
    'CharacterWorkflowError',
    'CharacterCreationWorkflowError',
    'CharacterUpdateWorkflowError',
    'CharacterLevelUpWorkflowError',
    'CharacterValidationWorkflowError',
    'CampaignWorkflowError',
    'CampaignCreationWorkflowError',
    'PlayerInvitationWorkflowError',
    'CampaignSessionWorkflowError',
    'BusinessProcessError',
    'CharacterBusinessRuleError',
    'CampaignBusinessRuleError',
    'ApplicationServiceError',
    'WorkflowStateError',
    'WorkflowTimeoutError',
    'InvalidWorkflowTransitionError',
    'WorkflowOrchestrationError',
    'WorkflowDependencyError',
    'ParallelWorkflowError',
    'WorkflowCompensationError',
    'categorize_workflow_error',
    'is_retryable_workflow_error',
    'get_workflow_retry_delay',
    'get_workflow_recovery_suggestions',
    'create_workflow_error_context',
    'validate_workflow_preconditions',
    
    # Export and Format Conversion Errors
    'ExportError',
    'VTTExportError',
    'DNDBeyondExportError',
    'Roll20ExportError',
    'FantasyGroundsExportError',
    'FoundryVTTExportError',
    'EncounterPlusExportError',
    'FormatConversionError',
    'JSONExportError',
    'XMLExportError',
    'PDFExportError',
    'CSVExportError',
    'TemplateRenderingError',
    'ExportTemplateMissingError',
    'ExportTemplateVariableError',
    'TemplateSyntaxError',
    'CharacterSheetExportError',
    'CharacterDataIncompleteError',
    'CharacterSheetLayoutError',
    'CustomContentExportError',
    'ContentTypeNotSupportedError',
    'UnsupportedContentError',
    'ContentComplexityExportError',
    'ExportQualityError',
    'ExportValidationError',
    'ExportTimeoutError',
    'ExportResourceError',
    'ExportFileSizeError',
    'categorize_export_error',
    'is_retryable_export_error',
    'get_export_retry_delay',
    'get_export_recovery_suggestions',
    'get_export_format_alternatives',
    'create_export_error_context',
    'validate_export_requirements',
    
    # Persistence and Repository Errors
    'PersistenceError',
    'RepositoryError',
    'DatabaseConnectionError',
    'DatabaseUnavailableError',
    'ConnectionPoolExhaustedError',
    'EntityNotFoundError',
    'CharacterNotFoundError',
    'CampaignNotFoundError',
    'UserNotFoundError',
    'ContentNotFoundError',
    'PersistenceDataIntegrityError',
    'ForeignKeyViolationError',
    'UniqueConstraintViolationError',
    'CheckConstraintViolationError',
    'OptimisticLockingError',
    'RepositoryOperationError',
    'CreateOperationError',
    'UpdateOperationError',
    'DeleteOperationError',
    'QueryOperationError',
    'BulkOperationError',
    'TransactionError',
    'TransactionRollbackError',
    'TransactionTimeoutError',
    'DeadlockError',
    'RepositoryConfigurationError',
    'RepositoryInitializationError',
    'DataMigrationError',
    'MigrationRollbackError',
    'categorize_persistence_error',
    'is_retryable_persistence_error',
    'get_persistence_retry_delay',
    'get_persistence_recovery_suggestions',
    'analyze_constraint_violation',
    
    # Integration and External Service Errors
    'IntegrationError',
    'ExternalServiceError',
    'APIIntegrationError',
    'APIConnectionError',
    'APITimeoutError',
    'APIRateLimitError',
    'APIAuthenticationError',
    'APIResponseError',
    'ServiceProviderError',
    'IntegrationLLMProviderError',
    'VTTProviderError',
    'ContentProviderError',
    'DataSynchronizationError',
    'SyncConflictError',
    'SyncTimeoutError',
    'WebhookError',
    'WebhookValidationError',
    'RealTimeUpdateError',
    'ThirdPartyServiceError',
    'ServiceUnavailableError',
    'ServiceConfigurationError',
    'IntegrationConfigError',
    'ServiceProviderConfigError',
    'IntegrationPerformanceError',
    'IntegrationTimeoutError',
    'IntegrationResourceError',
    'DataTransformationError',
    'DataMappingError',
    'IntegrationDataValidationError',
    'categorize_integration_error',
    'is_retryable_integration_error',
    'get_integration_retry_delay',
    'get_integration_recovery_suggestions',
    'create_integration_error_context',
    'validate_integration_requirements',
]

# Exception registry for dynamic access
EXCEPTION_REGISTRY = {
    # Base exceptions
    'base_framework_error': BaseFrameworkError,
    'dnd_framework_error': DnDFrameworkError,
    'validation_error': ValidationError,
    'schema_validation': SchemaValidationError,
    'field_validation': FieldValidationError,
    'data_integrity': DataIntegrityError,
    'reference_validation': ReferenceValidationError,
    'business_rule': BusinessRuleValidationError,
    'content_validation': ContentValidationError,
    'format_validation': FormatValidationError,
    'validation_pipeline': ValidationPipelineError,
    'validation_timeout': ValidationTimeoutError,
    'validation_config': ValidationConfigError,
    'validation_dependency': ValidationDependencyError,
    'validation_batch': ValidationBatchError,
    
    # Generation errors
    'generation_error': GenerationError,
    'generation_workflow': GenerationWorkflowError,
    'llm_provider': LLMProviderError,
    'llm_connection': LLMConnectionError,
    'llm_timeout': LLMTimeoutError,
    'llm_rate_limit': LLMRateLimitError,
    'llm_quota_exceeded': LLMQuotaExceededError,
    'llm_response': LLMResponseError,
    'llm_content_filter': LLMContentFilterError,
    'character_generation': CharacterGenerationError,
    'character_concept': CharacterConceptError,
    'character_build': CharacterBuildError,
    'character_progression': CharacterProgressionError,
    'custom_content': CustomContentError,
    'content_balance': ContentBalanceError,
    'content_theme': ContentThemeError,
    'content_complexity': ContentComplexityError,
    'template_error': TemplateError,
    'template_missing': TemplateMissingError,
    'template_variable': TemplateVariableError,
    'prompt_processing': PromptProcessingError,
    'generation_constraint': GenerationConstraintError,
    'creativity_limit': CreativityLimitError,
    'balance_limit': BalanceLimitError,
    'generation_timeout': ContentGenerationTimeoutError,
    'generation_limit': ContentGenerationLimitError,
    'iteration_limit': IterationLimitError,
    'content_dependency': ContentDependencyError,
    'conversation_flow': ConversationFlowError,
    'conversation_state': ConversationStateError,
    'conversation_context': ConversationContextError,
    
    # Balance and rule violation errors
    'balance_error': BalanceError,
    'balance_validation': BalanceValidationError,
    'rule_violation': RuleViolationError,
    'ability_score_violation': AbilityScoreViolation,
    'character_level_violation': CharacterLevelViolation,
    'multiclass_violation': MulticlassViolation,
    'proficiency_violation': ProficiencyViolation,
    'spellcasting_violation': SpellcastingViolation,
    'balance_content': BalanceContentError,
    'power_level_violation': PowerLevelViolation,
    'rarity_mismatch': RarityMismatchError,
    'theme_consistency': ThemeConsistencyError,
    'mechanical_complexity': MechanicalComplexityError,
    
    # Workflow errors
    'workflow_error': WorkflowError,
    'use_case': UseCaseError,
    'use_case_execution': UseCaseExecutionError,
    'use_case_validation': UseCaseValidationError,
    'use_case_precondition': UseCasePreconditionError,
    'use_case_postcondition': UseCasePostconditionError,
    'use_case_timeout': UseCaseTimeoutError,
    'use_case_dependency': UseCaseDependencyError,
    'character_workflow': CharacterWorkflowError,
    'character_creation_workflow': CharacterCreationWorkflowError,
    'character_update_workflow': CharacterUpdateWorkflowError,
    'character_levelup_workflow': CharacterLevelUpWorkflowError,
    'character_validation_workflow': CharacterValidationWorkflowError,
    'campaign_workflow': CampaignWorkflowError,
    'campaign_creation_workflow': CampaignCreationWorkflowError,
    'player_invitation_workflow': PlayerInvitationWorkflowError,
    'campaign_session_workflow': CampaignSessionWorkflowError,
    'business_process': BusinessProcessError,
    'character_business_rule': CharacterBusinessRuleError,
    'campaign_business_rule': CampaignBusinessRuleError,
    'application_service': ApplicationServiceError,
    'workflow_state': WorkflowStateError,
    'workflow_timeout': WorkflowTimeoutError,
    'invalid_workflow_transition': InvalidWorkflowTransitionError,
    'workflow_orchestration': WorkflowOrchestrationError,
    'workflow_dependency': WorkflowDependencyError,
    'parallel_workflow': ParallelWorkflowError,
    'workflow_compensation': WorkflowCompensationError,
    
    # Export errors
    'export_error': ExportError,
    'vtt_export': VTTExportError,
    'dndbeyond_export': DNDBeyondExportError,
    'roll20_export': Roll20ExportError,
    'fantasy_grounds_export': FantasyGroundsExportError,
    'foundry_vtt_export': FoundryVTTExportError,
    'encounter_plus_export': EncounterPlusExportError,
    'format_conversion': FormatConversionError,
    'json_export': JSONExportError,
    'xml_export': XMLExportError,
    'pdf_export': PDFExportError,
    'csv_export': CSVExportError,
    'template_rendering': TemplateRenderingError,
    'export_template_missing': ExportTemplateMissingError,
    'export_template_variable': ExportTemplateVariableError,
    'template_syntax': TemplateSyntaxError,
    'character_sheet_export': CharacterSheetExportError,
    'character_data_incomplete': CharacterDataIncompleteError,
    'character_sheet_layout': CharacterSheetLayoutError,
    'custom_content_export': CustomContentExportError,
    'content_type_not_supported': ContentTypeNotSupportedError,
    'unsupported_content': UnsupportedContentError,
    'content_complexity_export': ContentComplexityExportError,
    'export_quality': ExportQualityError,
    'export_validation': ExportValidationError,
    'export_timeout': ExportTimeoutError,
    'export_resource': ExportResourceError,
    'export_file_size': ExportFileSizeError,
    
    # Persistence errors
    'persistence_error': PersistenceError,
    'repository_error': RepositoryError,
    'database_connection': DatabaseConnectionError,
    'database_unavailable': DatabaseUnavailableError,
    'connection_pool_exhausted': ConnectionPoolExhaustedError,
    'entity_not_found': EntityNotFoundError,
    'character_not_found': CharacterNotFoundError,
    'campaign_not_found': CampaignNotFoundError,
    'user_not_found': UserNotFoundError,
    'content_not_found': ContentNotFoundError,
    'persistence_data_integrity': PersistenceDataIntegrityError,
    'foreign_key_violation': ForeignKeyViolationError,
    'unique_constraint_violation': UniqueConstraintViolationError,
    'check_constraint_violation': CheckConstraintViolationError,
    'optimistic_locking': OptimisticLockingError,
    'repository_operation': RepositoryOperationError,
    'create_operation': CreateOperationError,
    'update_operation': UpdateOperationError,
    'delete_operation': DeleteOperationError,
    'query_operation': QueryOperationError,
    'bulk_operation': BulkOperationError,
    'transaction_error': TransactionError,
    'transaction_rollback': TransactionRollbackError,
    'transaction_timeout': TransactionTimeoutError,
    'deadlock': DeadlockError,
    'repository_configuration': RepositoryConfigurationError,
    'repository_initialization': RepositoryInitializationError,
    'data_migration': DataMigrationError,
    'migration_rollback': MigrationRollbackError,
    
    # Integration errors
    'integration_error': IntegrationError,
    'external_service': ExternalServiceError,
    'api_integration': APIIntegrationError,
    'api_connection': APIConnectionError,
    'api_timeout': APITimeoutError,
    'api_rate_limit': APIRateLimitError,
    'api_authentication': APIAuthenticationError,
    'api_response': APIResponseError,
    'service_provider': ServiceProviderError,
    'integration_llm_provider': IntegrationLLMProviderError,
    'vtt_provider': VTTProviderError,
    'content_provider': ContentProviderError,
    'data_synchronization': DataSynchronizationError,
    'sync_conflict': SyncConflictError,
    'sync_timeout': SyncTimeoutError,
    'webhook_error': WebhookError,
    'webhook_validation': WebhookValidationError,
    'real_time_update': RealTimeUpdateError,
    'third_party_service': ThirdPartyServiceError,
    'service_unavailable': ServiceUnavailableError,
    'service_configuration': ServiceConfigurationError,
    'integration_config': IntegrationConfigError,
    'service_provider_config': ServiceProviderConfigError,
    'integration_performance': IntegrationPerformanceError,
    'integration_timeout': IntegrationTimeoutError,
    'integration_resource': IntegrationResourceError,
    'data_transformation': DataTransformationError,
    'data_mapping': DataMappingError,
    'integration_data_validation': IntegrationDataValidationError,
}


def get_exception_class(exception_type: str):
    """
    Get exception class by type name.
    
    Args:
        exception_type: String identifier for the exception type
        
    Returns:
        Exception class or None if not found
    """
    return EXCEPTION_REGISTRY.get(exception_type.lower())


def list_available_exceptions() -> list[str]:
    """
    Get list of all available exception types.
    
    Returns:
        List of exception type names
    """
    return list(EXCEPTION_REGISTRY.keys())


def get_exceptions_by_category() -> dict[str, list[str]]:
    """
    Get exceptions organized by their functional category.
    
    Returns:
        Dictionary of categories with their exception types
    """
    return {
        "base": [
            "base_framework_error", "dnd_framework_error", "validation_error",
            "schema_validation", "field_validation", "data_integrity",
            "reference_validation", "business_rule", "content_validation",
            "format_validation", "validation_pipeline", "validation_timeout",
            "validation_config", "validation_dependency", "validation_batch"
        ],
        "generation": [
            "generation_error", "generation_workflow", "llm_provider",
            "llm_connection", "llm_timeout", "llm_rate_limit", "llm_quota_exceeded",
            "llm_response", "llm_content_filter", "character_generation",
            "character_concept", "character_build", "character_progression",
            "custom_content", "content_balance", "content_theme", "content_complexity",
            "template_error", "template_missing", "template_variable",
            "prompt_processing", "generation_constraint", "creativity_limit",
            "balance_limit", "generation_timeout", "generation_limit",
            "iteration_limit", "content_dependency", "conversation_flow",
            "conversation_state", "conversation_context"
        ],
        "balance": [
            "balance_error", "balance_validation", "rule_violation",
            "ability_score_violation", "character_level_violation", "multiclass_violation",
            "proficiency_violation", "spellcasting_violation", "balance_content",
            "power_level_violation", "rarity_mismatch", "theme_consistency",
            "mechanical_complexity"
        ],
        "workflow": [
            "workflow_error", "use_case", "use_case_execution", "use_case_validation",
            "use_case_precondition", "use_case_postcondition", "use_case_timeout",
            "use_case_dependency", "character_workflow", "character_creation_workflow",
            "character_update_workflow", "character_levelup_workflow",
            "character_validation_workflow", "campaign_workflow",
            "campaign_creation_workflow", "player_invitation_workflow",
            "campaign_session_workflow", "business_process", "character_business_rule",
            "campaign_business_rule", "application_service", "workflow_state",
            "workflow_timeout", "invalid_workflow_transition", "workflow_orchestration",
            "workflow_dependency", "parallel_workflow", "workflow_compensation"
        ],
        "export": [
            "export_error", "vtt_export", "dndbeyond_export", "roll20_export",
            "fantasy_grounds_export", "foundry_vtt_export", "encounter_plus_export",
            "format_conversion", "json_export", "xml_export", "pdf_export",
            "csv_export", "template_rendering", "export_template_missing",
            "export_template_variable", "template_syntax", "character_sheet_export",
            "character_data_incomplete", "character_sheet_layout", "custom_content_export",
            "content_type_not_supported", "unsupported_content", "content_complexity_export",
            "export_quality", "export_validation", "export_timeout", "export_resource",
            "export_file_size"
        ],
        "persistence": [
            "persistence_error", "repository_error", "database_connection",
            "database_unavailable", "connection_pool_exhausted", "entity_not_found",
            "character_not_found", "campaign_not_found", "user_not_found",
            "content_not_found", "persistence_data_integrity", "foreign_key_violation",
            "unique_constraint_violation", "check_constraint_violation",
            "optimistic_locking", "repository_operation", "create_operation",
            "update_operation", "delete_operation", "query_operation", "bulk_operation",
            "transaction_error", "transaction_rollback", "transaction_timeout",
            "deadlock", "repository_configuration", "repository_initialization",
            "data_migration", "migration_rollback"
        ],
        "integration": [
            "integration_error", "external_service", "api_integration", "api_connection",
            "api_timeout", "api_rate_limit", "api_authentication", "api_response",
            "service_provider", "integration_llm_provider", "vtt_provider",
            "content_provider", "data_synchronization", "sync_conflict", "sync_timeout",
            "webhook_error", "webhook_validation", "real_time_update",
            "third_party_service", "service_unavailable", "service_configuration",
            "integration_config", "service_provider_config", "integration_performance",
            "integration_timeout", "integration_resource", "data_transformation",
            "data_mapping", "integration_data_validation"
        ]
    }


def create_exception_from_dict(exception_data: dict) -> Exception:
    """
    Create an exception instance from a dictionary representation.
    
    Args:
        exception_data: Dictionary containing exception type and parameters
        
    Returns:
        Exception instance
        
    Raises:
        ValueError: If exception type is unknown or data is invalid
    """
    exception_type = exception_data.get('type')
    if not exception_type:
        raise ValueError("Exception data must include 'type' field")
    
    exception_class = get_exception_class(exception_type)
    if not exception_class:
        raise ValueError(f"Unknown exception type: {exception_type}")
    
    # Extract parameters
    message = exception_data.get('message', 'Unknown error')
    kwargs = {k: v for k, v in exception_data.items() if k not in ['type', 'message']}
    
    try:
        return exception_class(message, **kwargs)
    except TypeError as e:
        raise ValueError(f"Invalid parameters for {exception_type}: {e}")


def exception_to_dict(exception: Exception) -> dict:
    """
    Convert an exception instance to a dictionary representation.
    
    Args:
        exception: Exception instance to convert
        
    Returns:
        Dictionary representation of the exception
    """
    result = {
        'type': type(exception).__name__.lower().replace('error', '').replace('violation', '_violation'),
        'message': str(exception),
        'class': type(exception).__name__
    }
    
    # Add specific attributes based on exception type
    if hasattr(exception, 'severity'):
        result['severity'] = exception.severity.value if hasattr(exception.severity, 'value') else str(exception.severity)
    
    if hasattr(exception, 'field_name') and exception.field_name:
        result['field_name'] = exception.field_name
    
    if hasattr(exception, 'rule_name') and exception.rule_name:
        result['rule_name'] = exception.rule_name
    
    if hasattr(exception, 'context') and exception.context:
        result['context'] = exception.context
    
    if hasattr(exception, 'recovery_suggestions') and exception.recovery_suggestions:
        result['suggestions'] = exception.recovery_suggestions
    
    return result


def is_framework_exception(exception: Exception) -> bool:
    """
    Check if an exception is a framework-specific exception.
    
    Args:
        exception: Exception to check
        
    Returns:
        True if this is a framework exception
    """
    framework_bases = (
        BaseFrameworkError, DnDFrameworkError, GenerationError, 
        ValidationError, BalanceError, WorkflowError, ExportError,
        PersistenceError, IntegrationError
    )
    return isinstance(exception, framework_bases)


def get_exception_category(exception: Exception) -> str:
    """
    Get the category of a framework exception.
    
    Args:
        exception: Exception to categorize
        
    Returns:
        Category string
    """
    if isinstance(exception, GenerationError):
        return "generation"
    elif isinstance(exception, ValidationError):
        return "validation"
    elif isinstance(exception, BalanceError):
        return "balance"
    elif isinstance(exception, WorkflowError):
        return "workflow"
    elif isinstance(exception, ExportError):
        return "export"
    elif isinstance(exception, PersistenceError):
        return "persistence"
    elif isinstance(exception, IntegrationError):
        return "integration"
    elif isinstance(exception, BaseFrameworkError):
        return "base"
    else:
        return "unknown"


def summarize_exception_collection(exceptions: list[Exception]) -> dict:
    """
    Create a summary of a collection of exceptions.
    
    Args:
        exceptions: List of exceptions to summarize
        
    Returns:
        Summary dictionary
    """
    if not exceptions:
        return {"total": 0, "categories": {}, "most_severe": None}
    
    categories = {}
    severity_counts = {}
    most_severe = None
    highest_severity = 0
    
    for exc in exceptions:
        # Categorize
        category = get_exception_category(exc)
        categories[category] = categories.get(category, 0) + 1
        
        # Track severity
        if hasattr(exc, 'severity'):
            severity = exc.severity.value if hasattr(exc.severity, 'value') else str(exc.severity)
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Find most severe
            severity_levels = {'info': 1, 'warning': 2, 'error': 3, 'critical': 4}
            level = severity_levels.get(severity.lower(), 0)
            if level > highest_severity:
                highest_severity = level
                most_severe = exc
    
    return {
        "total": len(exceptions),
        "categories": categories,
        "severity_counts": severity_counts,
        "most_severe": exception_to_dict(most_severe) if most_severe else None,
        "framework_exceptions": sum(1 for exc in exceptions if is_framework_exception(exc)),
        "external_exceptions": sum(1 for exc in exceptions if not is_framework_exception(exc))
    }