"""Error handling and retry mechanisms."""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, Optional, Type, TypeVar

from image_service.core.config import get_settings
from image_service.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

T = TypeVar("T")


@dataclass
class RetryConfig:
    """Retry configuration."""

    max_retries: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0
    jitter: float = 0.1  # 10% jitter


class GenerationError(Exception):
    """Base class for generation errors."""

    def __init__(
        self,
        message: str,
        error_type: str,
        is_retryable: bool = True,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize generation error."""
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.is_retryable = is_retryable
        self.details = details or {}
        self.timestamp = datetime.utcnow()


class APIError(GenerationError):
    """Error from external API."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
    ):
        """Initialize API error."""
        super().__init__(
            message=message,
            error_type="api_error",
            is_retryable=self._is_retryable(status_code),
            details={
                "status_code": status_code,
                "response": response,
            },
        )

    @staticmethod
    def _is_retryable(status_code: Optional[int]) -> bool:
        """Determine if error is retryable based on status code."""
        if not status_code:
            return True
        # 4xx errors are typically not retryable (except rate limits)
        if 400 <= status_code < 500:
            return status_code in {408, 429}  # Timeout and rate limit
        # 5xx errors are typically retryable
        return status_code >= 500


class ValidationError(GenerationError):
    """Error during input validation."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
    ):
        """Initialize validation error."""
        super().__init__(
            message=message,
            error_type="validation_error",
            is_retryable=False,  # Validation errors are not retryable
            details={
                "field": field,
                "value": value,
            },
        )


class ProcessingError(GenerationError):
    """Error during image processing."""

    def __init__(
        self,
        message: str,
        stage: str,
        is_retryable: bool = True,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize processing error."""
        super().__init__(
            message=message,
            error_type="processing_error",
            is_retryable=is_retryable,
            details={"stage": stage, **(details or {})},
        )


def with_retry(
    config: Optional[RetryConfig] = None,
    retryable_exceptions: Optional[tuple[Type[Exception], ...]] = None,
) -> Callable:
    """Decorator for retrying async functions with exponential backoff."""

    config = config or RetryConfig()
    if retryable_exceptions is None:
        retryable_exceptions = (GenerationError,)

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            attempt = 0
            last_error = None

            while attempt < config.max_retries:
                try:
                    return await func(*args, **kwargs)

                except retryable_exceptions as e:
                    # Check if error is retryable
                    if isinstance(e, GenerationError) and not e.is_retryable:
                        raise

                    attempt += 1
                    last_error = e

                    if attempt >= config.max_retries:
                        break

                    # Calculate delay with exponential backoff and jitter
                    delay = min(
                        config.base_delay * (config.exponential_base ** (attempt - 1)),
                        config.max_delay,
                    )
                    jitter_range = delay * config.jitter
                    actual_delay = delay + (jitter_range * (asyncio.get_running_loop().time() % 1))

                    logger.warning(
                        "Retrying operation",
                        attempt=attempt,
                        max_retries=config.max_retries,
                        delay=actual_delay,
                        error=str(e),
                    )

                    await asyncio.sleep(actual_delay)

                except Exception as e:
                    # Non-retryable exception
                    raise

            # Max retries exceeded
            raise last_error or RuntimeError("Max retries exceeded")

        return wrapper

    return decorator


def rate_limit_handler(
    window_size: int = 60,  # seconds
    max_requests: int = 100,  # requests per window
    retry_after: Optional[int] = None,  # seconds
) -> Callable:
    """Decorator for handling rate limits with exponential backoff."""

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        window_start = datetime.utcnow()
        request_count = 0

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            nonlocal window_start, request_count

            # Reset window if needed
            now = datetime.utcnow()
            if now - window_start > timedelta(seconds=window_size):
                window_start = now
                request_count = 0

            # Check rate limit
            if request_count >= max_requests:
                delay = retry_after or window_size - (now - window_start).seconds
                raise APIError(
                    message=f"Rate limit exceeded, retry after {delay} seconds",
                    status_code=429,
                    response={"retry_after": delay},
                )

            # Execute function
            try:
                request_count += 1
                return await func(*args, **kwargs)
            except Exception:
                # Decrement counter on error
                request_count -= 1
                raise

        return wrapper

    return decorator
