"""
Tests for Retry Manager

Comprehensive test suite for retry mechanism with exponential backoff and dead letter queue.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import aioredis
from freezegun import freeze_time

from src.retry_manager import (
    RetryManager,
    RetryRecord,
    RetryStatus
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
    redis.hset = AsyncMock(return_value=1)
    redis.hget = AsyncMock(return_value=None)
    redis.hgetall = AsyncMock(return_value={})
    redis.lrange = AsyncMock(return_value=[])
    redis.lpush = AsyncMock(return_value=1)
    redis.lrem = AsyncMock(return_value=1)
    redis.llen = AsyncMock(return_value=0)
    redis.close = AsyncMock()
    return redis


@pytest.fixture
async def retry_manager(redis_mock):
    """Create retry manager with mocked Redis."""
    settings = Settings()
    manager = RetryManager(settings)
    
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


class TestRetryRecord:
    """Test RetryRecord data class."""
    
    def test_retry_record_creation(self, sample_message):
        """Test creating a retry record."""
        record = RetryRecord(
            message_id="msg-123",
            correlation_id="corr-123",
            source=ServiceType.CHARACTER_SERVICE,
            destination=ServiceType.RULES_SERVICE,
            message_type=MessageType.CHARACTER_UPDATED,
            payload={"test": "data"},
            attempt_count=1,
            max_attempts=5,
            next_retry_at=datetime.utcnow(),
            status=RetryStatus.PENDING
        )
        
        assert record.message_id == "msg-123"
        assert record.attempt_count == 1
        assert record.status == RetryStatus.PENDING
        assert record.created_at is not None
        assert record.updated_at is not None
    
    def test_retry_record_serialization(self, sample_message):
        """Test serializing retry record to dict."""
        now = datetime.utcnow()
        record = RetryRecord(
            message_id="msg-123",
            correlation_id="corr-123",
            source=ServiceType.CHARACTER_SERVICE,
            destination=ServiceType.RULES_SERVICE,
            message_type=MessageType.CHARACTER_UPDATED,
            payload={"test": "data"},
            attempt_count=1,
            max_attempts=5,
            next_retry_at=now,
            status=RetryStatus.PENDING,
            error="Test error"
        )
        
        data = record.to_dict()
        
        assert data["message_id"] == "msg-123"
        assert data["source"] == ServiceType.CHARACTER_SERVICE.value
        assert data["status"] == RetryStatus.PENDING.value
        assert data["error"] == "Test error"
        assert isinstance(data["next_retry_at"], str)
    
    def test_retry_record_deserialization(self):
        """Test deserializing retry record from dict."""
        data = {
            "message_id": "msg-123",
            "correlation_id": "corr-123",
            "source": "character-service",
            "destination": "rules-service",
            "message_type": "character.updated",
            "payload": {"test": "data"},
            "attempt_count": 2,
            "max_attempts": 5,
            "next_retry_at": datetime.utcnow().isoformat(),
            "status": "retrying",
            "error": "Connection timeout",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        record = RetryRecord.from_dict(data)
        
        assert record.message_id == "msg-123"
        assert record.source == ServiceType.CHARACTER_SERVICE
        assert record.status == RetryStatus.RETRYING
        assert record.attempt_count == 2
        assert isinstance(record.next_retry_at, datetime)


class TestRetryManager:
    """Test RetryManager functionality."""
    
    @pytest.mark.asyncio
    async def test_initialization(self, redis_mock):
        """Test retry manager initialization."""
        settings = Settings()
        manager = RetryManager(settings)
        
        with patch('aioredis.from_url', return_value=redis_mock):
            await manager.initialize()
            
            assert manager.redis_client is not None
            assert manager._retry_processor_task is not None
            
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_schedule_retry_success(self, retry_manager, sample_message, redis_mock):
        """Test scheduling a message for retry."""
        redis_mock.zadd = AsyncMock(return_value=1)
        redis_mock.hset = AsyncMock(return_value=1)
        
        record = await retry_manager.schedule_retry(
            sample_message,
            "Connection error",
            attempt_count=0
        )
        
        assert record.attempt_count == 1
        assert record.status == RetryStatus.PENDING
        assert record.error == "Connection error"
        assert record.next_retry_at > datetime.utcnow()
        
        # Verify Redis operations
        redis_mock.zadd.assert_called_once()
        redis_mock.hset.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_schedule_retry_max_attempts(self, retry_manager, sample_message, redis_mock):
        """Test message moves to dead letter after max attempts."""
        redis_mock.lpush = AsyncMock(return_value=1)
        redis_mock.hset = AsyncMock(return_value=1)
        
        record = await retry_manager.schedule_retry(
            sample_message,
            "Persistent error",
            attempt_count=4  # Max is 5, so this is the 5th attempt
        )
        
        assert record.attempt_count == 5
        assert record.status == RetryStatus.DEAD_LETTER
        
        # Verify it was added to dead letter queue
        redis_mock.lpush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_exponential_backoff_calculation(self, retry_manager):
        """Test exponential backoff delay calculation."""
        # First attempt - base delay
        delay1 = retry_manager._calculate_backoff_delay(0)
        assert 1.0 <= delay1 <= 1.1  # Base delay plus jitter
        
        # Second attempt - doubled
        delay2 = retry_manager._calculate_backoff_delay(1)
        assert 2.0 <= delay2 <= 2.2
        
        # Third attempt - quadrupled
        delay3 = retry_manager._calculate_backoff_delay(2)
        assert 4.0 <= delay3 <= 4.4
        
        # Max delay cap
        delay_max = retry_manager._calculate_backoff_delay(10)
        assert delay_max <= retry_manager.max_delay * (1 + retry_manager.jitter_factor)
    
    @pytest.mark.asyncio
    async def test_get_retry_status(self, retry_manager, redis_mock):
        """Test getting retry status for a message."""
        record = RetryRecord(
            message_id="msg-123",
            correlation_id="corr-123",
            source=ServiceType.CHARACTER_SERVICE,
            destination=ServiceType.RULES_SERVICE,
            message_type=MessageType.CHARACTER_UPDATED,
            payload={"test": "data"},
            attempt_count=2,
            max_attempts=5,
            next_retry_at=datetime.utcnow(),
            status=RetryStatus.RETRYING
        )
        
        redis_mock.hget = AsyncMock(return_value=json.dumps(record.to_dict()))
        
        retrieved = await retry_manager.get_retry_status("msg-123")
        
        assert retrieved is not None
        assert retrieved.message_id == "msg-123"
        assert retrieved.attempt_count == 2
        assert retrieved.status == RetryStatus.RETRYING
    
    @pytest.mark.asyncio
    async def test_get_dead_letter_messages(self, retry_manager, redis_mock):
        """Test retrieving messages from dead letter queue."""
        records = [
            RetryRecord(
                message_id=f"msg-{i}",
                correlation_id=f"corr-{i}",
                source=ServiceType.CHARACTER_SERVICE,
                destination=ServiceType.RULES_SERVICE,
                message_type=MessageType.CHARACTER_UPDATED,
                payload={"id": i},
                attempt_count=5,
                max_attempts=5,
                next_retry_at=datetime.utcnow(),
                status=RetryStatus.DEAD_LETTER
            )
            for i in range(3)
        ]
        
        redis_mock.lrange = AsyncMock(
            return_value=[json.dumps(r.to_dict()) for r in records]
        )
        
        dead_letters = await retry_manager.get_dead_letter_messages(limit=10)
        
        assert len(dead_letters) == 3
        assert all(msg.status == RetryStatus.DEAD_LETTER for msg in dead_letters)
        assert dead_letters[0].message_id == "msg-0"
    
    @pytest.mark.asyncio
    async def test_reprocess_dead_letter(self, retry_manager, redis_mock):
        """Test reprocessing a message from dead letter queue."""
        record = RetryRecord(
            message_id="msg-123",
            correlation_id="corr-123",
            source=ServiceType.CHARACTER_SERVICE,
            destination=ServiceType.RULES_SERVICE,
            message_type=MessageType.CHARACTER_UPDATED,
            payload={"test": "data"},
            attempt_count=5,
            max_attempts=5,
            next_retry_at=datetime.utcnow(),
            status=RetryStatus.DEAD_LETTER
        )
        
        redis_mock.lrange = AsyncMock(
            return_value=[json.dumps(record.to_dict())]
        )
        redis_mock.lrem = AsyncMock(return_value=1)
        redis_mock.zadd = AsyncMock(return_value=1)
        redis_mock.hset = AsyncMock(return_value=1)
        
        success = await retry_manager.reprocess_dead_letter("msg-123")
        
        assert success is True
        redis_mock.lrem.assert_called_once()
        redis_mock.zadd.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mark_success(self, retry_manager, redis_mock):
        """Test marking a message as successfully processed."""
        record = RetryRecord(
            message_id="msg-123",
            correlation_id="corr-123",
            source=ServiceType.CHARACTER_SERVICE,
            destination=ServiceType.RULES_SERVICE,
            message_type=MessageType.CHARACTER_UPDATED,
            payload={"test": "data"},
            attempt_count=2,
            max_attempts=5,
            next_retry_at=datetime.utcnow(),
            status=RetryStatus.RETRYING
        )
        
        redis_mock.hget = AsyncMock(return_value=json.dumps(record.to_dict()))
        redis_mock.hset = AsyncMock(return_value=1)
        
        await retry_manager.mark_success("msg-123")
        
        # Verify the record was updated
        call_args = redis_mock.hset.call_args[0]
        assert call_args[0] == retry_manager.retry_records_key
        assert call_args[1] == "msg-123"
        
        # Parse the updated record
        updated_data = json.loads(call_args[2])
        assert updated_data["status"] == RetryStatus.SUCCESS.value
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, retry_manager, redis_mock):
        """Test getting retry metrics."""
        redis_mock.zcard = AsyncMock(return_value=5)
        redis_mock.llen = AsyncMock(return_value=2)
        
        records = {
            "msg-1": json.dumps(RetryRecord(
                message_id="msg-1",
                correlation_id="corr-1",
                source=ServiceType.CHARACTER_SERVICE,
                destination=ServiceType.RULES_SERVICE,
                message_type=MessageType.CHARACTER_UPDATED,
                payload={},
                attempt_count=1,
                max_attempts=5,
                next_retry_at=datetime.utcnow(),
                status=RetryStatus.PENDING
            ).to_dict()),
            "msg-2": json.dumps(RetryRecord(
                message_id="msg-2",
                correlation_id="corr-2",
                source=ServiceType.CHARACTER_SERVICE,
                destination=ServiceType.RULES_SERVICE,
                message_type=MessageType.CHARACTER_UPDATED,
                payload={},
                attempt_count=5,
                max_attempts=5,
                next_retry_at=datetime.utcnow(),
                status=RetryStatus.DEAD_LETTER
            ).to_dict())
        }
        
        redis_mock.hgetall = AsyncMock(return_value=records)
        
        metrics = await retry_manager.get_metrics()
        
        assert metrics["retry_queue_size"] == 5
        assert metrics["dead_letter_queue_size"] == 2
        assert metrics["status_counts"]["pending"] == 1
        assert metrics["status_counts"]["dead_letter"] == 1
        assert metrics["max_attempts"] == 5


class TestRetryProcessing:
    """Test background retry processing."""
    
    @pytest.mark.asyncio
    async def test_retry_processor_loop(self, redis_mock):
        """Test the background retry processor."""
        settings = Settings()
        manager = RetryManager(settings)
        
        # Create a message ready for retry
        record = RetryRecord(
            message_id="msg-123",
            correlation_id="corr-123",
            source=ServiceType.CHARACTER_SERVICE,
            destination=ServiceType.RULES_SERVICE,
            message_type=MessageType.CHARACTER_UPDATED,
            payload={"test": "data"},
            attempt_count=1,
            max_attempts=5,
            next_retry_at=datetime.utcnow() - timedelta(seconds=10),  # Past due
            status=RetryStatus.PENDING
        )
        
        redis_mock.zrangebyscore = AsyncMock(
            return_value=[json.dumps(record.to_dict())]
        )
        redis_mock.hset = AsyncMock(return_value=1)
        redis_mock.zrem = AsyncMock(return_value=1)
        
        with patch('aioredis.from_url', return_value=redis_mock):
            await manager.initialize()
            
            # Let the processor run briefly
            await asyncio.sleep(0.1)
            
            # Verify it processed the message
            redis_mock.zrangebyscore.assert_called()
            redis_mock.zrem.assert_called()
            
            await manager.shutdown()


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.mark.asyncio
    async def test_retry_with_no_redis(self, sample_message):
        """Test behavior when Redis is unavailable."""
        settings = Settings()
        manager = RetryManager(settings)
        
        # Don't initialize (no Redis connection)
        with pytest.raises(AttributeError):
            await manager.schedule_retry(sample_message, "Error", 0)
    
    @pytest.mark.asyncio
    async def test_invalid_message_data(self, retry_manager, redis_mock):
        """Test handling invalid message data."""
        redis_mock.lrange = AsyncMock(return_value=["invalid json"])
        
        messages = await retry_manager.get_dead_letter_messages()
        
        # Should handle the error gracefully
        assert len(messages) == 0
    
    @pytest.mark.asyncio
    @freeze_time("2024-01-01 12:00:00")
    async def test_retry_timing(self, retry_manager, sample_message, redis_mock):
        """Test retry timing with frozen time."""
        redis_mock.zadd = AsyncMock(return_value=1)
        redis_mock.hset = AsyncMock(return_value=1)
        
        record = await retry_manager.schedule_retry(
            sample_message,
            "Timeout",
            attempt_count=0
        )
        
        # First retry should be ~1 second later
        expected_time = datetime(2024, 1, 1, 12, 0, 1)
        actual_time = record.next_retry_at.replace(microsecond=0)
        assert actual_time == expected_time
