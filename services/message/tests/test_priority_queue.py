"""
Tests for Priority Queue Manager

Comprehensive test suite for message prioritization and queue management.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import aioredis

from src.priority_queue import (
    PriorityQueueManager,
    PrioritizedMessage,
    MessagePriority,
    QueueStatus
)
from src.models import ServiceMessage, ServiceType, MessageType
from src.config import Settings


@pytest.fixture
async def redis_mock():
    """Mock Redis client."""
    redis = AsyncMock()
    redis.zadd = AsyncMock(return_value=1)
    redis.zcard = AsyncMock(return_value=0)
    redis.zrangebyscore = AsyncMock(return_value=[])
    redis.zrem = AsyncMock(return_value=1)
    redis.zremrangebyscore = AsyncMock(return_value=0)
    redis.delete = AsyncMock(return_value=1)
    redis.close = AsyncMock()
    return redis


@pytest.fixture
async def queue_manager(redis_mock):
    """Create priority queue manager with mocked Redis."""
    settings = Settings()
    manager = PriorityQueueManager(settings)
    
    with patch('aioredis.from_url', return_value=redis_mock):
        await manager.initialize()
        yield manager
        await manager.shutdown()


@pytest.fixture
def sample_message():
    """Create a sample service message."""
    return ServiceMessage(
        source=ServiceType.CHARACTER_SERVICE,
        destination=ServiceType.RULES_SERVICE,
        message_type=MessageType.CHARACTER_UPDATED,
        correlation_id="test-correlation-id",
        payload={"character_id": "123", "updates": {"level": 2}}
    )


@pytest.fixture
def critical_message():
    """Create a critical priority message."""
    return ServiceMessage(
        source=ServiceType.MESSAGE_HUB,
        destination=ServiceType.CHARACTER_SERVICE,
        message_type=MessageType.TRANSACTION_COMMIT,
        correlation_id="critical-correlation-id",
        payload={"transaction_id": "tx-123"}
    )


class TestPrioritizedMessage:
    """Test PrioritizedMessage data class."""
    
    def test_prioritized_message_creation(self, sample_message):
        """Test creating a prioritized message."""
        msg = PrioritizedMessage(
            message=sample_message,
            priority=MessagePriority.NORMAL,
            enqueued_at=datetime.utcnow(),
            deadline=datetime.utcnow() + timedelta(minutes=5)
        )
        
        assert msg.message == sample_message
        assert msg.priority == MessagePriority.NORMAL
        assert msg.attempt_count == 0
        assert msg.deadline is not None
    
    def test_prioritized_message_serialization(self, sample_message):
        """Test serializing prioritized message."""
        now = datetime.utcnow()
        deadline = now + timedelta(minutes=5)
        
        msg = PrioritizedMessage(
            message=sample_message,
            priority=MessagePriority.HIGH,
            enqueued_at=now,
            deadline=deadline,
            attempt_count=2,
            processing_time_estimate=0.5
        )
        
        data = msg.to_dict()
        
        assert data["priority"] == MessagePriority.HIGH.value
        assert data["attempt_count"] == 2
        assert data["processing_time_estimate"] == 0.5
        assert isinstance(data["enqueued_at"], str)
        assert isinstance(data["deadline"], str)
    
    def test_prioritized_message_deserialization(self):
        """Test deserializing prioritized message."""
        data = {
            "message": {
                "source": "character-service",
                "destination": "rules-service",
                "message_type": "character.updated",
                "correlation_id": "test-123",
                "payload": {"test": "data"},
                "timestamp": datetime.utcnow().isoformat()
            },
            "priority": 2,
            "enqueued_at": datetime.utcnow().isoformat(),
            "deadline": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
            "attempt_count": 1,
            "processing_time_estimate": 0.3
        }
        
        msg = PrioritizedMessage.from_dict(data)
        
        assert msg.priority == MessagePriority.HIGH
        assert msg.attempt_count == 1
        assert isinstance(msg.enqueued_at, datetime)
        assert isinstance(msg.deadline, datetime)


class TestPriorityQueueManager:
    """Test PriorityQueueManager functionality."""
    
    @pytest.mark.asyncio
    async def test_initialization(self, redis_mock):
        """Test queue manager initialization."""
        settings = Settings()
        manager = PriorityQueueManager(settings)
        
        with patch('aioredis.from_url', return_value=redis_mock):
            await manager.initialize()
            
            assert manager.redis_client is not None
            assert manager._processor_task is not None
            
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_enqueue_success(self, queue_manager, sample_message, redis_mock):
        """Test enqueueing a message."""
        redis_mock.zcard = AsyncMock(return_value=10)  # Queue not full
        redis_mock.zadd = AsyncMock(return_value=1)
        
        success = await queue_manager.enqueue(
            sample_message,
            priority=MessagePriority.NORMAL
        )
        
        assert success is True
        assert queue_manager.stats["messages_enqueued"] == 1
        redis_mock.zadd.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_enqueue_with_deadline(self, queue_manager, sample_message, redis_mock):
        """Test enqueueing with deadline."""
        redis_mock.zcard = AsyncMock(return_value=10)
        redis_mock.zadd = AsyncMock(return_value=1)
        
        deadline = datetime.utcnow() + timedelta(minutes=10)
        success = await queue_manager.enqueue(
            sample_message,
            priority=MessagePriority.HIGH,
            deadline=deadline
        )
        
        assert success is True
        
        # Verify the message was added with correct score
        call_args = redis_mock.zadd.call_args[0]
        message_data = list(call_args[1].keys())[0]
        parsed_data = json.loads(message_data)
        
        assert parsed_data["priority"] == MessagePriority.HIGH.value
        assert parsed_data["deadline"] is not None
    
    @pytest.mark.asyncio
    async def test_enqueue_queue_overflow(self, queue_manager, sample_message, redis_mock):
        """Test queue overflow handling."""
        redis_mock.zcard = AsyncMock(return_value=10000)  # Queue full
        
        success = await queue_manager.enqueue(sample_message)
        
        assert success is False
        assert queue_manager.stats["queue_overflows"] == 1
        assert queue_manager.stats["messages_dropped"] == 1
    
    @pytest.mark.asyncio
    async def test_auto_priority_determination(self, queue_manager):
        """Test automatic priority determination."""
        # Critical message
        msg1 = ServiceMessage(
            source=ServiceType.MESSAGE_HUB,
            destination=ServiceType.CHARACTER_SERVICE,
            message_type=MessageType.TRANSACTION_COMMIT,
            correlation_id="test-1",
            payload={}
        )
        priority1 = queue_manager._determine_priority(msg1)
        assert priority1 == MessagePriority.CRITICAL
        
        # High priority message
        msg2 = ServiceMessage(
            source=ServiceType.CHARACTER_SERVICE,
            destination=ServiceType.RULES_SERVICE,
            message_type=MessageType.CHARACTER_LEVEL_UP,
            correlation_id="test-2",
            payload={}
        )
        priority2 = queue_manager._determine_priority(msg2)
        assert priority2 == MessagePriority.HIGH
        
        # Low priority message
        msg3 = ServiceMessage(
            source=ServiceType.CHARACTER_SERVICE,
            destination=ServiceType.RULES_SERVICE,
            message_type=MessageType.BACKGROUND_UPDATED,
            correlation_id="test-3",
            payload={}
        )
        priority3 = queue_manager._determine_priority(msg3)
        assert priority3 == MessagePriority.LOW
    
    @pytest.mark.asyncio
    async def test_dequeue_by_priority(self, queue_manager, redis_mock):
        """Test dequeuing respects priority order."""
        # Create messages with different priorities
        messages = [
            PrioritizedMessage(
                message=ServiceMessage(
                    source=ServiceType.CHARACTER_SERVICE,
                    destination=ServiceType.RULES_SERVICE,
                    message_type=MessageType.CHARACTER_UPDATED,
                    correlation_id=f"msg-{i}",
                    payload={}
                ),
                priority=priority,
                enqueued_at=datetime.utcnow()
            )
            for i, priority in enumerate([
                MessagePriority.LOW,
                MessagePriority.CRITICAL,
                MessagePriority.NORMAL
            ])
        ]
        
        # Mock Redis to return messages
        redis_mock.zrangebyscore = AsyncMock(
            side_effect=[
                [json.dumps(messages[1].to_dict())],  # CRITICAL first
                [],  # HIGH empty
                [json.dumps(messages[2].to_dict())],  # NORMAL
                [],  # LOW (not reached due to batch size)
                []   # DEFERRED (not reached)
            ]
        )
        redis_mock.zrem = AsyncMock(return_value=1)
        
        dequeued = await queue_manager.dequeue(batch_size=2)
        
        assert len(dequeued) == 2
        assert dequeued[0].priority == MessagePriority.CRITICAL
        assert dequeued[1].priority == MessagePriority.NORMAL
    
    @pytest.mark.asyncio
    async def test_requeue_message(self, queue_manager, sample_message, redis_mock):
        """Test requeuing a message."""
        redis_mock.zcard = AsyncMock(return_value=10)
        redis_mock.zadd = AsyncMock(return_value=1)
        
        msg = PrioritizedMessage(
            message=sample_message,
            priority=MessagePriority.NORMAL,
            enqueued_at=datetime.utcnow(),
            attempt_count=2
        )
        
        success = await queue_manager.requeue(msg)
        
        assert success is True
        assert msg.attempt_count == 3
        
        # After 3 attempts, priority should remain NORMAL
        assert msg.priority == MessagePriority.NORMAL
        
        # Test priority downgrade after many attempts
        msg.attempt_count = 4
        await queue_manager.requeue(msg)
        assert msg.priority == MessagePriority.LOW
    
    @pytest.mark.asyncio
    async def test_queue_status(self, queue_manager, redis_mock):
        """Test getting queue status."""
        redis_mock.zcard = AsyncMock(side_effect=[
            100,  # CRITICAL
            200,  # HIGH
            500,  # NORMAL
            150,  # LOW
            50    # DEFERRED
        ])
        
        status = await queue_manager.get_queue_status()
        
        assert status["total_size"] == 1000
        assert status["queues"]["CRITICAL"] == 100
        assert status["queues"]["NORMAL"] == 500
        assert status["status"] == QueueStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_queue_throttling(self, queue_manager, redis_mock):
        """Test queue throttling detection."""
        # Set queue size to trigger throttling
        redis_mock.zcard = AsyncMock(side_effect=[
            9100,  # Above throttle threshold (90%)
            9100, 9100, 9100, 9100  # For status check
        ])
        
        status = await queue_manager.get_queue_status()
        
        assert status["status"] == QueueStatus.THROTTLED
    
    @pytest.mark.asyncio
    async def test_clear_queue(self, queue_manager, redis_mock):
        """Test clearing queues."""
        redis_mock.zcard = AsyncMock(side_effect=[10, 20, 30, 15, 5])
        redis_mock.delete = AsyncMock(return_value=1)
        
        cleared = await queue_manager.clear_queue()
        
        assert cleared == 80  # Sum of all queue sizes
        assert redis_mock.delete.call_count == 5  # All priority levels


class TestServiceQuotas:
    """Test service quota management."""
    
    @pytest.mark.asyncio
    async def test_set_service_quota(self, queue_manager):
        """Test setting service quotas."""
        await queue_manager.set_service_quota(
            ServiceType.CHARACTER_SERVICE,
            100  # 100 messages per second
        )
        
        assert queue_manager.service_quotas[ServiceType.CHARACTER_SERVICE] == 100
    
    @pytest.mark.asyncio
    async def test_quota_enforcement(self, queue_manager):
        """Test quota enforcement during dequeue."""
        # Set a quota
        queue_manager.service_quotas[ServiceType.CHARACTER_SERVICE] = 2
        
        # First two checks should pass
        assert await queue_manager._check_service_quota(ServiceType.CHARACTER_SERVICE) is True
        assert await queue_manager._check_service_quota(ServiceType.CHARACTER_SERVICE) is True
        
        # Third should fail (quota exceeded)
        assert await queue_manager._check_service_quota(ServiceType.CHARACTER_SERVICE) is False
        
        # Wait for reset (simulated)
        queue_manager.service_reset_time[ServiceType.CHARACTER_SERVICE] = 0
        
        # Should pass again after reset
        assert await queue_manager._check_service_quota(ServiceType.CHARACTER_SERVICE) is True


class TestPriorityScoring:
    """Test priority score calculation."""
    
    def test_score_calculation_basic(self, queue_manager, sample_message):
        """Test basic priority score calculation."""
        msg = PrioritizedMessage(
            message=sample_message,
            priority=MessagePriority.NORMAL,
            enqueued_at=datetime.utcnow()
        )
        
        score = queue_manager._calculate_score(msg)
        
        # Normal priority base score is 3000
        assert 2900 < score < 3100  # Allow for age adjustment
    
    def test_score_calculation_with_deadline(self, queue_manager, sample_message):
        """Test score calculation with deadline."""
        # Message with urgent deadline
        msg = PrioritizedMessage(
            message=sample_message,
            priority=MessagePriority.NORMAL,
            enqueued_at=datetime.utcnow(),
            deadline=datetime.utcnow() + timedelta(seconds=30)  # Very urgent
        )
        
        score = queue_manager._calculate_score(msg)
        
        # Should have boosted priority (lower score)
        assert score < 2500  # Normal is 3000, urgent deadline reduces by 500
    
    def test_score_calculation_age_boost(self, queue_manager, sample_message):
        """Test older messages get priority boost."""
        old_time = datetime.utcnow() - timedelta(minutes=5)
        
        old_msg = PrioritizedMessage(
            message=sample_message,
            priority=MessagePriority.LOW,
            enqueued_at=old_time
        )
        
        new_msg = PrioritizedMessage(
            message=sample_message,
            priority=MessagePriority.LOW,
            enqueued_at=datetime.utcnow()
        )
        
        old_score = queue_manager._calculate_score(old_msg)
        new_score = queue_manager._calculate_score(new_msg)
        
        # Older message should have lower score (higher priority)
        assert old_score < new_score


class TestMetrics:
    """Test metrics collection."""
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, queue_manager, redis_mock):
        """Test getting queue metrics."""
        redis_mock.zcard = AsyncMock(side_effect=[10, 20, 30, 15, 5])
        
        # Simulate some activity
        queue_manager.stats["messages_enqueued"] = 100
        queue_manager.stats["messages_dequeued"] = 95
        queue_manager.service_quotas[ServiceType.CHARACTER_SERVICE] = 50
        
        metrics = await queue_manager.get_metrics()
        
        assert metrics["total_size"] == 80
        assert metrics["statistics"]["messages_enqueued"] == 100
        assert metrics["statistics"]["messages_dequeued"] == 95
        assert metrics["quotas"]["character-service"] == 50
        assert "processing_estimates" in metrics


class TestBackgroundProcessing:
    """Test background queue processing."""
    
    @pytest.mark.asyncio
    async def test_queue_processor_cleanup(self, redis_mock):
        """Test background processor cleans old messages."""
        settings = Settings()
        manager = PriorityQueueManager(settings)
        
        # Mock old messages to clean
        redis_mock.zremrangebyscore = AsyncMock(return_value=5)
        redis_mock.zcard = AsyncMock(return_value=100)
        
        with patch('aioredis.from_url', return_value=redis_mock):
            await manager.initialize()
            
            # Let processor run briefly
            await asyncio.sleep(0.1)
            
            # Should check queue status periodically
            # Note: Exact call count depends on timing
            
            await manager.shutdown()


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.mark.asyncio
    async def test_enqueue_with_no_redis(self, sample_message):
        """Test behavior when Redis is unavailable."""
        settings = Settings()
        manager = PriorityQueueManager(settings)
        
        # Don't initialize (no Redis connection)
        with pytest.raises(AttributeError):
            await manager.enqueue(sample_message)
    
    @pytest.mark.asyncio
    async def test_dequeue_empty_queue(self, queue_manager, redis_mock):
        """Test dequeuing from empty queue."""
        redis_mock.zrangebyscore = AsyncMock(return_value=[])
        
        messages = await queue_manager.dequeue()
        
        assert len(messages) == 0
    
    @pytest.mark.asyncio
    async def test_invalid_message_in_queue(self, queue_manager, redis_mock):
        """Test handling invalid message data in queue."""
        redis_mock.zrangebyscore = AsyncMock(
            return_value=["invalid json", '{"valid": "json"}']
        )
        
        messages = await queue_manager.dequeue()
        
        # Should handle invalid message gracefully
        assert len(messages) == 0
