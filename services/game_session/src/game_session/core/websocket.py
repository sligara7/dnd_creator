"""Game Session Service - WebSocket Manager.

This module implements the WebSocket connection management and message handling.
"""
from collections import defaultdict
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from structlog import get_logger
from prometheus_client import Counter

from game_session.core.config import Settings
from game_session.core.redis import RedisClient
from game_session.models.websocket import (
    WebSocketEventType,
    ConnectionEvent,
    ConnectionErrorEvent,
    HeartbeatEvent,
)

logger = get_logger(__name__)

# Metrics
WS_CONNECTIONS_ACTIVE = Counter(
    "game_session_websocket_connections_active",
    "Number of active WebSocket connections",
)
WS_CONNECTIONS_TOTAL = Counter(
    "game_session_websocket_connections_total",
    "Total number of WebSocket connections",
)
WS_MESSAGES_SENT = Counter(
    "game_session_websocket_messages_sent",
    "Number of WebSocket messages sent",
    ["event_type"],
)
WS_MESSAGES_RECEIVED = Counter(
    "game_session_websocket_messages_received",
    "Number of WebSocket messages received",
    ["event_type"],
)


class WebSocketManager:
    """Manages WebSocket connections for game sessions."""

    def __init__(self, settings: Settings, redis_client: Optional[RedisClient] = None):
        """Initialize WebSocket manager.

        Args:
            settings: Service configuration settings.
            redis_client: Optional Redis client for state persistence.
        """
        self.settings = settings
        self.redis = redis_client
        self.active_connections: Dict[UUID, Dict[UUID, WebSocket]] = defaultdict(dict)
        self.heartbeat_tasks: Dict[UUID, Dict[UUID, asyncio.Task]] = defaultdict(dict)

    async def connect(
        self,
        websocket: WebSocket,
        session_id: UUID,
        player_id: UUID,
    ) -> None:
        """Handle new WebSocket connection.

        Args:
            websocket: WebSocket connection.
            session_id: Game session ID.
            player_id: Player ID.
        """
        await websocket.accept()
        
        # Store connection locally
        self.active_connections[session_id][player_id] = websocket
        WS_CONNECTIONS_ACTIVE.inc()
        WS_CONNECTIONS_TOTAL.inc()

        # Persist connection state in Redis if available
        if self.redis:
            # Add player to session
            await self.redis.add_player(session_id, player_id)
            
            # Store connection ID (using player_id for now as conn_id)
            await self.redis.set_player_connection(
                session_id,
                player_id,
                str(player_id),  # Using player_id as conn_id for simplicity
            )

            # Update session metadata if empty
            meta = await self.redis.get_session_meta(session_id)
            if not meta:
                await self.redis.set_session_meta(
                    session_id,
                    {
                        "status": "active",
                        "last_active": str(datetime.utcnow()),
                    }
                )

        # Start heartbeat task
        self.heartbeat_tasks[session_id][player_id] = asyncio.create_task(
            self._heartbeat_loop(websocket, session_id, player_id)
        )

        # Send connection established event
        await self.send_event(
            session_id,
            player_id,
            ConnectionEvent(
                type=WebSocketEventType.CONNECTION_ESTABLISHED,
                session_id=session_id,
                player_id=player_id,
            ),
        )

        logger.info(
            "WebSocket connection established",
            session_id=str(session_id),
            player_id=str(player_id),
        )

    async def disconnect(self, session_id: UUID, player_id: UUID) -> None:
        """Handle WebSocket disconnection.

        Args:
            session_id: Game session ID.
            player_id: Player ID.
        """
        # Cancel heartbeat task
        if task := self.heartbeat_tasks[session_id].pop(player_id, None):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Remove connection from local state
        if player_id in self.active_connections[session_id]:
            del self.active_connections[session_id][player_id]
            WS_CONNECTIONS_ACTIVE.dec()

        # Clean up empty session from local state
        if not self.active_connections[session_id]:
            del self.active_connections[session_id]

        # Clean up Redis state if available
        if self.redis:
            # Remove connection record
            await self.redis.remove_player_connection(session_id, player_id)
            
            # Remove player from session
            await self.redis.remove_player(session_id, player_id)
            
            # Check if session is empty
            players = await self.redis.get_players(session_id)
            if not players:
                # Update session metadata to inactive
                await self.redis.set_session_meta(
                    session_id,
                    {
                        "status": "inactive",
                        "last_active": str(datetime.utcnow()),
                    }
                )

        logger.info(
            "WebSocket connection closed",
            session_id=str(session_id),
            player_id=str(player_id),
        )

    async def send_event(
        self,
        session_id: UUID,
        player_id: UUID,
        event: Any,
    ) -> None:
        """Send event to specific player.

        Args:
            session_id: Game session ID.
            player_id: Player ID.
            event: Event to send.
        """
        if (
            session_id in self.active_connections
            and player_id in self.active_connections[session_id]
        ):
            websocket = self.active_connections[session_id][player_id]
            try:
                await websocket.send_json(event.model_dump())
                WS_MESSAGES_SENT.labels(event_type=event.type).inc()
            except Exception as e:
                logger.error(
                    "Error sending WebSocket message",
                    session_id=str(session_id),
                    player_id=str(player_id),
                    error=str(e),
                )
                await self.disconnect(session_id, player_id)

    async def broadcast_event(
        self,
        session_id: UUID,
        event: Any,
        exclude: Optional[Set[UUID]] = None,
    ) -> None:
        """Broadcast event to all players in session.

        Args:
            session_id: Game session ID.
            event: Event to broadcast.
            exclude: Set of player IDs to exclude from broadcast.
        """
        if session_id in self.active_connections:
            exclude = exclude or set()
            for player_id, websocket in self.active_connections[session_id].items():
                if player_id not in exclude:
                    await self.send_event(session_id, player_id, event)

    async def _heartbeat_loop(
        self,
        websocket: WebSocket,
        session_id: UUID,
        player_id: UUID,
    ) -> None:
        """Send periodic heartbeat messages.

        Args:
            websocket: WebSocket connection.
            session_id: Game session ID.
            player_id: Player ID.
        """
        try:
            while True:
                await asyncio.sleep(self.settings.WS_HEARTBEAT_INTERVAL)
                await self.send_event(
                    session_id,
                    player_id,
                    HeartbeatEvent(type=WebSocketEventType.HEARTBEAT),
                )
        except Exception as e:
            logger.error(
                "Error in heartbeat loop",
                session_id=str(session_id),
                player_id=str(player_id),
                error=str(e),
            )
            await self.disconnect(session_id, player_id)