"""
Priority Queue Management for Message Hub

Implements message prioritization and intelligent queue management.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum, IntEnum
from dataclasses import dataclass, asdict
import structlog
import redis.asyncio as redis
from collections import defaultdict

from .models import ServiceMessage, ServiceType, MessageType
from .config import Settings

logger = structlog.get_logger()


class MessagePriority(IntEnum):
    """Message priority levels."""
    CRITICAL = 1  # System critical messages
    HIGH = 2      # High priority business operations
    NORMAL = 3    # Standard messages
    LOW = 4       # Low priority, batch-able messages
    DEFERRED = 5  # Messages that can be processed later


class QueueStatus(str, Enum):
    """Queue status."""
    ACTIVE = "active"
    PAUSED = "paused"
    THROTTLED = "throttled"
    OVERLOADED = "overloaded"


@dataclass
class PrioritizedMessage:
    """Message with priority metadata."""
    message: ServiceMessage
    priority: MessagePriority
    enqueued_at: datetime
    deadline: Optional[datetime] = None
    attempt_count: int = 0
    processing_time_estimate: float = 0.0  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message": self.message.model_dump(),
            "priority": self.priority.value,
            "enqueued_at": self.enqueued_at.isoformat(),
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "attempt_count": self.attempt_count,
            "processing_time_estimate": self.processing_time_estimate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PrioritizedMessage':
        """Create from dictionary."""
        return cls(
            message=ServiceMessage(**data["message"]),
            priority=MessagePriority(data["priority"]),
            enqueued_at=datetime.fromisoformat(data["enqueued_at"]),
            deadline=datetime.fromisoformat(data["deadline"]) if data.get("deadline") else None,
            attempt_count=data.get("attempt_count", 0),
            processing_time_estimate=data.get("processing_time_estimate", 0.0)
        )


class PriorityQueueManager:
    """
    Manages priority-based message queuing with intelligent scheduling.
    
    Features:
    - Multi-level priority queues
    - Deadline-aware scheduling
    - Service-specific queue management
    - Adaptive throttling
    - Queue overflow handling
    - Fair scheduling with priority
    """
    
    def __init__(self, settings: Settings):
        """Initialize priority queue manager."""
        self.settings = settings
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Queue configuration
        self.max_queue_size = 10000
        self.overflow_threshold = 0.8  # 80% capacity
        self.throttle_threshold = 0.9   # 90% capacity
        
        # Priority weights for scheduling
        self.priority_weights = {
            MessagePriority.CRITICAL: 1.0,
            MessagePriority.HIGH: 0.7,
            MessagePriority.NORMAL: 0.4,
            MessagePriority.LOW: 0.2,
            MessagePriority.DEFERRED: 0.1
        }
        
        # Service-specific settings
        self.service_quotas: Dict[ServiceType, int] = {}  # Messages per second
        self.service_counters: Dict[ServiceType, int] = defaultdict(int)
        self.service_reset_time: Dict[ServiceType, float] = {}
        
        # Queue statistics
        self.stats = {
            "messages_enqueued": 0,
            "messages_dequeued": 0,
            "messages_dropped": 0,
            "queue_overflows": 0,
            "throttle_events": 0
        }
        
        # Background processor
        self._processor_task = None
    
    async def initialize(self):
        """Initialize Redis connection and start processor."""
        self.redis_client = await aioredis.from_url(
            self.settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        
        # Start background processor
        self._processor_task = asyncio.create_task(self._process_queues())
        
        logger.info("priority_queue_manager_initialized")
    
    async def shutdown(self):
        """Shutdown queue manager."""
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("priority_queue_manager_shutdown")
    
    async def enqueue(self,
                     message: ServiceMessage,
                     priority: Optional[MessagePriority] = None,
                     deadline: Optional[datetime] = None) -> bool:
        """
        Enqueue a message with priority.
        
        Args:
            message: Message to enqueue
            priority: Message priority (auto-determined if not provided)
            deadline: Optional deadline for message processing
        
        Returns:
            True if message was enqueued, False if rejected
        """
        # Auto-determine priority if not provided
        if priority is None:
            priority = self._determine_priority(message)
        
        # Check queue capacity
        queue_size = await self._get_queue_size()
        if queue_size >= self.max_queue_size:
            self.stats["queue_overflows"] += 1
            self.stats["messages_dropped"] += 1
            logger.warning("queue_overflow",
                          queue_size=queue_size,
                          message_type=message.message_type)
            return False
        
        # Create prioritized message
        prioritized_msg = PrioritizedMessage(
            message=message,
            priority=priority,
            enqueued_at=datetime.utcnow(),
            deadline=deadline,
            processing_time_estimate=self._estimate_processing_time(message)
        )
        
        # Get queue key for priority
        queue_key = self._get_queue_key(priority, message.destination)
        
        # Calculate score for sorted set (lower score = higher priority)
        score = self._calculate_score(prioritized_msg)
        
        # Add to queue
        await self.redis_client.zadd(
            queue_key,
            {json.dumps(prioritized_msg.to_dict()): score}
        )
        
        self.stats["messages_enqueued"] += 1
        
        logger.debug("message_enqueued",
                    correlation_id=message.correlation_id,
                    priority=priority.name,
                    destination=message.destination.value)
        
        # Check if we need to throttle
        if queue_size > self.max_queue_size * self.throttle_threshold:
            await self._apply_throttling()
        
        return True
    
    async def dequeue(self,
                     service: Optional[ServiceType] = None,
                     batch_size: int = 1) -> List[PrioritizedMessage]:
        """
        Dequeue messages for processing.
        
        Args:
            service: Specific service to dequeue for (None for any)
            batch_size: Number of messages to dequeue
        
        Returns:
            List of prioritized messages
        """
        messages = []
        
        # Get messages from each priority queue
        for priority in MessagePriority:
            if len(messages) >= batch_size:
                break
            
            # Calculate how many to take from this priority
            weight = self.priority_weights[priority]
            take_count = max(1, int(batch_size * weight))
            take_count = min(take_count, batch_size - len(messages))
            
            # Get queue key
            queue_key = self._get_queue_key(priority, service)
            
            # Get messages with deadline consideration
            now = datetime.utcnow().timestamp()
            
            # Get messages that are ready or past deadline
            raw_messages = await self.redis_client.zrangebyscore(
                queue_key,
                0,
                now + 3600,  # Look ahead 1 hour for deadlines
                start=0,
                num=take_count
            )
            
            for raw_msg in raw_messages:
                try:
                    msg = PrioritizedMessage.from_dict(json.loads(raw_msg))
                    
                    # Check service quota
                    if not await self._check_service_quota(msg.message.destination):
                        continue
                    
                    # Remove from queue
                    await self.redis_client.zrem(queue_key, raw_msg)
                    
                    messages.append(msg)
                    self.stats["messages_dequeued"] += 1
                    
                except Exception as e:
                    logger.error("dequeue_error",
                               error=str(e),
                               raw_message=raw_msg)
        
        return messages
    
    async def requeue(self,
                     message: PrioritizedMessage,
                     new_priority: Optional[MessagePriority] = None) -> bool:
        """
        Requeue a message (e.g., after processing failure).
        
        Args:
            message: Message to requeue
            new_priority: Optional new priority
        
        Returns:
            True if requeued successfully
        """
        # Update attempt count
        message.attempt_count += 1
        
        # Adjust priority if needed
        if new_priority:
            message.priority = new_priority
        elif message.attempt_count > 3:
            # Lower priority after multiple attempts
            message.priority = min(MessagePriority.LOW, message.priority + 1)
        
        # Re-enqueue
        return await self.enqueue(
            message.message,
            message.priority,
            message.deadline
        )
    
    async def get_queue_status(self,
                              service: Optional[ServiceType] = None) -> Dict[str, Any]:
        """Get queue status and statistics."""
        status = {
            "status": QueueStatus.ACTIVE,
            "queues": {},
            "total_size": 0,
            "statistics": self.stats.copy()
        }
        
        # Get size of each priority queue
        for priority in MessagePriority:
            queue_key = self._get_queue_key(priority, service)
            size = await self.redis_client.zcard(queue_key)
            status["queues"][priority.name] = size
            status["total_size"] += size
        
        # Determine overall status
        if status["total_size"] > self.max_queue_size * self.overflow_threshold:
            status["status"] = QueueStatus.OVERLOADED
        elif status["total_size"] > self.max_queue_size * self.throttle_threshold:
            status["status"] = QueueStatus.THROTTLED
        
        # Add service-specific quotas
        if service:
            status["service_quota"] = self.service_quotas.get(service, float("inf"))
            status["service_counter"] = self.service_counters.get(service, 0)
        
        return status
    
    async def clear_queue(self,
                         priority: Optional[MessagePriority] = None,
                         service: Optional[ServiceType] = None) -> int:
        """
        Clear messages from queue.
        
        Args:
            priority: Specific priority to clear (None for all)
            service: Specific service queue to clear (None for all)
        
        Returns:
            Number of messages cleared
        """
        cleared = 0
        
        priorities = [priority] if priority else list(MessagePriority)
        
        for p in priorities:
            queue_key = self._get_queue_key(p, service)
            size = await self.redis_client.zcard(queue_key)
            await self.redis_client.delete(queue_key)
            cleared += size
        
        logger.info("queue_cleared",
                   priority=priority.name if priority else "all",
                   service=service.value if service else "all",
                   messages_cleared=cleared)
        
        return cleared
    
    def _determine_priority(self, message: ServiceMessage) -> MessagePriority:
        """Auto-determine message priority based on type and content."""
        # Critical system messages
        critical_types = [
            MessageType.TRANSACTION_PREPARE,
            MessageType.TRANSACTION_COMMIT,
            MessageType.TRANSACTION_ROLLBACK
        ]
        if message.message_type in critical_types:
            return MessagePriority.CRITICAL
        
        # High priority updates
        high_types = [
            MessageType.CHARACTER_LEVEL_UP,
            MessageType.CHARACTER_DELETED
        ]
        if message.message_type in high_types:
            return MessagePriority.HIGH
        
        # Low priority updates
        low_types = [
            MessageType.BACKGROUND_UPDATED,
            MessageType.FEATURES_UPDATED
        ]
        if message.message_type in low_types:
            return MessagePriority.LOW
        
        # Default to normal
        return MessagePriority.NORMAL
    
    def _calculate_score(self, message: PrioritizedMessage) -> float:
        """
        Calculate priority score for sorted set.
        Lower score = higher priority.
        """
        base_score = message.priority.value * 1000
        
        # Adjust for deadline
        if message.deadline:
            time_to_deadline = (message.deadline - datetime.utcnow()).total_seconds()
            if time_to_deadline < 60:  # Less than 1 minute
                base_score -= 500  # Boost priority
            elif time_to_deadline < 300:  # Less than 5 minutes
                base_score -= 200
        
        # Adjust for age (older messages get slight priority boost)
        age = (datetime.utcnow() - message.enqueued_at).total_seconds()
        age_adjustment = min(100, age / 10)  # Cap at 100
        base_score -= age_adjustment
        
        # Add timestamp component for FIFO within same priority
        base_score += message.enqueued_at.timestamp() / 1000000
        
        return base_score
    
    def _get_queue_key(self,
                      priority: MessagePriority,
                      service: Optional[ServiceType] = None) -> str:
        """Get Redis key for a queue."""
        if service:
            return f"message_hub:queue:{service.value}:{priority.name}"
        return f"message_hub:queue:global:{priority.name}"
    
    async def _get_queue_size(self) -> int:
        """Get total queue size across all priorities."""
        total = 0
        for priority in MessagePriority:
            queue_key = self._get_queue_key(priority, None)
            total += await self.redis_client.zcard(queue_key)
        return total
    
    def _estimate_processing_time(self, message: ServiceMessage) -> float:
        """Estimate processing time for a message."""
        # Simple estimation based on message type
        # In production, this would use historical data
        estimates = {
            MessageType.CHARACTER_CREATED: 0.5,
            MessageType.CHARACTER_UPDATED: 0.3,
            MessageType.INVENTORY_UPDATED: 0.2,
            MessageType.CHARACTER_LEVEL_UP: 1.0,
            MessageType.TRANSACTION_PREPARE: 0.1,
        }
        return estimates.get(message.message_type, 0.25)
    
    async def _check_service_quota(self, service: ServiceType) -> bool:
        """Check if service is within its quota."""
        if service not in self.service_quotas:
            return True  # No quota set
        
        quota = self.service_quotas[service]
        current_time = time.time()
        
        # Reset counter if needed
        if service not in self.service_reset_time or \
           current_time - self.service_reset_time[service] >= 1.0:
            self.service_counters[service] = 0
            self.service_reset_time[service] = current_time
        
        # Check quota
        if self.service_counters[service] >= quota:
            return False
        
        # Increment counter
        self.service_counters[service] += 1
        return True
    
    async def _apply_throttling(self):
        """Apply throttling when queue is near capacity."""
        self.stats["throttle_events"] += 1
        
        # Could implement various throttling strategies:
        # - Reject low priority messages
        # - Increase processing delays
        # - Alert administrators
        
        logger.warning("queue_throttling_applied",
                      queue_size=await self._get_queue_size(),
                      max_size=self.max_queue_size)
    
    async def _process_queues(self):
        """Background task to monitor and optimize queues."""
        logger.info("queue_processor_started")
        
        while True:
            try:
                # Monitor queue health
                status = await self.get_queue_status()
                
                # Log if overloaded
                if status["status"] == QueueStatus.OVERLOADED:
                    logger.error("queue_overloaded",
                               total_size=status["total_size"],
                               max_size=self.max_queue_size)
                
                # Clean up old deferred messages
                for priority in [MessagePriority.DEFERRED, MessagePriority.LOW]:
                    queue_key = self._get_queue_key(priority, None)
                    
                    # Remove messages older than 1 hour
                    cutoff_time = (datetime.utcnow() - timedelta(hours=1)).timestamp()
                    removed = await self.redis_client.zremrangebyscore(
                        queue_key,
                        0,
                        cutoff_time
                    )
                    
                    if removed > 0:
                        logger.info("old_messages_cleaned",
                                   priority=priority.name,
                                   count=removed)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("queue_processor_error", error=str(e))
                await asyncio.sleep(60)
        
        logger.info("queue_processor_stopped")
    
    async def set_service_quota(self, service: ServiceType, quota: int):
        """Set rate limit quota for a service."""
        self.service_quotas[service] = quota
        logger.info("service_quota_set",
                   service=service.value,
                   quota=quota)
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get queue metrics."""
        status = await self.get_queue_status()
        
        return {
            **status,
            "quotas": {
                service.value: quota
                for service, quota in self.service_quotas.items()
            },
            "processing_estimates": {
                msg_type.value: self._estimate_processing_time(
                    ServiceMessage(
                        source=ServiceType.MESSAGE_HUB,
                        destination=ServiceType.MESSAGE_HUB,
                        message_type=msg_type,
                        correlation_id="test",
                        payload={}
                    )
                )
                for msg_type in MessageType
            }
        }
