"""
Enhanced Service Registry with Load Balancing

Provides advanced service discovery, health monitoring, and load balancing.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
from dataclasses import dataclass, field
import structlog
import httpx
from collections import defaultdict
import random

from .config import Settings
from .models import ServiceType, ServiceRegistration, ServiceStatus, MessageType

logger = structlog.get_logger()


class ServiceHealthStatus(str, Enum):
    """Service health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class LoadBalancingStrategy(str, Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"
    RANDOM = "random"
    HEALTH_AWARE = "health_aware"


@dataclass
class ServiceInstance:
    """Represents a service instance."""
    service_type: ServiceType
    instance_id: str
    url: str
    health_check: str
    version: str
    capabilities: List[MessageType]
    weight: float = 1.0
    active_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    average_latency: float = 0.0
    health_status: ServiceHealthStatus = ServiceHealthStatus.UNKNOWN
    last_health_check: Optional[datetime] = None
    metadata: Dict[str, any] = field(default_factory=dict)
    
    @property
    def health_score(self) -> float:
        """Calculate health score (0-1)."""
        if self.health_status == ServiceHealthStatus.HEALTHY:
            base_score = 1.0
        elif self.health_status == ServiceHealthStatus.DEGRADED:
            base_score = 0.5
        else:
            return 0.0
        
        # Adjust for failure rate
        failure_rate = self.failed_requests / max(1, self.total_requests)
        base_score *= (1 - failure_rate)
        
        # Adjust for latency (penalize if > 1 second)
        if self.average_latency > 1.0:
            base_score *= (1.0 / self.average_latency)
        
        return min(1.0, max(0.0, base_score))


@dataclass
class ServiceDependency:
    """Represents a service dependency."""
    dependent_service: ServiceType
    required_service: ServiceType
    is_critical: bool = True
    minimum_instances: int = 1
    preferred_version: Optional[str] = None


class EnhancedServiceRegistry:
    """
    Enhanced service registry with advanced features.
    
    Features:
    - Multi-instance service support
    - Load balancing strategies
    - Health-aware routing
    - Service dependency tracking
    - Automatic failover
    - Circuit breaker integration
    - Service versioning
    """
    
    def __init__(self, settings: Settings):
        """Initialize enhanced service registry."""
        self.settings = settings
        self.instances: Dict[ServiceType, List[ServiceInstance]] = defaultdict(list)
        self.dependencies: List[ServiceDependency] = []
        self.load_balancing_strategy = LoadBalancingStrategy.HEALTH_AWARE
        self.round_robin_counters: Dict[ServiceType, int] = defaultdict(int)
        
        # Health check configuration
        self.health_check_interval = settings.service_check_interval
        self.health_check_timeout = settings.service_timeout
        self.unhealthy_threshold = 3  # Consecutive failures before marking unhealthy
        self.healthy_threshold = 2    # Consecutive successes before marking healthy
        
        # Tracking
        self.health_check_history: Dict[str, List[bool]] = defaultdict(list)
        self.http_client = httpx.AsyncClient(timeout=self.health_check_timeout)
        
        # Background tasks
        self._health_checker_task = None
        self._dependency_checker_task = None
    
    async def initialize(self):
        """Initialize registry and start background tasks."""
        # Start health checker
        self._health_checker_task = asyncio.create_task(self._health_check_loop())
        
        # Start dependency checker
        self._dependency_checker_task = asyncio.create_task(self._dependency_check_loop())
        
        logger.info("enhanced_service_registry_initialized")
    
    async def shutdown(self):
        """Shutdown registry."""
        if self._health_checker_task:
            self._health_checker_task.cancel()
            try:
                await self._health_checker_task
            except asyncio.CancelledError:
                pass
        
        if self._dependency_checker_task:
            self._dependency_checker_task.cancel()
            try:
                await self._dependency_checker_task
            except asyncio.CancelledError:
                pass
        
        if self.http_client:
            await self.http_client.aclose()
        
        logger.info("enhanced_service_registry_shutdown")
    
    async def register_instance(self,
                               service_type: ServiceType,
                               instance_id: str,
                               url: str,
                               health_check: str,
                               version: str,
                               capabilities: List[MessageType],
                               weight: float = 1.0,
                               metadata: Optional[Dict[str, any]] = None) -> bool:
        """
        Register a service instance.
        
        Args:
            service_type: Type of service
            instance_id: Unique instance identifier
            url: Service URL
            health_check: Health check endpoint
            version: Service version
            capabilities: Supported message types
            weight: Weight for load balancing
            metadata: Optional metadata
        
        Returns:
            True if registration successful
        """
        instance = ServiceInstance(
            service_type=service_type,
            instance_id=instance_id,
            url=url,
            health_check=health_check,
            version=version,
            capabilities=capabilities,
            weight=weight,
            metadata=metadata or {}
        )
        
        # Check if instance already exists
        existing = self._find_instance(service_type, instance_id)
        if existing:
            # Update existing instance
            existing.url = url
            existing.health_check = health_check
            existing.version = version
            existing.capabilities = capabilities
            existing.weight = weight
            existing.metadata = metadata or {}
        else:
            # Add new instance
            self.instances[service_type].append(instance)
        
        # Perform initial health check
        await self._check_instance_health(instance)
        
        logger.info("service_instance_registered",
                   service=service_type.value,
                   instance_id=instance_id,
                   version=version)
        
        return True
    
    async def deregister_instance(self,
                                 service_type: ServiceType,
                                 instance_id: str) -> bool:
        """
        Deregister a service instance.
        
        Args:
            service_type: Type of service
            instance_id: Instance to deregister
        
        Returns:
            True if deregistration successful
        """
        instances = self.instances.get(service_type, [])
        original_count = len(instances)
        
        self.instances[service_type] = [
            inst for inst in instances
            if inst.instance_id != instance_id
        ]
        
        if len(self.instances[service_type]) < original_count:
            logger.info("service_instance_deregistered",
                       service=service_type.value,
                       instance_id=instance_id)
            return True
        
        return False
    
    async def get_instance(self,
                          service_type: ServiceType,
                          message_type: Optional[MessageType] = None,
                          prefer_version: Optional[str] = None) -> Optional[ServiceInstance]:
        """
        Get a service instance using load balancing.
        
        Args:
            service_type: Type of service
            message_type: Optional message type to filter by capability
            prefer_version: Preferred version
        
        Returns:
            Selected service instance or None
        """
        # Get eligible instances
        instances = await self._get_eligible_instances(
            service_type,
            message_type,
            prefer_version
        )
        
        if not instances:
            return None
        
        # Select instance based on load balancing strategy
        return await self._select_instance(instances, service_type)
    
    async def get_all_instances(self,
                               service_type: ServiceType,
                               healthy_only: bool = True) -> List[ServiceInstance]:
        """
        Get all instances of a service.
        
        Args:
            service_type: Type of service
            healthy_only: Only return healthy instances
        
        Returns:
            List of service instances
        """
        instances = self.instances.get(service_type, [])
        
        if healthy_only:
            return [
                inst for inst in instances
                if inst.health_status in [ServiceHealthStatus.HEALTHY, ServiceHealthStatus.DEGRADED]
            ]
        
        return instances.copy()
    
    async def add_dependency(self,
                            dependent_service: ServiceType,
                            required_service: ServiceType,
                            is_critical: bool = True,
                            minimum_instances: int = 1,
                            preferred_version: Optional[str] = None):
        """
        Add a service dependency.
        
        Args:
            dependent_service: Service that has the dependency
            required_service: Service that is required
            is_critical: Whether dependency is critical
            minimum_instances: Minimum required instances
            preferred_version: Preferred version of required service
        """
        dependency = ServiceDependency(
            dependent_service=dependent_service,
            required_service=required_service,
            is_critical=is_critical,
            minimum_instances=minimum_instances,
            preferred_version=preferred_version
        )
        
        self.dependencies.append(dependency)
        
        logger.info("service_dependency_added",
                   dependent=dependent_service.value,
                   required=required_service.value,
                   critical=is_critical)
    
    async def check_dependencies(self,
                                service_type: ServiceType) -> Tuple[bool, List[str]]:
        """
        Check if service dependencies are satisfied.
        
        Args:
            service_type: Service to check dependencies for
        
        Returns:
            Tuple of (dependencies_satisfied, list_of_issues)
        """
        issues = []
        all_satisfied = True
        
        for dep in self.dependencies:
            if dep.dependent_service != service_type:
                continue
            
            # Get healthy instances of required service
            instances = await self.get_all_instances(dep.required_service, healthy_only=True)
            
            if len(instances) < dep.minimum_instances:
                issue = f"Requires {dep.minimum_instances} instances of {dep.required_service.value}, found {len(instances)}"
                issues.append(issue)
                
                if dep.is_critical:
                    all_satisfied = False
            
            # Check version if specified
            if dep.preferred_version and instances:
                matching_version = any(
                    inst.version == dep.preferred_version
                    for inst in instances
                )
                if not matching_version:
                    issue = f"Preferred version {dep.preferred_version} of {dep.required_service.value} not available"
                    issues.append(issue)
        
        return all_satisfied, issues
    
    async def set_load_balancing_strategy(self, strategy: LoadBalancingStrategy):
        """Set load balancing strategy."""
        self.load_balancing_strategy = strategy
        logger.info("load_balancing_strategy_set", strategy=strategy.value)
    
    def _find_instance(self,
                      service_type: ServiceType,
                      instance_id: str) -> Optional[ServiceInstance]:
        """Find a specific service instance."""
        for instance in self.instances.get(service_type, []):
            if instance.instance_id == instance_id:
                return instance
        return None
    
    async def _get_eligible_instances(self,
                                     service_type: ServiceType,
                                     message_type: Optional[MessageType],
                                     prefer_version: Optional[str]) -> List[ServiceInstance]:
        """Get eligible instances for a request."""
        instances = self.instances.get(service_type, [])
        
        # Filter by health
        eligible = [
            inst for inst in instances
            if inst.health_status in [ServiceHealthStatus.HEALTHY, ServiceHealthStatus.DEGRADED]
        ]
        
        # Filter by capability
        if message_type:
            eligible = [
                inst for inst in eligible
                if message_type in inst.capabilities
            ]
        
        # Sort by version preference
        if prefer_version:
            eligible.sort(
                key=lambda x: 0 if x.version == prefer_version else 1
            )
        
        return eligible
    
    async def _select_instance(self,
                              instances: List[ServiceInstance],
                              service_type: ServiceType) -> Optional[ServiceInstance]:
        """Select an instance based on load balancing strategy."""
        if not instances:
            return None
        
        if self.load_balancing_strategy == LoadBalancingStrategy.ROUND_ROBIN:
            index = self.round_robin_counters[service_type] % len(instances)
            self.round_robin_counters[service_type] += 1
            selected = instances[index]
        
        elif self.load_balancing_strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            selected = min(instances, key=lambda x: x.active_connections)
        
        elif self.load_balancing_strategy == LoadBalancingStrategy.WEIGHTED:
            # Weighted random selection
            weights = [inst.weight for inst in instances]
            selected = random.choices(instances, weights=weights)[0]
        
        elif self.load_balancing_strategy == LoadBalancingStrategy.RANDOM:
            selected = random.choice(instances)
        
        elif self.load_balancing_strategy == LoadBalancingStrategy.HEALTH_AWARE:
            # Select based on health score
            healthy_instances = [
                inst for inst in instances
                if inst.health_score > 0.5
            ]
            
            if healthy_instances:
                # Among healthy, choose least loaded
                selected = min(healthy_instances, key=lambda x: x.active_connections / max(1, x.weight))
            else:
                # Fall back to least degraded
                selected = max(instances, key=lambda x: x.health_score)
        
        else:
            selected = instances[0]
        
        # Track connection
        selected.active_connections += 1
        selected.total_requests += 1
        
        return selected
    
    async def release_instance(self, instance: ServiceInstance):
        """Release an instance after use."""
        if instance.active_connections > 0:
            instance.active_connections -= 1
    
    async def _check_instance_health(self, instance: ServiceInstance) -> bool:
        """Check health of a specific instance."""
        start_time = time.time()
        
        try:
            response = await self.http_client.get(f"{instance.url}{instance.health_check}")
            response.raise_for_status()
            
            # Update metrics
            latency = time.time() - start_time
            instance.average_latency = (
                instance.average_latency * 0.9 + latency * 0.1  # Exponential moving average
            )
            instance.last_health_check = datetime.utcnow()
            
            # Track success
            self._track_health_check(instance.instance_id, True)
            
            # Update status based on history
            history = self.health_check_history[instance.instance_id][-self.healthy_threshold:]
            if all(history) and len(history) >= self.healthy_threshold:
                instance.health_status = ServiceHealthStatus.HEALTHY
            
            return True
            
        except Exception as e:
            # Track failure
            self._track_health_check(instance.instance_id, False)
            instance.failed_requests += 1
            instance.last_health_check = datetime.utcnow()
            
            # Update status based on history
            history = self.health_check_history[instance.instance_id][-self.unhealthy_threshold:]
            if not any(history) and len(history) >= self.unhealthy_threshold:
                instance.health_status = ServiceHealthStatus.UNHEALTHY
                logger.warning("service_instance_unhealthy",
                             service=instance.service_type.value,
                             instance_id=instance.instance_id,
                             error=str(e))
            elif instance.health_status == ServiceHealthStatus.HEALTHY:
                instance.health_status = ServiceHealthStatus.DEGRADED
            
            return False
    
    def _track_health_check(self, instance_id: str, success: bool):
        """Track health check history."""
        history = self.health_check_history[instance_id]
        history.append(success)
        
        # Keep only recent history
        if len(history) > max(self.healthy_threshold, self.unhealthy_threshold) * 2:
            self.health_check_history[instance_id] = history[-10:]
    
    async def _health_check_loop(self):
        """Background task to check service health."""
        logger.info("health_check_loop_started")
        
        while True:
            try:
                # Check all instances
                for service_type, instances in self.instances.items():
                    for instance in instances:
                        await self._check_instance_health(instance)
                
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("health_check_loop_error", error=str(e))
                await asyncio.sleep(10)
        
        logger.info("health_check_loop_stopped")
    
    async def _dependency_check_loop(self):
        """Background task to check service dependencies."""
        logger.info("dependency_check_loop_started")
        
        while True:
            try:
                # Check dependencies for all services
                for service_type in ServiceType:
                    satisfied, issues = await self.check_dependencies(service_type)
                    
                    if not satisfied:
                        logger.warning("service_dependencies_not_satisfied",
                                     service=service_type.value,
                                     issues=issues)
                
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("dependency_check_loop_error", error=str(e))
                await asyncio.sleep(60)
        
        logger.info("dependency_check_loop_stopped")
    
    async def get_metrics(self) -> Dict[str, any]:
        """Get registry metrics."""
        metrics = {
            "total_instances": sum(len(instances) for instances in self.instances.values()),
            "services": {},
            "load_balancing_strategy": self.load_balancing_strategy.value,
            "dependencies": len(self.dependencies)
        }
        
        for service_type, instances in self.instances.items():
            service_metrics = {
                "total_instances": len(instances),
                "healthy_instances": len([i for i in instances if i.health_status == ServiceHealthStatus.HEALTHY]),
                "degraded_instances": len([i for i in instances if i.health_status == ServiceHealthStatus.DEGRADED]),
                "unhealthy_instances": len([i for i in instances if i.health_status == ServiceHealthStatus.UNHEALTHY]),
                "total_requests": sum(i.total_requests for i in instances),
                "failed_requests": sum(i.failed_requests for i in instances),
                "active_connections": sum(i.active_connections for i in instances),
                "average_latency": sum(i.average_latency for i in instances) / max(1, len(instances))
            }
            
            metrics["services"][service_type.value] = service_metrics
        
        return metrics
