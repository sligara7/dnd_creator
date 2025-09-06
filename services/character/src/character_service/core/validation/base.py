"""Base validation rule implementation."""
from typing import List, Optional

from character_service.core.validation.interfaces import (
    RuleCategory,
    ValidationIssue,
    ValidationResult,
    ValidationRule,
    ValidationSeverity,
)
from character_service.domain.models import Character


class BaseValidationRule:
    """Base class for validation rules with common functionality."""

    def __init__(
        self,
        rule_id: str,
        category: RuleCategory,
        dependencies: Optional[List[str]] = None,
    ) -> None:
        """Initialize rule.

        Args:
            rule_id: Unique ID for this rule
            category: Rule category
            dependencies: Optional list of rule IDs this rule depends on
        """
        self.rule_id = rule_id
        self.category = category
        self.dependencies = dependencies or []

    def create_issue(
        self,
        severity: ValidationSeverity,
        message: str,
        field: str,
        fix_available: bool = False,
        metadata: Optional[dict] = None,
    ) -> ValidationIssue:
        """Create a validation issue.

        Args:
            severity: Issue severity
            message: Human-readable description
            field: Path to problematic field
            fix_available: Whether this issue can be auto-fixed
            metadata: Additional context about the issue

        Returns:
            ValidationIssue
        """
        return ValidationIssue(
            rule_id=self.rule_id,
            severity=severity,
            message=message,
            field=field,
            fix_available=fix_available,
            metadata=metadata or {},
        )

    def create_result(
        self,
        character: Character,
        passed: bool,
        issues: Optional[List[ValidationIssue]] = None,
        fix_applied: bool = False,
    ) -> ValidationResult:
        """Create a validation result.

        Args:
            character: Character that was validated
            passed: Whether validation passed
            issues: Optional list of issues found
            fix_applied: Whether fixes were applied

        Returns:
            ValidationResult
        """
        return ValidationResult(
            rule_id=self.rule_id,
            passed=passed,
            issues=issues or [],
            character_id=character.id,
            fix_applied=fix_applied,
        )

    async def validate(self, character: Character) -> ValidationResult:
        """Validate the character.

        Args:
            character: Character to validate

        Returns:
            ValidationResult

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement validate()")

    async def fix(self, character: Character) -> Optional[ValidationResult]:
        """Fix validation issues.

        Args:
            character: Character to fix

        Returns:
            ValidationResult after fixes, or None if no fix available

        Notes:
            Default implementation returns None (no fix available)
        """
        return None  # No fix available by default
