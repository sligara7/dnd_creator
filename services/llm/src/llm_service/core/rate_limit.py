from typing import Optional

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from llm_service.core.cache import RateLimiter
from llm_service.core.exceptions import QuotaExceededError
from llm_service.core.settings import Settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for enforcing rate limits."""

    def __init__(self, app, settings: Settings, rate_limiter: RateLimiter) -> None:
        super().__init__(app)
        self.settings = settings
        self.rate_limiter = rate_limiter

    async def get_identity_key(self, request: Request) -> str:
        """Get key for rate limiting.

        By default, uses the client's IP address. Can be extended to use API key,
        user ID, or other identifiers.
        """
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        return ip

    async def get_user_id(self, request: Request) -> Optional[str]:
        """Get user ID from request, if available."""
        # TODO: Implement proper user ID extraction from auth token/headers
        return request.headers.get("X-User-ID", "anonymous")

    async def check_rate_limits(self, request: Request) -> None:
        """Check if request passes all rate limits."""
        identity_key = await self.get_identity_key(request)
        user_id = await self.get_user_id(request)

        # Skip rate limiting for health check endpoints
        if request.url.path == "/health":
            return

        # Get rate limit results
        results = await self.rate_limiter.check_all_limits(identity_key, user_id)

        # Check text generation limits
        if request.url.path.startswith("/api/v2/text"):
            allowed, remaining = results["text"]
            if not allowed:
                raise QuotaExceededError(
                    message="Text generation rate limit exceeded",
                    details={
                        "limit": self.settings.rate_limits.text_generation_rpm,
                        "window": "60 seconds",
                        "retry_after": "60 seconds",
                    },
                )

        # Check image generation limits
        elif request.url.path.startswith("/api/v2/image"):
            allowed, remaining = results["image"]
            if not allowed:
                raise QuotaExceededError(
                    message="Image generation rate limit exceeded",
                    details={
                        "limit": self.settings.rate_limits.image_generation_rpm,
                        "window": "60 seconds",
                        "retry_after": "60 seconds",
                    },
                )

        # Check user limits
        user_allowed, user_remaining = results["user"]
        if not user_allowed:
            raise QuotaExceededError(
                message="User rate limit exceeded",
                details={
                    "limit": self.settings.rate_limits.user_rpm,
                    "window": "60 seconds",
                    "retry_after": "60 seconds",
                },
            )

        # Check global limits
        global_allowed, global_remaining = results["global"]
        if not global_allowed:
            raise QuotaExceededError(
                message="Global rate limit exceeded",
                details={
                    "limit": self.settings.rate_limits.global_rpm,
                    "window": "60 seconds",
                    "retry_after": "60 seconds",
                },
            )

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        """Process request and enforce rate limits."""
        await self.check_rate_limits(request)

        response = await call_next(request)
        return response
