"""
Base Exceptions for the D&D Creative Content Framework.

This module defines the foundational exception hierarchy and common validation
failures that form the basis for all domain-specific exceptions. These exceptions
represent fundamental business rule violations and failure states that are
infrastructure-independent and focused on D&D content creation business logic.

Following Clean Architecture principles, these exceptions are:
- Infrastructure-independent (don't depend on specific technologies)
- Focused on fundamental D&D content validation business rules
- Designed as building blocks for domain-specific exceptions
- Aligned with the core validation and content creation workflow
"""

from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
from datetime import datetime
from ..enums.validation_types import ValidationType, ValidationSeverity, ValidationStatus, RuleCompliance
from ..enums.content_types import ContentType, ContentRarity, ThemeCategory
from ..enums.balance_levels import BalanceLevel, PowerTier


# ============ ABSTRACT BASE EXCEPTION INTERFACE ============

class BaseFrameworkError(Exception, ABC):
    """
    Abstract base class for all framework exceptions.
    
    Defines the common interface and behavior that all framework exceptions
    must implement, ensuring consistent error handling across the system.
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        recovery_suggestions: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None
    ):
        super().__init__(message)
        self.error_code = error_code or self._generate_error_code()
        self.context = context or {}
        self.recovery_suggestions = recovery_suggestions or []
        self.timestamp = timestamp or datetime.utcnow()
        
        # Initialize domain-specific attributes
        self._initialize_domain_attributes()
    
    @abstractmethod
    def _generate_error_code(self) -> str:
        """Generate a unique error code for this exception type."""
        pass
    
    @abstractmethod
    def _initialize_domain_attributes(self) -> None:
        """Initialize domain-specific attributes for the exception."""
        pass
    
    @abstractmethod
    def get_category(self) -> str:
        """Get the category of this exception for handling and routing."""
        pass
    
    @abstractmethod
    def is_retryable(self) -> bool:
        """Determine if this exception represents a retryable failure."""
        pass
    
    @abstractmethod
    def should_fail_fast(self) -> bool:
        """Determine if this exception should cause immediate processing termination."""
        pass
    
    def add_context(self, key: str, value: Any) -> None:
        """Add contextual information to the exception."""
        self.context[key] = value
    
    def add_recovery_suggestion(self, suggestion: str) -> None:
        """Add a recovery suggestion to the exception."""
        if suggestion not in self.recovery_suggestions:
            self.recovery_suggestions.append(suggestion)
    
    def get_detailed_info(self) -> Dict[str, Any]:
        """Get comprehensive exception information for logging and analysis."""
        return {
            "error_code": self.error_code,
            "message": str(self),
            "category": self.get_category(),
            "timestamp": self.timestamp.isoformat(),
            "is_retryable": self.is_retryable(),
            "should_fail_fast": self.should_fail_fast(),
            "context": self.context,
            "recovery_suggestions": self.recovery_suggestions,
            "exception_type": self.__class__.__name__
        }
    
    def __str__(self) -> str:
        parts = [super().__str__()]
        
        if self.error_code:
            parts.append(f"Code: {self.error_code}")
        
        return " | ".join(parts)


# ============ CORE DOMAIN EXCEPTION BASE CLASSES ============

class DnDFrameworkError(BaseFrameworkError):
    """
    Base exception for all D&D-specific framework errors.
    
    Provides common functionality for D&D content creation and validation
    exceptions while maintaining Clean Architecture principles.
    """
    
    def __init__(
        self,
        message: str,
        content_type: Optional[ContentType] = None,
        character_level: Optional[int] = None,
        power_tier: Optional[PowerTier] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.content_type = content_type
        self.character_level = character_level
        self.power_tier = power_tier
    
    def _generate_error_code(self) -> str:
        """Generate D&D-specific error code."""
        base_code = "DND"
        category_code = self.get_category().upper()[:3]
        timestamp_code = str(int(self.timestamp.timestamp()))[-6:]
        return f"{base_code}_{category_code}_{timestamp_code}"
    
    def _initialize_domain_attributes(self) -> None:
        """Initialize D&D-specific attributes."""
        # Can be overridden by subclasses for specific initialization
        pass
    
    def get_category(self) -> str:
        """Default D&D framework category."""
        return "dnd_framework"
    
    def is_retryable(self) -> bool:
        """D&D framework errors are generally not retryable by default."""
        return False
    
    def should_fail_fast(self) -> bool:
        """D&D framework errors don't fail fast by default."""
        return False
    
    def __str__(self) -> str:
        parts = [super().__str__()]
        
        if self.content_type:
            parts.append(f"Content: {self.content_type.value}")
        
        if self.character_level:
            parts.append(f"Level: {self.character_level}")
        
        if self.power_tier:
            parts.append(f"Tier: {self.power_tier.value}")
        
        return " | ".join(parts)


class ValidationError(DnDFrameworkError):
    """
    Base exception for all validation failures in the D&D framework.
    
    Represents violations of D&D business rules, content validation failures,
    and data integrity issues while maintaining infrastructure independence.
    """
    
    def __init__(
        self,
        message: str,
        validation_type: Optional[ValidationType] = None,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        rule_compliance: RuleCompliance = RuleCompliance.CORE_RULES,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        rule_name: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.validation_type = validation_type
        self.severity = severity
        self.rule_compliance = rule_compliance
        self.field_name = field_name
        self.field_value = field_value
        self.rule_name = rule_name
    
    def _generate_error_code(self) -> str:
        """Generate validation-specific error code."""
        base_code = "VAL"
        severity_code = self.severity.name[:3]
        validation_code = self.validation_type.name[:3] if self.validation_type else "GEN"
        timestamp_code = str(int(self.timestamp.timestamp()))[-4:]
        return f"{base_code}_{severity_code}_{validation_code}_{timestamp_code}"
    
    def get_category(self) -> str:
        """Validation error category."""
        return "validation"
    
    def is_retryable(self) -> bool:
        """Most validation errors are not retryable."""
        # Only timeout and dependency errors might be retryable
        return self.validation_type in [ValidationType.TIMEOUT, ValidationType.DEPENDENCY]
    
    def should_fail_fast(self) -> bool:
        """Critical validation errors should fail fast."""
        return self.severity == ValidationSeverity.CRITICAL
    
    def __str__(self) -> str:
        parts = [super().__str__()]
        
        if self.validation_type:
            parts.append(f"Type: {self.validation_type.value}")
        
        parts.append(f"Severity: {self.severity.value}")
        
        if self.field_name:
            parts.append(f"Field: {self.field_name}")
        
        if self.rule_name:
            parts.append(f"Rule: {self.rule_name}")
        
        return " | ".join(parts)


# ============ FOUNDATIONAL VALIDATION EXCEPTIONS ============

class SchemaValidationError(ValidationError):
    """Exception for schema and structure validation failures."""
    
    def __init__(
        self,
        schema_name: str,
        schema_version: Optional[str] = None,
        validation_errors: Optional[List[str]] = None,
        invalid_fields: Optional[List[str]] = None,
        **kwargs
    ):
        validation_errors = validation_errors or []
        message = f"Schema validation failed for {schema_name}"
        if schema_version:
            message += f" (version {schema_version})"
        
        if validation_errors:
            error_summary = '; '.join(validation_errors[:3])
            if len(validation_errors) > 3:
                error_summary += f" (and {len(validation_errors) - 3} more errors)"
            message += f": {error_summary}"
        
        super().__init__(
            message,
            validation_type=ValidationType.SCHEMA,
            **kwargs
        )
        self.schema_name = schema_name
        self.schema_version = schema_version
        self.validation_errors = validation_errors
        self.invalid_fields = invalid_fields or []
    
    def get_category(self) -> str:
        return "schema_validation"


class FieldValidationError(ValidationError):
    """Exception for individual field validation failures."""
    
    def __init__(
        self,
        field_name: str,
        field_value: Any,
        constraint_type: str,
        constraint_value: Optional[Any] = None,
        constraint_description: Optional[str] = None,
        **kwargs
    ):
        message = self._build_field_error_message(
            field_name, field_value, constraint_type, constraint_value, constraint_description
        )
        
        super().__init__(
            message,
            validation_type=ValidationType.FIELD,
            field_name=field_name,
            field_value=field_value,
            **kwargs
        )
        self.constraint_type = constraint_type
        self.constraint_value = constraint_value
        self.constraint_description = constraint_description
    
    def _build_field_error_message(
        self, 
        field_name: str, 
        field_value: Any, 
        constraint_type: str, 
        constraint_value: Optional[Any], 
        constraint_description: Optional[str]
    ) -> str:
        """Build a detailed field validation error message."""
        if constraint_type == "required":
            return f"Required field '{field_name}' is missing or empty"
        elif constraint_type == "type":
            expected_type = constraint_value if isinstance(constraint_value, str) else type(constraint_value).__name__
            actual_type = type(field_value).__name__
            return f"Field '{field_name}' has invalid type: expected {expected_type}, got {actual_type}"
        elif constraint_type == "length":
            if constraint_description:
                return f"Field '{field_name}' length constraint violated: {constraint_description}"
            return f"Field '{field_name}' length constraint violated: {constraint_value}"
        elif constraint_type == "range":
            return f"Field '{field_name}' value {field_value} outside allowed range: {constraint_value}"
        elif constraint_type == "pattern":
            return f"Field '{field_name}' doesn't match required pattern"
        elif constraint_type == "enum":
            return f"Field '{field_name}' value '{field_value}' not in allowed values: {constraint_value}"
        elif constraint_type == "format":
            return f"Field '{field_name}' has invalid format: {constraint_description or constraint_type}"
        elif constraint_type == "unique":
            return f"Field '{field_name}' value '{field_value}' must be unique"
        else:
            return f"Field '{field_name}' validation failed: {constraint_type}"
    
    def get_category(self) -> str:
        return "field_validation"


class DataIntegrityError(ValidationError):
    """Exception for data integrity and consistency validation failures."""
    
    def __init__(
        self,
        integrity_type: str,
        integrity_description: str,
        affected_fields: Optional[List[str]] = None,
        integrity_constraints: Optional[Dict[str, Any]] = None,
        data_state: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Data integrity violation: {integrity_description}"
        if affected_fields:
            message += f" (affects: {', '.join(affected_fields)})"
        
        super().__init__(
            message,
            validation_type=ValidationType.INTEGRITY,
            **kwargs
        )
        self.integrity_type = integrity_type
        self.integrity_description = integrity_description
        self.affected_fields = affected_fields or []
        self.integrity_constraints = integrity_constraints or {}
        self.data_state = data_state or {}
    
    def get_category(self) -> str:
        return "data_integrity"
    
    def should_fail_fast(self) -> bool:
        """Data integrity errors often require immediate attention."""
        critical_integrity_types = ["critical_consistency", "data_corruption", "mandatory_relationship"]
        return self.integrity_type in critical_integrity_types


class ReferenceValidationError(ValidationError):
    """Exception for reference and relationship validation failures."""
    
    def __init__(
        self,
        reference_field: str,
        reference_value: Any,
        target_type: str,
        reference_type: str = "foreign_key",
        target_constraints: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = self._build_reference_error_message(
            reference_field, reference_value, target_type, reference_type
        )
        
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
        self.target_constraints = target_constraints or {}
    
    def _build_reference_error_message(
        self, 
        reference_field: str, 
        reference_value: Any, 
        target_type: str, 
        reference_type: str
    ) -> str:
        """Build a detailed reference validation error message."""
        if reference_type == "foreign_key":
            return f"Foreign key reference failed: {reference_field}='{reference_value}' not found in {target_type}"
        elif reference_type == "circular":
            return f"Circular reference detected in {reference_field}: {reference_value}"
        elif reference_type == "orphaned":
            return f"Orphaned reference in {reference_field}: {reference_value} has no parent"
        elif reference_type == "invalid_target":
            return f"Invalid reference target in {reference_field}: {reference_value} -> {target_type}"
        elif reference_type == "cascade_conflict":
            return f"Cascade operation conflict in {reference_field}: {reference_value}"
        elif reference_type == "constraint_violation":
            return f"Reference constraint violation in {reference_field}: {reference_value}"
        else:
            return f"Reference validation failed for {reference_field}: {reference_type}"
    
    def get_category(self) -> str:
        return "reference_validation"


class BusinessRuleValidationError(ValidationError):
    """Exception for D&D business rule validation failures."""
    
    def __init__(
        self,
        rule_name: str,
        rule_description: Optional[str] = None,
        violated_constraints: Optional[List[str]] = None,
        rule_context: Optional[Dict[str, Any]] = None,
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
            rule_name=rule_name,
            **kwargs
        )
        self.rule_description = rule_description
        self.violated_constraints = violated_constraints or []
        self.rule_context = rule_context or {}
    
    def get_category(self) -> str:
        return "business_rule_validation"
    
    def should_fail_fast(self) -> bool:
        """Core D&D rules should fail fast when violated."""
        return self.rule_compliance == RuleCompliance.CORE_RULES


class ContentValidationError(ValidationError):
    """Exception for D&D content-specific validation failures."""
    
    def __init__(
        self,
        content_type: ContentType,
        content_name: str,
        validation_issue: str,
        content_data: Optional[Dict[str, Any]] = None,
        rarity: Optional[ContentRarity] = None,
        themes: Optional[List[ThemeCategory]] = None,
        **kwargs
    ):
        message = f"{content_type.value} '{content_name}' validation failed: {validation_issue}"
        
        super().__init__(
            message,
            validation_type=ValidationType.CONTENT,
            content_type=content_type,
            **kwargs
        )
        self.content_name = content_name
        self.validation_issue = validation_issue
        self.content_data = content_data or {}
        self.rarity = rarity
        self.themes = themes or []
    
    def get_category(self) -> str:
        return "content_validation"


class FormatValidationError(ValidationError):
    """Exception for format and structure validation failures."""
    
    def __init__(
        self,
        format_type: str,
        expected_format: str,
        actual_format: Optional[str] = None,
        format_issues: Optional[List[str]] = None,
        format_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Format validation failed for {format_type}: expected {expected_format}"
        if actual_format:
            message += f", got {actual_format}"
        
        if format_issues:
            issue_summary = ', '.join(format_issues[:3])
            if len(format_issues) > 3:
                issue_summary += f" (and {len(format_issues) - 3} more)"
            message += f" (issues: {issue_summary})"
        
        super().__init__(
            message,
            validation_type=ValidationType.FORMAT,
            **kwargs
        )
        self.format_type = format_type
        self.expected_format = expected_format
        self.actual_format = actual_format
        self.format_issues = format_issues or []
        self.format_context = format_context or {}
    
    def get_category(self) -> str:
        return "format_validation"


# ============ SYSTEM-LEVEL VALIDATION EXCEPTIONS ============

class ValidationPipelineError(ValidationError):
    """Exception for validation pipeline and workflow failures."""
    
    def __init__(
        self,
        pipeline_stage: str,
        pipeline_issue: str,
        stage_input: Optional[Dict[str, Any]] = None,
        stage_output: Optional[Dict[str, Any]] = None,
        stage_errors: Optional[List[ValidationError]] = None,
        pipeline_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Validation pipeline failed at {pipeline_stage}: {pipeline_issue}"
        if stage_errors:
            message += f" ({len(stage_errors)} stage errors)"
        
        super().__init__(
            message,
            validation_type=ValidationType.PIPELINE,
            context=pipeline_context,
            **kwargs
        )
        self.pipeline_stage = pipeline_stage
        self.pipeline_issue = pipeline_issue
        self.stage_input = stage_input or {}
        self.stage_output = stage_output or {}
        self.stage_errors = stage_errors or []
        self.pipeline_context = pipeline_context or {}
    
    def get_category(self) -> str:
        return "validation_pipeline"
    
    def is_retryable(self) -> bool:
        """Pipeline errors might be retryable depending on the stage."""
        retryable_stages = ["external_validation", "api_check", "dependency_validation"]
        return self.pipeline_stage in retryable_stages


class ValidationTimeoutError(ValidationError):
    """Exception for validation timeout failures."""
    
    def __init__(
        self,
        timeout_duration: float,
        validation_stage: Optional[str] = None,
        partial_results: Optional[Dict[str, Any]] = None,
        timeout_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Validation timed out after {timeout_duration} seconds"
        if validation_stage:
            message += f" during {validation_stage}"
        
        super().__init__(
            message,
            validation_type=ValidationType.TIMEOUT,
            severity=ValidationSeverity.WARNING,  # Timeouts are warnings by default
            **kwargs
        )
        self.timeout_duration = timeout_duration
        self.validation_stage = validation_stage
        self.partial_results = partial_results or {}
        self.timeout_context = timeout_context or {}
    
    def get_category(self) -> str:
        return "validation_timeout"
    
    def is_retryable(self) -> bool:
        """Timeout errors are generally retryable."""
        return True


class ValidationConfigError(ValidationError):
    """Exception for validation configuration and setup errors."""
    
    def __init__(
        self,
        config_issue: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        valid_options: Optional[List[str]] = None,
        config_context: Optional[Dict[str, Any]] = None,
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
            severity=ValidationSeverity.CRITICAL,  # Config errors are critical
            **kwargs
        )
        self.config_issue = config_issue
        self.config_key = config_key
        self.config_value = config_value
        self.valid_options = valid_options or []
        self.config_context = config_context or {}
    
    def get_category(self) -> str:
        return "validation_config"
    
    def should_fail_fast(self) -> bool:
        """Configuration errors should fail fast."""
        return True


class ValidationDependencyError(ValidationError):
    """Exception for validation dependency and prerequisite failures."""
    
    def __init__(
        self,
        dependency_type: str,
        dependency_name: str,
        dependency_issue: str,
        dependent_validations: Optional[List[str]] = None,
        dependency_context: Optional[Dict[str, Any]] = None,
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
        self.dependency_context = dependency_context or {}
    
    def get_category(self) -> str:
        return "validation_dependency"
    
    def is_retryable(self) -> bool:
        """Dependency errors might be retryable."""
        return True


class ValidationBatchError(ValidationError):
    """Exception for batch validation and bulk operation failures."""
    
    def __init__(
        self,
        batch_size: int,
        failed_items: List[Dict[str, Any]],
        batch_context: Optional[Dict[str, Any]] = None,
        failure_threshold: Optional[float] = None,
        **kwargs
    ):
        failed_count = len(failed_items)
        failure_rate = (failed_count / batch_size) * 100 if batch_size > 0 else 0
        
        message = f"Batch validation failed: {failed_count}/{batch_size} items failed ({failure_rate:.1f}%)"
        
        if failure_threshold and failure_rate > failure_threshold:
            message += f" (exceeds {failure_threshold:.1f}% threshold)"
        
        super().__init__(
            message,
            validation_type=ValidationType.BATCH,
            context=batch_context,
            **kwargs
        )
        self.batch_size = batch_size
        self.failed_items = failed_items
        self.batch_context = batch_context or {}
        self.failure_threshold = failure_threshold
        self.failure_rate = failure_rate
    
    def get_category(self) -> str:
        return "validation_batch"


# ============ VALIDATION RESULT CLASSES ============

class ValidationResult:
    """
    Container for comprehensive validation results with enhanced reporting capabilities.
    
    Provides structured access to validation outcomes, error categorization,
    and detailed reporting for both successful and failed validations.
    """
    
    def __init__(
        self,
        is_valid: bool = True,
        errors: Optional[List[ValidationError]] = None,
        warnings: Optional[List[ValidationError]] = None,
        info: Optional[List[ValidationError]] = None,
        context: Optional[Dict[str, Any]] = None,
        validation_metadata: Optional[Dict[str, Any]] = None
    ):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.info = info or []
        self.context = context or {}
        self.validation_metadata = validation_metadata or {}
        self._update_validity()
    
    def _update_validity(self):
        """Update validity based on current errors."""
        self.is_valid = len(self.errors) == 0
    
    @property
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
    
    @property
    def has_info(self) -> bool:
        """Check if there are any info messages."""
        return len(self.info) > 0
    
    @property
    def total_issues(self) -> int:
        """Get total count of all issues."""
        return len(self.errors) + len(self.warnings) + len(self.info)
    
    @property
    def critical_errors(self) -> List[ValidationError]:
        """Get all critical errors."""
        return [error for error in self.errors if error.severity == ValidationSeverity.CRITICAL]
    
    @property
    def has_critical_errors(self) -> bool:
        """Check if there are any critical errors."""
        return len(self.critical_errors) > 0
    
    @property
    def should_fail_fast(self) -> bool:
        """Check if any errors require immediate failure."""
        return any(error.should_fail_fast() for error in self.errors)
    
    @property
    def status(self) -> ValidationStatus:
        """Get overall validation status."""
        if self.has_critical_errors:
            return ValidationStatus.CRITICAL_FAILURE
        elif self.has_errors:
            return ValidationStatus.FAILED
        elif self.has_warnings:
            return ValidationStatus.PASSED_WITH_WARNINGS
        else:
            return ValidationStatus.PASSED
    
    def add_error(self, error: ValidationError):
        """Add an error to the validation result."""
        self.errors.append(error)
        self._update_validity()
    
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
        self.validation_metadata.update(other.validation_metadata)
        self._update_validity()
    
    def filter_by_severity(self, severity: ValidationSeverity) -> List[ValidationError]:
        """Get all issues with a specific severity level."""
        all_issues = self.errors + self.warnings + self.info
        return [issue for issue in all_issues if issue.severity == severity]
    
    def filter_by_type(self, validation_type: ValidationType) -> List[ValidationError]:
        """Get all issues of a specific validation type."""
        all_issues = self.errors + self.warnings + self.info
        return [issue for issue in all_issues if issue.validation_type == validation_type]
    
    def filter_by_category(self, category: str) -> List[ValidationError]:
        """Get all issues of a specific category."""
        all_issues = self.errors + self.warnings + self.info
        return [issue for issue in all_issues if issue.get_category() == category]
    
    def get_most_severe_error(self) -> Optional[ValidationError]:
        """Get the most severe error."""
        if not self.errors:
            return None
        return max(self.errors, key=lambda e: get_validation_severity_level(e))
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get summary count of errors by severity."""
        all_issues = self.errors + self.warnings + self.info
        summary = {}
        
        for severity in ValidationSeverity:
            count = len([issue for issue in all_issues if issue.severity == severity])
            if count > 0:
                summary[severity.value] = count
        
        return summary
    
    def get_category_summary(self) -> Dict[str, int]:
        """Get summary count of issues by category."""
        all_issues = self.errors + self.warnings + self.info
        summary = {}
        
        for issue in all_issues:
            category = issue.get_category()
            summary[category] = summary.get(category, 0) + 1
        
        return summary


# ============ UTILITY FUNCTIONS FOR EXCEPTION HANDLING ============

def categorize_validation_error(error: ValidationError) -> str:
    """
    Categorize a validation error for handling and reporting.
    
    Args:
        error: The validation error to categorize
        
    Returns:
        Category string for routing and handling
    """
    return error.get_category()


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
    return error.severity == ValidationSeverity.CRITICAL or error.should_fail_fast()


def is_retryable_validation_error(error: ValidationError) -> bool:
    """
    Check if validation error is retryable.
    
    Args:
        error: The validation error to check
        
    Returns:
        True if this error might succeed on retry
    """
    return error.is_retryable()


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


def group_validation_errors_by_category(errors: List[ValidationError]) -> Dict[str, List[ValidationError]]:
    """
    Group validation errors by category for organized reporting.
    
    Args:
        errors: List of validation errors
        
    Returns:
        Dictionary mapping categories to errors
    """
    grouped = {}
    
    for error in errors:
        category = error.get_category()
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(error)
    
    return grouped


def create_validation_summary(result: ValidationResult) -> Dict[str, Any]:
    """
    Create a comprehensive summary of validation results for reporting.
    
    Args:
        result: The validation result to summarize
        
    Returns:
        Summary dictionary with detailed breakdown
    """
    all_issues = result.errors + result.warnings + result.info
    
    summary = {
        "is_valid": result.is_valid,
        "status": result.status.value,
        "total_issues": result.total_issues,
        "error_count": len(result.errors),
        "warning_count": len(result.warnings),
        "info_count": len(result.info),
        "critical_error_count": len(result.critical_errors),
        "should_fail_fast": result.should_fail_fast,
        "errors_by_severity": result.get_error_summary(),
        "errors_by_category": result.get_category_summary(),
        "errors_by_type": group_validation_errors_by_type(result.errors),
        "errors_by_field": group_validation_errors_by_field(result.errors),
        "warnings_by_type": group_validation_errors_by_type(result.warnings),
        "most_severe": None,
        "context": result.context,
        "validation_metadata": result.validation_metadata
    }
    
    # Find most severe error
    if all_issues:
        most_severe = max(all_issues, key=get_validation_severity_level)
        summary["most_severe"] = {
            "message": str(most_severe),
            "error_code": most_severe.error_code,
            "severity": most_severe.severity.value,
            "type": most_severe.validation_type.value if most_severe.validation_type else "unknown",
            "category": most_severe.get_category(),
            "field": most_severe.field_name,
            "is_retryable": most_severe.is_retryable(),
            "should_fail_fast": most_severe.should_fail_fast(),
            "recovery_suggestions": most_severe.recovery_suggestions
        }
    
    return summary


def create_error_context(
    operation: str,
    content_type: Optional[ContentType] = None,
    stage: Optional[str] = None,
    progress: Optional[float] = None,
    additional_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized error context for validation operations.
    
    Args:
        operation: Name of the operation that failed
        content_type: Type of content being validated
        stage: Current stage of the operation
        progress: Progress percentage (0.0-1.0)
        additional_context: Additional context information
        
    Returns:
        Context dictionary for error reporting
    """
    context = {
        "operation": operation,
        "timestamp": datetime.utcnow().isoformat(),
        "stage": stage,
        "progress": progress
    }
    
    if content_type:
        context["content_type"] = content_type.value
    
    if additional_context:
        context.update(additional_context)
    
    return context


# ============ MODULE METADATA ============

__version__ = '2.0.0'
__description__ = 'Base exceptions and validation framework for D&D Creative Content Framework'
__author__ = 'D&D Character Creator Backend6'

# Clean Architecture compliance metadata
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/exceptions",
    "dependencies": ["core/enums"],
    "dependents": ["domain/services", "application/use_cases", "infrastructure"],
    "infrastructure_independent": True,
    "focuses_on": "Fundamental D&D validation business rules and exception hierarchy"
}

# Exception statistics
EXCEPTION_STATISTICS = {
    "abstract_base_exceptions": 1,
    "framework_base_exceptions": 2, 
    "foundational_validation_exceptions": 6,
    "system_validation_exceptions": 6,
    "result_classes": 1,
    "total_exception_types": 16,
    "utility_functions": 12
}