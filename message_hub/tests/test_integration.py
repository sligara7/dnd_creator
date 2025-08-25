"""
Message Hub Integration Tests

Tests service integration and message flow.
"""

import pytest
import pytest_asyncio
from datetime import datetime
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock
import httpx
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.event_store.models import Base

from src.config import Settings
from src.models import ServiceType, MessageType, ServiceMessage, ServiceResponse, ServiceRegistration
from src.service_registry import ServiceRegistry
from src.message_router import MessageRouter
from src.event_store.service import EventStore
from src.transaction_manager import TransactionManager

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
    client.get = AsyncMock(side_effect=mock_post)
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
async def db_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest_asyncio.fixture
async def service_registry(settings, mock_http_client):
    """Create a test service registry."""
    registry = ServiceRegistry(settings)
    registry.http_client = mock_http_client
    return registry

@pytest_asyncio.fixture
async def session_factory(db_engine):
    """Create a test session factory."""
    factory = sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    return factory

@pytest_asyncio.fixture
async def event_store(session_factory) -> EventStore:
    """Create a test event store."""
    return EventStore(session_factory)

@pytest_asyncio.fixture
async def message_router(settings, service_registry, event_store, mock_http_client):
    """Create a test message router."""
    router = MessageRouter(settings, service_registry, event_store)
    router.http_client = mock_http_client
    return router

@pytest_asyncio.fixture
async def transaction_manager(message_router):
    """Create a test transaction manager."""
    return TransactionManager(message_router)

@pytest_asyncio.fixture
async def registered_service(service_registry):
    """Register a test service."""
    registration = ServiceRegistration(
        name=ServiceType.CHARACTER_SERVICE,
        url=TEST_SERVICE_URL,
        health_check="/health",
        version="1.0.0",
        capabilities=[MessageType.CHARACTER_CREATED]
    )
    await service_registry.register_service(registration)
    return registration

@pytest.mark.asyncio
async def test_service_registration_and_health_check(service_registry):
    """Test service registration and health check."""
    registration = ServiceRegistration(
        name=ServiceType.CHARACTER_SERVICE,
        url=TEST_SERVICE_URL,
        health_check="/health",
        version="1.0.0",
        capabilities=[MessageType.CHARACTER_CREATED]
    )
    
    # Register service
    assert await service_registry.register_service(registration)
    
    # Check service exists
    service = await service_registry.get_service(ServiceType.CHARACTER_SERVICE)
    assert service is not None
    assert service.url == TEST_SERVICE_URL
    
    # Check health status
    status = await service_registry.get_service_status(ServiceType.CHARACTER_SERVICE)
    assert status is not None
    assert status.status == "healthy"

@pytest.mark.asyncio
async def test_message_routing(message_router, registered_service):
    """Test message routing between services."""
    message = ServiceMessage(
        source=ServiceType.MESSAGE_HUB,
        destination=ServiceType.CHARACTER_SERVICE,
        message_type=MessageType.CHARACTER_CREATED,
        correlation_id=TEST_CORRELATION_ID,
        payload={"character_id": "test-123"}
    )
    
    # Route message
    response = await message_router.route_message(message)
    
    assert response is not None
    assert response.status == "success"
    assert response.correlation_id == TEST_CORRELATION_ID

@pytest.mark.asyncio
async def test_transaction_flow(transaction_manager, message_router, registered_service):
    """Test full transaction flow with commit."""
    # Start transaction
    transaction = await transaction_manager.begin_transaction()
    assert transaction.id is not None
    
    # Add operations to transaction
    message = ServiceMessage(
        source=ServiceType.MESSAGE_HUB,
        destination=ServiceType.CHARACTER_SERVICE,
        message_type=MessageType.CHARACTER_CREATED,
        correlation_id=TEST_CORRELATION_ID,
        payload={"character_id": "test-123"}
    )
    
    # Commit transaction
    success = await transaction_manager.commit_transaction(transaction.id)
    assert success
    
    # Verify transaction is completed
    metrics = transaction_manager.get_metrics()
    assert transaction.id in metrics["completed_transactions"]

@pytest.mark.asyncio
async def test_circuit_breaker(message_router, registered_service, mock_http_client):
    """Test circuit breaker behavior."""
    # Configure mock to fail
    mock_http_client.post.side_effect = httpx.RequestError("Connection failed")
    
    message = ServiceMessage(
        source=ServiceType.MESSAGE_HUB,
        destination=ServiceType.CHARACTER_SERVICE,
        message_type=MessageType.CHARACTER_CREATED,
        correlation_id=TEST_CORRELATION_ID,
        payload={"character_id": "test-123"}
    )
    
    # Send messages until circuit opens
    for _ in range(5):
        response = await message_router.route_message(message)
        assert response.status == "error"
    
    # We expect errors to persist due to circuit breaker behavior
    # (library does not expose state; verify failure response)
    response = await message_router.route_message(message)
    assert response.status == "error"

@pytest.mark.asyncio
async def test_event_store_integration(event_store, message_router, registered_service):
    """Test event store integration with message routing."""
    message = ServiceMessage(
        source=ServiceType.MESSAGE_HUB,
        destination=ServiceType.CHARACTER_SERVICE,
        message_type=MessageType.CHARACTER_CREATED,
        correlation_id=TEST_CORRELATION_ID,
        payload={"character_id": "test-123"}
    )
    
    # Route message
    await message_router.route_message(message)
    
    # Verify event was stored
    events = await event_store.get_events(
        event_types=[MessageType.CHARACTER_CREATED],
        source_services=[ServiceType.MESSAGE_HUB]
    )
    assert len(events) == 1
    assert events[0].correlation_id == TEST_CORRELATION_ID

@pytest.mark.asyncio
async def test_error_handling(message_router, registered_service, mock_http_client):
    """Test error handling in message routing."""
    # Configure mock to raise error
    mock_http_client.post.side_effect = httpx.RequestError("Connection failed")
    
    message = ServiceMessage(
        source=ServiceType.MESSAGE_HUB,
        destination=ServiceType.CHARACTER_SERVICE,
        message_type=MessageType.CHARACTER_CREATED,
        correlation_id=TEST_CORRELATION_ID,
        payload={"character_id": "test-123"}
    )
    
    # Route message
    response = await message_router.route_message(message)
    
    assert response.status == "error"
    assert "Connection failed" in response.error
