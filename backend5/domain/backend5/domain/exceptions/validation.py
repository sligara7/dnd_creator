class ValidationException(Exception):
    """Base class for validation exceptions."""
    pass

class ValidationError(ValidationException):
    """Raised when validation fails."""
    
    def __init__(self, message: str):
        super().__init__(message)

class MissingFieldError(ValidationError):
    """Raised when a required field is missing."""
    
    def __init__(self, field_name: str):
        super().__init__(f"Missing required field: {field_name}")

class InvalidValueError(ValidationError):
    """Raised when a field has an invalid value."""
    
    def __init__(self, field_name: str, value: str):
        super().__init__(f"Invalid value '{value}' for field: {field_name}")

class ValueOutOfRangeError(ValidationError):
    """Raised when a value is out of the allowed range."""
    
    def __init__(self, field_name: str, value: float, min_value: float, max_value: float):
        super().__init__(f"Value '{value}' for field '{field_name}' is out of range ({min_value} - {max_value})")