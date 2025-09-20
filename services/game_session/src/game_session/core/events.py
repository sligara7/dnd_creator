"""Game Session Service Event Handlers.

This module defines startup and shutdown handlers for the FastAPI application.
"""
import asyncio
from typing import Callable, Dict, Optional
from uuid import UUID

import aio_pika
import redis.asyncio as redis
from fastapi import FastAPI
from structlog import get_logger

from game_session.core.config import Settings, get_settings
from game_session.core.message_hub import MessageHubClient
from game_session.core.redis import RedisClient
from game_session.core.storage import StorageOperations, SessionState
from game_session.core.websocket import WebSocketManager

logger = get_logger(__name__)

async def init_redis(app: FastAPI, settings: Settings) -> RedisClient:
    """Initialize Redis client.

    Args:
        app: FastAPI application instance.
        settings: Service configuration settings.

    Returns:
        Initialized Redis client wrapper.
    """
    client = RedisClient(settings)
    await client.connect()
    app.state.redis = client
    return client


async def init_message_hub(app: FastAPI, settings: Settings) -> aio_pika.Connection:
    """Initialize Message Hub connection.

    Args:
        app: FastAPI application instance.
        settings: Service configuration settings.

    Returns:
        Initialized Message Hub connection.
    """
    try:
        # Build connection URL
        connection_str = f"amqp://{settings.MESSAGE_HUB_USER}:{settings.MESSAGE_HUB_PASSWORD}"
        connection_str += f"@{settings.MESSAGE_HUB_HOST}:{settings.MESSAGE_HUB_PORT}/{settings.MESSAGE_HUB_VHOST}"

        # Connect to Message Hub
        connection = await aio_pika.connect_robust(
            connection_str,
            ssl=settings.MESSAGE_HUB_SSL,
        )
        logger.info("Successfully connected to Message Hub")

        # Store connection in app state
        app.state.message_hub = connection
        return connection
    except Exception as e:
        logger.error("Failed to connect to Message Hub", error=str(e))
        raise


def create_start_app_handler(app: FastAPI) -> Callable:
    """Create startup event handler.

    Args:
        app: FastAPI application instance.

    Returns:
        Startup handler function.
    """
async def start_app() -> None:
        settings = get_settings()
        
        # Initialize Redis
        app.state.redis = await init_redis(app, settings)
        
        # Initialize Message Hub
        app.state.message_hub = await init_message_hub(app, settings)
        
        # Initialize session state map and storage operations
        app.state.sessions: Dict[UUID, SessionState] = {}
        app.state.storage = StorageOperations(app.state.message_hub)

        # Initialize WebSocket manager
        app.state.websocket_manager = WebSocketManager(settings, app.state.redis)
        
        # Subscribe to storage service responses
        await app.state.message_hub.subscribe(
            "state.session.loaded",
            _handle_session_loaded,
            "game_session_state_loader"
        )
        
        # Subscribe to character and campaign events
        await app.state.message_hub.subscribe(
            "character.state.changed",
            _handle_character_update,
            "game_session_character_updates"
        )
        await app.state.message_hub.subscribe(
            "campaign.state.changed",
            _handle_campaign_update,
            "game_session_campaign_updates"
        )

        logger.info("Application startup complete")

    # Event handlers for subscriptions
    async def _handle_session_loaded(data: Dict[str, Any]) -> None:
        session_id = UUID(data["session_id"])
        if session_id not in app.state.sessions:
            app.state.sessions[session_id] = SessionState()
        
        # Update session state from storage
        app.state.sessions[session_id].update(
            data["state"],
            data.get("version")
        )

        # Notify connected clients if any
        websocket_manager: WebSocketManager = app.state.websocket_manager
        await websocket_manager.broadcast_event(
            session_id,
            {
                "type": "state_update",
                "state": data["state"],
                "version": data.get("version", "0"),
                "source": "storage",
            }
        )
        logger.info("Session state loaded", session_id=str(session_id))
    
    async def _handle_character_update(data: Dict[str, Any]) -> None:
        character_id = UUID(data["character_id"])
        change_type = data["change_type"]
        details = data["details"]

        # Find sessions with this character
        affected_sessions = []
        for session_id, state in app.state.sessions.items():
            if any(
                str(character_id) in [
                    p.get("character_id") for p in 
                    state.state.get("players", [])
                ]
            ):
                affected_sessions.append(session_id)

        # Update relevant session states
        for session_id in affected_sessions:
            # Update state
            session_state = app.state.sessions[session_id]
            if "players" in session_state.state:
                for player in session_state.state["players"]:
                    if player.get("character_id") == str(character_id):
                        player.update(details)

            # Notify clients
            websocket_manager: WebSocketManager = app.state.websocket_manager
            await websocket_manager.broadcast_event(
                session_id,
                {
                    "type": "character_update",
                    "character_id": str(character_id),
                    "change_type": change_type,
                    "details": details,
                }
            )

            # Save state
            storage: StorageOperations = app.state.storage
            await storage.save_session_state(
                session_id,
                session_state.state,
                {"source": "character_update"}
            )

        logger.info(
            "Character state updated",
            character_id=str(character_id),
            change_type=change_type,
            affected_sessions=len(affected_sessions)
        )
    
    async def _handle_campaign_update(data: Dict[str, Any]) -> None:
        campaign_id = UUID(data["campaign_id"])
        change_type = data["change_type"]
        details = data["details"]

        # Find sessions for this campaign
        affected_sessions = [
            session_id for session_id, state in app.state.sessions.items()
            if state.state.get("campaign_id") == str(campaign_id)
        ]

        # Update relevant session states
        for session_id in affected_sessions:
            # Update state
            session_state = app.state.sessions[session_id]
            session_state.state["campaign"] = session_state.state.get(
                "campaign", {}
            ).update(details)

            # Notify clients
            websocket_manager: WebSocketManager = app.state.websocket_manager
            await websocket_manager.broadcast_event(
                session_id,
                {
                    "type": "campaign_update",
                    "campaign_id": str(campaign_id),
                    "change_type": change_type,
                    "details": details,
                }
            )

            # Save state
            storage: StorageOperations = app.state.storage
            await storage.save_session_state(
                session_id,
                session_state.state,
                {"source": "campaign_update"}
            )

        logger.info(
            "Campaign state updated",
            campaign_id=str(campaign_id),
            change_type=change_type,
            affected_sessions=len(affected_sessions)
        )

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    """Create shutdown event handler.

    Args:
        app: FastAPI application instance.

    Returns:
        Shutdown handler function.
    """
    async def stop_app() -> None:
        # Close Redis connection
        if hasattr(app.state, "redis"):
            await app.state.redis.close()
            logger.info("Redis connection closed")

        # Close Message Hub connection
        if hasattr(app.state, "message_hub"):
            await app.state.message_hub.close()
            logger.info("Message Hub connection closed")

        logger.info("Application shutdown complete")

    return stop_app