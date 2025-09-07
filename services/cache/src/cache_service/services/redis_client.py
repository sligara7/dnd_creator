"""Redis client implementation for cache service."""

import asyncio
import json
import pickle
import zlib
from typing import Any, Dict, List, Optional, Tuple, Set
from contextlib import asynccontextmanager

import redis.asyncio as redis
from redis.asyncio.cluster import RedisCluster
from redis.asyncio.sentinel import Sentinel
from redis.exceptions import RedisError, ConnectionError, TimeoutError
import structlog

from ..core.config import settings
from ..core.exceptions import (
    CacheConnectionError,
    CacheOperationError,
    CacheKeyError,
)
from ..core.monitoring import metrics_collector

logger = structlog.get_logger()


class RedisClient:
    """Redis client with cluster and sentinel support."""

    def __init__(self):
        self.primary_client: Optional[redis.Redis] = None
        self.replica_client: Optional[redis.Redis] = None
        self.cluster_client: Optional[RedisCluster] = None
        self.sentinel: Optional[Sentinel] = None
        self.is_connected = False
        self.use_cluster = settings.REDIS_CLUSTER_ENABLED
        self.use_sentinel = settings.REDIS_SENTINEL_ENABLED
        self.compression_enabled = settings.COMPRESSION_ENABLED
        self.compression_threshold = settings.COMPRESSION_THRESHOLD

    async def connect(self) -> None:
        """Connect to Redis based on configuration."""
        try:
            if self.use_cluster:
                await self._connect_cluster()
            elif self.use_sentinel:
                await self._connect_sentinel()
            else:
                await self._connect_standalone()
            
            self.is_connected = True
            logger.info("Redis connection established", 
                       mode=self._get_connection_mode())
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            raise CacheConnectionError(
                node="redis",
                error=str(e)
            )

    async def _connect_cluster(self) -> None:
        """Connect to Redis cluster."""
        try:
            startup_nodes = [
                {"host": host, "port": int(port)}
                for host, port in [node.split(":") for node in settings.REDIS_CLUSTER_NODES]
            ]
            
            self.cluster_client = RedisCluster(
                startup_nodes=startup_nodes,
                decode_responses=False,
                password=settings.REDIS_PASSWORD.get_secret_value() if settings.REDIS_PASSWORD else None,
                skip_full_coverage_check=True,
                max_connections=settings.REDIS_POOL_MAX_SIZE,
                socket_connect_timeout=settings.REDIS_CONNECTION_TIMEOUT,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
            )
            
            # Test connection
            await self.cluster_client.ping()
            logger.info("Connected to Redis cluster")
        except Exception as e:
            logger.error("Failed to connect to Redis cluster", error=str(e))
            raise

    async def _connect_sentinel(self) -> None:
        """Connect to Redis via Sentinel."""
        try:
            sentinels = [
                (host, int(port))
                for host, port in [node.split(":") for node in settings.REDIS_SENTINEL_HOSTS]
            ]
            
            self.sentinel = Sentinel(
                sentinels,
                password=settings.REDIS_PASSWORD.get_secret_value() if settings.REDIS_PASSWORD else None,
                socket_connect_timeout=settings.REDIS_CONNECTION_TIMEOUT,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
            )
            
            # Get master and replica clients
            self.primary_client = self.sentinel.master_for(
                settings.REDIS_SENTINEL_MASTER,
                socket_connect_timeout=settings.REDIS_CONNECTION_TIMEOUT,
                decode_responses=False,
                max_connections=settings.REDIS_POOL_MAX_SIZE,
            )
            
            self.replica_client = self.sentinel.slave_for(
                settings.REDIS_SENTINEL_MASTER,
                socket_connect_timeout=settings.REDIS_CONNECTION_TIMEOUT,
                decode_responses=False,
                max_connections=settings.REDIS_POOL_MAX_SIZE,
            )
            
            # Test connections
            await self.primary_client.ping()
            await self.replica_client.ping()
            logger.info("Connected to Redis via Sentinel")
        except Exception as e:
            logger.error("Failed to connect to Redis via Sentinel", error=str(e))
            raise

    async def _connect_standalone(self) -> None:
        """Connect to standalone Redis instances."""
        try:
            # Create primary connection
            self.primary_client = redis.Redis(
                host=settings.REDIS_PRIMARY_HOST,
                port=settings.REDIS_PRIMARY_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD.get_secret_value() if settings.REDIS_PASSWORD else None,
                decode_responses=False,
                max_connections=settings.REDIS_POOL_MAX_SIZE,
                socket_connect_timeout=settings.REDIS_CONNECTION_TIMEOUT,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                socket_keepalive=settings.REDIS_SOCKET_KEEPALIVE,
            )
            
            # Create replica connection if configured
            if settings.REDIS_REPLICA_HOST:
                self.replica_client = redis.Redis(
                    host=settings.REDIS_REPLICA_HOST,
                    port=settings.REDIS_REPLICA_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD.get_secret_value() if settings.REDIS_PASSWORD else None,
                    decode_responses=False,
                    max_connections=settings.REDIS_POOL_MAX_SIZE,
                    socket_connect_timeout=settings.REDIS_CONNECTION_TIMEOUT,
                    socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                    socket_keepalive=settings.REDIS_SOCKET_KEEPALIVE,
                )
            
            # Test connections
            await self.primary_client.ping()
            if self.replica_client:
                await self.replica_client.ping()
            
            logger.info("Connected to standalone Redis")
        except Exception as e:
            logger.error("Failed to connect to standalone Redis", error=str(e))
            raise

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        try:
            if self.cluster_client:
                await self.cluster_client.close()
            if self.primary_client:
                await self.primary_client.close()
            if self.replica_client:
                await self.replica_client.close()
            
            self.is_connected = False
            logger.info("Disconnected from Redis")
        except Exception as e:
            logger.error("Error disconnecting from Redis", error=str(e))

    def _get_client(self, read_only: bool = False) -> redis.Redis:
        """Get appropriate Redis client."""
        if self.cluster_client:
            return self.cluster_client
        
        if read_only and self.replica_client:
            return self.replica_client
        
        return self.primary_client

    def _get_connection_mode(self) -> str:
        """Get current connection mode."""
        if self.use_cluster:
            return "cluster"
        elif self.use_sentinel:
            return "sentinel"
        else:
            return "standalone"

    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage."""
        # Try JSON first for simple types
        try:
            json_str = json.dumps(value)
            data = json_str.encode('utf-8')
            
            # Compress if enabled and data is large enough
            if self.compression_enabled and len(data) > self.compression_threshold:
                compressed = zlib.compress(data, level=6)
                # Only use compressed if it's actually smaller
                if len(compressed) < len(data):
                    return b'Z' + compressed  # Prefix with 'Z' to indicate compression
            
            return b'J' + data  # Prefix with 'J' to indicate JSON
        except (TypeError, ValueError):
            # Fall back to pickle for complex types
            pickled = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
            
            if self.compression_enabled and len(pickled) > self.compression_threshold:
                compressed = zlib.compress(pickled, level=6)
                if len(compressed) < len(pickled):
                    return b'z' + compressed  # Lowercase 'z' for compressed pickle
            
            return b'P' + pickled  # 'P' for pickle

    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value from storage."""
        if not data:
            return None
        
        prefix = data[0:1]
        content = data[1:]
        
        try:
            if prefix == b'Z':  # Compressed JSON
                decompressed = zlib.decompress(content)
                return json.loads(decompressed.decode('utf-8'))
            elif prefix == b'J':  # Plain JSON
                return json.loads(content.decode('utf-8'))
            elif prefix == b'z':  # Compressed pickle
                decompressed = zlib.decompress(content)
                return pickle.loads(decompressed)
            elif prefix == b'P':  # Plain pickle
                return pickle.loads(content)
            else:
                # Try to decode as string for backward compatibility
                return data.decode('utf-8')
        except Exception as e:
            logger.warning("Failed to deserialize value", error=str(e))
            return data

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.is_connected:
            raise CacheConnectionError(node="redis", error="Not connected")
        
        try:
            client = self._get_client(read_only=True)
            data = await client.get(key)
            
            if data is None:
                return None
            
            return self._deserialize_value(data)
        except TimeoutError:
            raise CacheOperationError(
                operation="get",
                key=key,
                error="Operation timeout"
            )
        except RedisError as e:
            logger.error("Redis get error", key=key, error=str(e))
            raise CacheOperationError(
                operation="get",
                key=key,
                error=str(e)
            )

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache."""
        if not self.is_connected:
            raise CacheConnectionError(node="redis", error="Not connected")
        
        try:
            client = self._get_client(read_only=False)
            serialized = self._serialize_value(value)
            
            if ttl:
                result = await client.setex(key, ttl, serialized)
            else:
                result = await client.set(key, serialized)
            
            return bool(result)
        except TimeoutError:
            raise CacheOperationError(
                operation="set",
                key=key,
                error="Operation timeout"
            )
        except RedisError as e:
            logger.error("Redis set error", key=key, error=str(e))
            raise CacheOperationError(
                operation="set",
                key=key,
                error=str(e)
            )

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.is_connected:
            raise CacheConnectionError(node="redis", error="Not connected")
        
        try:
            client = self._get_client(read_only=False)
            result = await client.delete(key)
            return bool(result)
        except TimeoutError:
            raise CacheOperationError(
                operation="delete",
                key=key,
                error="Operation timeout"
            )
        except RedisError as e:
            logger.error("Redis delete error", key=key, error=str(e))
            raise CacheOperationError(
                operation="delete",
                key=key,
                error=str(e)
            )

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self.is_connected:
            raise CacheConnectionError(node="redis", error="Not connected")
        
        try:
            client = self._get_client(read_only=True)
            result = await client.exists(key)
            return bool(result)
        except RedisError as e:
            logger.error("Redis exists error", key=key, error=str(e))
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key."""
        if not self.is_connected:
            raise CacheConnectionError(node="redis", error="Not connected")
        
        try:
            client = self._get_client(read_only=False)
            result = await client.expire(key, ttl)
            return bool(result)
        except RedisError as e:
            logger.error("Redis expire error", key=key, error=str(e))
            return False

    async def ttl(self, key: str) -> int:
        """Get TTL for a key."""
        if not self.is_connected:
            raise CacheConnectionError(node="redis", error="Not connected")
        
        try:
            client = self._get_client(read_only=True)
            result = await client.ttl(key)
            return result
        except RedisError as e:
            logger.error("Redis ttl error", key=key, error=str(e))
            return -1

    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache."""
        if not self.is_connected:
            raise CacheConnectionError(node="redis", error="Not connected")
        
        if not keys:
            return {}
        
        try:
            client = self._get_client(read_only=True)
            
            # Use pipeline for efficiency
            pipe = client.pipeline()
            for key in keys:
                pipe.get(key)
            
            results = await pipe.execute()
            
            # Deserialize and build result dict
            return {
                key: self._deserialize_value(data) if data else None
                for key, data in zip(keys, results)
            }
        except RedisError as e:
            logger.error("Redis get_many error", error=str(e))
            raise CacheOperationError(
                operation="get_many",
                key=",".join(keys[:5]) + "...",
                error=str(e)
            )

    async def set_many(
        self,
        items: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> int:
        """Set multiple values in cache."""
        if not self.is_connected:
            raise CacheConnectionError(node="redis", error="Not connected")
        
        if not items:
            return 0
        
        try:
            client = self._get_client(read_only=False)
            
            # Use pipeline for efficiency
            pipe = client.pipeline()
            for key, value in items.items():
                serialized = self._serialize_value(value)
                if ttl:
                    pipe.setex(key, ttl, serialized)
                else:
                    pipe.set(key, serialized)
            
            results = await pipe.execute()
            
            # Count successful operations
            return sum(1 for r in results if r)
        except RedisError as e:
            logger.error("Redis set_many error", error=str(e))
            raise CacheOperationError(
                operation="set_many",
                key=",".join(list(items.keys())[:5]) + "...",
                error=str(e)
            )

    async def delete_many(self, keys: List[str]) -> int:
        """Delete multiple keys from cache."""
        if not self.is_connected:
            raise CacheConnectionError(node="redis", error="Not connected")
        
        if not keys:
            return 0
        
        try:
            client = self._get_client(read_only=False)
            result = await client.delete(*keys)
            return result
        except RedisError as e:
            logger.error("Redis delete_many error", error=str(e))
            raise CacheOperationError(
                operation="delete_many",
                key=",".join(keys[:5]) + "...",
                error=str(e)
            )

    async def scan_keys(
        self,
        pattern: str = "*",
        count: int = 100
    ) -> List[str]:
        """Scan for keys matching pattern."""
        if not self.is_connected:
            raise CacheConnectionError(node="redis", error="Not connected")
        
        try:
            client = self._get_client(read_only=True)
            keys = []
            
            async for key in client.scan_iter(pattern, count=count):
                keys.append(key.decode('utf-8') if isinstance(key, bytes) else key)
                if len(keys) >= count:
                    break
            
            return keys
        except RedisError as e:
            logger.error("Redis scan_keys error", pattern=pattern, error=str(e))
            return []

    async def flush_db(self) -> bool:
        """Flush the entire database."""
        if not self.is_connected:
            raise CacheConnectionError(node="redis", error="Not connected")
        
        try:
            client = self._get_client(read_only=False)
            result = await client.flushdb()
            return bool(result)
        except RedisError as e:
            logger.error("Redis flush_db error", error=str(e))
            raise CacheOperationError(
                operation="flush_db",
                key="*",
                error=str(e)
            )

    async def get_info(self) -> Dict[str, Any]:
        """Get Redis server information."""
        if not self.is_connected:
            raise CacheConnectionError(node="redis", error="Not connected")
        
        try:
            client = self._get_client(read_only=True)
            info = await client.info()
            
            # Extract relevant metrics
            return {
                "mode": self._get_connection_mode(),
                "connected": self.is_connected,
                "memory": {
                    "used": info.get("used_memory", 0),
                    "peak": info.get("used_memory_peak", 0),
                    "rss": info.get("used_memory_rss", 0),
                },
                "stats": {
                    "total_connections": info.get("total_connections_received", 0),
                    "total_commands": info.get("total_commands_processed", 0),
                    "instantaneous_ops": info.get("instantaneous_ops_per_sec", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0),
                },
                "persistence": {
                    "rdb_last_save": info.get("rdb_last_save_time", 0),
                    "aof_enabled": info.get("aof_enabled", 0),
                },
                "replication": {
                    "role": info.get("role", "unknown"),
                    "connected_slaves": info.get("connected_slaves", 0),
                    "repl_backlog_active": info.get("repl_backlog_active", 0),
                }
            }
        except RedisError as e:
            logger.error("Redis get_info error", error=str(e))
            return {"error": str(e)}

    async def health_check(self) -> bool:
        """Check Redis health."""
        try:
            client = self._get_client(read_only=True)
            result = await client.ping()
            return result
        except Exception as e:
            logger.error("Redis health check failed", error=str(e))
            return False
