import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from llm_service.core.settings import Settings


class RedisCache:
    """Redis client wrapper for caching and rate limiting."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.prefix = settings.redis.prefix
        self._client: Redis | None = None
        self._pool: ConnectionPool | None = None

    async def initialize(self) -> None:
        """Initialize Redis connection pool."""
        if not self._pool:
            self._pool = ConnectionPool.from_url(
                url=str(self.settings.redis.dsn),
                max_connections=self.settings.redis.max_connections,
                decode_responses=True,
            )
            self._client = Redis(connection_pool=self._pool)

    async def close(self) -> None:
        """Close Redis connection pool."""
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
            self._client = None

    def _make_key(self, key: str) -> str:
        """Create prefixed key."""
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if not self._client:
            raise RuntimeError("Redis client not initialized")
        return await self._client.get(self._make_key(key))

    async def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Get JSON value from cache."""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(
        self, key: str, value: Union[str, Dict[str, Any]], ttl_seconds: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL."""
        if not self._client:
            raise RuntimeError("Redis client not initialized")

        if isinstance(value, dict):
            value = json.dumps(value)

        return await self._client.set(
            self._make_key(key),
            value,
            ex=ttl_seconds,
        )

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self._client:
            raise RuntimeError("Redis client not initialized")
        return bool(await self._client.delete(self._make_key(key)))

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self._client:
            raise RuntimeError("Redis client not initialized")
        return bool(await self._client.exists(self._make_key(key)))

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment value in cache."""
        if not self._client:
            raise RuntimeError("Redis client not initialized")
        return await self._client.incr(self._make_key(key), amount)

    async def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement value in cache."""
        if not self._client:
            raise RuntimeError("Redis client not initialized")
        return await self._client.decr(self._make_key(key), amount)


class RateLimiter:
    """Rate limiter using Redis for storage."""

    def __init__(self, cache: RedisCache) -> None:
        self.cache = cache
        self.settings = cache.settings.rate_limits

    async def _check_limit(
        self, key: str, limit: int, window_seconds: int = 60
    ) -> tuple[bool, int]:
        """Check if rate limit is exceeded."""
        now = datetime.utcnow()
        window_start = int(now.timestamp()) - (int(now.timestamp()) % window_seconds)
        window_key = f"rate_limit:{key}:{window_start}"
        count = await self.cache.increment(window_key)

        if count == 1:
            # Set expiry for new window
            await self.cache.set(window_key, str(count), ttl_seconds=window_seconds)

        return count <= limit, limit - count

    async def check_text_limit(self, key: str) -> tuple[bool, int]:
        """Check text generation rate limit."""
        return await self._check_limit(
            f"text_generation:{key}", self.settings.text_generation_rpm
        )

    async def check_image_limit(self, key: str) -> tuple[bool, int]:
        """Check image generation rate limit."""
        return await self._check_limit(
            f"image_generation:{key}", self.settings.image_generation_rpm
        )

    async def check_user_limit(self, user_id: str) -> tuple[bool, int]:
        """Check user-specific rate limit."""
        return await self._check_limit(
            f"user:{user_id}", self.settings.user_rpm
        )

    async def check_global_limit(self) -> tuple[bool, int]:
        """Check global rate limit."""
        return await self._check_limit(
            "global", self.settings.global_rpm
        )

    async def check_all_limits(self, key: str, user_id: str) -> Dict[str, tuple[bool, int]]:
        """Check all applicable rate limits."""
        results = {
            "text": await self.check_text_limit(key),
            "image": await self.check_image_limit(key),
            "user": await self.check_user_limit(user_id),
            "global": await self.check_global_limit(),
        }
        return results
