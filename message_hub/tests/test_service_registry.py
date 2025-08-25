"""
Service Registry Tests

Tests for service registration and health check functionality.
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock
import httpx

from src.config import Settings
from src.models import ServiceType, MessageType, ServiceRegistration, ServiceStatus
from src.service_registry import ServiceRegistry

@pytest.fixture
def settings():
    """Create test settings."""
    return Settings(
        debug=True,
        database_url="sqlite+aiosqlite:///:memory:",
        service_timeout=1
    )

@pytest_asyncio.fixture
async def mock_http_client():
    """Create a mock HTTP client."""
    async def mock_get(*args, **kwargs):
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json = lambda: {"status": "healthy"}
        mock_response.raise_for_status = lambda: None
        return mock_response
    
    client = Mock(spec=httpx.AsyncClient)
    client.get = AsyncMock(side_effect=mock_get)
    return client

@pytest_asyncio.fixture
async def service_registry(settings, mock_http_client):
    """Create a test service registry."""
    registry = ServiceRegistry(settings)
    registry.http_client = mock_http_client
    return registry

@pytest.mark.asyncio
async def test_service_registration(service_registry):
    """Test basic service registration."""
    registration = ServiceRegistration(
        name=ServiceType.CHARACTER_SERVICE,
        url="http://character-service:8000",
        health_check="/health",
        version="1.0.0",
        capabilities=[MessageType.CHARACTER_CREATED]
    )
    
    # Register service
    assert await service_registry.register_service(registration)
    
    # Verify service is registered
    service = await service_registry.get_service(ServiceType.CHARACTER_SERVICE)
    assert service is not None
    assert service.url == "http://character-service:8000"
    assert service.capabilities == [MessageType.CHARACTER_CREATED]

@pytest.mark.asyncio
async def test_health_check(service_registry, mock_http_client):
    """Test service health check."""
    registration = ServiceRegistration(
        name=ServiceType.CHARACTER_SERVICE,
        url="http://character-service:8000",
        health_check="/health",
        version="1.0.0",
        capabilities=[MessageType.CHARACTER_CREATED]
    )
    await service_registry.register_service(registration)
    
    # Check healthy service
    status = await service_registry.get_service_status(ServiceType.CHARACTER_SERVICE)
    assert status.status == "healthy"
    assert status.error is None
    
        # Test unhealthy service
        mock_http_client.get.side_effect = httpx.RequestError("Connection failed")
        status = await service_registry.get_service_status(ServiceType.CHARACTER_SERVICE)
        assert status is not None
        assert status.status == "unhealthy"
        assert "Connection failed" in str(status.error)

@pytest.mark.asyncio
async def test_service_deregistration(service_registry):
    """Test service deregistration."""
    registration = ServiceRegistration(
        name=ServiceType.CHARACTER_SERVICE,
        url="http://character-service:8000",
        health_check="/health",
        version="1.0.0",
        capabilities=[MessageType.CHARACTER_CREATED]
    )
    await service_registry.register_service(registration)
    
    # Deregister service
    assert await service_registry.deregister_service(ServiceType.CHARACTER_SERVICE)
    
    # Verify service is gone
    service = await service_registry.get_service(ServiceType.CHARACTER_SERVICE)
    assert service is None

@pytest.mark.asyncio
async def test_service_update(service_registry):
    """Test service registration update."""
    initial_registration = ServiceRegistration(
        name=ServiceType.CHARACTER_SERVICE,
        url="http://character-service:8000",
        health_check="/health",
        version="1.0.0",
        capabilities=[MessageType.CHARACTER_CREATED]
    )
    await service_registry.register_service(initial_registration)
    
    # Update registration
    updated_registration = ServiceRegistration(
        name=ServiceType.CHARACTER_SERVICE,
        url="http://character-service:8001",  # New port
        health_check="/health",
        version="1.1.0",  # New version
        capabilities=[
            MessageType.CHARACTER_CREATED,
            MessageType.CHARACTER_UPDATED  # Added capability
        ]
    )
    assert await service_registry.register_service(updated_registration)
    
    # Verify update
    service = await service_registry.get_service(ServiceType.CHARACTER_SERVICE)
    assert service is not None
    assert service.url == "http://character-service:8001"
    assert service.version == "1.1.0"
    assert MessageType.CHARACTER_UPDATED in service.capabilities

@pytest.mark.asyncio
async def test_invalid_registration(service_registry):
    """Test registration with invalid data."""
    # Test missing required fields
    invalid_registration = ServiceRegistration(
        name=ServiceType.CHARACTER_SERVICE,
        url="",  # Invalid URL
        health_check="/health",
        version="1.0.0",
        capabilities=[MessageType.CHARACTER_CREATED]
    )
    
    # Should fail registration
    assert not await service_registry.register_service(invalid_registration)
    
    # Service should not be registered
    service = await service_registry.get_service(ServiceType.CHARACTER_SERVICE)
    assert service is None
