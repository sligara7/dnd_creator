"""Core utilities and configuration for Auth Service."""

from auth_service.core.config import settings
from auth_service.core.exceptions import AuthServiceError

__all__ = ["settings", "AuthServiceError"]
