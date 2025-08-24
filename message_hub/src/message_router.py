"""
Message Hub Router

Handles message routing and delivery between services.
"""

import structlog
import httpx
from circuitbreaker import circuit
from typing import Optional

from .config import Settings
from .models import ServiceMessage, ServiceResponse, ServiceType
from .service_registry import ServiceRegistry
from .circuit_breaker import CircuitBreakerOpen
from .circuit_breaker_manager import CircuitBreakerManager
from .event_store.service import EventStore
from .event_store.helpers import message_to_event_type, create_event_metadata

logger = structlog.get_logger()

class MessageRouter:
    """Routes messages between services with circuit breaker pattern."""
    
    def __init__(
        self,
        settings: Settings,
        registry: ServiceRegistry,
        event_store: EventStore
    ):
        """Initialize the message router."""
        self.settings = settings
        self.registry = registry
        self.event_store = event_store
        self.http_client = httpx.AsyncClient(timeout=settings.message_timeout)
        self.circuit_breaker_manager = CircuitBreakerManager()
    
    @circuit(
        failure_threshold=5,
        recovery_timeout=60,
        name="message_delivery"
    )
    async def route_message(self, message: ServiceMessage) -> ServiceResponse:
        """Route a message to its destination service."""
        try:
            # Get destination service
            service = await self.registry.get_service(message.destination)
            if not service:
                raise ValueError(f"Unknown service: {message.destination}")
            
            # Check if service is healthy
            status = await self.registry.get_service_status(message.destination)
            if status and status.status != "healthy":
                raise ValueError(f"Service {message.destination} is unhealthy: {status.error}")
            
            # Validate message type is supported
            if message.message_type not in service.capabilities:
                raise ValueError(
                    f"Service {message.destination} does not support {message.message_type}"
                )
            
            # Get circuit breaker for this service path
            circuit_breaker = self.circuit_breaker_manager.get_circuit_breaker(
                source=message.source,
                destination=message.destination,
                operation=message.message_type
            )
            
            # Execute request through circuit breaker
            try:
                return await circuit_breaker.call(
                    self._send_message,
                    message=message,
                    service=service
                )
                
            except CircuitBreakerOpen as e:
                return ServiceResponse(
                    correlation_id=message.correlation_id,
                    status="error",
                    data={},
                    error=f"Service unavailable: {str(e)}"
                )
            
        except ValueError as e:
            # Business logic errors
            logger.warning("message_routing_failed",
                       source=message.source,
                       destination=message.destination,
                       error=str(e))
            return ServiceResponse(
                correlation_id=message.correlation_id,
                status="error",
                data={},
                error=str(e)
            )
            
        except Exception as e:
            # Technical errors (will trigger circuit breaker)
            logger.error("message_delivery_failed",
                      source=message.source,
                      destination=message.destination,
                      error=str(e))
            raise
    
    async def _send_message(self, message: ServiceMessage, service: Any) -> ServiceResponse:
        """Send a message to a service."""
        # Construct endpoint URL based on message type
        endpoint = self._get_endpoint_for_message(message)
        url = f"{service.url}{endpoint}"
        
        # Send message
        response = await self.http_client.post(
            url,
            json=message.model_dump()
        )
        response.raise_for_status()
        
        return ServiceResponse(
            correlation_id=message.correlation_id,
            status="success",
            data=response.json()
        )
        
        # Store event if message type has a corresponding event type
        event_type = message_to_event_type(message.message_type)
        if event_type:
            metadata = create_event_metadata(
                service_type=message.source,
                correlation_id=message.correlation_id
            )
            await self.event_store.append_event(
                event_type=event_type,
                source_service=message.source,
                data=message.payload,
                metadata=metadata
            )
    
    def _get_endpoint_for_message(self, message: ServiceMessage) -> str:
        """Determine the appropriate endpoint for a message type."""
        
        # Map message types to endpoints
        endpoints = {
            # Character Service Endpoints
            "create_character": "/v1/characters",
            "update_character": "/v1/characters/{id}",
            "get_character": "/v1/characters/{id}",
            
            # Campaign Service Endpoints
            "create_campaign": "/v1/campaigns",
            "update_campaign": "/v1/campaigns/{id}",
            "add_character": "/v1/campaigns/{id}/characters",
            
            # Image Service Endpoints
            "generate_portrait": "/v1/images/portrait",
            "generate_map": "/v1/images/map",
            
            # LLM Service Endpoints
            "generate_text": "/v1/generate/text",
            "generate_image": "/v1/generate/image"
        }
        
        endpoint = endpoints.get(message.message_type)
        if not endpoint:
            raise ValueError(f"Unknown message type: {message.message_type}")
        
        # Replace any path parameters
        if "{id}" in endpoint:
            if "id" not in message.payload:
                raise ValueError(f"Message type {message.message_type} requires id in payload")
            endpoint = endpoint.replace("{id}", str(message.payload["id"]))
        
        return endpoint
