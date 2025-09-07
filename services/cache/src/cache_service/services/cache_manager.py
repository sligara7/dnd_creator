"""Cache manager implementation for cache service."""

import asyncio
import time
from typing import Any, Dict, List, Optional, Set
import structlog

from .redis_client import RedisClient
from .local_cache import LocalCache
from .circuit_breaker import CircuitBreaker
from ..core.config import settings
from ..core.exceptions import (
    CacheOperationError,
    CacheKeyError,
    InvalidKeyspaceError,
)
from ..core.monitoring import (
    record_cache_operation,
    update_cache_stats,
)

logger = structlog.get_logger()


class CacheManager:
    """Main cache manager coordinating all cache operations."""

    # Allowed keyspaces for different services
    ALLOWED_KEYSPACES = {
        "character": ["characters", "sheets", "inventory", "journal"],
        "campaign": ["campaigns", "plots", "themes", "npcs"],
        "image": ["portraits", "maps", "items", "overlays"],
        "llm": ["prompts", "completions", "embeddings"],
        "auth": ["sessions", "tokens", "permissions"],
        "catalog": ["items", "spells", "equipment", "rules"],
    }

    def __init__(
        self,
        local_cache: Optional[LocalCache] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
    ):
        """Initialize cache manager.
        
        Args:
            local_cache: Optional local cache instance
            circuit_breaker: Optional circuit breaker instance
        """
        self.redis_client = RedisClient()
        self.local_cache = local_cache
        self.circuit_breaker = circuit_breaker
        self.stats = {
            "operations": 0,
            "hits": 0,
            "misses": 0,
            "errors": 0,
        }

    async def setup(self) -> None:
        """Setup cache manager."""
        try:
            # Connect to Redis
            await self.redis_client.connect()
            
            # Initialize monitoring
            asyncio.create_task(self._update_metrics_loop())
            
            logger.info("Cache manager initialized")
        except Exception as e:
            logger.error("Failed to setup cache manager", error=str(e))
            raise

    async def cleanup(self) -> None:
        """Cleanup cache manager resources."""
        try:
            await self.redis_client.disconnect()
            logger.info("Cache manager cleanup complete")
        except Exception as e:
            logger.error("Error during cache manager cleanup", error=str(e))

    def _validate_key(self, key: str, service: Optional[str] = None) -> None:
        """Validate cache key format and permissions.
        
        Args:
            key: Cache key to validate
            service: Service making the request
            
        Raises:
            CacheKeyError: If key is invalid
            InvalidKeyspaceError: If service doesn't have access to keyspace
        """
        if not key:
            raise CacheKeyError("Key cannot be empty", key="")
        
        # Check key format (service:keyspace:identifier)
        parts = key.split(":")
        if len(parts) < 2:
            raise CacheKeyError(
                f"Invalid key format: {key}. Expected format: service:keyspace:identifier",
                key=key
            )
        
        # Check service permissions if provided
        if service:
            key_service = parts[0]
            keyspace = parts[1] if len(parts) > 1 else ""
            
            if key_service != service:
                # Check if service has cross-service access (future feature)
                pass
            
            if keyspace and keyspace not in self.ALLOWED_KEYSPACES.get(service, []):
                raise InvalidKeyspaceError(
                    service=service,
                    keyspace=keyspace,
                    allowed_keyspaces=self.ALLOWED_KEYSPACES.get(service, [])
                )

    async def get(
        self,
        key: str,
        service: Optional[str] = None,
        use_local: bool = True,
    ) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key
            service: Service making the request
            use_local: Whether to check local cache first
            
        Returns:
            Cached value or None if not found
        """
        start_time = time.time()
        
        try:
            # Validate key
            self._validate_key(key, service)
            
            # Check local cache first if enabled
            if use_local and self.local_cache:
                value = self.local_cache.get(key)
                if value is not None:
                    self.stats["hits"] += 1
                    record_cache_operation(
                        "get", "hit", service or "unknown",
                        time.time() - start_time
                    )
                    return value
            
            # Get from Redis
            if self.circuit_breaker:
                value = await self.circuit_breaker.call(
                    self.redis_client.get,
                    operation="get",
                    node="primary",
                    key
                )
            else:
                value = await self.redis_client.get(key)
            
            if value is not None:
                # Update local cache if enabled
                if use_local and self.local_cache:
                    self.local_cache.set(key, value)
                
                self.stats["hits"] += 1
                record_cache_operation(
                    "get", "hit", service or "unknown",
                    time.time() - start_time
                )
            else:
                self.stats["misses"] += 1
                record_cache_operation(
                    "get", "miss", service or "unknown",
                    time.time() - start_time
                )
            
            return value
            
        except Exception as e:
            self.stats["errors"] += 1
            record_cache_operation(
                "get", "error", service or "unknown",
                time.time() - start_time
            )
            logger.error("Cache get error", key=key, error=str(e))
            raise

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        service: Optional[str] = None,
        update_local: bool = True,
    ) -> bool:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            service: Service making the request
            update_local: Whether to update local cache
            
        Returns:
            True if successful
        """
        start_time = time.time()
        
        try:
            # Validate key
            self._validate_key(key, service)
            
            # Apply default TTL if not specified
            if ttl is None:
                ttl = settings.CACHE_DEFAULT_TTL
            
            # Set in Redis
            if self.circuit_breaker:
                result = await self.circuit_breaker.call(
                    self.redis_client.set,
                    operation="set",
                    node="primary",
                    key, value, ttl
                )
            else:
                result = await self.redis_client.set(key, value, ttl)
            
            # Update local cache if enabled
            if result and update_local and self.local_cache:
                self.local_cache.set(key, value, ttl)
            
            record_cache_operation(
                "set", "success" if result else "failed",
                service or "unknown",
                time.time() - start_time
            )
            
            return result
            
        except Exception as e:
            self.stats["errors"] += 1
            record_cache_operation(
                "set", "error", service or "unknown",
                time.time() - start_time
            )
            logger.error("Cache set error", key=key, error=str(e))
            raise

    async def delete(
        self,
        key: str,
        service: Optional[str] = None,
        delete_local: bool = True,
    ) -> bool:
        """Delete key from cache.
        
        Args:
            key: Cache key
            service: Service making the request
            delete_local: Whether to delete from local cache
            
        Returns:
            True if key was deleted
        """
        start_time = time.time()
        
        try:
            # Validate key
            self._validate_key(key, service)
            
            # Delete from Redis
            if self.circuit_breaker:
                result = await self.circuit_breaker.call(
                    self.redis_client.delete,
                    operation="delete",
                    node="primary",
                    key
                )
            else:
                result = await self.redis_client.delete(key)
            
            # Delete from local cache if enabled
            if delete_local and self.local_cache:
                self.local_cache.delete(key)
            
            record_cache_operation(
                "delete", "success" if result else "not_found",
                service or "unknown",
                time.time() - start_time
            )
            
            return result
            
        except Exception as e:
            self.stats["errors"] += 1
            record_cache_operation(
                "delete", "error", service or "unknown",
                time.time() - start_time
            )
            logger.error("Cache delete error", key=key, error=str(e))
            raise

    async def get_many(
        self,
        keys: List[str],
        service: Optional[str] = None,
        use_local: bool = True,
    ) -> Dict[str, Any]:
        """Get multiple values from cache.
        
        Args:
            keys: List of cache keys
            service: Service making the request
            use_local: Whether to check local cache first
            
        Returns:
            Dictionary of key-value pairs
        """
        start_time = time.time()
        
        try:
            # Validate keys
            for key in keys:
                self._validate_key(key, service)
            
            result = {}
            redis_keys = []
            
            # Check local cache first if enabled
            if use_local and self.local_cache:
                for key in keys:
                    value = self.local_cache.get(key)
                    if value is not None:
                        result[key] = value
                    else:
                        redis_keys.append(key)
            else:
                redis_keys = keys
            
            # Get remaining keys from Redis
            if redis_keys:
                if self.circuit_breaker:
                    redis_result = await self.circuit_breaker.call(
                        self.redis_client.get_many,
                        operation="get_many",
                        node="primary",
                        redis_keys
                    )
                else:
                    redis_result = await self.redis_client.get_many(redis_keys)
                
                # Update result and local cache
                for key, value in redis_result.items():
                    if value is not None:
                        result[key] = value
                        if use_local and self.local_cache:
                            self.local_cache.set(key, value)
            
            record_cache_operation(
                "get_many", "success", service or "unknown",
                time.time() - start_time
            )
            
            return result
            
        except Exception as e:
            self.stats["errors"] += 1
            record_cache_operation(
                "get_many", "error", service or "unknown",
                time.time() - start_time
            )
            logger.error("Cache get_many error", error=str(e))
            raise

    async def set_many(
        self,
        items: Dict[str, Any],
        ttl: Optional[int] = None,
        service: Optional[str] = None,
        update_local: bool = True,
    ) -> int:
        """Set multiple values in cache.
        
        Args:
            items: Dictionary of key-value pairs
            ttl: Time-to-live in seconds
            service: Service making the request
            update_local: Whether to update local cache
            
        Returns:
            Number of items successfully set
        """
        start_time = time.time()
        
        try:
            # Validate keys
            for key in items.keys():
                self._validate_key(key, service)
            
            # Apply default TTL if not specified
            if ttl is None:
                ttl = settings.CACHE_DEFAULT_TTL
            
            # Set in Redis
            if self.circuit_breaker:
                count = await self.circuit_breaker.call(
                    self.redis_client.set_many,
                    operation="set_many",
                    node="primary",
                    items, ttl
                )
            else:
                count = await self.redis_client.set_many(items, ttl)
            
            # Update local cache if enabled
            if update_local and self.local_cache:
                for key, value in items.items():
                    self.local_cache.set(key, value, ttl)
            
            record_cache_operation(
                "set_many", "success", service or "unknown",
                time.time() - start_time
            )
            
            return count
            
        except Exception as e:
            self.stats["errors"] += 1
            record_cache_operation(
                "set_many", "error", service or "unknown",
                time.time() - start_time
            )
            logger.error("Cache set_many error", error=str(e))
            raise

    async def delete_many(
        self,
        keys: List[str],
        service: Optional[str] = None,
        delete_local: bool = True,
    ) -> int:
        """Delete multiple keys from cache.
        
        Args:
            keys: List of cache keys
            service: Service making the request
            delete_local: Whether to delete from local cache
            
        Returns:
            Number of keys deleted
        """
        start_time = time.time()
        
        try:
            # Validate keys
            for key in keys:
                self._validate_key(key, service)
            
            # Delete from Redis
            if self.circuit_breaker:
                count = await self.circuit_breaker.call(
                    self.redis_client.delete_many,
                    operation="delete_many",
                    node="primary",
                    keys
                )
            else:
                count = await self.redis_client.delete_many(keys)
            
            # Delete from local cache if enabled
            if delete_local and self.local_cache:
                for key in keys:
                    self.local_cache.delete(key)
            
            record_cache_operation(
                "delete_many", "success", service or "unknown",
                time.time() - start_time
            )
            
            return count
            
        except Exception as e:
            self.stats["errors"] += 1
            record_cache_operation(
                "delete_many", "error", service or "unknown",
                time.time() - start_time
            )
            logger.error("Cache delete_many error", error=str(e))
            raise

    async def scan_keys(
        self,
        pattern: str = "*",
        count: int = 100,
        service: Optional[str] = None,
    ) -> List[str]:
        """Scan for keys matching pattern.
        
        Args:
            pattern: Key pattern to match
            count: Maximum number of keys to return
            service: Service making the request
            
        Returns:
            List of matching keys
        """
        try:
            # Add service prefix to pattern if provided
            if service:
                pattern = f"{service}:{pattern}"
            
            return await self.redis_client.scan_keys(pattern, count)
            
        except Exception as e:
            logger.error("Cache scan_keys error", pattern=pattern, error=str(e))
            return []

    async def flush(
        self,
        service: Optional[str] = None,
        pattern: Optional[str] = None,
    ) -> bool:
        """Flush cache entries.
        
        Args:
            service: Flush only keys for specific service
            pattern: Flush only keys matching pattern
            
        Returns:
            True if successful
        """
        try:
            if service or pattern:
                # Selective flush
                if service:
                    pattern = f"{service}:*"
                
                keys = await self.scan_keys(pattern or "*", count=10000)
                if keys:
                    await self.delete_many(keys)
                
                logger.info("Cache flushed", service=service, pattern=pattern, count=len(keys))
            else:
                # Full flush
                result = await self.redis_client.flush_db()
                if self.local_cache:
                    self.local_cache.clear()
                
                logger.info("Cache fully flushed")
                return result
            
            return True
            
        except Exception as e:
            logger.error("Cache flush error", error=str(e))
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            # Get Redis info
            redis_info = await self.redis_client.get_info()
            
            # Calculate hit rate
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            miss_rate = (self.stats["misses"] / total_requests * 100) if total_requests > 0 else 0
            
            # Get local cache stats if available
            local_stats = self.local_cache.get_stats() if self.local_cache else {}
            
            return {
                "hit_rate": hit_rate,
                "miss_rate": miss_rate,
                "total_operations": self.stats["operations"],
                "total_hits": self.stats["hits"],
                "total_misses": self.stats["misses"],
                "total_errors": self.stats["errors"],
                "memory_used": redis_info.get("memory", {}).get("used", 0),
                "memory_limit": self._parse_memory_limit(),
                "total_keys": redis_info.get("stats", {}).get("keyspace_hits", 0),
                "replication_lag": self._calculate_replication_lag(redis_info),
                "local_cache": local_stats,
                "redis": redis_info,
            }
        except Exception as e:
            logger.error("Failed to get cache stats", error=str(e))
            return {
                "error": str(e),
                "hit_rate": 0,
                "miss_rate": 0,
            }

    async def check_primary_health(self) -> bool:
        """Check primary cache health."""
        try:
            return await self.redis_client.health_check()
        except Exception:
            return False

    async def check_replica_health(self) -> bool:
        """Check replica cache health."""
        try:
            # For now, just check primary as replica check would be similar
            return await self.redis_client.health_check()
        except Exception:
            return False

    def _parse_memory_limit(self) -> int:
        """Parse memory limit from configuration."""
        limit_str = settings.CACHE_MEMORY_LIMIT
        if limit_str.endswith("GB"):
            return int(limit_str[:-2]) * 1024 * 1024 * 1024
        elif limit_str.endswith("MB"):
            return int(limit_str[:-2]) * 1024 * 1024
        elif limit_str.endswith("KB"):
            return int(limit_str[:-2]) * 1024
        else:
            return int(limit_str)

    def _calculate_replication_lag(self, redis_info: Dict[str, Any]) -> float:
        """Calculate replication lag from Redis info."""
        # This is a simplified calculation
        # In production, you'd want more sophisticated monitoring
        replication = redis_info.get("replication", {})
        if replication.get("role") == "master" and replication.get("connected_slaves", 0) > 0:
            # Would need to parse slave info for actual lag
            return 0.0
        return 0.0

    async def _update_metrics_loop(self) -> None:
        """Background task to update metrics."""
        while True:
            try:
                await asyncio.sleep(30)  # Update every 30 seconds
                
                stats = await self.get_stats()
                update_cache_stats(stats)
                
            except Exception as e:
                logger.error("Failed to update metrics", error=str(e))
                await asyncio.sleep(60)  # Wait longer on error
