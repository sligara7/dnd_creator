"""Game Session Service - WebSocket Router.

This module implements the WebSocket endpoints for real-time game session communication.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from structlog import get_logger

from game_session.api.dependencies import RedisClientDep, SettingsDep
from game_session.core.config import Settings
from game_session.core.redis import RedisClient
from game_session.core.websocket import WebSocketManager

router = APIRouter()
logger = get_logger(__name__)


def _get_manager(settings: Settings, redis_client: RedisClient) -> WebSocketManager:
    # In a real app, you'd likely attach this to app.state
    return WebSocketManager(settings, redis_client)


@router.websocket("/{session_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    redis_client: RedisClientDep,
    settings: SettingsDep,
) -> None:
    """WebSocket endpoint for game session communication.

    Args:
        websocket: WebSocket connection.
        session_id: ID of the game session.
        settings: Service configuration settings.
    """
    logger.info("WebSocket connection attempt", session_id=session_id)

    # Minimal header presence checks (Auth enforcement handled at gateway in prod)
    auth = websocket.headers.get("Authorization")
    session_token = websocket.headers.get("X-Session-Token")
    if not auth or not session_token:
        await websocket.close(code=4401)
        logger.warn("Missing auth headers", session_id=session_id)
        return

    # Get player_id from query params for now (ICD implies auth service validation)
    qp = dict(websocket.query_params)
    player_id_str = qp.get("player_id")
    if not player_id_str:
        await websocket.close(code=4400)
        logger.warn("Missing player_id query param", session_id=session_id)
        return

    manager = _get_manager(settings, redis_client)

    try:
        await manager.connect(
            websocket,
            UUID(session_id),
            UUID(player_id_str),
        )
        # Basic echo/receive loop; heartbeat handled by manager task
        while True:
            data = await websocket.receive_json()
            logger.debug("Received message", session_id=session_id, data=data)
            await websocket.send_json({"type": "echo", "data": data})

    except WebSocketDisconnect:
        logger.info("WebSocket connection closed", session_id=session_id)
        await manager.disconnect(UUID(session_id), UUID(player_id_str))
    except Exception as e:
        logger.error(
            "Error in WebSocket connection",
            session_id=session_id,
            error=str(e)
        )
        await manager.disconnect(UUID(session_id), UUID(player_id_str))
