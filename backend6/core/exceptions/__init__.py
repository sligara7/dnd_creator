"""
Core domain exceptions for the D&D Creative Content Framework.

This module provides a comprehensive set of exceptions for content generation,
validation failures, and D&D rule violations, supporting robust error handling
and debugging throughout the framework.
"""

# Generation Errors
from .generation_errors import (
    GenerationError,
    LLMError,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMQuotaExceededError,
    LLMResponseError,
    TemplateError,
    TemplateMissingError,
    TemplateVariableError,
    ContentGenerationTimeoutError,
    ContentGenerationLimitError,
    IterationLimitError,
    ContentDependencyError,
    ContentFormatError,
    ContentParsingError,
    GenerationConfigError,
    ProviderUnavailableError,
    ContentPostProcessingError,
    GenerationRetryExhaustedError,
    categorize_generation_error,
    is_retryable_error,
    get_retry_delay,
)

# Validation Errors
from .validation_errors import (
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

# Rule Violation Errors
from .rule_violation_errors import (
    RuleViolationError,
    AbilityScoreViolation,
    CharacterLevelViolation,
    MulticlassViolation,
    ProficiencyViolation,
    SpellcastingViolation,
    CombatRuleViolation,
    EquipmentViolation,
    BalanceViolation,
    FeatureUsageViolation,
    RestingViolation,
    ConditionViolation,
    categorize_rule_violation,
    get_violation_severity_level,
    is_core_rule_violation,
    suggest_violation_fix,
    group_violations_by_category,
)

__all__ = [
    # Generation Errors
    'GenerationError',
    'LLMError',
    'LLMTimeoutError',
    'LLMRateLimitError',
    'LLMQuotaExceededError',
    'LLMResponseError',
    'TemplateError',
    'TemplateMissingError',
    'TemplateVariableError',
    'ContentGenerationTimeoutError',
    'ContentGenerationLimitError',
    'IterationLimitError',
    'ContentDependencyError',
    'ContentFormatError',
    'ContentParsingError',
    'GenerationConfigError',
    'ProviderUnavailableError',
    'ContentPostProcessingError',
    'GenerationRetryExhaustedError',
    'categorize_generation_error',
    'is_retryable_error',
    'get_retry_delay',
    
    # Validation Errors
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
    
    # Rule Violation Errors
    'RuleViolationError',
    'AbilityScoreViolation',
    'CharacterLevelViolation',
    'MulticlassViolation',
    'ProficiencyViolation',
    'SpellcastingViolation',
    'CombatRuleViolation',
    'EquipmentViolation',
    'BalanceViolation',
    'FeatureUsageViolation',
    'RestingViolation',
    'ConditionViolation',
    'categorize_rule_violation',
    'get_violation_severity_level',
    'is_core_rule_violation',
    'suggest_violation_fix',
    'group_violations_by_category',
]

# Exception registry for dynamic access
EXCEPTION_REGISTRY = {
    # Generation errors
    'generation_error': GenerationError,
    'llm_error': LLMError,
    'llm_timeout': LLMTimeoutError,
    'llm_rate_limit': LLMRateLimitError,
    'llm_quota_exceeded': LLMQuotaExceededError,
    'llm_response_error': LLMResponseError,
    'template_error': TemplateError,
    'template_missing': TemplateMissingError,
    'template_variable': TemplateVariableError,
    'generation_timeout': ContentGenerationTimeoutError,
    'generation_limit': ContentGenerationLimitError,
    'iteration_limit': IterationLimitError,
    'content_dependency': ContentDependencyError,
    'content_format': ContentFormatError,
    'content_parsing': ContentParsingError,
    'generation_config': GenerationConfigError,
    'provider_unavailable': ProviderUnavailableError,
    'post_processing': ContentPostProcessingError,
    'retry_exhausted': GenerationRetryExhaustedError,
    
    # Validation errors
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
    
    # Rule violation errors
    'rule_violation': RuleViolationError,
    'ability_score_violation': AbilityScoreViolation,
    'character_level_violation': CharacterLevelViolation,
    'multiclass_violation': MulticlassViolation,
    'proficiency_violation': ProficiencyViolation,
    'spellcasting_violation': SpellcastingViolation,
    'combat_rule_violation': CombatRuleViolation,
    'equipment_violation': EquipmentViolation,
    'balance_violation': BalanceViolation,
    'feature_usage_violation': FeatureUsageViolation,
    'resting_violation': RestingViolation,
    'condition_violation': ConditionViolation,
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
        "generation": [
            "generation_error", "llm_error", "llm_timeout", "llm_rate_limit",
            "llm_quota_exceeded", "llm_response_error", "template_error",
            "template_missing", "template_variable", "generation_timeout",
            "generation_limit", "iteration_limit", "content_dependency",
            "content_format", "content_parsing", "generation_config",
            "provider_unavailable", "post_processing", "retry_exhausted"
        ],
        "validation": [
            "validation_error", "schema_validation", "field_validation",
            "data_integrity", "reference_validation", "business_rule",
            "content_validation", "format_validation", "validation_pipeline",
            "validation_timeout", "validation_config", "validation_dependency",
            "validation_batch"
        ],
        "rule_violations": [
            "rule_violation", "ability_score_violation", "character_level_violation",
            "multiclass_violation", "proficiency_violation", "spellcasting_violation",
            "combat_rule_violation", "equipment_violation", "balance_violation",
            "feature_usage_violation", "resting_violation", "condition_violation"
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
    
    if hasattr(exception, 'suggestions') and exception.suggestions:
        result['suggestions'] = exception.suggestions
    
    return result


def is_framework_exception(exception: Exception) -> bool:
    """
    Check if an exception is a framework-specific exception.
    
    Args:
        exception: Exception to check
        
    Returns:
        True if this is a framework exception
    """
    framework_bases = (GenerationError, ValidationError, RuleViolationError)
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
    elif isinstance(exception, RuleViolationError):
        return "rule_violation"
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