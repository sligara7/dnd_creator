"""
Message Hub Service Registry

Manages service registration and health monitoring.
"""

import asyncio
import time
import structlog
import httpx
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from .config import Settings
from .models import ServiceType, ServiceRegistration, ServiceStatus

logger = structlog.get_logger()

class ServiceRegistry:
    """Registry for managing service registration and health."""
    
    def __init__(self, settings: Settings):
        """Initialize the service registry."""
        self.settings = settings
        self.services: Dict[ServiceType, ServiceRegistration] = {}
        self.status_cache: Dict[ServiceType, ServiceStatus] = {}
        self.http_client = httpx.AsyncClient(timeout=settings.service_timeout)
        
        # Start health check loop
        asyncio.create_task(self._health_check_loop())
    
async def register_service(self, registration: ServiceRegistration) -> bool:
        """Register a service in the registry.
        
        Args:
            registration: Service registration info
            
        Returns:
            bool: True if registration successful
        """
        try:
            # Basic validation
            if not registration.url or not registration.health_check:
                return False
            
            # Store service info
            self.services[registration.name] = registration
            
            logger.info("service_registered",
                      service=registration.name.value,
                      url=registration.url)
            return True
            
        except ValidationError:
            return False
        """Register a new service or update existing registration."""
        try:
            # Validate service is reachable
            status = await self._check_service_health(
                registration.name,
                registration.url,
                registration.health_check
            )
            
            if status.status != "healthy":
                raise ValueError(f"Service {registration.name} is not healthy: {status.error}")
            
            # Update registration
            self.services[registration.name] = registration
            self.status_cache[registration.name] = status
            
            logger.info("service_registered",
                       service=registration.name,
                       url=registration.url)
            
            return True
            
        except Exception as e:
            logger.error("service_registration_failed",
                        service=registration.name,
                        error=str(e))
            raise
    
    async def get_service(self, service_type: ServiceType) -> Optional[ServiceRegistration]:
        """Get registration information for a service."""
        return self.services.get(service_type)
    
    async def get_service_status(self, service_type: ServiceType) -> Optional[ServiceStatus]:
        """Get current status for a service."""
        return self.status_cache.get(service_type)
    
    async def get_all_services(self) -> Dict[ServiceType, ServiceStatus]:
        """Get status for all registered services."""
        return self.status_cache.copy()
    
    async def check_all_services(self) -> Dict[str, any]:
        """Check health of all registered services."""
        results = {
            "all_healthy": True,
            "healthy_services": [],
            "unhealthy_services": [],
            "timestamp": datetime.utcnow()
        }
        
        for service_type, registration in self.services.items():
            status = await self._check_service_health(
                service_type,
                registration.url,
                registration.health_check
            )
            
            if status.status == "healthy":
                results["healthy_services"].append(service_type)
            else:
                results["all_healthy"] = False
                results["unhealthy_services"].append({
                    "service": service_type,
                    "error": status.error
                })
        
        return results
    
    async def _check_service_health(self,
                                  service_type: ServiceType,
                                  url: str,
                                  health_check: str) -> ServiceStatus:
        """Check health of a specific service."""
        start_time = time.time()
        try:
            response = await self.http_client.get(f"{url}{health_check}")
            response.raise_for_status()
            
            return ServiceStatus(
                name=service_type,
                url=url,
                status="healthy",
                last_check=datetime.utcnow(),
                latency=time.time() - start_time
            )
            
        except Exception as e:
            return ServiceStatus(
                name=service_type,
                url=url,
                status="unhealthy",
                last_check=datetime.utcnow(),
                latency=time.time() - start_time,
                error=str(e)
            )
    
    async def _health_check_loop(self):
        """Continuous health check loop for all services."""
        while True:
            try:
                for service_type, registration in self.services.items():
                    status = await self._check_service_health(
                        service_type,
                        registration.url,
                        registration.health_check
                    )
                    self.status_cache[service_type] = status
                    
                    if status.status != "healthy":
                        logger.warning("service_unhealthy",
                                    service=service_type,
                                    error=status.error)
                
            except Exception as e:
                logger.error("health_check_loop_error", error=str(e))
            
            await asyncio.sleep(self.settings.service_check_interval)
