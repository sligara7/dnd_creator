"""Circuit breaker implementation for Message Hub."""

import enum
import time
import asyncio
from typing import Any, Callable, Optional
from datetime import datetime, timedelta

class CircuitBreakerState(enum.Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"     # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    """Circuit breaker for external service calls."""

    class CircuitBreakerOpen(Exception):
        """Exception raised when circuit breaker is open."""
        pass

    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: float = 60.0,
        half_open_timeout: float = 30.0,
        on_state_change: Optional[Callable[[CircuitBreakerState, CircuitBreakerState], None]] = None
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            reset_timeout: Time to wait before attempting reset (seconds)
            half_open_timeout: Time to wait in half-open state (seconds)
            on_state_change: Optional callback for state changes
        """
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_timeout = half_open_timeout
        self.on_state_change = on_state_change

        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._state_change_time: datetime = datetime.now()
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitBreakerState:
        """Get current circuit breaker state."""
        return self._state

    @property
    def failure_count(self) -> int:
        """Get current failure count."""
        return self._failure_count

    @property
    def last_failure_time(self) -> Optional[datetime]:
        """Get last failure time."""
        return self._last_failure_time

    async def execute(self, operation: Callable[..., Any], *args, **kwargs) -> Any:
        """Execute operation with circuit breaker protection.

        Args:
            operation: Async function to execute
            *args: Positional arguments for operation
            **kwargs: Keyword arguments for operation

        Returns:
            Operation result

        Raises:
            CircuitBreakerOpen: If circuit is open
            Any exception from operation
        """
        async with self._lock:
            # Check if we should transition from open to half-open
            if self._state == CircuitBreakerState.OPEN:
                if datetime.now() - self._state_change_time > timedelta(seconds=self.reset_timeout):
                    await self._change_state(CircuitBreakerState.HALF_OPEN)

            # Check if we can proceed
            if self._state == CircuitBreakerState.OPEN:
                raise self.CircuitBreakerOpen("Circuit breaker is open")

        try:
            result = await operation(*args, **kwargs)

            # Success in half-open state closes the circuit
            if self._state == CircuitBreakerState.HALF_OPEN:
                async with self._lock:
                    await self._change_state(CircuitBreakerState.CLOSED)
                    self._failure_count = 0
                    self._last_failure_time = None

            return result

        except Exception as e:
            async with self._lock:
                self._failure_count += 1
                self._last_failure_time = datetime.now()

                # Open circuit if threshold reached
                if self._state == CircuitBreakerState.CLOSED and self._failure_count >= self.failure_threshold:
                    await self._change_state(CircuitBreakerState.OPEN)
                # Any failure in half-open state opens circuit
                elif self._state == CircuitBreakerState.HALF_OPEN:
                    await self._change_state(CircuitBreakerState.OPEN)

            raise

    async def _change_state(self, new_state: CircuitBreakerState) -> None:
        """Change circuit breaker state."""
        old_state = self._state
        self._state = new_state
        self._state_change_time = datetime.now()
        
        if self.on_state_change:
            await self.on_state_change(old_state, new_state)