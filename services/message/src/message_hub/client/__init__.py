"""MessageHub client package for inter-service communication.

This package provides a Python client library for services to integrate with the MessageHub.
It handles message delivery, event subscriptions, circuit breaker patterns, and monitoring.
"""

from .client import (
    MessageHubClient,
    CircuitBreaker,
    CircuitBreakerConfig,
    MESSAGE_COUNTER,
    MESSAGE_LATENCY
)

__all__ = [
    'MessageHubClient',
    'CircuitBreaker',
    'CircuitBreakerConfig',
    'MESSAGE_COUNTER',
    'MESSAGE_LATENCY'
]