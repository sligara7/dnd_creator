"""Redis cache client for state synchronization."""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Set, TypeVar, Union
from uuid import UUID

import msgpack
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from character_service.core.exceptions import CacheError
from character_service.domain.sync.models import (
    SyncConflict,
    SyncMetadata,
    SyncState,
    SyncSubscription,
)
from character_service.domain.sync.utils import with_retry, with_timeout

logger = logging.getLogger(__name__)


T = TypeVar("T")


class RedisCache:
    """Redis cache client."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: Optional[str] = None,
        db: int = 0,
        pool_size: int = 10,
        pool_timeout: int = 30,
        ttl: int = 3600,  # 1 hour default TTL
    ) -> None:
        """Initialize Redis client.

        Args:
            host: Redis host
            port: Redis port
            password: Optional Redis password
            db: Redis database number
            pool_size: Connection pool size
            pool_timeout: Connection pool timeout
            ttl: Default cache TTL in seconds
        """
        self._pool = ConnectionPool(
            host=host,
            port=port,
            password=password,
            db=db,
            max_connections=pool_size,
            timeout=pool_timeout,
            decode_responses=True,
        )
        self._client = Redis(connection_pool=self._pool)
        self._default_ttl = ttl

    async def close(self) -> None:
        """Close Redis client."""
        await self._client.close()
        await self._pool.disconnect()

    @with_retry()
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value if found
        """
        try:
            value = await self._client.get(key)
            if value:
                return msgpack.unpackb(value)
            return None
        except Exception as e:
            logger.error("Cache get error: %s", str(e))
            raise CacheError(f"Failed to get value: {str(e)}")

    @with_retry()
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL in seconds
        """
        try:
            await self._client.set(
                key,
                msgpack.packb(value),
                ex=ttl or self._default_ttl,
            )
        except Exception as e:
            logger.error("Cache set error: %s", str(e))
            raise CacheError(f"Failed to set value: {str(e)}")

    @with_retry()
    async def delete(self, key: str) -> None:
        """Delete value from cache.

        Args:
            key: Cache key
        """
        try:
            await self._client.delete(key)
        except Exception as e:
            logger.error("Cache delete error: %s", str(e))
            raise CacheError(f"Failed to delete value: {str(e)}")

    @with_retry()
    async def get_many(self, keys: Set[str]) -> Dict[str, Any]:
        """Get multiple values from cache.

        Args:
            keys: Set of cache keys

        Returns:
            Dict of key-value pairs
        """
        try:
            pipeline = self._client.pipeline()
            for key in keys:
                pipeline.get(key)
            values = await pipeline.execute()
            return {
                key: msgpack.unpackb(value) if value else None
                for key, value in zip(keys, values)
            }
        except Exception as e:
            logger.error("Cache get_many error: %s", str(e))
            raise CacheError(f"Failed to get values: {str(e)}")

    @with_retry()
    async def set_many(
        self,
        items: Dict[str, Any],
        ttl: Optional[int] = None,
    ) -> None:
        """Set multiple values in cache.

        Args:
            items: Dict of key-value pairs
            ttl: Optional TTL in seconds
        """
        try:
            pipeline = self._client.pipeline()
            for key, value in items.items():
                pipeline.set(
                    key,
                    msgpack.packb(value),
                    ex=ttl or self._default_ttl,
                )
            await pipeline.execute()
        except Exception as e:
            logger.error("Cache set_many error: %s", str(e))
            raise CacheError(f"Failed to set values: {str(e)}")

    @with_retry()
    async def delete_many(self, keys: Set[str]) -> None:
        """Delete multiple values from cache.

        Args:
            keys: Set of cache keys
        """
        try:
            pipeline = self._client.pipeline()
            for key in keys:
                pipeline.delete(key)
            await pipeline.execute()
        except Exception as e:
            logger.error("Cache delete_many error: %s", str(e))
            raise CacheError(f"Failed to delete values: {str(e)}")

    @with_retry()
    async def get_lock(
        self,
        key: str,
        ttl: int = 60,  # 1 minute default lock TTL
        retry_delay: float = 0.1,  # 100ms retry delay
        max_retries: int = 50,  # 5 seconds max wait
    ) -> bool:
        """Get distributed lock.

        Args:
            key: Lock key
            ttl: Lock TTL in seconds
            retry_delay: Delay between retries
            max_retries: Maximum number of retries

        Returns:
            Whether lock was acquired
        """
        try:
            retries = 0
            while retries < max_retries:
                locked = await self._client.set(
                    f"lock:{key}",
                    1,
                    ex=ttl,
                    nx=True,  # Only set if key doesn't exist
                )
                if locked:
                    return True
                retries += 1
                await asyncio.sleep(retry_delay)
            return False
        except Exception as e:
            logger.error("Cache lock error: %s", str(e))
            raise CacheError(f"Failed to acquire lock: {str(e)}")

    @with_retry()
    async def release_lock(self, key: str) -> None:
        """Release distributed lock.

        Args:
            key: Lock key
        """
        try:
            await self._client.delete(f"lock:{key}")
        except Exception as e:
            logger.error("Cache unlock error: %s", str(e))
            raise CacheError(f"Failed to release lock: {str(e)}")


class StateCache:
    """Cache for character state data."""

    def __init__(
        self,
        cache: RedisCache,
        ttl: int = 3600,  # 1 hour default TTL
    ) -> None:
        """Initialize cache.

        Args:
            cache: Redis cache client
            ttl: Default cache TTL in seconds
        """
        self._cache = cache
        self._ttl = ttl

    def _get_state_key(self, character_id: UUID) -> str:
        """Get cache key for character state."""
        return f"character:{character_id}:state"

    def _get_metadata_key(self, character_id: UUID, campaign_id: UUID) -> str:
        """Get cache key for sync metadata."""
        return f"character:{character_id}:campaign:{campaign_id}:metadata"

    def _get_subscription_key(self, character_id: UUID, campaign_id: UUID) -> str:
        """Get cache key for subscription."""
        return f"character:{character_id}:campaign:{campaign_id}:subscription"

    def _get_conflict_key(self, character_id: UUID, field_path: str) -> str:
        """Get cache key for conflict."""
        return f"character:{character_id}:conflict:{field_path}"

    async def get_state(self, character_id: UUID) -> Optional[Dict]:
        """Get cached character state."""
        key = self._get_state_key(character_id)
        return await self._cache.get(key)

    async def set_state(
        self,
        character_id: UUID,
        state: Dict,
        ttl: Optional[int] = None,
    ) -> None:
        """Cache character state."""
        key = self._get_state_key(character_id)
        await self._cache.set(key, state, ttl or self._ttl)

    async def get_metadata(
        self,
        character_id: UUID,
        campaign_id: UUID,
    ) -> Optional[SyncMetadata]:
        """Get cached sync metadata."""
        key = self._get_metadata_key(character_id, campaign_id)
        data = await self._cache.get(key)
        if data:
            return SyncMetadata(**data)
        return None

    async def set_metadata(
        self,
        metadata: SyncMetadata,
        ttl: Optional[int] = None,
    ) -> None:
        """Cache sync metadata."""
        key = self._get_metadata_key(metadata.character_id, metadata.campaign_id)
        await self._cache.set(key, metadata.__dict__, ttl or self._ttl)

    async def get_subscription(
        self,
        character_id: UUID,
        campaign_id: UUID,
    ) -> Optional[SyncSubscription]:
        """Get cached subscription."""
        key = self._get_subscription_key(character_id, campaign_id)
        data = await self._cache.get(key)
        if data:
            return SyncSubscription(**data)
        return None

    async def set_subscription(
        self,
        subscription: SyncSubscription,
        ttl: Optional[int] = None,
    ) -> None:
        """Cache subscription."""
        key = self._get_subscription_key(
            subscription.character_id,
            subscription.campaign_id,
        )
        await self._cache.set(key, subscription.__dict__, ttl or self._ttl)

    async def get_conflict(
        self,
        character_id: UUID,
        field_path: str,
    ) -> Optional[SyncConflict]:
        """Get cached conflict."""
        key = self._get_conflict_key(character_id, field_path)
        data = await self._cache.get(key)
        if data:
            return SyncConflict(**data)
        return None

    async def set_conflict(
        self,
        conflict: SyncConflict,
        ttl: Optional[int] = None,
    ) -> None:
        """Cache conflict."""
        key = self._get_conflict_key(conflict.character_id, conflict.field_path)
        await self._cache.set(key, conflict.__dict__, ttl or self._ttl)

    async def delete_state(self, character_id: UUID) -> None:
        """Delete cached character state."""
        key = self._get_state_key(character_id)
        await self._cache.delete(key)

    async def delete_metadata(
        self,
        character_id: UUID,
        campaign_id: UUID,
    ) -> None:
        """Delete cached sync metadata."""
        key = self._get_metadata_key(character_id, campaign_id)
        await self._cache.delete(key)

    async def delete_subscription(
        self,
        character_id: UUID,
        campaign_id: UUID,
    ) -> None:
        """Delete cached subscription."""
        key = self._get_subscription_key(character_id, campaign_id)
        await self._cache.delete(key)

    async def delete_conflict(
        self,
        character_id: UUID,
        field_path: str,
    ) -> None:
        """Delete cached conflict."""
        key = self._get_conflict_key(character_id, field_path)
        await self._cache.delete(key)

    async def clear_character_cache(
        self,
        character_id: UUID,
    ) -> None:
        """Clear all cached data for character."""
        # Get all keys for character
        pattern = f"character:{character_id}:*"
        try:
            keys = await self._cache._client.keys(pattern)
            if keys:
                await self._cache.delete_many(set(keys))
        except Exception as e:
            logger.error("Cache clear error: %s", str(e))
            raise CacheError(f"Failed to clear cache: {str(e)}")
