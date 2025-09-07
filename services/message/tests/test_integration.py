"""
Integration Tests for Message Hub

Tests for components working together in realistic scenarios.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import aioredis

from src.retry_manager import RetryManager, RetryStatus
from src.priority_queue import PriorityQueueManager, MessagePriority
from src.enhanced_service_registry import (
    EnhancedServiceRegistry,
    ServiceHealthStatus,
    LoadBalancingStrategy
)
from src.models import ServiceMessage, ServiceType, MessageType
from src.config import Settings


class TestMessageFlowIntegration:
    """Test complete message flow through the system."""
    
    @pytest.mark.asyncio
    async def test_message_retry_with_priority(self):
        """Test message retry with priority queue integration."""
        settings = Settings()
        
        # Create mocked Redis
        redis_mock = AsyncMock()
        redis_mock.zadd = AsyncMock(return_value=1)
        redis_mock.zcard = AsyncMock(return_value=10)
        redis_mock.hset = AsyncMock(return_value=1)
        redis_mock.lpush = AsyncMock(return_value=1)
        redis_mock.close = AsyncMock()
        
        with patch('aioredis.from_url', return_value=redis_mock):
            # Initialize components
            retry_manager = RetryManager(settings)
            queue_manager = PriorityQueueManager(settings)
            
            await retry_manager.initialize()
            await queue_manager.initialize()
            
            # Create a message
            message = ServiceMessage(
                source=ServiceType.CHARACTER_SERVICE,
                destination=ServiceType.RULES_SERVICE,
                message_type=MessageType.CHARACTER_LEVEL_UP,
                correlation_id="test-123",
                payload={"character_id": "char-456", "new_level": 5}
            )
            
            # First attempt fails - schedule retry
            retry_record = await retry_manager.schedule_retry(
                message,
                "Connection timeout",
                attempt_count=0
            )
            
            # Message should be queued with HIGH priority
            priority = queue_manager._determine_priority(message)
            assert priority == MessagePriority.HIGH
            
            # Enqueue the retry
            success = await queue_manager.enqueue(
                message,
                priority=priority,
                deadline=retry_record.next_retry_at
            )
            assert success is True
            
            await retry_manager.shutdown()
            await queue_manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_service_registry_with_load_balancing(self):
        """Test service registry with health-aware load balancing."""
        settings = Settings()
        
        # Create registry
        registry = EnhancedServiceRegistry(settings)
        registry._health_checker_task = None  # Disable background tasks
        registry._dependency_checker_task = None
        
        # Mock HTTP client
        http_mock = AsyncMock()
        registry.http_client = http_mock
        
        # Register multiple instances with different health states
        for i in range(3):
            await registry.register_instance(
                service_type=ServiceType.CHARACTER_SERVICE,
                instance_id=f"char-{i:03d}",
                url=f"http://localhost:800{i}",
                health_check="/health",
                version="1.0.0",
                capabilities=[MessageType.CHARACTER_UPDATED],
                weight=1.0
            )
        
        # Set health states
        registry.instances[ServiceType.CHARACTER_SERVICE][0].health_status = ServiceHealthStatus.HEALTHY
        registry.instances[ServiceType.CHARACTER_SERVICE][1].health_status = ServiceHealthStatus.DEGRADED
        registry.instances[ServiceType.CHARACTER_SERVICE][2].health_status = ServiceHealthStatus.UNHEALTHY
        
        # Test health-aware selection
        registry.load_balancing_strategy = LoadBalancingStrategy.HEALTH_AWARE
        
        selected_instances = []
        for _ in range(10):
            instance = await registry.get_instance(
                ServiceType.CHARACTER_SERVICE,
                message_type=MessageType.CHARACTER_UPDATED
            )
            if instance:
                selected_instances.append(instance.instance_id)
                await registry.release_instance(instance)
        
        # Should mostly select the healthy instance
        healthy_count = selected_instances.count("char-000")
        assert healthy_count >= 7  # At least 70% should go to healthy instance
        
        await registry.shutdown()
    
    @pytest.mark.asyncio
    async def test_message_dead_letter_flow(self):
        """Test message flow to dead letter queue after max retries."""
        settings = Settings()
        
        redis_mock = AsyncMock()
        redis_mock.lpush = AsyncMock(return_value=1)
        redis_mock.hset = AsyncMock(return_value=1)
        redis_mock.lrange = AsyncMock(return_value=[])
        redis_mock.close = AsyncMock()
        
        with patch('aioredis.from_url', return_value=redis_mock):
            retry_manager = RetryManager(settings)
            await retry_manager.initialize()
            
            message = ServiceMessage(
                source=ServiceType.CHARACTER_SERVICE,
                destination=ServiceType.RULES_SERVICE,
                message_type=MessageType.CHARACTER_DELETED,
                correlation_id="delete-123",
                payload={"character_id": "char-789"}
            )
            
            # Simulate max retries
            record = await retry_manager.schedule_retry(
                message,
                "Persistent failure",
                attempt_count=retry_manager.max_attempts - 1
            )
            
            assert record.status == RetryStatus.DEAD_LETTER
            redis_mock.lpush.assert_called_once()  # Added to dead letter queue
            
            await retry_manager.shutdown()


class TestPriorityAndQuotaIntegration:
    """Test priority queue with service quotas."""
    
    @pytest.mark.asyncio
    async def test_service_quota_with_priority(self):
        """Test that service quotas are respected across priorities."""
        settings = Settings()
        
        redis_mock = AsyncMock()
        redis_mock.zadd = AsyncMock(return_value=1)
        redis_mock.zcard = AsyncMock(return_value=100)
        redis_mock.zrangebyscore = AsyncMock(return_value=[])
        redis_mock.close = AsyncMock()
        
        with patch('aioredis.from_url', return_value=redis_mock):
            queue_manager = PriorityQueueManager(settings)
            await queue_manager.initialize()
            
            # Set quota for CHARACTER_SERVICE
            await queue_manager.set_service_quota(ServiceType.CHARACTER_SERVICE, 5)
            
            # Create messages with different priorities
            messages = []
            for i in range(10):
                priority = MessagePriority.CRITICAL if i < 5 else MessagePriority.LOW
                message = ServiceMessage(
                    source=ServiceType.MESSAGE_HUB,
                    destination=ServiceType.CHARACTER_SERVICE,
                    message_type=MessageType.CHARACTER_UPDATED,
                    correlation_id=f"msg-{i}",
                    payload={"id": i}
                )
                
                success = await queue_manager.enqueue(message, priority=priority)
                assert success is True
            
            # Check quota enforcement
            processed = 0
            for _ in range(10):
                if await queue_manager._check_service_quota(ServiceType.CHARACTER_SERVICE):
                    processed += 1
            
            assert processed == 5  # Should respect quota
            
            await queue_manager.shutdown()


class TestHealthMonitoringIntegration:
    """Test health monitoring with service selection."""
    
    @pytest.mark.asyncio
    async def test_health_degradation_affects_selection(self):
        """Test that health degradation affects service selection."""
        settings = Settings()
        registry = EnhancedServiceRegistry(settings)
        
        # Mock HTTP client
        http_mock = AsyncMock()
        registry.http_client = http_mock
        registry._health_checker_task = None
        registry._dependency_checker_task = None
        
        # Register two healthy instances
        for i in range(2):
            await registry.register_instance(
                service_type=ServiceType.RULES_SERVICE,
                instance_id=f"rules-{i:03d}",
                url=f"http://localhost:900{i}",
                health_check="/health",
                version="1.0.0",
                capabilities=[MessageType.CHARACTER_UPDATED]
            )
            registry.instances[ServiceType.RULES_SERVICE][i].health_status = ServiceHealthStatus.HEALTHY
        
        # Initially both should be selected
        selections_before = []
        for _ in range(20):
            instance = await registry.get_instance(ServiceType.RULES_SERVICE)
            if instance:
                selections_before.append(instance.instance_id)
                await registry.release_instance(instance)
        
        # Both should be selected roughly equally
        assert "rules-000" in selections_before
        assert "rules-001" in selections_before
        
        # Degrade one instance
        registry.instances[ServiceType.RULES_SERVICE][1].health_status = ServiceHealthStatus.UNHEALTHY
        
        # Now only healthy instance should be selected
        selections_after = []
        for _ in range(10):
            instance = await registry.get_instance(ServiceType.RULES_SERVICE)
            if instance:
                selections_after.append(instance.instance_id)
                await registry.release_instance(instance)
        
        # Only healthy instance should be selected
        assert all(id == "rules-000" for id in selections_after)
        
        await registry.shutdown()


class TestEventReplayIntegration:
    """Test event replay functionality."""
    
    @pytest.mark.asyncio
    async def test_event_replay_with_retry(self):
        """Test replaying events that need retry."""
        from src.event_persistence import EnhancedEventStore, EventReplayMode
        
        settings = Settings()
        
        # Mock database engine
        with patch('src.event_persistence.create_async_engine'):
            with patch('src.event_persistence.sessionmaker'):
                event_store = EnhancedEventStore(settings)
                
                # Mock session factory
                session_mock = AsyncMock()
                session_mock.execute = AsyncMock()
                session_mock.add = MagicMock()
                session_mock.commit = AsyncMock()
                session_mock.begin = AsyncMock()
                session_mock.run_sync = AsyncMock()
                
                event_store.session_factory = AsyncMock(return_value=session_mock)
                
                # Test replay from beginning
                events_processed = []
                
                async def process_event(event):
                    events_processed.append(event)
                
                # Mock event retrieval
                mock_events = [
                    MagicMock(
                        event_id=f"evt-{i}",
                        event_type="character.updated",
                        sequence_number=i,
                        data={"id": i}
                    )
                    for i in range(5)
                ]
                
                session_mock.execute.return_value.scalars.return_value.all.return_value = mock_events[:3]
                
                # Replay events
                batch_count = 0
                async for batch in event_store.replay_events(
                    EventReplayMode.FROM_BEGINNING,
                    callback=process_event,
                    batch_size=3
                ):
                    batch_count += 1
                    if batch_count >= 1:  # Stop after first batch
                        break
                
                assert len(events_processed) == 3


class TestCircuitBreakerIntegration:
    """Test circuit breaker with message routing."""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_trips_on_failures(self):
        """Test that circuit breaker trips after repeated failures."""
        from src.circuit_breaker_manager import CircuitBreakerManager
        
        manager = CircuitBreakerManager()
        
        # Get circuit breaker for a specific route
        breaker = manager.get_circuit_breaker(
            source=ServiceType.CHARACTER_SERVICE,
            destination=ServiceType.RULES_SERVICE,
            operation="update"
        )
        
        # Simulate failures
        async def failing_operation():
            raise Exception("Service unavailable")
        
        # Should trip after threshold failures
        for _ in range(6):  # Default threshold is 5
            try:
                await breaker.call(failing_operation)
            except:
                pass
        
        # Circuit should be open
        assert breaker.current_state == "open"
        
        # Further calls should fail immediately
        from src.circuit_breaker import CircuitBreakerOpen
        with pytest.raises(CircuitBreakerOpen):
            await breaker.call(failing_operation)


class TestEndToEndMessageFlow:
    """Test complete end-to-end message flow."""
    
    @pytest.mark.asyncio
    async def test_complete_message_lifecycle(self):
        """Test complete message lifecycle from send to delivery."""
        settings = Settings()
        
        # Mock components
        redis_mock = AsyncMock()
        redis_mock.zadd = AsyncMock(return_value=1)
        redis_mock.zcard = AsyncMock(return_value=10)
        redis_mock.zrangebyscore = AsyncMock(return_value=[])
        redis_mock.hset = AsyncMock(return_value=1)
        redis_mock.hget = AsyncMock(return_value=None)
        redis_mock.close = AsyncMock()
        
        with patch('aioredis.from_url', return_value=redis_mock):
            # Initialize all components
            retry_manager = RetryManager(settings)
            queue_manager = PriorityQueueManager(settings)
            registry = EnhancedServiceRegistry(settings)
            
            # Disable background tasks
            registry._health_checker_task = None
            registry._dependency_checker_task = None
            registry.http_client = AsyncMock()
            
            await retry_manager.initialize()
            await queue_manager.initialize()
            
            # Register service
            await registry.register_instance(
                service_type=ServiceType.CHARACTER_SERVICE,
                instance_id="char-001",
                url="http://localhost:8000",
                health_check="/health",
                version="1.0.0",
                capabilities=[MessageType.CHARACTER_CREATED]
            )
            
            registry.instances[ServiceType.CHARACTER_SERVICE][0].health_status = ServiceHealthStatus.HEALTHY
            
            # Create and send message
            message = ServiceMessage(
                source=ServiceType.MESSAGE_HUB,
                destination=ServiceType.CHARACTER_SERVICE,
                message_type=MessageType.CHARACTER_CREATED,
                correlation_id="create-001",
                payload={"name": "Test Character", "class": "Wizard"}
            )
            
            # 1. Enqueue message
            priority = queue_manager._determine_priority(message)
            enqueued = await queue_manager.enqueue(message, priority=priority)
            assert enqueued is True
            
            # 2. Get target service instance
            instance = await registry.get_instance(
                ServiceType.CHARACTER_SERVICE,
                message_type=MessageType.CHARACTER_CREATED
            )
            assert instance is not None
            assert instance.instance_id == "char-001"
            
            # 3. Simulate delivery failure and retry
            retry_record = await retry_manager.schedule_retry(
                message,
                "Temporary failure",
                attempt_count=0
            )
            assert retry_record.status == RetryStatus.PENDING
            
            # 4. Mark as successful after retry
            await retry_manager.mark_success(message.correlation_id)
            
            # 5. Release service instance
            await registry.release_instance(instance)
            
            # Cleanup
            await retry_manager.shutdown()
            await queue_manager.shutdown()
            await registry.shutdown()


class TestPerformanceIntegration:
    """Test system performance under load."""
    
    @pytest.mark.asyncio
    async def test_high_volume_message_processing(self):
        """Test handling high volume of messages."""
        settings = Settings()
        
        redis_mock = AsyncMock()
        redis_mock.zadd = AsyncMock(return_value=1)
        redis_mock.zcard = AsyncMock(side_effect=lambda: 5000)  # Simulate half-full queue
        redis_mock.close = AsyncMock()
        
        with patch('aioredis.from_url', return_value=redis_mock):
            queue_manager = PriorityQueueManager(settings)
            await queue_manager.initialize()
            
            # Enqueue many messages
            start_time = asyncio.get_event_loop().time()
            
            for i in range(1000):
                message = ServiceMessage(
                    source=ServiceType.CHARACTER_SERVICE,
                    destination=ServiceType.RULES_SERVICE,
                    message_type=MessageType.CHARACTER_UPDATED,
                    correlation_id=f"perf-{i}",
                    payload={"id": i}
                )
                
                priority = MessagePriority.NORMAL if i % 10 else MessagePriority.HIGH
                await queue_manager.enqueue(message, priority=priority)
            
            elapsed = asyncio.get_event_loop().time() - start_time
            
            # Should handle 1000 messages quickly
            assert elapsed < 5.0  # Less than 5 seconds
            assert queue_manager.stats["messages_enqueued"] == 1000
            
            await queue_manager.shutdown()
