"""Error handling for image service."""
import logging
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from fastapi import HTTPException, Request, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ErrorCode:
    """Error codes defined in ICD."""

    IMAGE_NOT_FOUND = "IMAGE_NOT_FOUND"
    INVALID_THEME = "INVALID_THEME"
    GENERATION_ERROR = "GENERATION_ERROR"
    OVERLAY_ERROR = "OVERLAY_ERROR"
    STORAGE_ERROR = "STORAGE_ERROR"
    API_ERROR = "API_ERROR"
    THEME_ERROR = "THEME_ERROR"
    PERMISSION_DENIED = "PERMISSION_DENIED"


class ErrorDetail(BaseModel):
    """Error detail model."""

    request_id: str
    timestamp: str
    field: Optional[str] = None


class ApiError(BaseModel):
    """API error response model."""

    code: str
    message: str
    details: ErrorDetail


class ImageError(HTTPException):
    """Base class for image service errors."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int,
        request_id: Optional[str] = None,
        field: Optional[str] = None
    ) -> None:
        """Initialize error.

        Args:
            code: Error code from ICD
            message: Error message
            status_code: HTTP status code
            request_id: Optional request ID
            field: Optional field name for validation errors
        """
        self.error_code = code
        self.error_time = datetime.utcnow().isoformat()
        self.request_id = request_id
        self.field = field

        super().__init__(
            status_code=status_code,
            detail=self.to_dict()
        )

    def to_dict(self) -> Dict:
        """Convert error to dict format.

        Returns:
            Error dict matching ICD format
        """
        return {
            "error": {
                "code": self.error_code,
                "message": str(self.detail)
            },
            "details": {
                "request_id": self.request_id,
                "timestamp": self.error_time,
                "field": self.field
            }
        }


class ImageNotFoundError(ImageError):
    """Error raised when image is not found."""

    def __init__(
        self,
        image_id: UUID,
        request_id: Optional[str] = None
    ) -> None:
        """Initialize error.

        Args:
            image_id: ID of image not found
            request_id: Optional request ID
        """
        super().__init__(
            code=ErrorCode.IMAGE_NOT_FOUND,
            message=f"Image not found: {image_id}",
            status_code=status.HTTP_404_NOT_FOUND,
            request_id=request_id
        )


class InvalidThemeError(ImageError):
    """Error raised for invalid theme operations."""

    def __init__(
        self,
        theme: str,
        request_id: Optional[str] = None
    ) -> None:
        """Initialize error.

        Args:
            theme: Invalid theme name
            request_id: Optional request ID
        """
        super().__init__(
            code=ErrorCode.INVALID_THEME,
            message=f"Invalid theme: {theme}",
            status_code=status.HTTP_400_BAD_REQUEST,
            request_id=request_id
        )


class GenerationError(ImageError):
    """Error raised when image generation fails."""

    def __init__(
        self,
        message: str,
        request_id: Optional[str] = None
    ) -> None:
        """Initialize error.

        Args:
            message: Error message
            request_id: Optional request ID
        """
        super().__init__(
            code=ErrorCode.GENERATION_ERROR,
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=request_id
        )


class OverlayError(ImageError):
    """Error raised when overlay operation fails."""

    def __init__(
        self,
        message: str,
        request_id: Optional[str] = None,
        field: Optional[str] = None
    ) -> None:
        """Initialize error.

        Args:
            message: Error message
            request_id: Optional request ID
            field: Optional field name
        """
        super().__init__(
            code=ErrorCode.OVERLAY_ERROR,
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            request_id=request_id,
            field=field
        )


class StorageError(ImageError):
    """Error raised for storage operations."""

    def __init__(
        self,
        message: str,
        request_id: Optional[str] = None
    ) -> None:
        """Initialize error.

        Args:
            message: Error message
            request_id: Optional request ID
        """
        super().__init__(
            code=ErrorCode.STORAGE_ERROR,
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=request_id
        )


class ThemeError(ImageError):
    """Error raised for theme operations."""

    def __init__(
        self,
        message: str,
        request_id: Optional[str] = None,
        field: Optional[str] = None
    ) -> None:
        """Initialize error.

        Args:
            message: Error message
            request_id: Optional request ID
            field: Optional field name
        """
        super().__init__(
            code=ErrorCode.THEME_ERROR,
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            request_id=request_id,
            field=field
        )


class PermissionError(ImageError):
    """Error raised for permission issues."""

    def __init__(
        self,
        message: str,
        request_id: Optional[str] = None
    ) -> None:
        """Initialize error.

        Args:
            message: Error message
            request_id: Optional request ID
        """
        super().__init__(
            code=ErrorCode.PERMISSION_DENIED,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            request_id=request_id
        )


async def handle_validation_error(
    request: Request,
    exc: Exception
) -> Dict:
    """Handle validation errors.

    Args:
        request: FastAPI request
        exc: Validation exception

    Returns:
        Error response dict
    """
    return {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": str(exc)
        },
        "details": {
            "request_id": request.headers.get("X-Request-ID"),
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [err["loc"] for err in exc.errors()]
        }
    }


async def handle_generic_error(
    request: Request,
    exc: Exception
) -> Dict:
    """Handle generic errors.

    Args:
        request: FastAPI request
        exc: Exception instance

    Returns:
        Error response dict
    """
    logger.exception("Unhandled error")
    return {
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "An internal error occurred"
        },
        "details": {
            "request_id": request.headers.get("X-Request-ID"),
            "timestamp": datetime.utcnow().isoformat()
        }
    }
