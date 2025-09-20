"""Message Hub client stub for testing."""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int
    reset_timeout: float
    half_open_timeout: float

class MessageHubClient:
    """Message Hub client."""
    
    def __init__(
        self,
        service_name: str,
        rabbitmq_url: str,
        auth_key: str,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None
    ):
        """Initialize Message Hub client."""
        self.service_name = service_name
        self.rabbitmq_url = rabbitmq_url
        self.auth_key = auth_key
        self.circuit_breaker_config = circuit_breaker_config or CircuitBreakerConfig(
            failure_threshold=5,
            reset_timeout=60,
            half_open_timeout=30
        )
        self.handlers: Dict[str, Callable] = {}
        
    async def connect(self) -> None:
        """Connect to Message Hub."""
        pass
        
    async def close(self) -> None:
        """Close connection to Message Hub."""
        pass
        
    async def publish_event(
        self,
        event_type: str,
        payload: Dict[str, Any]
    ) -> None:
        """Publish an event."""
        pass
        
    async def subscribe(
        self,
        event_types: List[str],
        handler: Callable
    ) -> None:
        """Subscribe to events."""
        for event_type in event_types:
            self.handlers[event_type] = handler