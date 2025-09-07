"""Local in-memory cache implementation."""

import time
from typing import Any, Dict, Optional, Tuple
from cachetools import TTLCache
import structlog

logger = structlog.get_logger()


class LocalCache:
    """Local in-memory cache with TTL support."""

    def __init__(self, maxsize: int = 1000, ttl: int = 60):
        """Initialize local cache.
        
        Args:
            maxsize: Maximum number of items in cache
            ttl: Default time-to-live in seconds
        """
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.default_ttl = ttl
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0,
        }

    def get(self, key: str) -> Optional[Any]:
        """Get value from local cache."""
        try:
            value = self.cache.get(key)
            if value is not None:
                self.stats["hits"] += 1
                logger.debug("Local cache hit", key=key)
            else:
                self.stats["misses"] += 1
                logger.debug("Local cache miss", key=key)
            return value
        except Exception as e:
            logger.warning("Local cache get error", key=key, error=str(e))
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in local cache."""
        try:
            # TTLCache handles TTL automatically based on initialization
            self.cache[key] = value
            self.stats["sets"] += 1
            logger.debug("Local cache set", key=key)
            return True
        except Exception as e:
            logger.warning("Local cache set error", key=key, error=str(e))
            return False

    def delete(self, key: str) -> bool:
        """Delete key from local cache."""
        try:
            if key in self.cache:
                del self.cache[key]
                self.stats["deletes"] += 1
                logger.debug("Local cache delete", key=key)
                return True
            return False
        except Exception as e:
            logger.warning("Local cache delete error", key=key, error=str(e))
            return False

    def clear(self) -> None:
        """Clear all items from local cache."""
        try:
            self.cache.clear()
            logger.info("Local cache cleared")
        except Exception as e:
            logger.error("Local cache clear error", error=str(e))

    def exists(self, key: str) -> bool:
        """Check if key exists in local cache."""
        return key in self.cache

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "maxsize": self.cache.maxsize,
            "ttl": self.default_ttl,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "sets": self.stats["sets"],
            "deletes": self.stats["deletes"],
            "evictions": self.stats["evictions"],
            "hit_rate": hit_rate,
        }

    def is_healthy(self) -> bool:
        """Check if local cache is healthy."""
        try:
            # Test basic operations
            test_key = "_health_check"
            self.set(test_key, "test")
            value = self.get(test_key)
            self.delete(test_key)
            return value == "test"
        except Exception as e:
            logger.error("Local cache health check failed", error=str(e))
            return False

    def __len__(self) -> int:
        """Get number of items in cache."""
        return len(self.cache)

    def __contains__(self, key: str) -> bool:
        """Check if key is in cache."""
        return key in self.cache
