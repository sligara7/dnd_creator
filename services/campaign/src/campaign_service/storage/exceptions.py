"""Storage service client exceptions."""

from typing import Any, Dict, Optional

class StorageError(Exception):
    """Base exception for storage service errors."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize storage error.
        
        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message)
        self.details = details or {}


class StorageConnectionError(StorageError):
    """Raised when connection to storage service fails."""
    pass


class StorageQueryError(StorageError):
    """Raised when storage query fails."""
    pass


class StorageTimeoutError(StorageError):
    """Raised when storage operation times out."""
    pass


class StorageNotFoundError(StorageError):
    """Raised when requested resource not found."""
    pass


class StorageValidationError(StorageError):
    """Raised when request validation fails."""
    pass


class StorageAuthenticationError(StorageError):
    """Raised when storage authentication fails."""
    pass