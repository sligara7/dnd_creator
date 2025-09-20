"""WebSocket relay for real-time game events.

Handles the relay of events between WebSocket connections and the message queue
for real-time gameplay coordination.
"""

import json
import asyncio
import logging
from typing import Any, Dict, List, Optional, Set
from uuid import UUID
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from .models.events import (
    EventType,
    EventStatus,
    GameEventPriority,
    GameEvent,
    CombatEvent,
)

logger = logging.getLogger(__name__)


class GameEventRelay:
    """Manages WebSocket connections and event relay for game sessions."""
    
    def __init__(self):
        """Initialize the relay manager."""
        # Map of session_id to list of connected clients
        self.active_sessions: Dict[str, Set[WebSocket]] = {}
        
        # Map of character_id to WebSocket for direct messages
        self.character_connections: Dict[str, WebSocket] = {}
        
        # Set of combat sessions for priority handling
        self.active_combats: Set[str] = set()
        
    async def connect(
        self,
        websocket: WebSocket,
        session_id: str,
        character_id: Optional[str] = None
    ):
        """Handle new WebSocket connection.
        
        Args:
            websocket: The WebSocket connection
            session_id: Game session identifier
            character_id: Optional character identifier
        """
        await websocket.accept()
        
        # Add to session map
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = set()
        self.active_sessions[session_id].add(websocket)
        
        # Add character mapping if provided
        if character_id:
            self.character_connections[character_id] = websocket
        
        await self._broadcast_session_event(
            session_id,
            EventType.GAME_SESSION_STARTED,
            {
                "character_id": character_id,
                "connection_time": datetime.utcnow().isoformat()
            }
        )
        
    async def disconnect(
        self,
        websocket: WebSocket,
        session_id: str,
        character_id: Optional[str] = None
    ):
        """Handle WebSocket disconnection.
        
        Args:
            websocket: The WebSocket connection
            session_id: Game session identifier
            character_id: Optional character identifier
        """
        # Remove from session map
        if session_id in self.active_sessions:
            self.active_sessions[session_id].remove(websocket)
            if not self.active_sessions[session_id]:
                del self.active_sessions[session_id]
        
        # Remove character mapping
        if character_id and character_id in self.character_connections:
            del self.character_connections[character_id]
            
        await self._broadcast_session_event(
            session_id,
            EventType.GAME_SESSION_ENDED,
            {
                "character_id": character_id,
                "disconnection_time": datetime.utcnow().isoformat()
            }
        )
        
    async def start_combat(self, session_id: str, combat_id: str):
        """Mark a session as being in combat.
        
        Args:
            session_id: Game session identifier
            combat_id: Combat encounter identifier
        """
        combat_key = f"{session_id}:{combat_id}"
        self.active_combats.add(combat_key)
        
        await self._broadcast_session_event(
            session_id,
            EventType.COMBAT_STARTED,
            {
                "combat_id": combat_id,
                "start_time": datetime.utcnow().isoformat()
            },
            priority=GameEventPriority.HIGH
        )
        
    async def end_combat(self, session_id: str, combat_id: str):
        """Mark a session as no longer in combat.
        
        Args:
            session_id: Game session identifier
            combat_id: Combat encounter identifier
        """
        combat_key = f"{session_id}:{combat_id}"
        if combat_key in self.active_combats:
            self.active_combats.remove(combat_key)
            
        await self._broadcast_session_event(
            session_id,
            EventType.COMBAT_ENDED,
            {
                "combat_id": combat_id,
                "end_time": datetime.utcnow().isoformat()
            },
            priority=GameEventPriority.HIGH
        )
        
    async def relay_event(self, event: GameEvent):
        """Relay a game event to relevant WebSocket connections.
        
        Args:
            event: The game event to relay
        """
        try:
            session_id = event.session_id
            
            if session_id not in self.active_sessions:
                logger.warning(f"No active connections for session {session_id}")
                return
                
            # Prepare event data
            event_data = {
                "type": event.type,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "payload": event.payload
            }
            
            # Send to all session connections
            for websocket in self.active_sessions[session_id]:
                try:
                    await websocket.send_json(event_data)
                except WebSocketDisconnect:
                    await self.disconnect(
                        websocket,
                        session_id
                    )
                except Exception as e:
                    logger.error(
                        f"Error sending event to websocket: {e}",
                        extra={
                            "session_id": session_id,
                            "event_type": event.type
                        }
                    )
                    
        except Exception as e:
            logger.error(
                f"Error relaying event: {e}",
                extra={"event": str(event)}
            )
            
    async def relay_combat_event(self, event: CombatEvent):
        """Relay a combat event with high priority.
        
        Args:
            event: The combat event to relay
        """
        try:
            session_id = event.session_id
            combat_key = f"{session_id}:{event.combat_id}"
            
            if combat_key not in self.active_combats:
                logger.warning(f"No active combat for {combat_key}")
                return
                
            # Prepare combat event data
            event_data = {
                "type": event.type,
                "session_id": session_id,
                "combat_id": event.combat_id,
                "round": event.round_number,
                "turn": event.turn_order,
                "character_id": event.character_id,
                "targets": event.target_ids,
                "action": event.action_type,
                "timestamp": datetime.utcnow().isoformat(),
                "payload": event.payload
            }
            
            # Send to all session connections
            if session_id in self.active_sessions:
                for websocket in self.active_sessions[session_id]:
                    try:
                        await websocket.send_json(event_data)
                    except WebSocketDisconnect:
                        await self.disconnect(
                            websocket,
                            session_id
                        )
                    except Exception as e:
                        logger.error(
                            f"Error sending combat event: {e}",
                            extra={
                                "session_id": session_id,
                                "combat_id": event.combat_id
                            }
                        )
                        
        except Exception as e:
            logger.error(
                f"Error relaying combat event: {e}",
                extra={"event": str(event)}
            )
            
    async def relay_direct_message(
        self,
        character_id: str,
        message_type: str,
        payload: Dict[str, Any]
    ):
        """Send a direct message to a specific character's connection.
        
        Args:
            character_id: Target character identifier
            message_type: Type of message
            payload: Message content
        """
        if character_id not in self.character_connections:
            logger.warning(f"No connection for character {character_id}")
            return
            
        websocket = self.character_connections[character_id]
        message_data = {
            "type": message_type,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload
        }
        
        try:
            await websocket.send_json(message_data)
        except WebSocketDisconnect:
            # Character disconnected - clean up
            session_id = None
            for sid, connections in self.active_sessions.items():
                if websocket in connections:
                    session_id = sid
                    break
                    
            if session_id:
                await self.disconnect(
                    websocket,
                    session_id,
                    character_id
                )
        except Exception as e:
            logger.error(
                f"Error sending direct message: {e}",
                extra={
                    "character_id": character_id,
                    "message_type": message_type
                }
            )
            
    async def _broadcast_session_event(
        self,
        session_id: str,
        event_type: EventType,
        payload: Dict[str, Any],
        priority: GameEventPriority = GameEventPriority.NORMAL
    ):
        """Broadcast an event to all connections in a session.
        
        Args:
            session_id: Game session identifier
            event_type: Type of event
            payload: Event data
            priority: Event priority
        """
        if session_id not in self.active_sessions:
            return
            
        event = GameEvent(
            id=UUID(int=0),  # Placeholder
            type=event_type,
            session_id=session_id,
            campaign_id="",  # Placeholder
            payload=payload,
            metadata={
                "timestamp": datetime.utcnow(),
                "priority": priority
            }
        )
        
        await self.relay_event(event)