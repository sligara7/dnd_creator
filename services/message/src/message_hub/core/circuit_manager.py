"""
Circuit Breaker Manager

Manages circuit breakers for all service endpoints.
"""

from typing import Dict, Optional, Any
import structlog
from .circuit_breaker import CircuitBreaker
from .models import ServiceType

logger = structlog.get_logger()

class CircuitBreakerManager:
    """
    Manages circuit breakers for all service endpoints.
    
    Provides centralized management of circuit breakers including:
    - Circuit breaker creation and configuration
    - Circuit breaker lookup by service
    - Metrics collection
    """
    
    def __init__(self):
        """Initialize circuit breaker manager."""
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Default configuration
        self.default_config = {
            "failure_threshold": 5,
            "recovery_timeout": 60,
            "half_open_max_calls": 2
        }
    
    def get_circuit_breaker(self,
                          source: ServiceType,
                          destination: ServiceType,
                          operation: str = None) -> CircuitBreaker:
        """
        Get or create a circuit breaker for a service path.
        
        Args:
            source: Source service
            destination: Destination service
            operation: Optional operation name for finer-grained control
        
        Returns:
            CircuitBreaker instance
        """
        circuit_id = self._get_circuit_id(source, destination, operation)
        
        if circuit_id not in self._circuit_breakers:
            self._circuit_breakers[circuit_id] = CircuitBreaker(
                name=circuit_id,
                **self.default_config
            )
            logger.info("circuit_breaker_created",
                       circuit_id=circuit_id,
                       source=source,
                       destination=destination,
                       operation=operation)
        
        return self._circuit_breakers[circuit_id]
    
    def configure_circuit_breaker(self,
                               source: ServiceType,
                               destination: ServiceType,
                               operation: str = None,
                               **config):
        """
        Configure a specific circuit breaker.
        
        Args:
            source: Source service
            destination: Destination service
            operation: Optional operation name
            **config: Circuit breaker configuration
        """
        circuit_id = self._get_circuit_id(source, destination, operation)
        
        if circuit_id in self._circuit_breakers:
            breaker = self._circuit_breakers[circuit_id]
            
            # Update configuration
            if "failure_threshold" in config:
                breaker.failure_threshold = config["failure_threshold"]
            if "recovery_timeout" in config:
                breaker.recovery_timeout = config["recovery_timeout"]
            if "half_open_max_calls" in config:
                breaker.half_open_max_calls = config["half_open_max_calls"]
            
            logger.info("circuit_breaker_configured",
                       circuit_id=circuit_id,
                       config=config)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics for all circuit breakers."""
        return {
            circuit_id: breaker.get_metrics()
            for circuit_id, breaker in self._circuit_breakers.items()
        }
    
    def _get_circuit_id(self,
                      source: ServiceType,
                      destination: ServiceType,
                      operation: str = None) -> str:
        """Generate a unique circuit breaker ID."""
        circuit_id = f"{source.value}->{destination.value}"
        if operation:
            circuit_id += f":{operation}"
        return circuit_id
