"""
Message Router Tests

Tests for message routing functionality.
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock
import httpx

from src.config import Settings
from src.models import ServiceType, MessageType, ServiceMessage, ServiceRegistration
from src.service_registry import ServiceRegistry
from src.message_router import MessageRouter
from src.event_store.service import EventStore

# Test constants
TEST_CORRELATION_ID = "test-correlation-id"
TEST_SERVICE_URL = "http://test-service:8000"

@pytest_asyncio.fixture
async def mock_http_client():
    """Create a mock HTTP client."""
    async def mock_post(*args, **kwargs):
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json = lambda: {"status": "success", "data": {}}
        mock_response.raise_for_status = lambda: None
        return mock_response
    
    client = Mock(spec=httpx.AsyncClient)
    client.post = AsyncMock(side_effect=mock_post)
    return client

@pytest.fixture
def settings():
    """Create test settings."""
    return Settings(
        debug=True,
        database_url="sqlite+aiosqlite:///:memory:",
        service_timeout=1
    )

@pytest_asyncio.fixture
async def mock_event_store():
    """Create a mock event store."""
    store = Mock(spec=EventStore)
    store.append_event = AsyncMock(return_value=None)
    return store

@pytest_asyncio.fixture
async def service_registry(settings, mock_http_client):
    """Create a test service registry."""
    registry = ServiceRegistry(settings)
    registry.http_client = mock_http_client
    
    # Register test service
    registration = ServiceRegistration(
        name=ServiceType.CHARACTER_SERVICE,
        url=TEST_SERVICE_URL,
        health_check="/health",
        version="1.0.0",
        capabilities=[
            MessageType.CHARACTER_CREATED,
            MessageType.CHARACTER_UPDATED
        ]
    )
    await registry.register_service(registration)
    
    return registry

@pytest_asyncio.fixture
async def message_router(settings, service_registry, mock_event_store, mock_http_client):
    """Create a test message router."""
    router = MessageRouter(settings, service_registry, mock_event_store)
    router.http_client = mock_http_client
    return router

@pytest.mark.asyncio
async def test_basic_message_routing(message_router):
    """Test basic message routing."""
    message = ServiceMessage(
        source=ServiceType.MESSAGE_HUB,
        destination=ServiceType.CHARACTER_SERVICE,
        message_type=MessageType.CHARACTER_CREATED,
        correlation_id=TEST_CORRELATION_ID,
        payload={"character_id": "test-123"}
    )
    
    response = await message_router.route_message(message)
    assert response.status == "success"
    assert response.correlation_id == TEST_CORRELATION_ID

@pytest.mark.asyncio
async def test_unknown_message_type(message_router):
    """Test routing message with unknown type."""
    message = ServiceMessage(
        source=ServiceType.MESSAGE_HUB,
        destination=ServiceType.CHARACTER_SERVICE,
        message_type="unknown_type",
        correlation_id=TEST_CORRELATION_ID,
        payload={}
    )
    
    response = await message_router.route_message(message)
    assert response.status == "error"
    assert "Unknown message type" in response.error

@pytest.mark.asyncio
async def test_service_unavailable(message_router, mock_http_client):
    """Test routing to unavailable service."""
    # Make service unavailable
    mock_http_client.post.side_effect = httpx.RequestError("Connection failed")
    
    message = ServiceMessage(
        source=ServiceType.MESSAGE_HUB,
        destination=ServiceType.CHARACTER_SERVICE,
        message_type=MessageType.CHARACTER_CREATED,
        correlation_id=TEST_CORRELATION_ID,
        payload={"character_id": "test-123"}
    )
    
    response = await message_router.route_message(message)
    assert response.status == "error"
    assert "Connection failed" in response.error

@pytest.mark.asyncio
async def test_endpoint_resolution(message_router):
    """Test endpoint resolution for different message types."""
    # Test CHARACTER_CREATED event
    message = ServiceMessage(
        source=ServiceType.MESSAGE_HUB,
        destination=ServiceType.CHARACTER_SERVICE,
        message_type=MessageType.CHARACTER_CREATED,
        correlation_id=TEST_CORRELATION_ID,
        payload={"character_id": "test-123"}
    )
    
    response = await message_router.route_message(message)
    assert response.status == "success"
    
    # Test CHARACTER_UPDATED event
    message.message_type = MessageType.CHARACTER_UPDATED
    message.payload["id"] = "test-123"  # Required for update
    
    response = await message_router.route_message(message)
    assert response.status == "success"

@pytest.mark.asyncio
async def test_event_store_integration(message_router, mock_event_store):
    """Test event store integration."""
    message = ServiceMessage(
        source=ServiceType.MESSAGE_HUB,
        destination=ServiceType.CHARACTER_SERVICE,
        message_type=MessageType.CHARACTER_CREATED,
        correlation_id=TEST_CORRELATION_ID,
        payload={"character_id": "test-123"}
    )
    
    await message_router.route_message(message)
    
    # Verify event was stored
    mock_event_store.append_event.assert_called_once()
    call_args = mock_event_store.append_event.call_args[1]
    assert call_args["event_type"] == MessageType.CHARACTER_CREATED
    assert call_args["source_service"] == ServiceType.MESSAGE_HUB

@pytest.mark.asyncio
async def test_circuit_breaker(message_router, mock_http_client):
    """Test circuit breaker behavior."""
    message = ServiceMessage(
        source=ServiceType.MESSAGE_HUB,
        destination=ServiceType.CHARACTER_SERVICE,
        message_type=MessageType.CHARACTER_CREATED,
        correlation_id=TEST_CORRELATION_ID,
        payload={"character_id": "test-123"}
    )
    
    # Make service fail
    mock_http_client.post.side_effect = httpx.RequestError("Connection failed")
    
    # Send requests until circuit opens
    for _ in range(5):
        response = await message_router.route_message(message)
        assert response.status == "error"
    
    # Circuit should be open, verify error
    response = await message_router.route_message(message)
    assert response.status == "error"
    assert "Circuit" in response.error
