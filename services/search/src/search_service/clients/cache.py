import json
from typing import Any, Dict, List, Optional, Union
from redis.asyncio import Redis
from redis.exceptions import RedisError

from search_service.core.config import settings
from search_service.core.exceptions import CacheError


class CacheManager:
    """Redis cache manager for search results and metadata"""

    def __init__(self) -> None:
        """Initialize Redis client"""
        self.client = Redis.from_url(
            settings.get_redis_url,
            decode_responses=True,
            encoding="utf-8"
        )

    async def close(self) -> None:
        """Close Redis connection"""
        await self.client.close()

    def _get_key(self, key: str) -> str:
        """Get full cache key with prefix"""
        return f"{settings.CACHE_PREFIX}{key}"

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from cache"""
        try:
            data = await self.client.get(self._get_key(key))
            return json.loads(data) if data else None
        except (RedisError, json.JSONDecodeError) as e:
            raise CacheError(str(e), "get", key)

    async def set(
        self,
        key: str,
        value: Union[Dict[str, Any], list],
        expire: Optional[int] = None,
    ) -> None:
        """Set value in cache with optional expiration"""
        try:
            await self.client.set(
                self._get_key(key),
                json.dumps(value),
                ex=expire or settings.CACHE_TTL,
            )
        except (RedisError, TypeError) as e:
            raise CacheError(str(e), "set", key)

    async def delete(self, key: str) -> None:
        """Delete value from cache"""
        try:
            await self.client.delete(self._get_key(key))
        except RedisError as e:
            raise CacheError(str(e), "delete", key)

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(await self.client.exists(self._get_key(key)))
        except RedisError as e:
            raise CacheError(str(e), "exists", key)

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter by amount"""
        try:
            return await self.client.incrby(self._get_key(key), amount)
        except RedisError as e:
            raise CacheError(str(e), "increment", key)

    async def expire(self, key: str, seconds: int) -> None:
        """Set key expiration"""
        try:
            await self.client.expire(self._get_key(key), seconds)
        except RedisError as e:
            raise CacheError(str(e), "expire", key)

    async def pipeline(self) -> "RedisPipeline":
        """Get pipeline for batch operations"""
        try:
            return RedisPipeline(await self.client.pipeline())
        except RedisError as e:
            raise CacheError(str(e), "pipeline", "")

    async def flush(self) -> None:
        """Clear all cache entries with service prefix"""
        try:
            cursor = 0
            while True:
                cursor, keys = await self.client.scan(
                    cursor,
                    match=f"{settings.CACHE_PREFIX}*"
                )
                if keys:
                    await self.client.delete(*keys)
                if cursor == 0:
                    break
        except RedisError as e:
            raise CacheError(str(e), "flush", "all")

    # Search-specific cache methods

    async def cache_search_results(
        self,
        query_hash: str,
        results: Dict[str, Any],
        expire: Optional[int] = None,
    ) -> None:
        """Cache search results"""
        key = f"search:results:{query_hash}"
        await self.set(key, results, expire)

    async def get_search_results(
        self,
        query_hash: str,
    ) -> Optional[Dict[str, Any]]:
        """Get cached search results"""
        key = f"search:results:{query_hash}"
        return await self.get(key)

    async def cache_suggestions(
        self,
        query: str,
        suggestions: List[str],
        expire: Optional[int] = None,
    ) -> None:
        """Cache search suggestions"""
        key = f"search:suggestions:{query}"
        await self.set(key, suggestions, expire)

    async def get_suggestions(
        self,
        query: str,
    ) -> Optional[List[str]]:
        """Get cached suggestions"""
        key = f"search:suggestions:{query}"
        return await self.get(key)

    async def track_popular_queries(
        self,
        query: str,
        index: str,
    ) -> None:
        """Track popular search queries"""
        key = f"stats:popular_queries:{index}"
        await self.client.zincrby(self._get_key(key), 1, query)

    async def get_popular_queries(
        self,
        index: str,
        limit: int = 10,
    ) -> List[tuple[str, float]]:
        """Get popular search queries"""
        key = f"stats:popular_queries:{index}"
        try:
            results = await self.client.zrevrange(
                self._get_key(key),
                0,
                limit - 1,
                withscores=True,
            )
            return [(query, score) for query, score in results]
        except RedisError as e:
            raise CacheError(str(e), "get_popular_queries", key)


class RedisPipeline:
    """Redis pipeline wrapper for batch operations"""

    def __init__(self, pipeline: Redis) -> None:
        self.pipeline = pipeline

    async def execute(self) -> Any:
        """Execute pipeline"""
        try:
            return await self.pipeline.execute()
        except RedisError as e:
            raise CacheError(str(e), "pipeline_execute", "")
