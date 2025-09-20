"""MessageHub testing framework for validating service integrations."""

from typing import Any, Dict, List, Optional, Set, Tuple
import asyncio
import json
import logging
from uuid import UUID, uuid4

from aio_pika import Connection, Channel, Exchange, Queue, Message
from prometheus_client import Counter, Histogram

from ..core.exceptions import (
    MessageHubConnectionError,
    MessageHubDeliveryError,
    MessageHubCircuitBreakerError,
)

logger = logging.getLogger(__name__)

# Test metrics
TEST_EVENT_COUNTER = Counter(
    "message_hub_test_events_total",
    "Total number of test events processed",
    ["type", "status"]
)

TEST_LATENCY = Histogram(
    "message_hub_test_latency_seconds",
    "Test event processing latency in seconds",
    ["type"]
)

class MockService:
    """Mock service for testing MessageHub integration."""
    
    def __init__(self, name: str, connection: Connection):
        """Initialize the mock service.
        
        Args:
            name: Service name
            connection: RabbitMQ connection
        """
        self.name = name
        self.connection = connection
        self.channel: Optional[Channel] = None
        self.events_received: List[Dict[str, Any]] = []
        self.messages_received: List[Dict[str, Any]] = []
        
    async def start(self):
        """Start the mock service."""
        self.channel = await self.connection.channel()
        
        # Create service queue for messages
        self.message_queue = await self.channel.declare_queue(
            f"{self.name}.messages",
            durable=True
        )
        await self.message_queue.consume(self._handle_message)
        
        logger.info("Started mock service: %s", self.name)
        
    async def _handle_message(self, message: Message):
        """Handle received messages.
        
        Args:
            message: Received message
        """
        async with message.process():
            payload = json.loads(message.body.decode())
            headers = message.headers or {}
            
            # Store received message
            self.messages_received.append({
                "payload": payload,
                "headers": headers,
                "message_id": message.message_id,
                "correlation_id": message.correlation_id
            })
            
            TEST_EVENT_COUNTER.labels(
                type="message",
                status="received"
            ).inc()
            
            logger.info(
                "Service %s received message: %s",
                self.name,
                message.message_id
            )
            
    async def _handle_event(self, message: Message):
        """Handle received events.
        
        Args:
            message: Received event message
        """
        async with message.process():
            payload = json.loads(message.body.decode())
            headers = message.headers or {}
            
            # Store received event
            self.events_received.append({
                "payload": payload,
                "headers": headers,
                "message_id": message.message_id,
                "correlation_id": message.correlation_id,
                "routing_key": message.routing_key
            })
            
            TEST_EVENT_COUNTER.labels(
                type="event",
                status="received"
            ).inc()
            
            logger.info(
                "Service %s received event: %s",
                self.name,
                message.message_id
            )
            
    async def subscribe_to_events(self, event_types: List[str]):
        """Subscribe to event types.
        
        Args:
            event_types: List of event types to subscribe to
        """
        if not self.channel:
            raise RuntimeError("Service not started")
            
        # Create events exchange
        events_exchange = await self.channel.declare_exchange(
            "events",
            type="topic",
            durable=True
        )
        
        # Create queue and bind to event types
        queue = await self.channel.declare_queue(
            f"{self.name}.events",
            durable=True
        )
        
        for event_type in event_types:
            await queue.bind(
                events_exchange,
                routing_key=event_type
            )
            
        await queue.consume(self._handle_event)
        logger.info("Service %s subscribed to events: %s", self.name, event_types)
            
    async def send_message(
        self,
        destination: str,
        payload: Dict[str, Any],
        correlation_id: Optional[UUID] = None,
        ttl: int = 300,
        priority: int = 0
    ) -> UUID:
        """Send a message to another service.
        
        Args:
            destination: Target service name
            payload: Message content
            correlation_id: Optional correlation ID
            ttl: Message time-to-live in seconds
            priority: Message priority (0-9)
            
        Returns:
            UUID of the sent message
        """
        if not self.channel:
            raise RuntimeError("Service not started")
            
        message_id = uuid4()
        
        message = Message(
            body=str(payload).encode(),
            message_id=str(message_id),
            correlation_id=str(correlation_id) if correlation_id else None,
            headers={
                "source": self.name,
                "destination": destination,
                "timestamp": str(asyncio.get_event_loop().time()),
                "ttl": ttl,
                "priority": priority
            },
            expiration=ttl
        )
        
        # Send through default exchange
        await self.channel.default_exchange.publish(
            message,
            routing_key=f"{destination}.messages"
        )
        
        TEST_EVENT_COUNTER.labels(
            type="message",
            status="sent"
        ).inc()
        
        logger.info(
            "Service %s sent message %s to %s",
            self.name,
            message_id,
            destination
        )
        return message_id
        
    async def publish_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        correlation_id: Optional[UUID] = None
    ) -> UUID:
        """Publish an event.
        
        Args:
            event_type: Type of event to publish
            payload: Event data
            correlation_id: Optional correlation ID
            
        Returns:
            UUID of the published event
        """
        if not self.channel:
            raise RuntimeError("Service not started")
            
        event_id = uuid4()
        
        message = Message(
            body=str(payload).encode(),
            message_id=str(event_id),
            correlation_id=str(correlation_id) if correlation_id else None,
            headers={
                "source": self.name,
                "event_type": event_type,
                "timestamp": str(asyncio.get_event_loop().time())
            }
        )
        
        # Publish through events exchange
        exchange = await self.channel.declare_exchange(
            "events",
            type="topic",
            durable=True
        )
        await exchange.publish(
            message,
            routing_key=event_type
        )
        
        TEST_EVENT_COUNTER.labels(
            type="event",
            status="published"
        ).inc()
        
        logger.info(
            "Service %s published event %s of type %s",
            self.name,
            event_id,
            event_type
        )
        return event_id

class MessageHubTestFramework:
    """Testing framework for MessageHub integration."""
    
    def __init__(self, rabbitmq_url: str):
        """Initialize the test framework.
        
        Args:
            rabbitmq_url: URL for RabbitMQ connection
        """
        self.rabbitmq_url = rabbitmq_url
        self.mock_services: Dict[str, MockService] = {}
        self.connection: Optional[Connection] = None
        
    async def start(self):
        """Start the test framework."""
        self.connection = await Connection.connect(self.rabbitmq_url)
        logger.info("Test framework started")
        
    async def stop(self):
        """Stop the test framework."""
        if self.connection:
            await self.connection.close()
            logger.info("Test framework stopped")
            
    async def create_mock_service(self, name: str) -> MockService:
        """Create a new mock service.
        
        Args:
            name: Service name
            
        Returns:
            The created mock service
        """
        if not self.connection:
            raise RuntimeError("Test framework not started")
            
        service = MockService(name, self.connection)
        await service.start()
        self.mock_services[name] = service
        return service
        
    async def verify_message_delivery(
        self,
        source: str,
        destination: str,
        message_id: UUID,
        timeout: int = 5
    ) -> bool:
        """Verify that a message was delivered.
        
        Args:
            source: Source service name
            destination: Destination service name
            message_id: Expected message ID
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if message was delivered, False otherwise
        """
        if destination not in self.mock_services:
            raise ValueError(f"Unknown destination service: {destination}")
            
        dest_service = self.mock_services[destination]
        
        # Wait for message to arrive
        start_time = asyncio.get_event_loop().time()
        while True:
            # Check if message was received
            for msg in dest_service.messages_received:
                if msg["message_id"] == str(message_id):
                    logger.info(
                        "Message %s delivered from %s to %s",
                        message_id,
                        source,
                        destination
                    )
                    return True
                    
            # Check timeout
            if asyncio.get_event_loop().time() - start_time > timeout:
                logger.warning(
                    "Message %s delivery timeout from %s to %s",
                    message_id,
                    source,
                    destination
                )
                return False
                
            await asyncio.sleep(0.1)
            
    async def verify_event_delivery(
        self,
        source: str,
        event_type: str,
        event_id: UUID,
        subscribers: List[str],
        timeout: int = 5
    ) -> Tuple[bool, Set[str]]:
        """Verify that an event was delivered to subscribers.
        
        Args:
            source: Source service name
            event_type: Event type
            event_id: Expected event ID
            subscribers: List of subscribed services
            timeout: Maximum time to wait in seconds
            
        Returns:
            Tuple of (success, set of services that received the event)
        """
        received_by = set()
        
        # Verify all subscribers exist
        for subscriber in subscribers:
            if subscriber not in self.mock_services:
                raise ValueError(f"Unknown subscriber service: {subscriber}")
                
        # Wait for event to arrive at all subscribers
        start_time = asyncio.get_event_loop().time()
        while True:
            # Check each subscriber
            for subscriber in subscribers:
                if subscriber in received_by:
                    continue
                    
                service = self.mock_services[subscriber]
                for event in service.events_received:
                    if event["message_id"] == str(event_id):
                        received_by.add(subscriber)
                        logger.info(
                            "Event %s of type %s delivered to %s",
                            event_id,
                            event_type,
                            subscriber
                        )
                        break
                        
            # Check if all subscribers received the event
            if len(received_by) == len(subscribers):
                return True, received_by
                
            # Check timeout
            if asyncio.get_event_loop().time() - start_time > timeout:
                logger.warning(
                    "Event %s delivery timeout. Received by: %s",
                    event_id,
                    received_by
                )
                return False, received_by
                
            await asyncio.sleep(0.1)
            
    async def verify_no_cross_talk(
        self,
        services: List[str],
        timeout: int = 5
    ) -> bool:
        """Verify that services are properly isolated.
        
        Args:
            services: List of services to verify
            timeout: Time to monitor for cross-talk
            
        Returns:
            True if no cross-talk detected, False otherwise
        """
        # Record initial message counts
        initial_counts = {}
        for name, service in self.mock_services.items():
            if name in services:
                initial_counts[name] = {
                    "messages": len(service.messages_received),
                    "events": len(service.events_received)
                }
                
        # Wait and monitor for changes
        await asyncio.sleep(timeout)
        
        # Check for unexpected messages
        for name, service in self.mock_services.items():
            if name not in services:
                continue
                
            current_messages = len(service.messages_received)
            current_events = len(service.events_received)
            
            if (current_messages > initial_counts[name]["messages"] or
                current_events > initial_counts[name]["events"]):
                logger.warning(
                    "Service %s received unexpected messages/events",
                    name
                )
                return False
                
        return True
        
    async def test_circuit_breaker(
        self,
        source: str,
        destination: str,
        failure_threshold: int = 5
    ) -> bool:
        """Test circuit breaker functionality.
        
        Args:
            source: Source service name
            destination: Destination service name
            failure_threshold: Number of failures before circuit opens
            
        Returns:
            True if circuit breaker works as expected, False otherwise
        """
        if source not in self.mock_services:
            raise ValueError(f"Unknown source service: {source}")
            
        source_service = self.mock_services[source]
        
        # Force failures by sending to non-existent queue
        failure_count = 0
        try:
            while failure_count < failure_threshold + 1:
                try:
                    await source_service.send_message(
                        "non-existent-service",
                        {"test": "data"}
                    )
                except Exception:
                    failure_count += 1
                    
                await asyncio.sleep(0.1)
                
        except MessageHubCircuitBreakerError:
            # Circuit breaker opened as expected
            logger.info(
                "Circuit breaker opened after %d failures",
                failure_count
            )
            return True
            
        logger.warning("Circuit breaker did not open as expected")
        return False