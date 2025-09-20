"""Game Session Service - Redis Client.

This module implements the Redis client wrapper for session state management.
"""
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

import redis.asyncio as redis
from prometheus_client import Counter, Histogram
from structlog import get_logger

from game_session.core.config import Settings

logger = get_logger(__name__)

# Metrics
REDIS_OPS = Counter(
    "game_session_redis_operations_total",
    "Total count of Redis operations",
    ["operation", "success"],
)

REDIS_LATENCY = Histogram(
    "game_session_redis_operation_latency_seconds",
    "Redis operation latency in seconds",
    ["operation"],
)


class RedisClient:
    """Redis client wrapper for session state management."""

    def __init__(self, settings: Settings):
        """Initialize Redis client.

        Args:
            settings: Service configuration settings.
        """
        self.settings = settings
        self.client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.client = redis.Redis(
                host=self.settings.REDIS_HOST,
                port=self.settings.REDIS_PORT,
                db=self.settings.REDIS_DB,
                password=self.settings.REDIS_PASSWORD,
                ssl=self.settings.REDIS_SSL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=self.settings.REDIS_POOL_SIZE,
                socket_timeout=self.settings.REDIS_POOL_TIMEOUT,
            )
            await self.client.ping()
            logger.info("Redis connection established")
        except redis.ConnectionError as e:
            logger.error("Failed to connect to Redis", error=str(e))
            raise

    async def close(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")

    @asynccontextmanager
    async def connection(self) -> redis.Redis:
        """Get Redis connection with automatic error handling.

        Yields:
            Redis client instance.
        """
        if not self.client:
            await self.connect()

        try:
            yield self.client
        except redis.ConnectionError as e:
            logger.error("Redis connection error", error=str(e))
            await self.close()
            await self.connect()
            yield self.client
        except Exception as e:
            logger.error("Redis operation error", error=str(e))
            raise

    # Session Metadata

    async def get_session_meta(self, session_id: UUID) -> Dict[str, str]:
        """Get session metadata.

        Args:
            session_id: Session ID.

        Returns:
            Session metadata.
        """
        key = f"session:{session_id}:meta"
        async with self.connection() as redis_client:
            with REDIS_LATENCY.labels("get_session_meta").time():
                result = await redis_client.hgetall(key)
                REDIS_OPS.labels("get_session_meta", "success").inc()
                return result

    async def set_session_meta(
        self,
        session_id: UUID,
        metadata: Dict[str, str],
        ttl: int = 86400,  # 24 hours
    ) -> None:
        """Set session metadata.

        Args:
            session_id: Session ID.
            metadata: Session metadata.
            ttl: Time-to-live in seconds.
        """
        key = f"session:{session_id}:meta"
        async with self.connection() as redis_client:
            with REDIS_LATENCY.labels("set_session_meta").time():
                await redis_client.hset(key, mapping=metadata)
                await redis_client.expire(key, ttl)
                REDIS_OPS.labels("set_session_meta", "success").inc()

    # Connected Players

    async def add_player(
        self,
        session_id: UUID,
        player_id: UUID,
        ttl: int = 3600,  # 1 hour
    ) -> None:
        """Add player to session.

        Args:
            session_id: Session ID.
            player_id: Player ID.
            ttl: Time-to-live in seconds.
        """
        key = f"session:{session_id}:players"
        async with self.connection() as redis_client:
            with REDIS_LATENCY.labels("add_player").time():
                await redis_client.sadd(key, str(player_id))
                await redis_client.expire(key, ttl)
                REDIS_OPS.labels("add_player", "success").inc()

    async def remove_player(self, session_id: UUID, player_id: UUID) -> None:
        """Remove player from session.

        Args:
            session_id: Session ID.
            player_id: Player ID.
        """
        key = f"session:{session_id}:players"
        async with self.connection() as redis_client:
            with REDIS_LATENCY.labels("remove_player").time():
                await redis_client.srem(key, str(player_id))
                REDIS_OPS.labels("remove_player", "success").inc()

    async def get_players(self, session_id: UUID) -> Set[str]:
        """Get all players in session.

        Args:
            session_id: Session ID.

        Returns:
            Set of player IDs.
        """
        key = f"session:{session_id}:players"
        async with self.connection() as redis_client:
            with REDIS_LATENCY.labels("get_players").time():
                result = await redis_client.smembers(key)
                REDIS_OPS.labels("get_players", "success").inc()
                return result

    # WebSocket Connections

    async def set_player_connection(
        self,
        session_id: UUID,
        player_id: UUID,
        connection_id: str,
        ttl: int = 300,  # 5 minutes
    ) -> None:
        """Set player connection ID.

        Args:
            session_id: Session ID.
            player_id: Player ID.
            connection_id: WebSocket connection ID.
            ttl: Time-to-live in seconds.
        """
        key = f"session:{session_id}:connections"
        async with self.connection() as redis_client:
            with REDIS_LATENCY.labels("set_connection").time():
                await redis_client.hset(key, str(player_id), connection_id)
                await redis_client.expire(key, ttl)
                REDIS_OPS.labels("set_connection", "success").inc()

    async def get_player_connection(
        self,
        session_id: UUID,
        player_id: UUID,
    ) -> Optional[str]:
        """Get player connection ID.

        Args:
            session_id: Session ID.
            player_id: Player ID.

        Returns:
            WebSocket connection ID if found.
        """
        key = f"session:{session_id}:connections"
        async with self.connection() as redis_client:
            with REDIS_LATENCY.labels("get_connection").time():
                result = await redis_client.hget(key, str(player_id))
                REDIS_OPS.labels("get_connection", "success").inc()
                return result

    async def remove_player_connection(
        self,
        session_id: UUID,
        player_id: UUID,
    ) -> None:
        """Remove player connection ID.

        Args:
            session_id: Session ID.
            player_id: Player ID.
        """
        key = f"session:{session_id}:connections"
        async with self.connection() as redis_client:
            with REDIS_LATENCY.labels("remove_connection").time():
                await redis_client.hdel(key, str(player_id))
                REDIS_OPS.labels("remove_connection", "success").inc()

    # Combat State

    async def set_combat_state(
        self,
        session_id: UUID,
        state: Dict[str, Any],
        ttl: int = 3600,  # 1 hour
    ) -> None:
        """Set combat state.

        Args:
            session_id: Session ID.
            state: Combat state.
            ttl: Time-to-live in seconds.
        """
        key = f"session:{session_id}:combat"
        async with self.connection() as redis_client:
            with REDIS_LATENCY.labels("set_combat_state").time():
                await redis_client.hset(key, mapping=state)
                await redis_client.expire(key, ttl)
                REDIS_OPS.labels("set_combat_state", "success").inc()

    async def get_combat_state(self, session_id: UUID) -> Dict[str, str]:
        """Get combat state.

        Args:
            session_id: Session ID.

        Returns:
            Combat state.
        """
        key = f"session:{session_id}:combat"
        async with self.connection() as redis_client:
            with REDIS_LATENCY.labels("get_combat_state").time():
                result = await redis_client.hgetall(key)
                REDIS_OPS.labels("get_combat_state", "success").inc()
                return result

    async def update_combat_field(
        self,
        session_id: UUID,
        field: str,
        value: str,
    ) -> None:
        """Update single combat state field.

        Args:
            session_id: Session ID.
            field: Field name.
            value: Field value.
        """
        key = f"session:{session_id}:combat"
        async with self.connection() as redis_client:
            with REDIS_LATENCY.labels("update_combat_field").time():
                await redis_client.hset(key, field, value)
                REDIS_OPS.labels("update_combat_field", "success").inc()

    # Connection Health

    async def check_health(self) -> bool:
        """Check Redis connection health.

        Returns:
            True if healthy.
        """
        try:
            async with self.connection() as redis_client:
                await redis_client.ping()
                return True
        except Exception as e:
            logger.error("Redis health check failed", error=str(e))
            return False