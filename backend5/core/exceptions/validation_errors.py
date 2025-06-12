"""
Validation failure exceptions for the D&D Creative Content Framework.

This module defines exceptions related to content validation failures,
schema validation errors, data integrity issues, and validation pipeline problems.
"""

from typing import Dict, List, Optional, Any, Union
from ..enums.validation_types import ValidationType, ValidationSeverity, ValidationStatus
from ..enums.content_types import ContentType, ContentRarity


class ValidationError(Exception):
    """Base exception for all validation failures."""
    
    def __init__(
        self,
        message: str,
        validation_type: Optional[ValidationType] = None,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None
    ):
        super().__init__(message)
        self.validation_type = validation_type
        self.severity = severity
        self.field_name = field_name
        self.field_value = field_value
        self.context = context or {}
        self.suggestions = suggestions or []
    
    def __str__(self) -> str:
        parts = [super().__str__()]
        
        if self.validation_type:
            parts.append(f"Type: {self.validation_type.value}")
        
        parts.append(f"Severity: {self.severity.value}")
        
        if self.field_name:
            parts.append(f"Field: {self.field_name}")
        
        if self.suggestions:
            parts.append(f"Suggestions: {'; '.join(self.suggestions)}")
        
        return " | ".join(parts)


class SchemaValidationError(ValidationError):
    """Exception for schema validation failures."""
    
    def __init__(
        self,
        schema_name: str,
        schema_version: Optional[str] = None,
        validation_errors: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Schema validation failed for {schema_name}"
        if schema_version:
            message += f" (version {schema_version})"
        
        if validation_errors:
            message += f": {'; '.join(validation_errors)}"
        
        super().__init__(
            message,
            validation_type=ValidationType.SCHEMA,
            **kwargs
        )
        self.schema_name = schema_name
        self.schema_version = schema_version
        self.validation_errors = validation_errors or []


class FieldValidationError(ValidationError):
    """Exception for individual field validation failures."""
    
    def __init__(
        self,
        field_name: str,
        field_value: Any,
        constraint_type: str,
        constraint_value: Optional[Any] = None,
        **kwargs
    ):
        if constraint_type == "required":
            message = f"Required field '{field_name}' is missing or empty"
        elif constraint_type == "type":
            message = f"Field '{field_name}' has invalid type: expected {constraint_value}, got {type(field_value).__name__}"
        elif constraint_type == "length":
            message = f"Field '{field_name}' length constraint violated: {constraint_value}"
        elif constraint_type == "range":
            message = f"Field '{field_name}' value {field_value} outside allowed range: {constraint_value}"
        elif constraint_type == "pattern":
            message = f"Field '{field_name}' doesn't match required pattern: {constraint_value}"
        elif constraint_type == "enum":
            message = f"Field '{field_name}' value '{field_value}' not in allowed values: {constraint_value}"
        else:
            message = f"Field '{field_name}' validation failed: {constraint_type}"
        
        super().__init__(
            message,
            validation_type=ValidationType.FIELD,
            field_name=field_name,
            field_value=field_value,
            **kwargs
        )
        self.constraint_type = constraint_type
        self.constraint_value = constraint_value


class DataIntegrityError(ValidationError):
    """Exception for data integrity validation failures."""
    
    def __init__(
        self,
        integrity_type: str,
        affected_fields: Optional[List[str]] = None,
        constraint_description: Optional[str] = None,
        **kwargs
    ):
        message = f"Data integrity violation: {integrity_type}"
        if constraint_description:
            message += f" - {constraint_description}"
        
        if affected_fields:
            message += f" (affects: {', '.join(affected_fields)})"
        
        super().__init__(
            message,
            validation_type=ValidationType.INTEGRITY,
            **kwargs
        )
        self.integrity_type = integrity_type
        self.affected_fields = affected_fields or []
        self.constraint_description = constraint_description


class ReferenceValidationError(ValidationError):
    """Exception for reference/relationship validation failures."""
    
    def __init__(
        self,
        reference_field: str,
        reference_value: Any,
        target_type: str,
        reference_type: str = "foreign_key",
        **kwargs
    ):
        if reference_type == "foreign_key":
            message = f"Foreign key reference failed: {reference_field}='{reference_value}' not found in {target_type}"
        elif reference_type == "circular":
            message = f"Circular reference detected in {reference_field}: {reference_value}"
        elif reference_type == "orphaned":
            message = f"Orphaned reference in {reference_field}: {reference_value} has no parent"
        else:
            message = f"Reference validation failed for {reference_field}: {reference_type}"
        
        super().__init__(
            message,
            validation_type=ValidationType.REFERENCE,
            field_name=reference_field,
            field_value=reference_value,
            **kwargs
        )
        self.reference_field = reference_field
        self.reference_value = reference_value
        self.target_type = target_type
        self.reference_type = reference_type


class BusinessRuleValidationError(ValidationError):
    """Exception for business rule validation failures."""
    
    def __init__(
        self,
        rule_name: str,
        rule_description: Optional[str] = None,
        violated_constraints: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Business rule violation: {rule_name}"
        if rule_description:
            message += f" - {rule_description}"
        
        if violated_constraints:
            message += f" (constraints: {', '.join(violated_constraints)})"
        
        super().__init__(
            message,
            validation_type=ValidationType.BUSINESS_RULE,
            **kwargs
        )
        self.rule_name = rule_name
        self.rule_description = rule_description
        self.violated_constraints = violated_constraints or []


class ContentValidationError(ValidationError):
    """Exception for content-specific validation failures."""
    
    def __init__(
        self,
        content_type: ContentType,
        content_name: str,
        validation_issue: str,
        content_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"{content_type.value} '{content_name}' validation failed: {validation_issue}"
        
        super().__init__(
            message,
            validation_type=ValidationType.CONTENT,
            **kwargs
        )
        self.content_type = content_type
        self.content_name = content_name
        self.validation_issue = validation_issue
        self.content_data = content_data or {}


class FormatValidationError(ValidationError):
    """Exception for format/structure validation failures."""
    
    def __init__(
        self,
        format_type: str,
        expected_format: str,
        actual_format: Optional[str] = None,
        format_issues: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Format validation failed for {format_type}: expected {expected_format}"
        if actual_format:
            message += f", got {actual_format}"
        
        if format_issues:
            message += f" (issues: {', '.join(format_issues)})"
        
        super().__init__(
            message,
            validation_type=ValidationType.FORMAT,
            **kwargs
        )
        self.format_type = format_type
        self.expected_format = expected_format
        self.actual_format = actual_format
        self.format_issues = format_issues or []


class ValidationPipelineError(ValidationError):
    """Exception for validation pipeline failures."""
    
    def __init__(
        self,
        pipeline_stage: str,
        stage_errors: Optional[List[ValidationError]] = None,
        pipeline_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Validation pipeline failed at stage: {pipeline_stage}"
        if stage_errors:
            message += f" (errors: {len(stage_errors)})"
        
        super().__init__(
            message,
            validation_type=ValidationType.PIPELINE,
            context=pipeline_context,
            **kwargs
        )
        self.pipeline_stage = pipeline_stage
        self.stage_errors = stage_errors or []
        self.pipeline_context = pipeline_context or {}


class ValidationTimeoutError(ValidationError):
    """Exception for validation timeout failures."""
    
    def __init__(
        self,
        timeout_duration: float,
        validation_stage: Optional[str] = None,
        partial_results: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Validation timed out after {timeout_duration} seconds"
        if validation_stage:
            message += f" during {validation_stage}"
        
        super().__init__(
            message,
            validation_type=ValidationType.TIMEOUT,
            **kwargs
        )
        self.timeout_duration = timeout_duration
        self.validation_stage = validation_stage
        self.partial_results = partial_results or {}


class ValidationConfigError(ValidationError):
    """Exception for validation configuration errors."""
    
    def __init__(
        self,
        config_issue: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        valid_options: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Validation configuration error: {config_issue}"
        if config_key:
            message += f" (key: {config_key})"
        
        if valid_options:
            message += f" (valid options: {', '.join(valid_options)})"
        
        super().__init__(
            message,
            validation_type=ValidationType.CONFIG,
            **kwargs
        )
        self.config_issue = config_issue
        self.config_key = config_key
        self.config_value = config_value
        self.valid_options = valid_options or []


class ValidationDependencyError(ValidationError):
    """Exception for validation dependency failures."""
    
    def __init__(
        self,
        dependency_type: str,
        dependency_name: str,
        dependency_issue: str,
        dependent_validations: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Validation dependency failed: {dependency_type} '{dependency_name}' - {dependency_issue}"
        
        if dependent_validations:
            message += f" (affects: {', '.join(dependent_validations)})"
        
        super().__init__(
            message,
            validation_type=ValidationType.DEPENDENCY,
            **kwargs
        )
        self.dependency_type = dependency_type
        self.dependency_name = dependency_name
        self.dependency_issue = dependency_issue
        self.dependent_validations = dependent_validations or []


class ValidationBatchError(ValidationError):
    """Exception for batch validation failures."""
    
    def __init__(
        self,
        batch_size: int,
        failed_items: List[Dict[str, Any]],
        batch_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Batch validation failed: {len(failed_items)}/{batch_size} items failed"
        
        super().__init__(
            message,
            validation_type=ValidationType.BATCH,
            context=batch_context,
            **kwargs
        )
        self.batch_size = batch_size
        self.failed_items = failed_items
        self.batch_context = batch_context or {}


# === VALIDATION RESULT CLASSES ===

class ValidationResult:
    """Container for validation results."""
    
    def __init__(
        self,
        is_valid: bool,
        errors: Optional[List[ValidationError]] = None,
        warnings: Optional[List[ValidationError]] = None,
        info: Optional[List[ValidationError]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.info = info or []
        self.context = context or {}
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
    
    @property
    def total_issues(self) -> int:
        return len(self.errors) + len(self.warnings) + len(self.info)
    
    def add_error(self, error: ValidationError):
        """Add an error to the validation result."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: ValidationError):
        """Add a warning to the validation result."""
        self.warnings.append(warning)
    
    def add_info(self, info: ValidationError):
        """Add an info message to the validation result."""
        self.info.append(info)
    
    def merge(self, other: 'ValidationResult'):
        """Merge another validation result into this one."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)
        self.context.update(other.context)
        
        if other.has_errors:
            self.is_valid = False


# === UTILITY FUNCTIONS ===

def categorize_validation_error(error: ValidationError) -> str:
    """
    Categorize a validation error for handling and reporting.
    
    Args:
        error: The validation error to categorize
        
    Returns:
        Category string
    """
    if isinstance(error, SchemaValidationError):
        return "schema"
    elif isinstance(error, FieldValidationError):
        return "field"
    elif isinstance(error, DataIntegrityError):
        return "integrity"
    elif isinstance(error, ReferenceValidationError):
        return "reference"
    elif isinstance(error, BusinessRuleValidationError):
        return "business_rule"
    elif isinstance(error, ContentValidationError):
        return "content"
    elif isinstance(error, FormatValidationError):
        return "format"
    elif isinstance(error, ValidationPipelineError):
        return "pipeline"
    elif isinstance(error, ValidationTimeoutError):
        return "timeout"
    elif isinstance(error, ValidationConfigError):
        return "config"
    elif isinstance(error, ValidationDependencyError):
        return "dependency"
    elif isinstance(error, ValidationBatchError):
        return "batch"
    else:
        return "general"


def get_validation_severity_level(error: ValidationError) -> int:
    """
    Get numeric severity level for sorting/prioritizing validation errors.
    
    Args:
        error: The validation error to assess
        
    Returns:
        Severity level (higher = more severe)
    """
    severity_map = {
        ValidationSeverity.INFO: 1,
        ValidationSeverity.WARNING: 2,
        ValidationSeverity.ERROR: 3,
        ValidationSeverity.CRITICAL: 4
    }
    
    return severity_map.get(error.severity, 2)


def is_critical_validation_error(error: ValidationError) -> bool:
    """
    Check if validation error is critical and should stop processing.
    
    Args:
        error: The validation error to check
        
    Returns:
        True if this is a critical error
    """
    return error.severity == ValidationSeverity.CRITICAL


def group_validation_errors_by_field(errors: List[ValidationError]) -> Dict[str, List[ValidationError]]:
    """
    Group validation errors by field name for organized reporting.
    
    Args:
        errors: List of validation errors
        
    Returns:
        Dictionary mapping field names to errors
    """
    grouped = {}
    
    for error in errors:
        field_name = error.field_name or "general"
        if field_name not in grouped:
            grouped[field_name] = []
        grouped[field_name].append(error)
    
    return grouped


def group_validation_errors_by_type(errors: List[ValidationError]) -> Dict[str, List[ValidationError]]:
    """
    Group validation errors by validation type for organized reporting.
    
    Args:
        errors: List of validation errors
        
    Returns:
        Dictionary mapping validation types to errors
    """
    grouped = {}
    
    for error in errors:
        validation_type = error.validation_type.value if error.validation_type else "unknown"
        if validation_type not in grouped:
            grouped[validation_type] = []
        grouped[validation_type].append(error)
    
    return grouped


def create_validation_summary(result: ValidationResult) -> Dict[str, Any]:
    """
    Create a summary of validation results for reporting.
    
    Args:
        result: The validation result to summarize
        
    Returns:
        Summary dictionary
    """
    summary = {
        "is_valid": result.is_valid,
        "total_issues": result.total_issues,
        "error_count": len(result.errors),
        "warning_count": len(result.warnings),
        "info_count": len(result.info),
        "errors_by_type": group_validation_errors_by_type(result.errors),
        "errors_by_field": group_validation_errors_by_field(result.errors),
        "most_severe": None,
        "context": result.context
    }
    
    # Find most severe error
    all_issues = result.errors + result.warnings + result.info
    if all_issues:
        most_severe = max(all_issues, key=get_validation_severity_level)
        summary["most_severe"] = {
            "message": str(most_severe),
            "severity": most_severe.severity.value,
            "type": most_severe.validation_type.value if most_severe.validation_type else "unknown"
        }
    
    return summary