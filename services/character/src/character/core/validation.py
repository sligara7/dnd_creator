"""Base validation utilities.

This module provides core validation functionality used across the service,
including generic validators, validation result types, and validation rules.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypeVar, Generic, Callable
from uuid import UUID

from ..core.errors import ValidationError

T = TypeVar('T')

@dataclass
class ValidationResult(Generic[T]):
    """Result of a validation operation.
    
    Args:
        valid: Whether validation passed
        errors: List of validation errors
        warnings: List of validation warnings
        data: Optional validated data
    """
    valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    data: Optional[T] = None

    def add_error(self, error: str) -> None:
        """Add an error and mark as invalid."""
        self.errors.append(error)
        self.valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning."""
        self.warnings.append(warning)
    
    def merge(self, other: 'ValidationResult') -> None:
        """Merge another validation result into this one."""
        self.valid = self.valid and other.valid
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        
        # Merge data if both are dicts
        if isinstance(self.data, dict) and isinstance(other.data, dict):
            self.data.update(other.data)

@dataclass
class Validator(Generic[T]):
    """Base validator class.
    
    Args:
        rules: List of validation rule functions
        allow_empty: Whether empty/null values are allowed
    """
    rules: List[Callable[[T], ValidationResult[T]]]
    allow_empty: bool = False
    
    def validate(self, value: Optional[T]) -> ValidationResult[T]:
        """Validate a value against all rules.
        
        Args:
            value: Value to validate
            
        Returns:
            Validation result
        
        Raises:
            ValidationError: If validation fails
        """
        # Handle empty values
        if value is None or (hasattr(value, '__len__') and len(value) == 0):
            if self.allow_empty:
                return ValidationResult(valid=True, data=value)
            return ValidationResult(valid=False, errors=["Value cannot be empty"])
            
        # Run all validation rules
        result = ValidationResult(valid=True, data=value)
        for rule in self.rules:
            rule_result = rule(value)
            result.merge(rule_result)
            
        return result

def required_fields(fields: List[str]) -> Callable[[Dict], ValidationResult]:
    """Create validator that checks required fields exist.
    
    Args:
        fields: List of required field names
        
    Returns:
        Validation function
    """
    def validate(data: Dict) -> ValidationResult:
        missing = [f for f in fields if not data.get(f)]
        result = ValidationResult()
        
        if missing:
            result.add_error(f"Missing required fields: {', '.join(missing)}")
            
        return result
        
    return validate

def field_type(field: str, expected_type: type) -> Callable[[Dict], ValidationResult]:
    """Create validator that checks field type.
    
    Args:
        field: Field name to check
        expected_type: Expected Python type
        
    Returns:
        Validation function
    """
    def validate(data: Dict) -> ValidationResult:
        result = ValidationResult()
        value = data.get(field)
        
        if value is not None and not isinstance(value, expected_type):
            result.add_error(
                f"Field {field} must be type {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
            
        return result
        
    return validate

def field_length(field: str, min_len: int = 0, max_len: Optional[int] = None) -> Callable[[Dict], ValidationResult]:
    """Create validator that checks field length.
    
    Args:
        field: Field name to check
        min_len: Minimum allowed length
        max_len: Maximum allowed length (optional)
        
    Returns:
        Validation function
    """
    def validate(data: Dict) -> ValidationResult:
        result = ValidationResult()
        value = data.get(field)
        
        if value is not None:
            if len(value) < min_len:
                result.add_error(f"Field {field} must be at least {min_len} characters")
                
            if max_len is not None and len(value) > max_len:
                result.add_error(f"Field {field} cannot exceed {max_len} characters")
                
        return result
        
    return validate

def field_range(field: str, min_val: Any, max_val: Any) -> Callable[[Dict], ValidationResult]:
    """Create validator that checks numeric field range.
    
    Args:
        field: Field name to check
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Validation function
    """
    def validate(data: Dict) -> ValidationResult:
        result = ValidationResult()
        value = data.get(field)
        
        if value is not None:
            if value < min_val:
                result.add_error(f"Field {field} must be at least {min_val}")
                
            if value > max_val:
                result.add_error(f"Field {field} cannot exceed {max_val}")
                
        return result
        
    return validate

def field_regex(field: str, pattern: str) -> Callable[[Dict], ValidationResult]:
    """Create validator that checks field matches regex pattern.
    
    Args:
        field: Field name to check
        pattern: Regex pattern to match
        
    Returns:
        Validation function
    """
    import re
    
    def validate(data: Dict) -> ValidationResult:
        result = ValidationResult()
        value = data.get(field)
        
        if value is not None and not re.match(pattern, str(value)):
            result.add_error(f"Field {field} must match pattern {pattern}")
            
        return result
        
    return validate

def field_choices(field: str, choices: List[Any]) -> Callable[[Dict], ValidationResult]:
    """Create validator that checks field value is in choices.
    
    Args:
        field: Field name to check
        choices: List of valid choices
        
    Returns:
        Validation function
    """
    def validate(data: Dict) -> ValidationResult:
        result = ValidationResult()
        value = data.get(field)
        
        if value is not None and value not in choices:
            result.add_error(
                f"Field {field} must be one of: {', '.join(str(c) for c in choices)}"
            )
            
        return result
        
    return validate

def validate_uuid(value: Any) -> ValidationResult:
    """Validate that a value is a valid UUID.
    
    Args:
        value: Value to validate
        
    Returns:
        Validation result
    """
    result = ValidationResult()
    
    try:
        if not isinstance(value, UUID):
            UUID(str(value))
    except (ValueError, AttributeError, TypeError):
        result.add_error("Invalid UUID format")
        
    return result

def validate_dict_types(data: Dict[str, Any], type_map: Dict[str, type]) -> ValidationResult:
    """Validate dictionary field types match expected types.
    
    Args:
        data: Dictionary to validate
        type_map: Mapping of field names to expected types
        
    Returns:
        Validation result
    """
    result = ValidationResult()
    
    for field, expected_type in type_map.items():
        value = data.get(field)
        if value is not None and not isinstance(value, expected_type):
            result.add_error(
                f"Field {field} must be type {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
            
    return result

def validate_list_types(values: List[Any], expected_type: type) -> ValidationResult:
    """Validate all list items match expected type.
    
    Args:
        values: List to validate
        expected_type: Expected type for all items
        
    Returns:
        Validation result
    """
    result = ValidationResult()
    
    for i, value in enumerate(values):
        if not isinstance(value, expected_type):
            result.add_error(
                f"List item {i} must be type {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
            
    return result
