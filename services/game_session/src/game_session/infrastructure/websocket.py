"""WebSocket connection management for game sessions."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Set
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
from prometheus_client import Counter, Gauge

# Metrics
ws_connections = Gauge("game_session_websocket_connections", "Number of active WebSocket connections")
ws_messages = Counter("game_session_websocket_messages", "Number of WebSocket messages", ["direction"])

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for a game session."""
    
    def __init__(self) -> None:
        """Initialize the WebSocket manager."""
        self.active_connections: Dict[UUID, Dict[UUID, WebSocket]] = {}
        self.last_heartbeat: Dict[UUID, Dict[UUID, datetime]] = {}
        
    async def connect(
        self,
        websocket: WebSocket,
        session_id: UUID,
        player_id: UUID
    ) -> None:
        """Accept a new WebSocket connection.
        
        Args:
            websocket: The WebSocket connection
            session_id: The game session ID
            player_id: The player's ID
        """
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = {}
            self.last_heartbeat[session_id] = {}
            
        self.active_connections[session_id][player_id] = websocket
        self.last_heartbeat[session_id][player_id] = datetime.utcnow()
        
        ws_connections.inc()
        logger.info(f"WebSocket connection established - session: {session_id}, player: {player_id}")
        
    def disconnect(self, session_id: UUID, player_id: UUID) -> None:
        """Handle a WebSocket disconnection.
        
        Args:
            session_id: The game session ID
            player_id: The player's ID
        """
        if (
            session_id in self.active_connections
            and player_id in self.active_connections[session_id]
        ):
            del self.active_connections[session_id][player_id]
            del self.last_heartbeat[session_id][player_id]
            
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
                del self.last_heartbeat[session_id]
            
            ws_connections.dec()
            logger.info(f"WebSocket connection closed - session: {session_id}, player: {player_id}")
            
    def get_session_connections(self, session_id: UUID) -> Set[UUID]:
        """Get all connected player IDs for a session.
        
        Args:
            session_id: The game session ID
            
        Returns:
            Set of connected player IDs
        """
        if session_id not in self.active_connections:
            return set()
        return set(self.active_connections[session_id].keys())
        
    async def broadcast(
        self,
        session_id: UUID,
        message: Dict[str, Any],
        exclude: Optional[UUID] = None
    ) -> None:
        """Broadcast a message to all connected players in a session.
        
        Args:
            session_id: The game session ID
            message: The message to broadcast
            exclude: Optional player ID to exclude from broadcast
        """
        if session_id not in self.active_connections:
            return
            
        message_json = json.dumps(message)
        
        for player_id, connection in self.active_connections[session_id].items():
            if exclude and player_id == exclude:
                continue
                
            try:
                await connection.send_text(message_json)
                ws_messages.labels(direction="out").inc()
            except WebSocketDisconnect:
                self.disconnect(session_id, player_id)
            except Exception as e:
                logger.error(
                    f"Error broadcasting to session {session_id}, player {player_id}: {e}"
                )
                
    async def send_personal_message(
        self,
        session_id: UUID,
        player_id: UUID,
        message: Dict[str, Any]
    ) -> None:
        """Send a message to a specific player.
        
        Args:
            session_id: The game session ID
            player_id: The player's ID
            message: The message to send
        """
        if (
            session_id not in self.active_connections
            or player_id not in self.active_connections[session_id]
        ):
            return
            
        try:
            connection = self.active_connections[session_id][player_id]
            await connection.send_text(json.dumps(message))
            ws_messages.labels(direction="out").inc()
        except WebSocketDisconnect:
            self.disconnect(session_id, player_id)
        except Exception as e:
            logger.error(
                f"Error sending to session {session_id}, player {player_id}: {e}"
            )
            
    async def heartbeat_monitor(self) -> None:
        """Monitor connection heartbeats and clean up stale connections."""
        while True:
            now = datetime.utcnow()
            
            for session_id in list(self.last_heartbeat.keys()):
                for player_id in list(self.last_heartbeat[session_id].keys()):
                    last_seen = self.last_heartbeat[session_id][player_id]
                    
                    # If no heartbeat for 1 minute, disconnect
                    if (now - last_seen).seconds > 60:
                        logger.warning(
                            f"Heartbeat timeout - session: {session_id}, player: {player_id}"
                        )
                        self.disconnect(session_id, player_id)
                        
            await asyncio.sleep(10)  # Check every 10 seconds
            
    def update_heartbeat(self, session_id: UUID, player_id: UUID) -> None:
        """Update the last heartbeat time for a connection.
        
        Args:
            session_id: The game session ID
            player_id: The player's ID
        """
        if (
            session_id in self.last_heartbeat
            and player_id in self.last_heartbeat[session_id]
        ):
            self.last_heartbeat[session_id][player_id] = datetime.utcnow()