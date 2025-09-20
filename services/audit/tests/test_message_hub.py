"""
Tests for Message Hub client.
"""
from typing import List
import pytest

from audit_service.core.message_hub import MessageHubClient
from audit_service.core.exceptions import EventRoutingError
from audit_service.models.events import Event

@pytest.mark.asyncio
async def test_message_hub_client_lifecycle():
    """Test Message Hub client lifecycle."""
    client = MessageHubClient()
    await client.setup()
    await client.cleanup()

@pytest.mark.asyncio
async def test_publish_event(event: Event):
    """Test publishing a single event."""
    client = MessageHubClient()
    await client.setup()
    try:
        await client.publish_event(event)
    finally:
        await client.cleanup()

@pytest.mark.asyncio
async def test_publish_events(event_batch: List[Event]):
    """Test publishing multiple events."""
    client = MessageHubClient()
    await client.setup()
    try:
        await client.publish_events(event_batch)
    finally:
        await client.cleanup()

@pytest.mark.asyncio
async def test_publish_event_with_retries(event: Event):
    """Test publishing with retry attempts."""
    client = MessageHubClient()
    client._max_retries = 3
    client._retry_delay = 0  # No delay for tests
    await client.setup()
    try:
        await client.publish_event(event)
    finally:
        await client.cleanup()

@pytest.mark.asyncio
async def test_publish_event_no_connection():
    """Test publishing without connection."""
    client = MessageHubClient()
    # Don't set up client
    with pytest.raises(EventRoutingError) as exc_info:
        await client.publish_event(Event(
            service="test",
            type="test",
            action="test",
            actor={
                "id": "test",
                "type": "test",
                "name": "test"
            },
            target={
                "id": "test",
                "type": "test",
                "name": "test"
            },
            context={
                "environment": "test",
                "source": "test"
            },
            severity="info",
            outcome="success",
            retention_period="30d"
        ))
    assert "No Message Hub connection available" in str(exc_info.value)