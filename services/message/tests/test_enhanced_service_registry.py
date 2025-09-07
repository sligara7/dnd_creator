"""
Tests for Enhanced Service Registry

Comprehensive test suite for service discovery, load balancing, and health monitoring.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from src.enhanced_service_registry import (
    EnhancedServiceRegistry,
    ServiceInstance,
    ServiceHealthStatus,
    LoadBalancingStrategy,
    ServiceDependency
)
from src.models import ServiceType, MessageType
from src.config import Settings


@pytest.fixture
async def http_mock():
    """Mock HTTP client."""
    client = AsyncMock()
    response = AsyncMock()
    response.raise_for_status = MagicMock()
    client.get = AsyncMock(return_value=response)
    client.aclose = AsyncMock()
    return client


@pytest.fixture
async def registry(http_mock):
    """Create service registry with mocked HTTP client."""
    settings = Settings()
    registry = EnhancedServiceRegistry(settings)
    registry.http_client = http_mock
    
    # Start without background tasks to avoid timing issues in tests
    registry._health_checker_task = None
    registry._dependency_checker_task = None
    
    yield registry
    
    await registry.shutdown()


@pytest.fixture
def sample_instance():
    """Create a sample service instance."""
    return ServiceInstance(
        service_type=ServiceType.CHARACTER_SERVICE,
        instance_id="char-001",
        url="http://localhost:8000",
        health_check="/health",
        version="1.0.0",
        capabilities=[
            MessageType.CHARACTER_CREATED,
            MessageType.CHARACTER_UPDATED,
            MessageType.CHARACTER_DELETED
        ],
        weight=1.0
    )


class TestServiceInstance:
    """Test ServiceInstance data class."""
    
    def test_service_instance_creation(self):
        """Test creating a service instance."""
        instance = ServiceInstance(
            service_type=ServiceType.CHARACTER_SERVICE,
            instance_id="test-001",
            url="http://localhost:8000",
            health_check="/health",
            version="1.0.0",
            capabilities=[MessageType.CHARACTER_CREATED]
        )
        
        assert instance.service_type == ServiceType.CHARACTER_SERVICE
        assert instance.instance_id == "test-001"
        assert instance.health_status == ServiceHealthStatus.UNKNOWN
        assert instance.active_connections == 0
    
    def test_health_score_calculation(self):
        """Test health score calculation."""
        instance = ServiceInstance(
            service_type=ServiceType.CHARACTER_SERVICE,
            instance_id="test-001",
            url="http://localhost:8000",
            health_check="/health",
            version="1.0.0",
            capabilities=[]
        )
        
        # Healthy instance
        instance.health_status = ServiceHealthStatus.HEALTHY
        assert instance.health_score == 1.0
        
        # Degraded instance
        instance.health_status = ServiceHealthStatus.DEGRADED
        assert instance.health_score == 0.5
        
        # Unhealthy instance
        instance.health_status = ServiceHealthStatus.UNHEALTHY
        assert instance.health_score == 0.0
        
        # Healthy with failures
        instance.health_status = ServiceHealthStatus.HEALTHY
        instance.total_requests = 100
        instance.failed_requests = 10
        assert 0.89 < instance.health_score < 0.91  # ~0.9
        
        # Healthy with high latency
        instance.failed_requests = 0
        instance.average_latency = 2.0  # 2 seconds
        assert instance.health_score == 0.5


class TestEnhancedServiceRegistry:
    """Test EnhancedServiceRegistry functionality."""
    
    @pytest.mark.asyncio
    async def test_initialization(self, http_mock):
        """Test registry initialization."""
        settings = Settings()
        registry = EnhancedServiceRegistry(settings)
        registry.http_client = http_mock
        
        await registry.initialize()
        
        assert registry._health_checker_task is not None
        assert registry._dependency_checker_task is not None
        
        await registry.shutdown()
    
    @pytest.mark.asyncio
    async def test_register_instance(self, registry, http_mock):
        """Test registering a service instance."""
        http_mock.get = AsyncMock(return_value=AsyncMock(raise_for_status=MagicMock()))
        
        success = await registry.register_instance(
            service_type=ServiceType.CHARACTER_SERVICE,
            instance_id="char-001",
            url="http://localhost:8000",
            health_check="/health",
            version="1.0.0",
            capabilities=[MessageType.CHARACTER_CREATED],
            weight=1.5
        )
        
        assert success is True
        assert len(registry.instances[ServiceType.CHARACTER_SERVICE]) == 1
        
        instance = registry.instances[ServiceType.CHARACTER_SERVICE][0]
        assert instance.instance_id == "char-001"
        assert instance.weight == 1.5
    
    @pytest.mark.asyncio
    async def test_register_duplicate_instance(self, registry, sample_instance, http_mock):
        """Test updating an existing instance."""
        http_mock.get = AsyncMock(return_value=AsyncMock(raise_for_status=MagicMock()))
        
        # Register first time
        await registry.register_instance(
            service_type=sample_instance.service_type,
            instance_id=sample_instance.instance_id,
            url=sample_instance.url,
            health_check=sample_instance.health_check,
            version="1.0.0",
            capabilities=sample_instance.capabilities
        )
        
        # Register again with updated version
        await registry.register_instance(
            service_type=sample_instance.service_type,
            instance_id=sample_instance.instance_id,
            url=sample_instance.url,
            health_check=sample_instance.health_check,
            version="2.0.0",
            capabilities=sample_instance.capabilities
        )
        
        # Should still have only one instance
        assert len(registry.instances[ServiceType.CHARACTER_SERVICE]) == 1
        
        # Version should be updated
        instance = registry.instances[ServiceType.CHARACTER_SERVICE][0]
        assert instance.version == "2.0.0"
    
    @pytest.mark.asyncio
    async def test_deregister_instance(self, registry, sample_instance):
        """Test deregistering a service instance."""
        # Add instance directly
        registry.instances[sample_instance.service_type].append(sample_instance)
        
        success = await registry.deregister_instance(
            sample_instance.service_type,
            sample_instance.instance_id
        )
        
        assert success is True
        assert len(registry.instances[sample_instance.service_type]) == 0
    
    @pytest.mark.asyncio
    async def test_get_instance_with_load_balancing(self, registry):
        """Test getting instance with different load balancing strategies."""
        # Create multiple instances
        instances = [
            ServiceInstance(
                service_type=ServiceType.CHARACTER_SERVICE,
                instance_id=f"char-{i:03d}",
                url=f"http://localhost:800{i}",
                health_check="/health",
                version="1.0.0",
                capabilities=[MessageType.CHARACTER_CREATED],
                weight=float(i + 1),
                health_status=ServiceHealthStatus.HEALTHY
            )
            for i in range(3)
        ]
        
        registry.instances[ServiceType.CHARACTER_SERVICE] = instances
        
        # Test round-robin
        registry.load_balancing_strategy = LoadBalancingStrategy.ROUND_ROBIN
        first = await registry.get_instance(ServiceType.CHARACTER_SERVICE)
        second = await registry.get_instance(ServiceType.CHARACTER_SERVICE)
        third = await registry.get_instance(ServiceType.CHARACTER_SERVICE)
        fourth = await registry.get_instance(ServiceType.CHARACTER_SERVICE)
        
        assert first.instance_id == "char-000"
        assert second.instance_id == "char-001"
        assert third.instance_id == "char-002"
        assert fourth.instance_id == "char-000"  # Wraps around
        
        # Test least connections
        registry.load_balancing_strategy = LoadBalancingStrategy.LEAST_CONNECTIONS
        instances[1].active_connections = 5
        instances[2].active_connections = 2
        
        selected = await registry.get_instance(ServiceType.CHARACTER_SERVICE)
        assert selected.instance_id == "char-000"  # Has 0 connections
    
    @pytest.mark.asyncio
    async def test_get_instance_with_capability_filter(self, registry):
        """Test getting instance filtered by capability."""
        # Create instances with different capabilities
        instance1 = ServiceInstance(
            service_type=ServiceType.CHARACTER_SERVICE,
            instance_id="char-001",
            url="http://localhost:8001",
            health_check="/health",
            version="1.0.0",
            capabilities=[MessageType.CHARACTER_CREATED],
            health_status=ServiceHealthStatus.HEALTHY
        )
        
        instance2 = ServiceInstance(
            service_type=ServiceType.CHARACTER_SERVICE,
            instance_id="char-002",
            url="http://localhost:8002",
            health_check="/health",
            version="1.0.0",
            capabilities=[MessageType.CHARACTER_UPDATED, MessageType.CHARACTER_DELETED],
            health_status=ServiceHealthStatus.HEALTHY
        )
        
        registry.instances[ServiceType.CHARACTER_SERVICE] = [instance1, instance2]
        
        # Get instance that supports CHARACTER_UPDATED
        selected = await registry.get_instance(
            ServiceType.CHARACTER_SERVICE,
            message_type=MessageType.CHARACTER_UPDATED
        )
        
        assert selected.instance_id == "char-002"
        
        # Get instance that supports CHARACTER_CREATED
        selected = await registry.get_instance(
            ServiceType.CHARACTER_SERVICE,
            message_type=MessageType.CHARACTER_CREATED
        )
        
        assert selected.instance_id == "char-001"
    
    @pytest.mark.asyncio
    async def test_get_all_instances(self, registry):
        """Test getting all instances of a service."""
        instances = [
            ServiceInstance(
                service_type=ServiceType.CHARACTER_SERVICE,
                instance_id=f"char-{i:03d}",
                url=f"http://localhost:800{i}",
                health_check="/health",
                version="1.0.0",
                capabilities=[],
                health_status=status
            )
            for i, status in enumerate([
                ServiceHealthStatus.HEALTHY,
                ServiceHealthStatus.DEGRADED,
                ServiceHealthStatus.UNHEALTHY
            ])
        ]
        
        registry.instances[ServiceType.CHARACTER_SERVICE] = instances
        
        # Get all instances
        all_instances = await registry.get_all_instances(
            ServiceType.CHARACTER_SERVICE,
            healthy_only=False
        )
        assert len(all_instances) == 3
        
        # Get only healthy instances
        healthy_instances = await registry.get_all_instances(
            ServiceType.CHARACTER_SERVICE,
            healthy_only=True
        )
        assert len(healthy_instances) == 2  # Healthy and degraded


class TestServiceDependencies:
    """Test service dependency management."""
    
    @pytest.mark.asyncio
    async def test_add_dependency(self, registry):
        """Test adding a service dependency."""
        await registry.add_dependency(
            dependent_service=ServiceType.CHARACTER_SERVICE,
            required_service=ServiceType.RULES_SERVICE,
            is_critical=True,
            minimum_instances=2,
            preferred_version="1.0.0"
        )
        
        assert len(registry.dependencies) == 1
        dep = registry.dependencies[0]
        assert dep.dependent_service == ServiceType.CHARACTER_SERVICE
        assert dep.required_service == ServiceType.RULES_SERVICE
        assert dep.is_critical is True
        assert dep.minimum_instances == 2
    
    @pytest.mark.asyncio
    async def test_check_dependencies_satisfied(self, registry):
        """Test checking satisfied dependencies."""
        # Add dependency
        await registry.add_dependency(
            dependent_service=ServiceType.CHARACTER_SERVICE,
            required_service=ServiceType.RULES_SERVICE,
            is_critical=True,
            minimum_instances=1
        )
        
        # Add required service instance
        registry.instances[ServiceType.RULES_SERVICE] = [
            ServiceInstance(
                service_type=ServiceType.RULES_SERVICE,
                instance_id="rules-001",
                url="http://localhost:8001",
                health_check="/health",
                version="1.0.0",
                capabilities=[],
                health_status=ServiceHealthStatus.HEALTHY
            )
        ]
        
        satisfied, issues = await registry.check_dependencies(ServiceType.CHARACTER_SERVICE)
        
        assert satisfied is True
        assert len(issues) == 0
    
    @pytest.mark.asyncio
    async def test_check_dependencies_not_satisfied(self, registry):
        """Test checking unsatisfied dependencies."""
        # Add dependency requiring 2 instances
        await registry.add_dependency(
            dependent_service=ServiceType.CHARACTER_SERVICE,
            required_service=ServiceType.RULES_SERVICE,
            is_critical=True,
            minimum_instances=2
        )
        
        # Add only 1 instance
        registry.instances[ServiceType.RULES_SERVICE] = [
            ServiceInstance(
                service_type=ServiceType.RULES_SERVICE,
                instance_id="rules-001",
                url="http://localhost:8001",
                health_check="/health",
                version="1.0.0",
                capabilities=[],
                health_status=ServiceHealthStatus.HEALTHY
            )
        ]
        
        satisfied, issues = await registry.check_dependencies(ServiceType.CHARACTER_SERVICE)
        
        assert satisfied is False
        assert len(issues) == 1
        assert "Requires 2 instances" in issues[0]


class TestHealthMonitoring:
    """Test health monitoring functionality."""
    
    @pytest.mark.asyncio
    async def test_check_instance_health_success(self, registry, sample_instance, http_mock):
        """Test successful health check."""
        http_mock.get = AsyncMock(return_value=AsyncMock(raise_for_status=MagicMock()))
        
        success = await registry._check_instance_health(sample_instance)
        
        assert success is True
        assert sample_instance.last_health_check is not None
        
        # After enough successful checks, should be healthy
        registry.health_check_history[sample_instance.instance_id] = [True, True]
        await registry._check_instance_health(sample_instance)
        
        assert sample_instance.health_status == ServiceHealthStatus.HEALTHY
    
    @pytest.mark.asyncio
    async def test_check_instance_health_failure(self, registry, sample_instance, http_mock):
        """Test failed health check."""
        http_mock.get = AsyncMock(side_effect=Exception("Connection error"))
        
        success = await registry._check_instance_health(sample_instance)
        
        assert success is False
        assert sample_instance.failed_requests == 1
        
        # After enough failures, should be unhealthy
        registry.health_check_history[sample_instance.instance_id] = [False, False, False]
        await registry._check_instance_health(sample_instance)
        
        assert sample_instance.health_status == ServiceHealthStatus.UNHEALTHY
    
    @pytest.mark.asyncio
    async def test_health_status_transitions(self, registry, sample_instance, http_mock):
        """Test health status transitions."""
        sample_instance.health_status = ServiceHealthStatus.HEALTHY
        
        # Single failure should degrade
        http_mock.get = AsyncMock(side_effect=Exception("Timeout"))
        registry.health_check_history[sample_instance.instance_id] = [True, True]
        
        await registry._check_instance_health(sample_instance)
        
        assert sample_instance.health_status == ServiceHealthStatus.DEGRADED
        
        # Recovery should return to healthy
        http_mock.get = AsyncMock(return_value=AsyncMock(raise_for_status=MagicMock()))
        registry.health_check_history[sample_instance.instance_id] = [True]
        
        await registry._check_instance_health(sample_instance)
        await registry._check_instance_health(sample_instance)
        
        assert sample_instance.health_status == ServiceHealthStatus.HEALTHY


class TestLoadBalancingStrategies:
    """Test different load balancing strategies."""
    
    @pytest.mark.asyncio
    async def test_health_aware_strategy(self, registry):
        """Test health-aware load balancing."""
        instances = [
            ServiceInstance(
                service_type=ServiceType.CHARACTER_SERVICE,
                instance_id=f"char-{i:03d}",
                url=f"http://localhost:800{i}",
                health_check="/health",
                version="1.0.0",
                capabilities=[],
                health_status=status,
                active_connections=connections
            )
            for i, (status, connections) in enumerate([
                (ServiceHealthStatus.HEALTHY, 10),
                (ServiceHealthStatus.HEALTHY, 5),
                (ServiceHealthStatus.DEGRADED, 2)
            ])
        ]
        
        registry.load_balancing_strategy = LoadBalancingStrategy.HEALTH_AWARE
        
        # Should select healthy instance with fewer connections
        selected = await registry._select_instance(
            instances,
            ServiceType.CHARACTER_SERVICE
        )
        
        assert selected.instance_id == "char-001"  # Healthy with 5 connections
    
    @pytest.mark.asyncio
    async def test_weighted_strategy(self, registry):
        """Test weighted load balancing."""
        instances = [
            ServiceInstance(
                service_type=ServiceType.CHARACTER_SERVICE,
                instance_id=f"char-{i:03d}",
                url=f"http://localhost:800{i}",
                health_check="/health",
                version="1.0.0",
                capabilities=[],
                weight=weight,
                health_status=ServiceHealthStatus.HEALTHY
            )
            for i, weight in enumerate([1.0, 2.0, 1.0])
        ]
        
        registry.load_balancing_strategy = LoadBalancingStrategy.WEIGHTED
        
        # With weighted random, instance 2 should be selected more often
        selections = []
        for _ in range(100):
            selected = await registry._select_instance(
                instances.copy(),  # Use copy to avoid connection tracking
                ServiceType.CHARACTER_SERVICE
            )
            selections.append(selected.instance_id)
        
        # Instance 2 (weight=2.0) should be selected roughly twice as often
        count_1 = selections.count("char-001")
        assert 35 < count_1 < 65  # Should be around 50


class TestMetrics:
    """Test metrics collection."""
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, registry):
        """Test getting registry metrics."""
        # Add some instances
        for i in range(3):
            instance = ServiceInstance(
                service_type=ServiceType.CHARACTER_SERVICE,
                instance_id=f"char-{i:03d}",
                url=f"http://localhost:800{i}",
                health_check="/health",
                version="1.0.0",
                capabilities=[],
                health_status=ServiceHealthStatus.HEALTHY if i < 2 else ServiceHealthStatus.UNHEALTHY,
                total_requests=100 * (i + 1),
                failed_requests=10 * i,
                active_connections=i
            )
            registry.instances[ServiceType.CHARACTER_SERVICE].append(instance)
        
        metrics = await registry.get_metrics()
        
        assert metrics["total_instances"] == 3
        assert metrics["load_balancing_strategy"] == LoadBalancingStrategy.HEALTH_AWARE.value
        
        service_metrics = metrics["services"]["character-service"]
        assert service_metrics["total_instances"] == 3
        assert service_metrics["healthy_instances"] == 2
        assert service_metrics["unhealthy_instances"] == 1
        assert service_metrics["total_requests"] == 600  # 100 + 200 + 300
        assert service_metrics["failed_requests"] == 30   # 0 + 10 + 20


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.mark.asyncio
    async def test_get_instance_no_instances(self, registry):
        """Test getting instance when none are registered."""
        instance = await registry.get_instance(ServiceType.CHARACTER_SERVICE)
        assert instance is None
    
    @pytest.mark.asyncio
    async def test_get_instance_all_unhealthy(self, registry):
        """Test getting instance when all are unhealthy."""
        instances = [
            ServiceInstance(
                service_type=ServiceType.CHARACTER_SERVICE,
                instance_id=f"char-{i:03d}",
                url=f"http://localhost:800{i}",
                health_check="/health",
                version="1.0.0",
                capabilities=[],
                health_status=ServiceHealthStatus.UNHEALTHY
            )
            for i in range(3)
        ]
        
        registry.instances[ServiceType.CHARACTER_SERVICE] = instances
        
        instance = await registry.get_instance(ServiceType.CHARACTER_SERVICE)
        assert instance is None
    
    @pytest.mark.asyncio
    async def test_release_instance(self, registry):
        """Test releasing an instance after use."""
        instance = ServiceInstance(
            service_type=ServiceType.CHARACTER_SERVICE,
            instance_id="char-001",
            url="http://localhost:8000",
            health_check="/health",
            version="1.0.0",
            capabilities=[],
            active_connections=5
        )
        
        await registry.release_instance(instance)
        
        assert instance.active_connections == 4
        
        # Test releasing with no connections
        instance.active_connections = 0
        await registry.release_instance(instance)
        
        assert instance.active_connections == 0  # Should not go negative
