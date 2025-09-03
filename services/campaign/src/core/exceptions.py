"""Campaign Service exceptions."""
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Error details for API responses."""
    request_id: str
    timestamp: str
    field: Optional[str] = None


class CampaignServiceError(HTTPException):
    """Base exception for Campaign Service."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.error_code = code
        self.error_details = details or {}
        super().__init__(
            status_code=status_code,
            detail={
                "code": code,
                "message": message,
                "details": details or {},
            }
        )


class CampaignNotFoundError(CampaignServiceError):
    """Raised when campaign is not found."""
    def __init__(self, campaign_id: UUID, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            status_code=404,
            code="CAMPAIGN_NOT_FOUND",
            message=f"Campaign {campaign_id} not found",
            details=details,
        )


class InvalidThemeError(CampaignServiceError):
    """Raised when theme is not supported."""
    def __init__(self, theme: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            status_code=400,
            code="INVALID_THEME",
            message=f"Theme '{theme}' is not supported",
            details=details,
        )


class GenerationError(CampaignServiceError):
    """Raised when content generation fails."""
    def __init__(self, content_type: str, error: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            status_code=500,
            code="GENERATION_ERROR",
            message=f"Failed to generate {content_type}: {error}",
            details=details,
        )


class BranchConflictError(CampaignServiceError):
    """Raised when plot branch conflict detected."""
    def __init__(self, branch: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            status_code=409,
            code="BRANCH_CONFLICT",
            message=f"Conflict detected in branch '{branch}'",
            details=details,
        )


class DependencyError(CampaignServiceError):
    """Raised when chapter dependency issue occurs."""
    def __init__(self, chapter_id: UUID, dependencies: list[str], details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            status_code=400,
            code="DEPENDENCY_ERROR",
            message=f"Chapter {chapter_id} has dependency issues: {', '.join(dependencies)}",
            details=details,
        )


class IntegrationError(CampaignServiceError):
    """Raised when service integration fails."""
    def __init__(self, service: str, error: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            status_code=503,
            code="INTEGRATION_ERROR",
            message=f"Integration error with {service}: {error}",
            details=details,
        )


class ThemeError(CampaignServiceError):
    """Raised when theme application fails."""
    def __init__(self, theme: str, error: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            status_code=500,
            code="THEME_ERROR",
            message=f"Failed to apply theme '{theme}': {error}",
            details=details,
        )


class ValidationError(CampaignServiceError):
    """Raised when validation fails."""
    def __init__(self, field: str, error: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            status_code=400,
            code="VALIDATION_ERROR",
            message=f"Validation error for {field}: {error}",
            details={"field": field, **(details or {})},
        )


class PermissionDeniedError(CampaignServiceError):
    """Raised when user lacks required permissions."""
    def __init__(self, action: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            status_code=403,
            code="PERMISSION_DENIED",
            message=f"Permission denied for action: {action}",
            details=details,
        )


class RateLimitExceededError(CampaignServiceError):
    """Raised when rate limit is exceeded."""
    def __init__(self, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            status_code=429,
            code="RATE_LIMIT_EXCEEDED",
            message="Rate limit exceeded",
            details=details,
        )


class LimitsExceededError(CampaignServiceError):
    """Raised when service limits are exceeded."""
    def __init__(self, limit_type: str, current: int, maximum: int, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            status_code=400,
            code="LIMITS_EXCEEDED",
            message=f"{limit_type} limit exceeded: {current}/{maximum}",
            details={"limit_type": limit_type, "current": current, "maximum": maximum, **(details or {})},
        )
