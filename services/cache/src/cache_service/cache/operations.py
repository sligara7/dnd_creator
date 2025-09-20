"""Cache operations implementation."""

import json
import zlib
from typing import Any, Dict, List, Optional
import redis.asyncio as redis

from ..integrations.message_hub import CacheServiceIntegration

class CacheOperations:
    """Cache operations handler."""
    
    def __init__(
        self,
        redis_client: redis.Redis,
        message_hub: CacheServiceIntegration,
        config: Dict[str, Any]
    ):
        """Initialize cache operations.

        Args:
            redis_client: Redis client instance
            message_hub: Message Hub integration
            config: Service configuration
        """
        self.redis = redis_client
        self.message_hub = message_hub
        self.config = config
        
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        value = await self.redis.get(key)
        if value is None:
            return None
            
        try:
            # Try to decompress if needed
            try:
                value = zlib.decompress(value)
            except zlib.error:
                pass
                
            return json.loads(value)
        except Exception:
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set a value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL in seconds

        Returns:
            bool: True if successful
        """
        # Convert value to JSON
        json_value = json.dumps(value)
        
        # Compress if needed
        if len(json_value) > self.config.get("compression_threshold", 1024):
            compressed = zlib.compress(json_value.encode())
            if len(compressed) < len(json_value):
                json_value = compressed
        
        try:
            if ttl:
                await self.redis.setex(key, ttl, json_value)
            else:
                await self.redis.set(key, json_value)
                
            await self.message_hub.notify_cache_operation("set", key, "cache")
            return True
            
        except Exception:
            return False
            
    async def delete(self, key: str) -> bool:
        """Delete a value from cache.

        Args:
            key: Cache key

        Returns:
            bool: True if key existed and was deleted
        """
        deleted = await self.redis.delete(key)
        
        if deleted:
            await self.message_hub.notify_cache_operation(
                "delete",
                key,
                "cache"
            )
            
        return bool(deleted)
        
    async def exists(self, key: str) -> bool:
        """Check if a key exists.

        Args:
            key: Cache key

        Returns:
            bool: True if key exists
        """
        return bool(await self.redis.exists(key))
        
    async def get_pattern(self, pattern: str) -> Dict[str, Any]:
        """Get all keys matching pattern.

        Args:
            pattern: Redis key pattern

        Returns:
            Dict of key-value pairs
        """
        keys = await self.redis.keys(pattern)
        
        if not keys:
            return {}
            
        # Get all values
        values = await self.redis.mget(keys)
        
        result = {}
        for key, value in zip(keys, values):
            if value is None:
                continue
                
            try:
                # Try to decompress
                try:
                    value = zlib.decompress(value)
                except zlib.error:
                    pass
                    
                result[key] = json.loads(value)
            except Exception:
                continue
                
        return result
        
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern.

        Args:
            pattern: Redis key pattern

        Returns:
            int: Number of keys deleted
        """
        keys = await self.redis.keys(pattern)
        
        if not keys:
            return 0
            
        deleted = await self.redis.delete(*keys)
        
        if deleted:
            await self.message_hub.notify_cache_operation(
                "delete_pattern",
                pattern,
                "cache"
            )
            
        return deleted
        
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter.

        Args:
            key: Counter key
            amount: Amount to increment by

        Returns:
            int: New counter value
        """
        return await self.redis.incr(key, amount)
        
    async def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement a counter.

        Args:
            key: Counter key
            amount: Amount to decrement by

        Returns:
            int: New counter value
        """
        return await self.redis.decr(key, amount)