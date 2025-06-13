"""
Validation Type Enumerations.

Defines validation types, severity levels, and status for content validation
in the D&D character creation system.
"""

from enum import Enum


class ValidationType(Enum):
    """Types of validation performed on generated content."""
    MECHANICAL = "mechanical"           # D&D rules and mechanics validation
    BALANCE = "balance"                 # Power level and balance validation
    THEMATIC = "thematic"               # Theme consistency validation
    INTEGRATION = "integration"         # Compatibility with existing content
    NAMING = "naming"                   # D&D naming convention validation
    PROGRESSION = "progression"         # Level progression validation
    MULTICLASS = "multiclass"           # Multiclass compatibility validation
    EXPORT = "export"                   # VTT export compatibility
    
    @property
    def is_blocking(self) -> bool:
        """Check if this validation type can block content generation."""
        return self in {
            self.MECHANICAL, 
            self.BALANCE, 
            self.PROGRESSION, 
            self.MULTICLASS
        }


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "info"                       # Informational message
    WARNING = "warning"                 # Potential issue, not blocking
    ERROR = "error"                     # Blocking issue that must be fixed
    CRITICAL = "critical"               # Fundamental rule violation
    
    @property
    def blocks_generation(self) -> bool:
        """Check if this severity blocks content generation."""
        return self in {self.ERROR, self.CRITICAL}
    
    @property
    def numeric_weight(self) -> int:
        """Get numeric weight for sorting."""
        weights = {
            self.INFO: 1,
            self.WARNING: 2, 
            self.ERROR: 3,
            self.CRITICAL: 4
        }
        return weights[self]


class ValidationStatus(Enum):
    """Status of validation results."""
    PENDING = "pending"                 # Validation not yet performed
    RUNNING = "running"                 # Validation in progress
    PASSED = "passed"                   # All validations successful
    FAILED = "failed"                   # One or more validations failed
    NEEDS_REVIEW = "needs_review"       # Manual review required
    APPROVED = "approved"               # Manually approved despite warnings
    REJECTED = "rejected"               # Manually rejected
    
    @property
    def is_complete(self) -> bool:
        """Check if validation is complete."""
        return self in {
            self.PASSED, 
            self.FAILED, 
            self.APPROVED, 
            self.REJECTED
        }
    
    @property
    def allows_usage(self) -> bool:
        """Check if content can be used with this status."""
        return self in {self.PASSED, self.APPROVED}


class ValidationScope(Enum):
    """Scope of validation being performed."""
    SINGLE_ITEM = "single_item"         # Validate single content item
    CHARACTER_BUILD = "character_build" # Validate complete character
    CONTENT_COLLECTION = "content_collection"  # Validate related content group
    FULL_PROGRESSION = "full_progression"      # Validate 1-20 progression
    MULTICLASS_BUILD = "multiclass_build"      # Validate multiclass character
    CAMPAIGN_INTEGRATION = "campaign_integration"  # Validate campaign fit


class RuleCompliance(Enum):
    """Levels of D&D rule compliance."""
    STRICT = "strict"                   # Follows all official rules exactly
    STANDARD = "standard"               # Follows core rules, allows variants
    VARIANT = "variant"                 # Uses official variant rules
    HOMEBREW = "homebrew"               # Custom rules that maintain balance
    EXPERIMENTAL = "experimental"       # Untested or edge-case rules
    
    @property
    def allows_custom_content(self) -> bool:
        """Check if this compliance level allows custom content."""
        return self in {self.HOMEBREW, self.EXPERIMENTAL}
    
    @property
    def strictness_multiplier(self) -> float:
        """Get strictness multiplier for validation."""
        multipliers = {
            self.STRICT: 1.0,
            self.STANDARD: 0.9,
            self.VARIANT: 0.8,
            self.HOMEBREW: 0.7,
            self.EXPERIMENTAL: 0.6
        }
        return multipliers[self]