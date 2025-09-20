"""MessageHub client for inter-service communication.

This module provides the primary client class for services to interact with MessageHub.
It handles message sending/receiving, event subscriptions, and circuit breaker patterns.
"""

from typing import Any, Dict, List, Optional, Tuple
import asyncio
from dataclasses import dataclass
import logging
from uuid import UUID, uuid4

import aio_pika
from prometheus_client import Counter, Histogram

from ..core.config import Config
from ..core.exceptions import (
    MessageHubConnectionError,
    MessageHubDeliveryError,
    MessageHubCircuitBreakerError,
    MessageHubRetryError,
)
from ..core.monitoring import configure_prometheus_metrics

logger = logging.getLogger(__name__)

# Metrics
MESSAGE_COUNTER = Counter(
    "message_hub_messages_total", 
    "Total number of messages sent/received",
    ["service", "type", "status"]
)

MESSAGE_LATENCY = Histogram(
    "message_hub_message_latency_seconds",
    "Message processing latency in seconds",
    ["service", "type"]
)

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5
    reset_timeout: int = 60
    half_open_timeout: int = 30
    
class CircuitBreaker:
    """Circuit breaker pattern implementation."""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failures = 0
        self.last_failure_time = 0
        self.state = "CLOSED"
        self._lock = asyncio.Lock()
        
    async def record_success(self):
        """Record a successful operation."""
        async with self._lock:
            self.failures = 0
            self.state = "CLOSED"
            
    async def record_failure(self):
        """Record a failed operation."""
        async with self._lock:
            self.failures += 1
            self.last_failure_time = asyncio.get_event_loop().time()
            
            if self.failures >= self.config.failure_threshold:
                self.state = "OPEN"
                logger.warning("Circuit breaker opened due to %d failures", self.failures)
                
    async def check_state(self) -> str:
        """Check the current circuit breaker state."""
        async with self._lock:
            if self.state == "OPEN":
                current_time = asyncio.get_event_loop().time()
                if current_time - self.last_failure_time >= self.config.reset_timeout:
                    self.state = "HALF_OPEN"
                    logger.info("Circuit breaker entering half-open state")
            return self.state

class MessageHubClient:
    """Client for interacting with the Message Hub service."""

    def __init__(
        self,
        service_name: str,
        rabbitmq_url: str,
        auth_key: str,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
    ):
        """Initialize the Message Hub client.
        
        Args:
            service_name: Unique identifier for the service using this client
            rabbitmq_url: URL for RabbitMQ connection
            auth_key: Authentication key for the service
            circuit_breaker_config: Optional circuit breaker configuration
        """
        self.service_name = service_name
        self.rabbitmq_url = rabbitmq_url
        self.auth_key = auth_key
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.subscriptions: Dict[str, asyncio.Task] = {}
        self.circuit_breaker = CircuitBreaker(
            circuit_breaker_config or CircuitBreakerConfig()
        )
        
    async def connect(self) -> None:
        """Establish connection to Message Hub."""
        try:
            self.connection = await aio_pika.connect_robust(
                self.rabbitmq_url,
                client_properties={
                    "service": self.service_name,
                    "auth_key": self.auth_key
                }
            )
            self.channel = await self.connection.channel()
            logger.info("Connected to Message Hub successfully")
            
        except Exception as e:
            logger.exception("Failed to connect to Message Hub")
            raise MessageHubConnectionError(f"Connection failed: {str(e)}")

    async def close(self) -> None:
        """Close the Message Hub connection."""
        for subscription in self.subscriptions.values():
            subscription.cancel()
            
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()
            
        logger.info("Message Hub connection closed")

    async def send_message(
        self,
        destination: str,
        payload: Dict[str, Any],
        correlation_id: Optional[UUID] = None,
        ttl: int = 300,
        priority: int = 0
    ) -> UUID:
        """Send a message to a specific service.
        
        Args:
            destination: Target service name
            payload: Message content
            correlation_id: Optional ID for request correlation
            ttl: Time-to-live in seconds
            priority: Message priority (0-9)
            
        Returns:
            UUID of the sent message
            
        Raises:
            MessageHubCircuitBreakerError: If circuit breaker is open
            MessageHubDeliveryError: If message delivery fails
        """
        # Check circuit breaker
        state = await self.circuit_breaker.check_state()
        if state == "OPEN":
            raise MessageHubCircuitBreakerError(
                f"Circuit breaker is open for {destination}"
            )
            
        try:
            message_id = uuid4()
            
            # Create message with headers
            message = aio_pika.Message(
                body=str(payload).encode(),
                message_id=str(message_id),
                correlation_id=str(correlation_id) if correlation_id else None,
                headers={
                    "source": self.service_name,
                    "destination": destination,
                    "timestamp": str(asyncio.get_event_loop().time()),
                    "ttl": ttl,
                    "priority": priority
                },
                expiration=ttl
            )
            
            with MESSAGE_LATENCY.labels(
                service=self.service_name, type="send"
            ).time():
                # Ensure we have a channel
                if not self.channel:
                    await self.connect()
                    
                # Send the message
                await self.channel.default_exchange.publish(
                    message,
                    routing_key=f"{destination}.messages"
                )
                
            # Record metrics
            MESSAGE_COUNTER.labels(
                service=self.service_name,
                type="send",
                status="success"
            ).inc()
            
            # Record success in circuit breaker
            await self.circuit_breaker.record_success()
            
            logger.info(
                "Message %s sent to %s successfully",
                message_id,
                destination
            )
            return message_id
            
        except Exception as e:
            # Record metrics
            MESSAGE_COUNTER.labels(
                service=self.service_name,
                type="send",
                status="error"
            ).inc()
            
            # Record failure in circuit breaker
            await self.circuit_breaker.record_failure()
            
            logger.exception("Failed to send message to %s", destination)
            raise MessageHubDeliveryError(
                f"Failed to deliver message to {destination}: {str(e)}"
            )

    async def subscribe(
        self,
        event_types: List[str],
        callback: callable,
        durable: bool = True
    ) -> None:
        """Subscribe to specific event types.
        
        Args:
            event_types: List of event types to subscribe to
            callback: Async callback function to handle events
            durable: Whether the subscription should survive restarts
        """
        if not self.channel:
            await self.connect()
            
        for event_type in event_types:
            # Create queue
            queue_name = f"{self.service_name}.{event_type}"
            queue = await self.channel.declare_queue(
                queue_name,
                durable=durable
            )
            
            # Bind queue to exchange
            await queue.bind(
                "events",
                routing_key=event_type
            )
            
            # Start consumer
            async def message_handler(message: aio_pika.IncomingMessage):
                async with message.process():
                    with MESSAGE_LATENCY.labels(
                        service=self.service_name,
                        type="receive"
                    ).time():
                        try:
                            await callback(message.body.decode())
                            MESSAGE_COUNTER.labels(
                                service=self.service_name,
                                type="receive",
                                status="success"
                            ).inc()
                        except Exception as e:
                            MESSAGE_COUNTER.labels(
                                service=self.service_name,
                                type="receive",
                                status="error"
                            ).inc()
                            logger.exception(
                                "Error processing message: %s", str(e)
                            )
                            
            # Start consumer task
            consumer_tag = f"{self.service_name}.{event_type}.consumer"
            task = asyncio.create_task(
                queue.consume(message_handler, consumer_tag=consumer_tag)
            )
            self.subscriptions[event_type] = task
            
            logger.info(
                "Subscribed to event type %s with consumer %s",
                event_type,
                consumer_tag
            )

    async def unsubscribe(self, event_type: str) -> None:
        """Unsubscribe from an event type.
        
        Args:
            event_type: Event type to unsubscribe from
        """
        if event_type in self.subscriptions:
            # Cancel the consumer task
            self.subscriptions[event_type].cancel()
            del self.subscriptions[event_type]
            
            # Clean up queue binding if needed
            if self.channel:
                queue_name = f"{self.service_name}.{event_type}"
                queue = await self.channel.declare_queue(queue_name)
                await queue.unbind(
                    exchange="events",
                    routing_key=event_type
                )
            
            logger.info("Unsubscribed from event type %s", event_type)

    async def publish_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        correlation_id: Optional[UUID] = None
    ) -> UUID:
        """Publish an event to the message hub.
        
        Args:
            event_type: Type of event being published
            payload: Event data
            correlation_id: Optional ID for request correlation
            
        Returns:
            UUID of the published event
        """
        try:
            event_id = uuid4()
            
            # Create event message
            message = aio_pika.Message(
                body=str(payload).encode(),
                message_id=str(event_id),
                correlation_id=str(correlation_id) if correlation_id else None,
                headers={
                    "source": self.service_name,
                    "event_type": event_type,
                    "timestamp": str(asyncio.get_event_loop().time())
                }
            )
            
            with MESSAGE_LATENCY.labels(
                service=self.service_name,
                type="publish"
            ).time():
                # Ensure we have a channel
                if not self.channel:
                    await self.connect()
                    
                # Publish the event
                exchange = await self.channel.declare_exchange(
                    "events",
                    aio_pika.ExchangeType.TOPIC
                )
                await exchange.publish(
                    message,
                    routing_key=event_type
                )
                
            # Record metrics
            MESSAGE_COUNTER.labels(
                service=self.service_name,
                type="publish",
                status="success"
            ).inc()
            
            logger.info(
                "Event %s of type %s published successfully",
                event_id,
                event_type
            )
            return event_id
            
        except Exception as e:
            # Record metrics
            MESSAGE_COUNTER.labels(
                service=self.service_name,
                type="publish",
                status="error"
            ).inc()
            
            logger.exception("Failed to publish event of type %s", event_type)
            raise MessageHubDeliveryError(
                f"Failed to publish event: {str(e)}"
            )
            
    def get_health_status(self) -> Dict[str, Any]:
        """Get the health status of the message hub client.
        
        Returns:
            Dictionary with health status information
        """
        return {
            "connected": self.connection is not None and not self.connection.is_closed,
            "subscriptions": list(self.subscriptions.keys()),
            "circuit_breaker_state": self.circuit_breaker.state,
            "service_name": self.service_name
        }