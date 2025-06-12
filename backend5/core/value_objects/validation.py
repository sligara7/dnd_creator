from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass(frozen=True)
class ValidationIssue:
    """Individual validation issue."""
    severity: ValidationSeverity
    code: str
    message: str
    field: Optional[str] = None
    suggested_fix: Optional[str] = None
    
    @property
    def is_blocking(self) -> bool:
        """Check if this issue blocks character creation."""
        return self.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]

@dataclass(frozen=True)
class ValidationResult:
    """Result of validation operation."""
    is_valid: bool
    issues: List[ValidationIssue]
    validator_name: str
    context: Optional[Dict[str, Any]] = None
    
    @property
    def blocking_issues(self) -> List[ValidationIssue]:
        """Get issues that block character creation."""
        return [issue for issue in self.issues if issue.is_blocking]
    
    @property
    def warnings(self) -> List[ValidationIssue]:
        """Get warning-level issues."""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.WARNING]
    
    @property
    def errors(self) -> List[ValidationIssue]:
        """Get error-level issues."""
        return [issue for issue in self.issues if issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]]