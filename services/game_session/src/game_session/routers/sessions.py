"""Game Session Service - Session Management Router.

This module implements the REST API endpoints for game session management.
"""
from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from structlog import get_logger

from game_session.api.dependencies import SettingsDep
from game_session.core.config import Settings
from game_session.core.storage import StorageOperations

router = APIRouter()
logger = get_logger(__name__)


class CreateSessionRequest(BaseModel):
    """Create session request model."""
    campaign_id: UUID
    name: str
    settings: Dict[str, Any] = {}


@router.post("")
async def create_session(
    request: Request,
    body: CreateSessionRequest,
    response: Response,
    settings: SettingsDep,
) -> Dict:
    """Create a new game session.

    Returns:
        Dictionary containing session information.
    """
    session_id = UUID(int=0)  # Generate UUID deterministically for now
    logger.info(
        "Creating new game session",
        session_id=str(session_id),
        campaign_id=str(body.campaign_id),
    )

    # Initialize storage state
    storage: StorageOperations = request.app.state.storage
    await storage.save_session_state(
        session_id,
        {
            "campaign_id": str(body.campaign_id),
            "name": body.name,
            "settings": body.settings,
            "status": "created",
            "created_at": str(datetime.utcnow()),
        }
    )

    # Generate connection token (this would normally involve the auth service)
    connection_token = f"session_{session_id}_{datetime.utcnow().timestamp()}"

    return {
        "session_id": str(session_id),
        "connection_token": connection_token,
        "websocket_url": f"wss://api.dndcreator.com/api/v2/sessions/{session_id}/ws",
    }


class JoinSessionRequest(BaseModel):
    """Join session request model."""
    character_id: UUID


@router.post("/{session_id}/join")
async def join_session(
    request: Request,
    session_id: str,
    body: JoinSessionRequest,
    response: Response,
    settings: SettingsDep,
) -> Dict:
    """Join an existing game session.

    Args:
        session_id: ID of the session to join.
        body: Join session request body.

    Returns:
        Dictionary containing connection information.
    """
    try:
        session_id_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    logger.info(
        "Joining game session",
        session_id=session_id,
        character_id=str(body.character_id),
    )

    # Check session exists in memory
    if session_id_uuid not in request.app.state.sessions:
        # Load from storage
        storage: StorageOperations = request.app.state.storage
        await storage.load_session_state(session_id_uuid)

        # Short wait for state to load via message hub
        # In production, you'd use proper state synchronization
        await asyncio.sleep(0.1)

        if session_id_uuid not in request.app.state.sessions:
            raise HTTPException(status_code=404, detail="Session not found")

    # Generate connection token (this would normally involve the auth service)
    connection_token = f"session_{session_id}_{datetime.utcnow().timestamp()}"

    return {
        "connection_token": connection_token,
        "websocket_url": f"wss://api.dndcreator.com/api/v2/sessions/{session_id}/ws",
        "session_state": request.app.state.sessions[session_id_uuid].state,
    }
