"""Storage service custom exceptions."""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class StorageException(HTTPException):
    """Base exception for storage service errors."""
    def __init__(
        self,
        status_code: int,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "message": message,
                "details": details or {}
            }
        )


class AssetNotFoundException(StorageException):
    """Exception raised when an asset is not found."""
    def __init__(self, asset_id: str, message: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message or f"Asset {asset_id} not found",
            details={"asset_id": asset_id}
        )


class AssetAlreadyExistsException(StorageException):
    """Exception raised when attempting to create a duplicate asset."""
    def __init__(self, checksum: str, existing_id: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message="Asset with this content already exists",
            details={
                "checksum": checksum,
                "existing_asset_id": existing_id
            }
        )


class InvalidAssetException(StorageException):
    """Exception raised when asset data is invalid."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            details=details
        )


class StorageOperationException(StorageException):
    """Exception raised when a storage operation fails."""
    def __init__(self, operation: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Storage operation '{operation}' failed: {message}",
            details=details
        )


class S3StorageException(StorageException):
    """Exception raised when S3 storage operations fail."""
    def __init__(self, operation: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"S3 operation '{operation}' failed: {message}",
            details=details
        )


class ValidationError(StorageException):
    """Exception raised when request validation fails."""
    def __init__(self, message: str, errors: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            details={"errors": errors or {}}
        )


class AuthorizationError(StorageException):
    """Exception raised when authorization fails."""
    def __init__(self, message: str = "Authorization failed"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message
        )


class QuotaExceededError(StorageException):
    """Exception raised when storage quota is exceeded."""
    def __init__(self, service: str, current_usage: int, limit: int):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            message="Storage quota exceeded",
            details={
                "service": service,
                "current_usage": current_usage,
                "limit": limit
            }
        )