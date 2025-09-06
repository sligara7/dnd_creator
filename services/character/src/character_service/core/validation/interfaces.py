"""Core validation interfaces and types."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Protocol, runtime_checkable
from uuid import UUID

from character_service.domain.models import Character


class RuleCategory(str, Enum):
    """Categories for validation rules."""

    BASE = "base"  # Basic D&D 5e rules
    THEME = "theme"  # Theme-specific rules
    CAMPAIGN = "campaign"  # Campaign-related rules
    CUSTOM = "custom"  # User-defined rules


class ValidationSeverity(str, Enum):
    """Severity levels for validation issues."""

    ERROR = "error"  # Must be fixed
    WARNING = "warning"  # Should be fixed
    INFO = "info"  # Informational only


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""

    rule_id: str  # Unique ID of the rule that created this issue
    severity: ValidationSeverity
    message: str  # Human-readable description
    field: str  # Path to the problematic field
    fix_available: bool  # Whether this issue can be auto-fixed
    metadata: Dict  # Additional context about the issue


@dataclass
class ValidationResult:
    """Result of a validation rule check."""

    rule_id: str
    passed: bool
    issues: List[ValidationIssue]
    character_id: UUID
    fix_applied: bool = False


@runtime_checkable
class ValidationRule(Protocol):
    """Protocol defining the interface for validation rules."""

    rule_id: str
    category: RuleCategory
    dependencies: List[str]  # IDs of rules that must run before this one

    async def validate(self, character: Character) -> ValidationResult:
        """Validate the character against this rule.

        Args:
            character: The character to validate

        Returns:
            ValidationResult containing any issues found
        """
        ...

    async def fix(self, character: Character) -> Optional[ValidationResult]:
        """Attempt to automatically fix any issues found by this rule.

        Args:
            character: The character to fix

        Returns:
            ValidationResult after applying fixes, or None if no fix is available
        """
        ...


class ValidationEngine(ABC):
    """Abstract base class for validation engines."""

    @abstractmethod
    async def add_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule to the engine.

        Args:
            rule: The validation rule to add
        """
        ...

    @abstractmethod
    async def validate(
        self,
        character: Character,
        categories: Optional[List[RuleCategory]] = None,
        auto_fix: bool = False,
    ) -> List[ValidationResult]:
        """Validate a character against applicable rules.

        Args:
            character: The character to validate
            categories: Optional list of rule categories to run, or None for all
            auto_fix: Whether to attempt automatic fixes for issues

        Returns:
            List of validation results
        """
        ...


@dataclass
class ValidationSummary:
    """Summary of validation results for a character."""

    character_id: UUID
    passed: bool
    results: List[ValidationResult]
    error_count: int
    warning_count: int
    info_count: int
    fixes_available: int
    fixes_applied: int
