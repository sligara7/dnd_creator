class ValidationError(Exception):
    """Base class for validation-related exceptions."""
    pass

class ValidationRuleViolation(ValidationError):
    """Exception raised for violations of validation rules."""
    def __init__(self, message):
        super().__init__(message)

class ValidationFailure(ValidationError):
    """Exception raised when validation fails."""
    def __init__(self, message):
        super().__init__(message)