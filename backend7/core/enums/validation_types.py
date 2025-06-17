"""
Essential Validation Type Enums

Streamlined validation type classifications following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
"""

from enum import Enum, auto

# ============ VALIDATION RESULT TYPES ============

class ValidationResult(Enum):
    """Validation result classifications."""
    VALID = auto()             # Passes validation
    INVALID = auto()           # Fails validation
    WARNING = auto()           # Passes with warnings
    INCOMPLETE = auto()        # Missing required data
    REQUIRES_APPROVAL = auto() # Needs DM approval

class ValidationSeverity(Enum):
    """Validation issue severity levels."""
    INFO = auto()              # Informational
    WARNING = auto()           # Non-critical issue
    ERROR = auto()             # Critical error
    BLOCKING = auto()          # Prevents progression

class ValidationScope(Enum):
    """Validation scope classifications."""
    FIELD = auto()             # Single field validation
    OBJECT = auto()            # Object-level validation
    RELATIONSHIP = auto()      # Cross-object validation
    SYSTEM = auto()            # System-wide validation

# ============ CHARACTER VALIDATION TYPES ============

class CharacterValidation(Enum):
    """Character-specific validation types."""
    ABILITY_SCORES = auto()    # Ability score validation
    RACE_CLASS_COMBO = auto()  # Race/class compatibility
    EQUIPMENT_LIMITS = auto()  # Equipment restrictions
    SPELL_SELECTION = auto()   # Spell choice validation
    PROFICIENCY_LIMITS = auto() # Proficiency restrictions
    MULTICLASS_REQS = auto()   # Multiclassing requirements

class RuleCompliance(Enum):
    """Rule compliance validation levels."""
    STRICT = auto()            # Rules as written
    LENIENT = auto()           # Rules as intended  
    FLEXIBLE = auto()          # Reasonable interpretations
    CUSTOM = auto()            # House rules allowed

class ContentValidation(Enum):
    """Content validation categories."""
    OFFICIAL = auto()          # Official content only
    VERIFIED = auto()          # Verified homebrew
    COMMUNITY = auto()         # Community content
    EXPERIMENTAL = auto()      # Unvetted content

# ============ INPUT VALIDATION TYPES ============

class InputType(Enum):
    """Input data type validations."""
    NUMBER = auto()            # Numeric input
    TEXT = auto()              # Text input
    CHOICE = auto()            # Selection from options
    BOOLEAN = auto()           # True/false input
    LIST = auto()              # List of values

class DataFormat(Enum):
    """Data format validation types."""
    JSON = auto()              # JSON format
    STRING = auto()            # String format
    INTEGER = auto()           # Integer format
    FLOAT = auto()             # Float format
    ENUM = auto()              # Enumerated value

# ============ VALIDATION STRATEGIES ============

class ValidationStrategy(Enum):
    """Validation execution strategies."""
    IMMEDIATE = auto()         # Validate immediately
    DEFERRED = auto()          # Validate later
    BATCH = auto()             # Batch validation
    PROGRESSIVE = auto()       # Progressive validation

class ErrorHandling(Enum):
    """Error handling approaches."""
    FAIL_FAST = auto()         # Stop on first error
    COLLECT_ALL = auto()       # Collect all errors
    BEST_EFFORT = auto()       # Continue with warnings
    SILENT = auto()            # Log but don't interrupt

# ============ VALIDATION MAPPINGS ============

VALIDATION_PRIORITIES = {
    ValidationSeverity.BLOCKING: 1,    # Highest priority
    ValidationSeverity.ERROR: 2,
    ValidationSeverity.WARNING: 3,
    ValidationSeverity.INFO: 4        # Lowest priority
}

COMPLIANCE_STRICTNESS = {
    RuleCompliance.STRICT: 1.0,       # 100% compliance required
    RuleCompliance.LENIENT: 0.8,      # 80% compliance required
    RuleCompliance.FLEXIBLE: 0.6,     # 60% compliance required
    RuleCompliance.CUSTOM: 0.0        # No compliance required
}

VALIDATION_SCOPES = {
    "character_creation": [
        CharacterValidation.ABILITY_SCORES,
        CharacterValidation.RACE_CLASS_COMBO,
        CharacterValidation.EQUIPMENT_LIMITS
    ],
    "character_advancement": [
        CharacterValidation.SPELL_SELECTION,
        CharacterValidation.PROFICIENCY_LIMITS,
        CharacterValidation.MULTICLASS_REQS
    ]
}

# ============ UTILITY FUNCTIONS ============

def is_blocking_issue(severity: ValidationSeverity) -> bool:
    """Check if validation severity blocks progression."""
    return severity in [ValidationSeverity.ERROR, ValidationSeverity.BLOCKING]

def requires_user_attention(result: ValidationResult) -> bool:
    """Check if validation result requires user attention."""
    return result in [ValidationResult.INVALID, ValidationResult.WARNING, ValidationResult.REQUIRES_APPROVAL]

def get_validation_priority(severity: ValidationSeverity) -> int:
    """Get numeric priority for validation severity."""
    return VALIDATION_PRIORITIES.get(severity, 5)

def is_strict_validation(compliance: RuleCompliance) -> bool:
    """Check if compliance level is strict."""
    return compliance == RuleCompliance.STRICT

def get_compliance_threshold(compliance: RuleCompliance) -> float:
    """Get compliance threshold value."""
    return COMPLIANCE_STRICTNESS.get(compliance, 0.8)

def supports_deferred_validation(strategy: ValidationStrategy) -> bool:
    """Check if strategy supports deferred validation."""
    return strategy in [ValidationStrategy.DEFERRED, ValidationStrategy.BATCH]

def is_creation_validation(validation_type: CharacterValidation) -> bool:
    """Check if validation type applies to character creation."""
    return validation_type in VALIDATION_SCOPES.get("character_creation", [])

def continues_on_error(handling: ErrorHandling) -> bool:
    """Check if error handling continues after errors."""
    return handling in [ErrorHandling.COLLECT_ALL, ErrorHandling.BEST_EFFORT, ErrorHandling.SILENT]

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Validation results
    'ValidationResult',
    'ValidationSeverity',
    'ValidationScope',
    
    # Character validation
    'CharacterValidation',
    'RuleCompliance',
    'ContentValidation',
    
    # Input validation
    'InputType',
    'DataFormat',
    
    # Validation strategies
    'ValidationStrategy',
    'ErrorHandling',
    
    # Mappings
    'VALIDATION_PRIORITIES',
    'COMPLIANCE_STRICTNESS',
    'VALIDATION_SCOPES',
    
    # Utility functions
    'is_blocking_issue',
    'requires_user_attention',
    'get_validation_priority',
    'is_strict_validation',
    'get_compliance_threshold',
    'supports_deferred_validation',
    'is_creation_validation',
    'continues_on_error',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential validation type enumerations'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/enums",
    "focus": "validation_classification_only",
    "line_target": 150,
    "dependencies": [],
    "philosophy": "crude_functional_inspired_essential_enums"
}