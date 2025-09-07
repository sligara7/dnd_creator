"""Circuit breaker implementation for cache service."""

import asyncio
import time
from enum import Enum
from typing import Any, Callable, Dict, Optional
import structlog

from ..core.exceptions import CircuitBreakerError
from ..core.monitoring import metrics_collector

logger = structlog.get_logger()


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = 0  # Normal operation
    OPEN = 1    # Circuit is open, rejecting requests
    HALF_OPEN = 2  # Testing if service is recovered


class CircuitBreaker:
    """Circuit breaker pattern implementation."""

    def __init__(
        self,
        threshold: int = 5,
        timeout: int = 60,
        half_open_requests: int = 3,
    ):
        """Initialize circuit breaker.
        
        Args:
            threshold: Number of failures before opening circuit
            timeout: Time in seconds before trying half-open state
            half_open_requests: Number of requests to test in half-open state
        """
        self.threshold = threshold
        self.timeout = timeout
        self.half_open_requests = half_open_requests
        
        # Circuit state tracking
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.half_open_count = 0
        
        # Node-specific tracking
        self.node_states: Dict[str, Dict[str, Any]] = {}

    async def setup(self) -> None:
        """Setup circuit breaker."""
        logger.info("Circuit breaker initialized",
                   threshold=self.threshold,
                   timeout=self.timeout)

    async def cleanup(self) -> None:
        """Cleanup circuit breaker resources."""
        logger.info("Circuit breaker cleanup")

    def _get_node_state(self, node: str) -> Dict[str, Any]:
        """Get or create state for a specific node."""
        if node not in self.node_states:
            self.node_states[node] = {
                "state": CircuitState.CLOSED,
                "failure_count": 0,
                "success_count": 0,
                "last_failure_time": None,
                "half_open_count": 0,
            }
        return self.node_states[node]

    def _update_metrics(self, operation: str, node: str, state: CircuitState) -> None:
        """Update circuit breaker metrics."""
        metrics_collector.update_circuit_breaker(
            operation=operation,
            node=node,
            state=state.value
        )

    async def call(
        self,
        func: Callable,
        operation: str = "unknown",
        node: str = "default",
        *args,
        **kwargs
    ) -> Any:
        """Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            operation: Operation name for tracking
            node: Node name for tracking
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        node_state = self._get_node_state(node)
        
        # Check circuit state
        current_state = self._get_state(node_state)
        
        if current_state == CircuitState.OPEN:
            logger.warning("Circuit breaker open",
                          operation=operation,
                          node=node)
            raise CircuitBreakerError(
                operation=operation,
                node=node,
                threshold=self.threshold,
                failures=node_state["failure_count"]
            )
        
        try:
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Record success
            self._record_success(node_state)
            
            # Check if we can close circuit from half-open
            if current_state == CircuitState.HALF_OPEN:
                node_state["half_open_count"] += 1
                if node_state["half_open_count"] >= self.half_open_requests:
                    self._close_circuit(node_state)
                    logger.info("Circuit breaker closed",
                               operation=operation,
                               node=node)
            
            return result
            
        except Exception as e:
            # Record failure
            self._record_failure(node_state)
            
            # Check if we should open circuit
            if node_state["failure_count"] >= self.threshold:
                self._open_circuit(node_state)
                logger.error("Circuit breaker opened",
                            operation=operation,
                            node=node,
                            failures=node_state["failure_count"])
            
            # Update metrics
            self._update_metrics(operation, node, node_state["state"])
            
            # Re-raise the original exception
            raise

    def _get_state(self, node_state: Dict[str, Any]) -> CircuitState:
        """Get current circuit state for a node."""
        if node_state["state"] == CircuitState.OPEN:
            # Check if timeout has passed
            if node_state["last_failure_time"]:
                time_since_failure = time.time() - node_state["last_failure_time"]
                if time_since_failure >= self.timeout:
                    # Try half-open state
                    node_state["state"] = CircuitState.HALF_OPEN
                    node_state["half_open_count"] = 0
                    logger.info("Circuit breaker entering half-open state")
        
        return node_state["state"]

    def _record_success(self, node_state: Dict[str, Any]) -> None:
        """Record successful operation."""
        node_state["success_count"] += 1
        
        # Reset failure count on success in closed state
        if node_state["state"] == CircuitState.CLOSED:
            node_state["failure_count"] = 0

    def _record_failure(self, node_state: Dict[str, Any]) -> None:
        """Record failed operation."""
        node_state["failure_count"] += 1
        node_state["last_failure_time"] = time.time()
        
        # If in half-open state, immediately open circuit on failure
        if node_state["state"] == CircuitState.HALF_OPEN:
            self._open_circuit(node_state)

    def _open_circuit(self, node_state: Dict[str, Any]) -> None:
        """Open the circuit."""
        node_state["state"] = CircuitState.OPEN
        node_state["last_failure_time"] = time.time()

    def _close_circuit(self, node_state: Dict[str, Any]) -> None:
        """Close the circuit."""
        node_state["state"] = CircuitState.CLOSED
        node_state["failure_count"] = 0
        node_state["half_open_count"] = 0

    def is_healthy(self) -> bool:
        """Check if circuit breaker is healthy."""
        # Check if any circuits are open
        for node, state in self.node_states.items():
            if state["state"] == CircuitState.OPEN:
                return False
        return True

    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status."""
        status = {
            "threshold": self.threshold,
            "timeout": self.timeout,
            "nodes": {}
        }
        
        for node, state in self.node_states.items():
            status["nodes"][node] = {
                "state": state["state"].name,
                "failure_count": state["failure_count"],
                "success_count": state["success_count"],
                "last_failure_time": state["last_failure_time"],
            }
        
        return status

    def reset(self, node: Optional[str] = None) -> None:
        """Reset circuit breaker state.
        
        Args:
            node: Specific node to reset, or None to reset all
        """
        if node:
            if node in self.node_states:
                self._close_circuit(self.node_states[node])
                logger.info("Circuit breaker reset", node=node)
        else:
            # Reset all nodes
            for node_name, node_state in self.node_states.items():
                self._close_circuit(node_state)
            logger.info("All circuit breakers reset")
