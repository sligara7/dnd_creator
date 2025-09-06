import pytest
from datetime import datetime

from api_gateway.services.discovery import ServiceDiscovery, ServiceRegistration, ServiceEndpoint

pytestmark = pytest.mark.asyncio

@pytest.fixture
def test_service():
    """Create test service registration."""
    return ServiceRegistration(
        name="test-service",
        status="healthy",
        endpoints=[
            ServiceEndpoint(path="/api/test", methods=["GET", "POST"])
        ],
        version="1.0.0"
    )

async def test_register_service(test_service):
    """Test service registration."""
    discovery = ServiceDiscovery()
    result = await discovery.register_service(test_service)
    
    assert result is True
    assert discovery.services["test-service"] == test_service

async def test_unregister_service(test_service):
    """Test service unregistration."""
    discovery = ServiceDiscovery()
    await discovery.register_service(test_service)
    
    result = await discovery.unregister_service("test-service")
    assert result is True
    assert "test-service" not in discovery.services

async def test_get_service(test_service):
    """Test getting service details."""
    discovery = ServiceDiscovery()
    await discovery.register_service(test_service)
    
    service = await discovery.get_service("test-service")
    assert service == test_service

async def test_list_services(test_service):
    """Test listing all services."""
    discovery = ServiceDiscovery()
    await discovery.register_service(test_service)
    
    services = await discovery.list_services()
    assert len(services) == 1
    assert services[0] == test_service

async def test_update_service_status(test_service):
    """Test updating service status."""
    discovery = ServiceDiscovery()
    await discovery.register_service(test_service)
    
    result = await discovery.update_service_status("test-service", "degraded")
    assert result is True
    assert discovery.services["test-service"].status == "degraded"

async def test_get_service_health(test_service):
    """Test getting service health status."""
    discovery = ServiceDiscovery()
    await discovery.register_service(test_service)
    
    health = await discovery.get_service_health("test-service")
    assert health["service"] == "test-service"
    assert health["status"] == "healthy"
    assert "last_check" in health
    assert health["version"] == "1.0.0"

async def test_get_system_health(test_service):
    """Test getting system health status."""
    discovery = ServiceDiscovery()
    await discovery.register_service(test_service)
    
    # Add an unhealthy service
    unhealthy_service = ServiceRegistration(
        name="unhealthy-service",
        status="unhealthy",
        endpoints=[],
        version="1.0.0"
    )
    await discovery.register_service(unhealthy_service)
    
    health = await discovery.get_system_health()
    assert health["status"] == "unhealthy"
    assert len(health["services"]) == 2
    assert health["services"]["test-service"] == "healthy"
    assert health["services"]["unhealthy-service"] == "unhealthy"
