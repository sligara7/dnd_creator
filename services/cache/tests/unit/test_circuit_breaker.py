"""Tests for circuit breaker behavior."""

import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest
from cache_service.circuit_breaker import CircuitBreaker, CircuitBreakerState
from tests.utils import wait_for_condition, AsyncContextManager

@pytest.mark.unit
class TestCircuitBreaker:
    """Test circuit breaker behavior."""

    @pytest.fixture
    def config(self):
        """Circuit breaker configuration."""
        return {
            "failure_threshold": 3,
            "reset_timeout": 5.0,
            "half_open_timeout": 2.0
        }

    @pytest.fixture
    def breaker(self, config):
        """Create a circuit breaker instance."""
        return CircuitBreaker(**config)

    async def test_initial_state(self, breaker):
        """Test initial circuit breaker state."""
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 0
        assert breaker.last_failure_time is None

    async def test_successful_operation(self, breaker):
        """Test successful operation execution."""
        # Arrange
        async def operation():
            return "success"

        # Act
        result = await breaker.execute(operation)

        # Assert
        assert result == "success"
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 0

    async def test_failure_threshold(self, breaker, config):
        """Test failure threshold triggering."""
        # Arrange
        async def failing_operation():
            raise Exception("Operation failed")

        # Act
        # Execute failing operation up to threshold
        for _ in range(config["failure_threshold"]):
            with pytest.raises(Exception):
                await breaker.execute(failing_operation)

        # Assert
        assert breaker.state == CircuitBreakerState.OPEN
        assert breaker.failure_count == config["failure_threshold"]

        # Try one more time - should raise CircuitBreakerOpen
        with pytest.raises(CircuitBreaker.CircuitBreakerOpen):
            await breaker.execute(failing_operation)

    async def test_reset_timeout(self, breaker, config):
        """Test reset timeout behavior."""
        # Arrange
        async def failing_operation():
            raise Exception("Operation failed")

        # Trigger open state
        for _ in range(config["failure_threshold"]):
            with pytest.raises(Exception):
                await breaker.execute(failing_operation)

        # Act
        # Wait for reset timeout
        await asyncio.sleep(config["reset_timeout"])

        # Execute a successful operation
        async def successful_operation():
            return "success"

        # First execution should be in HALF_OPEN state
        result = await breaker.execute(successful_operation)

        # Assert
        assert result == "success"
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 0

    async def test_half_open_state(self, breaker, config):
        """Test half-open state behavior."""
        # Arrange
        async def failing_operation():
            raise Exception("Operation failed")

        # Trigger open state
        for _ in range(config["failure_threshold"]):
            with pytest.raises(Exception):
                await breaker.execute(failing_operation)

        # Wait for half-open timeout
        await asyncio.sleep(config["half_open_timeout"])

        # Act & Assert
        assert breaker.state == CircuitBreakerState.HALF_OPEN

        # Fail in half-open should immediately open
        with pytest.raises(Exception):
            await breaker.execute(failing_operation)
        assert breaker.state == CircuitBreakerState.OPEN

    async def test_concurrent_operations(self, breaker):
        """Test concurrent operations behavior."""
        # Arrange
        async def slow_operation():
            await asyncio.sleep(0.1)
            return "success"

        # Act
        # Execute multiple operations concurrently
        results = await asyncio.gather(*(
            breaker.execute(slow_operation)
            for _ in range(5)
        ))

        # Assert
        assert all(result == "success" for result in results)
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 0

    async def test_mixed_success_failure(self, breaker):
        """Test mixed success and failure operations."""
        # Arrange
        success_count = 0
        failure_count = 0

        async def mixed_operation():
            nonlocal success_count, failure_count
            if success_count < 2:
                success_count += 1
                return "success"
            else:
                failure_count += 1
                raise Exception("Operation failed")

        # Act & Assert
        # First two operations succeed
        assert await breaker.execute(mixed_operation) == "success"
        assert await breaker.execute(mixed_operation) == "success"
        assert breaker.failure_count == 0

        # Next three operations fail
        for _ in range(3):
            with pytest.raises(Exception):
                await breaker.execute(mixed_operation)

        assert breaker.state == CircuitBreakerState.OPEN
        assert breaker.failure_count == 3

    @pytest.mark.parametrize("error", [
        Exception("Generic error"),
        TimeoutError("Operation timeout"),
        ConnectionError("Connection failed"),
        ValueError("Invalid value")
    ])
    async def test_different_exceptions(self, breaker, error):
        """Test circuit breaker with different types of exceptions."""
        # Arrange
        async def failing_operation():
            raise error

        # Act
        with pytest.raises(type(error)):
            await breaker.execute(failing_operation)

        # Assert
        assert breaker.failure_count == 1
        assert breaker.last_failure_time is not None

    async def test_state_transition_callbacks(self):
        """Test state transition callback notifications."""
        # Arrange
        on_state_change = AsyncMock()
        config = {
            "failure_threshold": 2,
            "reset_timeout": 5.0,
            "half_open_timeout": 2.0,
            "on_state_change": on_state_change
        }
        breaker = CircuitBreaker(**config)

        async def failing_operation():
            raise Exception("Operation failed")

        # Act
        # Trigger state change to OPEN
        for _ in range(config["failure_threshold"]):
            with pytest.raises(Exception):
                await breaker.execute(failing_operation)

        # Assert
        on_state_change.assert_awaited_with(
            CircuitBreakerState.CLOSED,
            CircuitBreakerState.OPEN
        )

    async def test_custom_failure_predicates(self):
        """Test custom failure predicate functions."""
        # Arrange
        def is_critical_error(error: Exception) -> bool:
            return isinstance(error, (ConnectionError, TimeoutError))

        config = {
            "failure_threshold": 2,
            "reset_timeout": 5.0,
            "half_open_timeout": 2.0,
            "failure_predicate": is_critical_error
        }
        breaker = CircuitBreaker(**config)

        # Act & Assert
        # Non-critical errors don't increment failure count
        for _ in range(3):
            with pytest.raises(ValueError):
                await breaker.execute(lambda: asyncio.sleep(0))
                raise ValueError("Non-critical error")

        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 0

        # Critical errors do increment failure count
        for _ in range(2):
            with pytest.raises(ConnectionError):
                await breaker.execute(lambda: asyncio.sleep(0))
                raise ConnectionError("Critical error")

        assert breaker.state == CircuitBreakerState.OPEN
        assert breaker.failure_count == 2

    async def test_timeout_handling(self):
        """Test timeout handling in circuit breaker."""
        # Arrange
        config = {
            "failure_threshold": 2,
            "reset_timeout": 5.0,
            "half_open_timeout": 2.0,
            "operation_timeout": 1.0
        }
        breaker = CircuitBreaker(**config)

        async def slow_operation():
            await asyncio.sleep(2.0)  # Longer than timeout
            return "success"

        # Act & Assert
        with pytest.raises(asyncio.TimeoutError):
            await breaker.execute(slow_operation)

        assert breaker.failure_count == 1

        # Second timeout should open circuit
        with pytest.raises(asyncio.TimeoutError):
            await breaker.execute(slow_operation)

        assert breaker.state == CircuitBreakerState.OPEN