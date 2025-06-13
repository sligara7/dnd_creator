class ValidationResult:
    """
    Represents the result of a validation process.
    Contains information about the validation status,
    any violations encountered, and suggestions for resolution.
    """

    def __init__(self, is_valid: bool, violations: list = None):
        self.is_valid = is_valid
        self.violations = violations if violations is not None else []

    def add_violation(self, violation: str):
        """
        Adds a violation to the validation result.
        """
        self.violations.append(violation)

    def __repr__(self):
        return f"<ValidationResult(is_valid={self.is_valid}, violations={self.violations})>"