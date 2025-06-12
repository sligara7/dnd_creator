from enum import Enum, auto


class ValidationType(Enum):
    """Types of validation performed on generated content."""
    MECHANICAL = "mechanical"           # D&D rules and mechanics validation
    BALANCE = "balance"                 # Power level and balance validation
    THEMATIC = "thematic"               # Theme consistency validation
    INTEGRATION = "integration"         # Compatibility with existing content
    NAMING = "naming"                   # D&D naming convention validation
    PROGRESSION = "progression"         # Level progression validation
    MULTICLASS = "multiclass"           # Multiclass compatibility validation


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "info"                       # Informational message
    WARNING = "warning"                 # Potential issue, but not blocking
    ERROR = "error"                     # Blocking issue that must be fixed
    CRITICAL = "critical"               # Fundamental rule violation


class ValidationStatus(Enum):
    """Status of validation results."""
    PENDING = "pending"                 # Validation not yet performed
    PASSED = "passed"                   # All validations successful
    FAILED = "failed"                   # One or more validations failed
    NEEDS_REVIEW = "needs_review"       # Manual review required
    APPROVED = "approved"               # Manually approved despite warnings


class BalanceCategory(Enum):
    """Categories for balance validation."""
    POWER_LEVEL = "power_level"         # Overall power level assessment
    UTILITY = "utility"                 # Out-of-combat utility assessment
    VERSATILITY = "versatility"         # Flexibility and options assessment
    SCALING = "scaling"                 # Level scaling assessment
    RESOURCE_COST = "resource_cost"     # Resource consumption assessment


class RuleCompliance(Enum):
    """Levels of D&D rule compliance."""
    STRICT = "strict"                   # Follows all official rules exactly
    VARIANT = "variant"                 # Uses official variant rules
    HOMEBREW = "homebrew"               # Custom rules that maintain balance
    EXPERIMENTAL = "experimental"       # Untested or edge-case rules