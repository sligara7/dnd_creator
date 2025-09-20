"""WebSocket API endpoints for game event relay."""

from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from ..relay import GameEventRelay

router = APIRouter(prefix="/ws")
game_relay = GameEventRelay()

@router.websocket("/game/{session_id}")
async def game_session_ws(
    websocket: WebSocket,
    session_id: str,
    character_id: Optional[str] = None
):
    """WebSocket endpoint for game session events.
    
    Args:
        websocket: The WebSocket connection
        session_id: Game session identifier
        character_id: Optional character identifier for direct messages
    """
    try:
        await game_relay.connect(
            websocket,
            session_id,
            character_id
        )
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_json()
                # Process incoming messages if needed
                
            except WebSocketDisconnect:
                await game_relay.disconnect(
                    websocket,
                    session_id,
                    character_id
                )
                break
                
            except Exception as e:
                logger.error(f"Error in game session websocket: {e}")
                break
                
    except Exception as e:
        logger.error(
            f"Error establishing game session websocket: {e}",
            extra={
                "session_id": session_id,
                "character_id": character_id
            }
        )
        raise HTTPException(status_code=500, detail=str(e))
        
@router.websocket("/combat/{session_id}/{combat_id}")
async def combat_session_ws(
    websocket: WebSocket,
    session_id: str,
    combat_id: str,
    character_id: Optional[str] = None
):
    """WebSocket endpoint for combat events.
    
    Args:
        websocket: The WebSocket connection
        session_id: Game session identifier
        combat_id: Combat encounter identifier
        character_id: Optional character identifier for direct messages
    """
    try:
        await game_relay.connect(
            websocket,
            session_id,
            character_id
        )
        
        # Mark session as in combat
        await game_relay.start_combat(session_id, combat_id)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_json()
                # Process incoming combat messages
                
            except WebSocketDisconnect:
                # End combat if this was the last connection
                await game_relay.end_combat(session_id, combat_id)
                await game_relay.disconnect(
                    websocket,
                    session_id,
                    character_id
                )
                break
                
            except Exception as e:
                logger.error(f"Error in combat session websocket: {e}")
                break
                
    except Exception as e:
        logger.error(
            f"Error establishing combat session websocket: {e}",
            extra={
                "session_id": session_id,
                "combat_id": combat_id,
                "character_id": character_id
            }
        )
        raise HTTPException(status_code=500, detail=str(e))