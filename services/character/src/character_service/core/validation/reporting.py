"""Enhanced validation reporting system."""
from dataclasses import dataclass
from typing import Dict, List, Optional

from character_service.core.validation.interfaces import ValidationResult, ValidationSeverity


@dataclass
class FixSuggestion:
    """Represents a suggested fix for a validation issue."""

    description: str  # Human-readable description of the fix
    auto_fixable: bool  # Whether this can be auto-fixed
    field_path: str  # JSON path to the field that needs fixing
    example_value: Optional[str] = None  # Example of valid value if applicable
    related_fields: Optional[List[str]] = None  # Other fields that might need attention


@dataclass
class ValidationReport:
    """Comprehensive validation report with fix suggestions."""

    results: List[ValidationResult]
    character_id: str
    summary: str
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    fixes_available: int = 0
    auto_fixes_available: int = 0
    suggestions: Dict[str, List[FixSuggestion]] = None

    def __post_init__(self):
        """Initialize derived fields."""
        self.suggestions = {}
        self._analyze_results()

    def _analyze_results(self) -> None:
        """Analyze validation results and generate statistics and suggestions."""
        for result in self.results:
            # Count issues by severity
            for issue in result.issues:
                if issue.severity == ValidationSeverity.ERROR:
                    self.error_count += 1
                elif issue.severity == ValidationSeverity.WARNING:
                    self.warning_count += 1
                else:
                    self.info_count += 1

                # Track fixes
                if issue.fix_available:
                    self.fixes_available += 1
                    if self._can_auto_fix(issue):
                        self.auto_fixes_available += 1

                # Generate fix suggestions
                if suggestion := self._generate_fix_suggestion(issue):
                    if issue.field not in self.suggestions:
                        self.suggestions[issue.field] = []
                    self.suggestions[issue.field].append(suggestion)

    def _can_auto_fix(self, issue) -> bool:
        """Check if an issue can be automatically fixed."""
        # Check issue metadata for auto-fix capability
        metadata = issue.metadata or {}
        return (
            issue.fix_available
            and metadata.get("auto_fixable", False)
            and metadata.get("fix_value") is not None
        )

    def _generate_fix_suggestion(self, issue) -> Optional[FixSuggestion]:
        """Generate a fix suggestion for a validation issue."""
        metadata = issue.metadata or {}

        # Get example value if available
        example = None
        if "recommended_value" in metadata:
            example = str(metadata["recommended_value"])
        elif "recommended_max" in metadata:
            example = f"<= {metadata['recommended_max']}"
        elif "expected" in metadata:
            example = str(metadata["expected"])

        # Get related fields
        related = metadata.get("related_fields", [])

        # Generate fix description
        description = self._generate_fix_description(issue)

        return FixSuggestion(
            description=description,
            auto_fixable=self._can_auto_fix(issue),
            field_path=issue.field,
            example_value=example,
            related_fields=related,
        )

    def _generate_fix_description(self, issue) -> str:
        """Generate a detailed fix description based on the issue."""
        metadata = issue.metadata or {}

        # Base message
        message = issue.message

        # Add specific guidance based on metadata
        if "current" in metadata and "expected" in metadata:
            message += f" (Current: {metadata['current']}, Expected: {metadata['expected']})"

        if "recommended_max" in metadata:
            message += f" (Recommended maximum: {metadata['recommended_max']})"

        if "alternatives" in metadata:
            alternatives = metadata["alternatives"]
            if isinstance(alternatives, list) and alternatives:
                message += f" Consider using: {', '.join(alternatives)}"

        # Add auto-fix information
        if self._can_auto_fix(issue):
            message += f" This can be automatically fixed to: {metadata['fix_value']}"

        return message


class ValidationReporter:
    """Generates comprehensive validation reports."""

    def create_report(
        self, results: List[ValidationResult], character_id: str
    ) -> ValidationReport:
        """Create a validation report from results.

        Args:
            results: List of validation results
            character_id: ID of the validated character

        Returns:
            ValidationReport with analysis and suggestions
        """
        # Create initial report
        report = ValidationReport(
            results=results,
            character_id=character_id,
            summary=self._generate_summary(results),
        )

        return report

    def _generate_summary(self, results: List[ValidationResult]) -> str:
        """Generate a human-readable summary of validation results."""
        # Count issues by type
        error_count = sum(
            1
            for r in results
            for i in r.issues
            if i.severity == ValidationSeverity.ERROR
        )
        warning_count = sum(
            1
            for r in results
            for i in r.issues
            if i.severity == ValidationSeverity.WARNING
        )
        info_count = sum(
            1
            for r in results
            for i in r.issues
            if i.severity == ValidationSeverity.INFO
        )

        # Generate summary message
        if not (error_count or warning_count or info_count):
            return "Character validation passed with no issues."

        parts = []
        if error_count:
            parts.append(f"{error_count} error{'s' if error_count != 1 else ''}")
        if warning_count:
            parts.append(f"{warning_count} warning{'s' if warning_count != 1 else ''}")
        if info_count:
            parts.append(f"{info_count} suggestion{'s' if info_count != 1 else ''}")

        summary = "Character validation found " + ", ".join(parts)
        if error_count:
            summary += ". Character may not be playable until errors are fixed."
        elif warning_count:
            summary += ". Character is playable but could be improved."
        else:
            summary += ". Character is valid with optional improvements available."

        return summary
