from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api_gateway.services.discovery import ServiceDiscovery, ServiceRegistration
from api_gateway.middleware.auth import APIKeyAuth

router = APIRouter(
    prefix="/discovery",
    tags=["service-discovery"],
    dependencies=[Depends(APIKeyAuth)]
)

# Initialize service discovery
service_discovery = ServiceDiscovery()

@router.post("/register", response_model=bool)
async def register_service(service: ServiceRegistration):
    """Register a service with the gateway."""
    return await service_discovery.register_service(service)

@router.delete("/services/{service_name}", response_model=bool)
async def unregister_service(service_name: str):
    """Unregister a service."""
    return await service_discovery.unregister_service(service_name)

@router.get("/services")
async def list_services():
    """Get list of all registered services."""
    return await service_discovery.list_services()

@router.get("/services/{service_name}")
async def get_service(service_name: str):
    """Get details for a specific service."""
    return await service_discovery.get_service(service_name)

@router.patch("/services/{service_name}/status")
async def update_service_status(service_name: str, status: str):
    """Update service health status."""
    return await service_discovery.update_service_status(service_name, status)

@router.get("/health")
async def get_system_health():
    """Get overall system health status."""
    return await service_discovery.get_system_health()

@router.get("/health/{service_name}")
async def get_service_health(service_name: str):
    """Get health status for a specific service."""
    return await service_discovery.get_service_health(service_name)
