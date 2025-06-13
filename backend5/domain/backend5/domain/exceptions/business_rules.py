class BusinessRuleViolation(Exception):
    """Exception raised for violations of business rules."""
    def __init__(self, message: str):
        super().__init__(message)