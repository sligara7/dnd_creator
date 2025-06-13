from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from ..enums.validation_types import ValidationSeverity, ValidationType


@dataclass(frozen=True)
class ValidationIssue:
    """Individual validation issue found during content validation."""
    
    severity: ValidationSeverity
    code: str
    message: str
    field: Optional[str] = None
    suggested_fix: Optional[str] = None
    rule_reference: Optional[str] = None  # D&D rule reference
    
    @property
    def is_blocking(self) -> bool:
        """Check if this issue blocks content usage."""
        return self.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
    
    @property
    def is_warning(self) -> bool:
        """Check if this is a warning-level issue."""
        return self.severity == ValidationSeverity.WARNING
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
            "field": self.field,
            "suggested_fix": self.suggested_fix,
            "rule_reference": self.rule_reference,
            "is_blocking": self.is_blocking
        }


@dataclass(frozen=True)
class ValidationResult:
    """Complete result of a validation operation."""
    
    is_valid: bool
    validation_type: ValidationType
    validator_name: str
    issues: List[ValidationIssue] = field(default_factory=list)
    context: Optional[Dict[str, Any]] = None
    score: Optional[float] = None  # Numerical score if applicable (0.0 to 1.0)
    
    @property
    def blocking_issues(self) -> List[ValidationIssue]:
        """Get issues that prevent content usage."""
        return [issue for issue in self.issues if issue.is_blocking]
    
    @property
    def warnings(self) -> List[ValidationIssue]:
        """Get warning-level issues."""
        return [issue for issue in self.issues if issue.is_warning]
    
    @property
    def errors(self) -> List[ValidationIssue]:
        """Get error and critical issues."""
        return [issue for issue in self.issues if issue.is_blocking]
    
    @property
    def has_blocking_issues(self) -> bool:
        """Check if result has any blocking issues."""
        return len(self.blocking_issues) > 0
    
    @property
    def severity_summary(self) -> Dict[str, int]:
        """Get count of issues by severity."""
        summary = {severity.value: 0 for severity in ValidationSeverity}
        for issue in self.issues:
            summary[issue.severity.value] += 1
        return summary
    
    def get_issues_by_field(self, field_name: str) -> List[ValidationIssue]:
        """Get all issues related to a specific field."""
        return [issue for issue in self.issues if issue.field == field_name]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "is_valid": self.is_valid,
            "validation_type": self.validation_type.value,
            "validator_name": self.validator_name,
            "score": self.score,
            "issues": [issue.to_dict() for issue in self.issues],
            "context": self.context,
            "summary": {
                "total_issues": len(self.issues),
                "blocking_issues": len(self.blocking_issues),
                "warnings": len(self.warnings),
                "severity_breakdown": self.severity_summary
            }
        }


@dataclass(frozen=True)
class ValidationSummary:
    """Summary of multiple validation results."""
    
    results: List[ValidationResult]
    overall_valid: bool
    
    @property
    def all_issues(self) -> List[ValidationIssue]:
        """Get all issues from all validation results."""
        issues = []
        for result in self.results:
            issues.extend(result.issues)
        return issues
    
    @property
    def blocking_issues(self) -> List[ValidationIssue]:
        """Get all blocking issues."""
        return [issue for issue in self.all_issues if issue.is_blocking]
    
    @property
    def validation_types_run(self) -> List[ValidationType]:
        """Get list of validation types that were executed."""
        return [result.validation_type for result in self.results]
    
    @property
    def overall_score(self) -> Optional[float]:
        """Calculate overall validation score if scores are available."""
        scores = [result.score for result in self.results if result.score is not None]
        if not scores:
            return None
        return sum(scores) / len(scores)
    
    def get_results_by_type(self, validation_type: ValidationType) -> List[ValidationResult]:
        """Get validation results of a specific type."""
        return [result for result in self.results if result.validation_type == validation_type]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "overall_valid": self.overall_valid,
            "overall_score": self.overall_score,
            "validation_types": [vt.value for vt in self.validation_types_run],
            "results": [result.to_dict() for result in self.results],
            "summary": {
                "total_validations": len(self.results),
                "passed_validations": sum(1 for r in self.results if r.is_valid),
                "total_issues": len(self.all_issues),
                "blocking_issues": len(self.blocking_issues)
            }
        }

# update to the following code snippet   
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass(frozen=True)
class ValidationResult:
    """Immutable validation result following D&D 5e standards."""
    
    valid: bool
    issues: List[str]
    warnings: List[str]
    validator_name: str
    step_name: Optional[str] = None
    total_checks: int = 0
    passed_checks: int = 0
    detailed_results: Optional[Dict[str, Any]] = None
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.total_checks == 0:
            object.__setattr__(self, 'total_checks', len(self.issues) + len(self.warnings) + 1)
        if self.passed_checks == 0:
            object.__setattr__(self, 'passed_checks', 1 if self.valid else 0)
        if self.recommendations is None:
            object.__setattr__(self, 'recommendations', [])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "valid": self.valid,
            "issues": self.issues,
            "warnings": self.warnings,
            "validator": self.validator_name,
            "step": self.step_name,
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "detailed_results": self.detailed_results,
            "recommendations": self.recommendations
        }
    
    def merge_with(self, other: 'ValidationResult') -> 'ValidationResult':
        """Merge this result with another validation result."""
        return ValidationResult(
            valid=self.valid and other.valid,
            issues=self.issues + other.issues,
            warnings=self.warnings + other.warnings,
            validator_name=f"{self.validator_name}+{other.validator_name}",
            step_name=self.step_name or other.step_name,
            total_checks=self.total_checks + other.total_checks,
            passed_checks=self.passed_checks + other.passed_checks,
            recommendations=self.recommendations + other.recommendations
        )