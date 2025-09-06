from datetime import datetime
from typing import Dict, List, Optional

from fastapi import HTTPException
from pydantic import BaseModel


class ServiceEndpoint(BaseModel):
    path: str
    methods: List[str]
    rate_limit: Optional[int] = None

class ServiceRegistration(BaseModel):
    name: str
    status: str
    endpoints: List[ServiceEndpoint]
    version: str
    last_seen: datetime = datetime.utcnow()

class ServiceDiscovery:
    def __init__(self):
        self.services: Dict[str, ServiceRegistration] = {}

    async def register_service(self, registration: ServiceRegistration) -> bool:
        """Register a service with the discovery system."""
        registration.last_seen = datetime.utcnow()
        self.services[registration.name] = registration
        return True

    async def unregister_service(self, service_name: str) -> bool:
        """Unregister a service."""
        if service_name in self.services:
            del self.services[service_name]
            return True
        return False

    async def get_service(self, service_name: str) -> ServiceRegistration:
        """Get service details by name."""
        service = self.services.get(service_name)
        if not service:
            raise HTTPException(
                status_code=404,
                detail=f"Service {service_name} not found"
            )
        return service

    async def list_services(self) -> List[ServiceRegistration]:
        """Get a list of all registered services."""
        return list(self.services.values())

    async def update_service_status(self, service_name: str, status: str) -> bool:
        """Update service health status."""
        if service_name not in self.services:
            return False
        
        self.services[service_name].status = status
        self.services[service_name].last_seen = datetime.utcnow()
        return True

    async def get_service_health(self, service_name: str) -> Dict:
        """Get detailed health status for a service."""
        service = await self.get_service(service_name)
        return {
            "service": service.name,
            "status": service.status,
            "last_check": service.last_seen.isoformat(),
            "version": service.version
        }

    async def get_system_health(self) -> Dict:
        """Get overall system health status."""
        services_health = {
            service.name: service.status 
            for service in self.services.values()
        }
        
        # Consider system healthy if all services are healthy
        system_status = "healthy"
        if any(status == "unhealthy" for status in services_health.values()):
            system_status = "unhealthy"
        elif any(status == "degraded" for status in services_health.values()):
            system_status = "degraded"
            
        return {
            "status": system_status,
            "services": services_health
        }
