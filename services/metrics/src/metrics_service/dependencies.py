"""Dependency providers for the Metrics service."""

from typing import Annotated
from fastapi import Depends, Request
from metrics_service.core.message_client import MessageClient
from metrics_service.config import ServiceConfig

async def get_message_client(request: Request) -> MessageClient:
    """Retrieve the message client from app state."""
    client = getattr(request.app.state, "message_client", None)
    if client is None:
        # Lazily initialize if not present (should be set in lifespan)
        config = getattr(request.app.state, "service_config", ServiceConfig())
        client = MessageClient(config)
        await client.connect()
        request.app.state.message_client = client
    return client