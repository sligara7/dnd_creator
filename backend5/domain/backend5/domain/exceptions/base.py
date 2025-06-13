class BaseDomainException(Exception):
    """Base class for all domain-specific exceptions."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"BaseDomainException: {self.message}"