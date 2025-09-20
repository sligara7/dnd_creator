from typing import Any, Dict, Optional

from fastapi import HTTPException
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    request_id: str
    service: str = "llm-service"
    timestamp: str


class ErrorResponse(BaseModel):
    error: Dict[str, Any]


class LLMServiceError(HTTPException):
    """Base exception for LLM service."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.error_code = code
        self.error_details = details or {}
        super().__init__(status_code=status_code, detail={"code": code, "message": message})


class TextGenerationError(LLMServiceError):
    """Error during text generation."""
    def __init__(
        self, message: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            status_code=500,
            code="TEXT_GENERATION_FAILED",
            message=message,
            details=details,
        )


class ImageGenerationError(LLMServiceError):
    """Error during image generation."""
    def __init__(
        self, message: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            status_code=500,
            code="IMAGE_GENERATION_FAILED",
            message=message,
            details=details,
        )


class InvalidPromptError(LLMServiceError):
    """Invalid prompt provided."""
    def __init__(
        self, message: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            status_code=400,
            code="INVALID_PROMPT",
            message=message,
            details=details,
        )


class QuotaExceededError(LLMServiceError):
    """API quota exceeded."""
    def __init__(
        self, message: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            status_code=429,
            code="QUOTA_EXCEEDED",
            message=message,
            details=details,
        )


class ThemeError(LLMServiceError):
    """Error applying theme."""
    def __init__(
        self, message: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            status_code=500,
            code="THEME_ERROR",
            message=message,
            details=details,
        )


class QueueFullError(LLMServiceError):
    """Processing queue is full."""
    def __init__(
        self, message: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            status_code=503,
            code="QUEUE_FULL",
            message=message,
            details=details,
        )


class InvalidParametersError(LLMServiceError):
    """Invalid request parameters."""
    def __init__(
        self, message: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            status_code=400,
            code="INVALID_PARAMETERS",
            message=message,
            details=details,
        )


class ServiceUnavailableError(LLMServiceError):
    """External service is unavailable."""
    def __init__(
        self, message: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            status_code=503,
            code="SERVICE_UNAVAILABLE",
            message=message,
            details=details,
        )


class ContentGenerationError(LLMServiceError):
    """Error during content generation."""
    def __init__(
        self, message: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            status_code=500,
            code="CONTENT_GENERATION_FAILED",
            message=message,
            details=details,
        )
