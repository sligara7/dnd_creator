"""Game Session Service - API Dependencies."""
from typing import Annotated

from fastapi import Depends, FastAPI, Request

from game_session.core.config import Settings, get_settings
from game_session.core.redis import RedisClient
from game_session.core.websocket import WebSocketManager


def get_redis_client(request: Request) -> RedisClient:
    """Get Redis client from app state.

    Args:
        request: FastAPI request object.

    Returns:
        Redis client wrapper.
    """
    return request.app.state.redis


RedisClientDep = Annotated[RedisClient, Depends(get_redis_client)]
SettingsDep = Annotated[Settings, Depends(get_settings)]