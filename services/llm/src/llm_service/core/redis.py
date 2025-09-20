"""Redis cache and rate limiting implementation.

This module provides Redis-based caching and rate limiting functionality
following the requirements specified in the SRD.
"""
import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, TypeVar, Union, cast
from uuid import UUID

import redis.asyncio as redis
from prometheus_client import Counter, Histogram
from pydantic import BaseModel, Field
from structlog import get_logger

from ..core.config import Settings


# Prometheus metrics
CACHE_HITS = Counter(
    "llm_cache_hits_total",
    "Total number of cache hits",
    ["type"]
)
CACHE_MISSES = Counter(
    "llm_cache_misses_total",
    "Total number of cache misses",
    ["type"]
)
RATE_LIMIT_EXCEEDED = Counter(
    "llm_rate_limit_exceeded_total",
    "Total number of rate limit exceeded events",
    ["type"]
)
RATE_LIMIT_REMAINING = Histogram(
    "llm_rate_limit_remaining",
    "Rate limit remaining values",
    ["type"]
)
CACHE_LATENCY = Histogram(
    "llm_cache_latency_seconds",
    "Cache operation latency",
    ["operation"]
)


class RateLimitInfo(BaseModel):
    """Rate limit information."""
    limit: int = Field(..., description="Rate limit max requests")
    remaining: int = Field(..., description="Remaining requests")
    reset_at: str = Field(..., description="When the limit resets")
    ttl: int = Field(..., description="Time to live in seconds")


class CacheItem(BaseModel):
    """Cached item with metadata."""
    content: Any = Field(..., description="Cached content")
    content_type: str = Field(..., description="Content MIME type")
    created_at: str = Field(..., description="Creation timestamp")
    expires_at: str = Field(..., description="Expiration timestamp")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )


class RateLimiter:
    """Rate limiter using Redis."""

    def __init__(
        self,
        redis_client: redis.Redis,
        settings: Settings,
        logger = None
    ):
        self.redis = redis_client
        self.settings = settings
        self.logger = logger or get_logger()

    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int = 60,
        service: Optional[str] = None,
    ) -> RateLimitInfo:
        """Check if rate limit is exceeded for key.

        Args:
            key: Rate limit key
            limit: Maximum requests allowed
            window_seconds: Time window in seconds
            service: Optional service identifier for metrics

        Returns:
            RateLimitInfo with limit details
        
        Raises:
            redis.RedisError: If Redis operation fails
        """
        now = datetime.utcnow()
        window_key = f"rate_limit:{key}:{now.timestamp():.0f}"
        
        try:
            # Use Redis pipeline for atomic operations
            async with self.redis.pipeline() as pipe:
                # Get current count
                count = await pipe.incr(window_key)

                # Set expiry on first write
                if count == 1:
                    await pipe.expire(window_key, window_seconds)

                # Get remaining TTL
                ttl = await pipe.ttl(window_key)

                # Execute pipeline
                await pipe.execute()

            # Calculate remaining requests and reset time
            remaining = max(0, limit - count)
            reset_at = (now + timedelta(seconds=ttl)).isoformat()

            # Record metrics
            if service:
                RATE_LIMIT_REMAINING.labels(type=service).observe(remaining)
                if remaining == 0:
                    RATE_LIMIT_EXCEEDED.labels(type=service).inc()

            # Return rate limit info
            return RateLimitInfo(
                limit=limit,
                remaining=remaining,
                reset_at=reset_at,
                ttl=ttl
            )

        except redis.RedisError as e:
            self.logger.error(
                "rate_limit_error",
                key=key,
                error=str(e),
                service=service
            )
            raise


class Cache:
    """Redis cache implementation."""

    def __init__(
        self,
        redis_client: redis.Redis,
        settings: Settings,
        logger = None
    ):
        self.redis = redis_client
        self.settings = settings
        self.logger = logger or get_logger()
        self.default_ttl = settings.CACHE_TTL

    async def get(
        self,
        key: str,
        default: Any = None,
        service: Optional[str] = None,
    ) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key
            default: Default value if key not found
            service: Optional service identifier for metrics

        Returns:
            Cached value or default if not found

        Raises:
            redis.RedisError: If Redis operation fails
        """
        try:
            with CACHE_LATENCY.labels(operation="get").time():
                data = await self.redis.get(key)

            if not data:
                if service:
                    CACHE_MISSES.labels(type=service).inc()
                return default

            if service:
                CACHE_HITS.labels(type=service).inc()

            # Parse cached item
            item = CacheItem.parse_raw(data)

            # Check if expired
            if datetime.fromisoformat(item.expires_at) < datetime.utcnow():
                await self.delete(key)
                return default

            return item.content

        except redis.RedisError as e:
            self.logger.error(
                "cache_get_error",
                key=key,
                error=str(e),
                service=service
            )
            raise

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        content_type: str = "application/json",
        metadata: Optional[Dict[str, Any]] = None,
        service: Optional[str] = None,
    ) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            content_type: Content MIME type
            metadata: Optional metadata
            service: Optional service identifier for metrics

        Returns:
            True if successful

        Raises:
            redis.RedisError: If Redis operation fails
        """
        try:
            expires_at = datetime.utcnow() + timedelta(
                seconds=ttl or self.default_ttl
            )

            # Create cache item
            item = CacheItem(
                content=value,
                content_type=content_type,
                created_at=datetime.utcnow().isoformat(),
                expires_at=expires_at.isoformat(),
                metadata=metadata or {}
            )

            # Store in Redis
            with CACHE_LATENCY.labels(operation="set").time():
                return await self.redis.set(
                    key,
                    item.json(),
                    ex=ttl or self.default_ttl
                )

        except redis.RedisError as e:
            self.logger.error(
                "cache_set_error",
                key=key,
                error=str(e),
                service=service
            )
            raise

    async def delete(
        self,
        key: str,
        service: Optional[str] = None,
    ) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key
            service: Optional service identifier for metrics

        Returns:
            True if key was deleted

        Raises:
            redis.RedisError: If Redis operation fails
        """
        try:
            with CACHE_LATENCY.labels(operation="delete").time():
                return bool(await self.redis.delete(key))
        except redis.RedisError as e:
            self.logger.error(
                "cache_delete_error",
                key=key,
                error=str(e),
                service=service
            )
            raise

    async def exists(
        self,
        key: str,
        service: Optional[str] = None,
    ) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key to check
            service: Optional service identifier for metrics

        Returns:
            True if key exists

        Raises:
            redis.RedisError: If Redis operation fails
        """
        try:
            with CACHE_LATENCY.labels(operation="exists").time():
                return bool(await self.redis.exists(key))
        except redis.RedisError as e:
            self.logger.error(
                "cache_exists_error",
                key=key,
                error=str(e),
                service=service
            )
            raise