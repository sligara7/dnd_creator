"""
Essential D&D Character Creator Exceptions

Streamlined exception hierarchy following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
"""

from typing import Optional, Dict, Any, List

# ============ BASE EXCEPTION HIERARCHY ============

class DnDCharacterCreatorError(Exception):
    """Base exception for all D&D character creator errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }

# ============ VALIDATION EXCEPTIONS ============

class ValidationError(DnDCharacterCreatorError):
    """Character data validation failures."""
    
    def __init__(self, field: str, value: Any, reason: str, **kwargs):
        message = f"Validation failed for '{field}': {reason}"
        details = {"field": field, "value": value, "reason": reason, **kwargs}
        super().__init__(message, details)
        self.field = field
        self.value = value
        self.reason = reason

class RuleViolationError(DnDCharacterCreatorError):
    """D&D rule violations during character creation."""
    
    def __init__(self, rule: str, violation: str, **kwargs):
        message = f"D&D rule violation: {rule} - {violation}"
        details = {"rule": rule, "violation": violation, **kwargs}
        super().__init__(message, details)
        self.rule = rule
        self.violation = violation

class CompatibilityError(DnDCharacterCreatorError):
    """Race/class/feature compatibility issues."""
    
    def __init__(self, incompatible_elements: List[str], reason: str, **kwargs):
        elements_str = ", ".join(incompatible_elements)
        message = f"Incompatible elements: {elements_str} - {reason}"
        details = {"elements": incompatible_elements, "reason": reason, **kwargs}
        super().__init__(message, details)
        self.incompatible_elements = incompatible_elements

# ============ DATA EXCEPTIONS ============

class DataNotFoundError(DnDCharacterCreatorError):
    """Required D&D data not found."""
    
    def __init__(self, data_type: str, identifier: str, **kwargs):
        message = f"{data_type} not found: {identifier}"
        details = {"data_type": data_type, "identifier": identifier, **kwargs}
        super().__init__(message, details)
        self.data_type = data_type
        self.identifier = identifier

class DataCorruptionError(DnDCharacterCreatorError):
    """D&D data corruption or format errors."""
    
    def __init__(self, data_source: str, corruption_type: str, **kwargs):
        message = f"Data corruption in {data_source}: {corruption_type}"
        details = {"source": data_source, "type": corruption_type, **kwargs}
        super().__init__(message, details)
        self.data_source = data_source
        self.corruption_type = corruption_type

# ============ CHARACTER CREATION EXCEPTIONS ============

class CharacterCreationError(DnDCharacterCreatorError):
    """General character creation process errors."""
    
    def __init__(self, stage: str, issue: str, **kwargs):
        message = f"Character creation failed at {stage}: {issue}"
        details = {"stage": stage, "issue": issue, **kwargs}
        super().__init__(message, details)
        self.stage = stage
        self.issue = issue

class InvalidChoiceError(DnDCharacterCreatorError):
    """Invalid choice during character creation."""
    
    def __init__(self, choice_type: str, invalid_choice: str, valid_choices: List[str], **kwargs):
        message = f"Invalid {choice_type}: '{invalid_choice}'"
        details = {
            "choice_type": choice_type,
            "invalid_choice": invalid_choice,
            "valid_choices": valid_choices,
            **kwargs
        }
        super().__init__(message, details)
        self.choice_type = choice_type
        self.invalid_choice = invalid_choice
        self.valid_choices = valid_choices

# ============ SYSTEM EXCEPTIONS ============

class ConfigurationError(DnDCharacterCreatorError):
    """System configuration errors."""
    
    def __init__(self, config_key: str, issue: str, **kwargs):
        message = f"Configuration error for '{config_key}': {issue}"
        details = {"config_key": config_key, "issue": issue, **kwargs}
        super().__init__(message, details)
        self.config_key = config_key

class ResourceError(DnDCharacterCreatorError):
    """Resource availability or access errors."""
    
    def __init__(self, resource: str, issue: str, **kwargs):
        message = f"Resource error with '{resource}': {issue}"
        details = {"resource": resource, "issue": issue, **kwargs}
        super().__init__(message, details)
        self.resource = resource

# ============ UTILITY FUNCTIONS ============

def create_validation_error(field: str, value: Any, reason: str) -> ValidationError:
    """Factory function for validation errors."""
    return ValidationError(field, value, reason)

def create_rule_violation(rule: str, violation: str) -> RuleViolationError:
    """Factory function for rule violation errors."""
    return RuleViolationError(rule, violation)

def create_data_not_found(data_type: str, identifier: str) -> DataNotFoundError:
    """Factory function for data not found errors."""
    return DataNotFoundError(data_type, identifier)

def is_recoverable_error(error: DnDCharacterCreatorError) -> bool:
    """Check if error is recoverable and allows retry."""
    recoverable_types = [ValidationError, InvalidChoiceError, CompatibilityError]
    return any(isinstance(error, error_type) for error_type in recoverable_types)

def get_error_severity(error: DnDCharacterCreatorError) -> str:
    """Get error severity level."""
    severity_map = {
        ValidationError: "warning",
        InvalidChoiceError: "warning",
        CompatibilityError: "error",
        RuleViolationError: "error",
        DataNotFoundError: "error",
        DataCorruptionError: "critical",
        ConfigurationError: "critical",
        ResourceError: "error"
    }
    return severity_map.get(type(error), "error")

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Base exception
    'DnDCharacterCreatorError',
    
    # Validation exceptions
    'ValidationError',
    'RuleViolationError',
    'CompatibilityError',
    
    # Data exceptions
    'DataNotFoundError',
    'DataCorruptionError',
    
    # Character creation exceptions
    'CharacterCreationError',
    'InvalidChoiceError',
    
    # System exceptions
    'ConfigurationError',
    'ResourceError',
    
    # Utility functions
    'create_validation_error',
    'create_rule_violation',
    'create_data_not_found',
    'is_recoverable_error',
    'get_error_severity',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D character creator exceptions'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/exceptions",
    "focus": "essential_error_handling_only",
    "line_target": 150,
    "dependencies": [],
    "philosophy": "crude_functional_inspired_simple_exceptions"
}