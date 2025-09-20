"""Custom exception classes for the Catalog Service."""

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import status

class CatalogError(Exception):
    """Base exception class for catalog service errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        validation_errors: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.validation_errors = validation_errors or {}
        self.timestamp = datetime.utcnow()

class ContentNotFoundError(CatalogError):
    """Raised when requested content is not found."""
    
    def __init__(self, content_id: str, content_type: str):
        super().__init__(
            message=f"{content_type.title()} with ID {content_id} not found",
            error_code="CONTENT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )

class ValidationError(CatalogError):
    """Raised when content validation fails."""
    
    def __init__(self, message: str, validation_errors: Dict[str, Any]):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            validation_errors=validation_errors,
        )

class StorageServiceError(CatalogError):
    """Raised when there is an error communicating with the storage service."""
    
    def __init__(self, message: str):
        super().__init__(
            message=f"Storage service error: {message}",
            error_code="STORAGE_SERVICE_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY,
        )