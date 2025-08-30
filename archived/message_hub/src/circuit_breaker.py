"""
Circuit Breaker Pattern Implementation

Provides service protection with automatic failure detection and recovery.
"""

from enum import Enum
from datetime import datetime, timedelta
import asyncio
from typing import Dict, Optional, Callable, Any
import structlog

logger = structlog.get_logger()

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation, requests allowed
    OPEN = "open"         # Failure detected, requests blocked
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """
    Circuit breaker implementation with failure detection and automatic recovery.
    
    Protects services from cascade failures by temporarily blocking requests
    when a failure threshold is reached.
    """
    
    def __init__(self,
                 name: str,
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 half_open_max_calls: int = 2):
        """Initialize circuit breaker."""
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        # State management
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_successes = 0
        
        # Metrics
        self.total_failures = 0
        self.total_successes = 0
        self.last_state_change: Optional[datetime] = None
        
        logger.info("circuit_breaker_initialized",
                   name=name,
                   failure_threshold=failure_threshold,
                   recovery_timeout=recovery_timeout)
    
    async def call(self,
                  protected_operation: Callable[..., Any],
                  *args,
                  **kwargs) -> Any:
        """
        Execute a protected operation through the circuit breaker.
        
        Args:
            protected_operation: Async function to execute
            *args, **kwargs: Arguments for the protected operation
        
        Returns:
            Result of the protected operation
        
        Raises:
            CircuitBreakerOpen: If circuit is open
            Exception: Any exception from the protected operation
        """
        await self._check_state_transition()
        
        if self.state == CircuitState.OPEN:
            raise CircuitBreakerOpen(
                f"Circuit breaker '{self.name}' is OPEN. "
                f"Next retry after: {self._get_remaining_timeout()} seconds"
            )
        
        try:
            # Execute operation
            result = await protected_operation(*args, **kwargs)
            
            # Handle success
            await self._handle_success()
            return result
            
        except Exception as e:
            # Handle failure
            await self._handle_failure(e)
            raise
    
    async def _check_state_transition(self):
        """Check and update circuit breaker state."""
        if self.state == CircuitState.OPEN:
            if await self._should_transition_to_half_open():
                await self._transition_state(CircuitState.HALF_OPEN)
                
        elif self.state == CircuitState.HALF_OPEN:
            if self.half_open_successes >= self.half_open_max_calls:
                await self._transition_state(CircuitState.CLOSED)
    
    async def _handle_success(self):
        """Handle successful operation."""
        self.total_successes += 1
        
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_successes += 1
            
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
            self.last_failure_time = None
    
    async def _handle_failure(self, error: Exception):
        """Handle operation failure."""
        self.total_failures += 1
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                await self._transition_state(CircuitState.OPEN)
                
        elif self.state == CircuitState.HALF_OPEN:
            await self._transition_state(CircuitState.OPEN)
    
    async def _should_transition_to_half_open(self) -> bool:
        """Check if circuit should transition from OPEN to HALF-OPEN."""
        if not self.last_failure_time:
            return False
            
        elapsed = datetime.utcnow() - self.last_failure_time
        return elapsed.total_seconds() >= self.recovery_timeout
    
    async def _transition_state(self, new_state: CircuitState):
        """Transition circuit breaker to a new state."""
        old_state = self.state
        self.state = new_state
        self.last_state_change = datetime.utcnow()
        
        # Reset state-specific counters
        if new_state == CircuitState.CLOSED:
            self.failure_count = 0
            self.last_failure_time = None
        elif new_state == CircuitState.HALF_OPEN:
            self.half_open_successes = 0
        
        logger.info("circuit_breaker_state_change",
                   name=self.name,
                   old_state=old_state.value,
                   new_state=new_state.value)
    
    def _get_remaining_timeout(self) -> int:
        """Get remaining timeout before next retry attempt."""
        if not self.last_failure_time:
            return 0
            
        elapsed = datetime.utcnow() - self.last_failure_time
        remaining = self.recovery_timeout - int(elapsed.total_seconds())
        return max(0, remaining)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "total_failures": self.total_failures,
            "total_successes": self.total_successes,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_state_change": self.last_state_change.isoformat() if self.last_state_change else None,
            "remaining_timeout": self._get_remaining_timeout()
        }

class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open."""
    pass
