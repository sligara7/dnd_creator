"""
Retry Manager for Message Hub

Implements exponential backoff retry strategy and dead letter queue handling.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum
import structlog
import redis.asyncio as redis
from dataclasses import dataclass, asdict

from .models import ServiceMessage, ServiceType, MessageType
from .config import Settings

logger = structlog.get_logger()


class RetryStatus(str, Enum):
    """Retry status for messages."""
    PENDING = "pending"
    RETRYING = "retrying"
    SUCCESS = "success"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


@dataclass
class RetryRecord:
    """Record of retry attempts for a message."""
    message_id: str
    correlation_id: str
    source: ServiceType
    destination: ServiceType
    message_type: MessageType
    payload: Dict[str, Any]
    attempt_count: int
    max_attempts: int
    next_retry_at: datetime
    status: RetryStatus
    error: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert enums to strings
        data['source'] = self.source.value if isinstance(self.source, ServiceType) else self.source
        data['destination'] = self.destination.value if isinstance(self.destination, ServiceType) else self.destination
        data['message_type'] = self.message_type.value if isinstance(self.message_type, MessageType) else self.message_type
        data['status'] = self.status.value if isinstance(self.status, RetryStatus) else self.status
        # Convert datetime to ISO format
        for field in ['created_at', 'updated_at', 'next_retry_at']:
            if data[field] and isinstance(data[field], datetime):
                data[field] = data[field].isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RetryRecord':
        """Create from dictionary."""
        # Convert string timestamps back to datetime
        for field in ['created_at', 'updated_at', 'next_retry_at']:
            if data.get(field) and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field])
        # Convert string enums back to enum types
        if isinstance(data.get('source'), str):
            data['source'] = ServiceType(data['source'])
        if isinstance(data.get('destination'), str):
            data['destination'] = ServiceType(data['destination'])
        if isinstance(data.get('message_type'), str):
            data['message_type'] = MessageType(data['message_type'])
        if isinstance(data.get('status'), str):
            data['status'] = RetryStatus(data['status'])
        return cls(**data)


class RetryManager:
    """
    Manages message retries with exponential backoff and dead letter queue.
    
    Features:
    - Exponential backoff with jitter
    - Configurable max attempts
    - Dead letter queue for failed messages
    - Persistent retry state in Redis
    - Automatic retry processing
    """
    
    def __init__(self, settings: Settings):
        """Initialize retry manager."""
        self.settings = settings
        self.redis_client: Optional[redis.Redis] = None
        self.retry_queue_key = "message_hub:retry_queue"
        self.dead_letter_key = "message_hub:dead_letter_queue"
        self.retry_records_key = "message_hub:retry_records"
        
        # Retry configuration
        self.base_delay = 1  # Base delay in seconds
        self.max_delay = 300  # Maximum delay in seconds (5 minutes)
        self.max_attempts = 5  # Maximum retry attempts
        self.jitter_factor = 0.1  # Jitter factor for randomization
        
        # Background task handle
        self._retry_processor_task = None
    
    async def initialize(self):
        """Initialize Redis connection and start retry processor."""
        self.redis_client = redis.from_url(
            self.settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        
        # Start retry processor
        self._retry_processor_task = asyncio.create_task(self._process_retries())
        
        logger.info("retry_manager_initialized")
    
    async def shutdown(self):
        """Shutdown retry manager."""
        if self._retry_processor_task:
            self._retry_processor_task.cancel()
            try:
                await self._retry_processor_task
            except asyncio.CancelledError:
                pass
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("retry_manager_shutdown")
    
    async def schedule_retry(self,
                            message: ServiceMessage,
                            error: str,
                            attempt_count: int = 0) -> RetryRecord:
        """
        Schedule a message for retry.
        
        Args:
            message: The message to retry
            error: The error that occurred
            attempt_count: Current attempt count
        
        Returns:
            RetryRecord for the scheduled retry
        """
        # Calculate next retry time with exponential backoff
        delay = self._calculate_backoff_delay(attempt_count)
        next_retry_at = datetime.utcnow() + timedelta(seconds=delay)
        
        # Create retry record
        record = RetryRecord(
            message_id=message.correlation_id,
            correlation_id=message.correlation_id,
            source=message.source,
            destination=message.destination,
            message_type=message.message_type,
            payload=message.payload,
            attempt_count=attempt_count + 1,
            max_attempts=self.max_attempts,
            next_retry_at=next_retry_at,
            status=RetryStatus.PENDING if attempt_count < self.max_attempts else RetryStatus.DEAD_LETTER,
            error=error
        )
        
        if record.status == RetryStatus.DEAD_LETTER:
            # Move to dead letter queue
            await self._add_to_dead_letter(record)
            logger.warning("message_moved_to_dead_letter",
                          message_id=record.message_id,
                          attempts=record.attempt_count,
                          error=error)
        else:
            # Add to retry queue
            await self._add_to_retry_queue(record)
            logger.info("message_scheduled_for_retry",
                       message_id=record.message_id,
                       attempt=record.attempt_count,
                       next_retry_at=next_retry_at.isoformat())
        
        # Store retry record
        await self._store_retry_record(record)
        
        return record
    
    async def get_retry_status(self, message_id: str) -> Optional[RetryRecord]:
        """Get retry status for a message."""
        data = await self.redis_client.hget(self.retry_records_key, message_id)
        if data:
            return RetryRecord.from_dict(json.loads(data))
        return None
    
    async def get_dead_letter_messages(self, limit: int = 100) -> List[RetryRecord]:
        """Get messages from dead letter queue."""
        messages = await self.redis_client.lrange(self.dead_letter_key, 0, limit - 1)
        return [RetryRecord.from_dict(json.loads(msg)) for msg in messages]
    
    async def reprocess_dead_letter(self, message_id: str) -> bool:
        """
        Reprocess a message from dead letter queue.
        
        Args:
            message_id: ID of the message to reprocess
        
        Returns:
            True if message was found and reprocessed
        """
        # Get all dead letter messages
        messages = await self.get_dead_letter_messages(limit=1000)
        
        for record in messages:
            if record.message_id == message_id:
                # Reset attempt count and schedule for retry
                record.attempt_count = 0
                record.status = RetryStatus.PENDING
                record.next_retry_at = datetime.utcnow()
                
                # Remove from dead letter queue
                await self.redis_client.lrem(
                    self.dead_letter_key,
                    1,
                    json.dumps(record.to_dict())
                )
                
                # Add back to retry queue
                await self._add_to_retry_queue(record)
                await self._store_retry_record(record)
                
                logger.info("dead_letter_message_reprocessed",
                           message_id=message_id)
                return True
        
        return False
    
    async def _add_to_retry_queue(self, record: RetryRecord):
        """Add message to retry queue."""
        # Use sorted set with retry time as score
        score = record.next_retry_at.timestamp()
        await self.redis_client.zadd(
            self.retry_queue_key,
            {json.dumps(record.to_dict()): score}
        )
    
    async def _add_to_dead_letter(self, record: RetryRecord):
        """Add message to dead letter queue."""
        await self.redis_client.lpush(
            self.dead_letter_key,
            json.dumps(record.to_dict())
        )
    
    async def _store_retry_record(self, record: RetryRecord):
        """Store retry record in Redis."""
        await self.redis_client.hset(
            self.retry_records_key,
            record.message_id,
            json.dumps(record.to_dict())
        )
    
    def _calculate_backoff_delay(self, attempt_count: int) -> float:
        """
        Calculate exponential backoff delay with jitter.
        
        Args:
            attempt_count: Number of attempts already made
        
        Returns:
            Delay in seconds
        """
        import random
        
        # Exponential backoff: base_delay * 2^attempt
        delay = min(self.base_delay * (2 ** attempt_count), self.max_delay)
        
        # Add jitter to prevent thundering herd
        jitter = delay * self.jitter_factor * random.random()
        
        return delay + jitter
    
    async def _process_retries(self):
        """Background task to process retry queue."""
        logger.info("retry_processor_started")
        
        while True:
            try:
                # Get messages ready for retry
                now = datetime.utcnow().timestamp()
                messages = await self.redis_client.zrangebyscore(
                    self.retry_queue_key,
                    0,
                    now,
                    start=0,
                    num=10
                )
                
                for message_data in messages:
                    try:
                        record = RetryRecord.from_dict(json.loads(message_data))
                        
                        # Update status
                        record.status = RetryStatus.RETRYING
                        record.updated_at = datetime.utcnow()
                        await self._store_retry_record(record)
                        
                        # Remove from retry queue
                        await self.redis_client.zrem(self.retry_queue_key, message_data)
                        
                        # Notify that message is ready for retry
                        # This would typically trigger the message router to retry
                        logger.info("message_ready_for_retry",
                                   message_id=record.message_id,
                                   attempt=record.attempt_count)
                        
                        # In a real implementation, you would call the message router here
                        # For now, we'll just mark it as processed
                        
                    except Exception as e:
                        logger.error("retry_processing_error",
                                   error=str(e),
                                   message=message_data)
                
                # Sleep before next check
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("retry_processor_error", error=str(e))
                await asyncio.sleep(5)
        
        logger.info("retry_processor_stopped")
    
    async def mark_success(self, message_id: str):
        """Mark a message as successfully processed."""
        record = await self.get_retry_status(message_id)
        if record:
            record.status = RetryStatus.SUCCESS
            record.updated_at = datetime.utcnow()
            await self._store_retry_record(record)
            
            logger.info("retry_marked_success", message_id=message_id)
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get retry metrics."""
        retry_count = await self.redis_client.zcard(self.retry_queue_key)
        dead_letter_count = await self.redis_client.llen(self.dead_letter_key)
        
        # Get status counts from retry records
        all_records = await self.redis_client.hgetall(self.retry_records_key)
        status_counts = {
            RetryStatus.PENDING: 0,
            RetryStatus.RETRYING: 0,
            RetryStatus.SUCCESS: 0,
            RetryStatus.FAILED: 0,
            RetryStatus.DEAD_LETTER: 0
        }
        
        for record_data in all_records.values():
            record = RetryRecord.from_dict(json.loads(record_data))
            status_counts[record.status] = status_counts.get(record.status, 0) + 1
        
        return {
            "retry_queue_size": retry_count,
            "dead_letter_queue_size": dead_letter_count,
            "status_counts": {k.value: v for k, v in status_counts.items()},
            "max_attempts": self.max_attempts,
            "base_delay": self.base_delay,
            "max_delay": self.max_delay
        }
