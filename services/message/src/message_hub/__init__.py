"""Message Hub for D&D Character Creator.

The Message Hub acts as the central communication backbone for the D&D Character Creator system.
It provides reliable message delivery, service coordination, and event management.
"""

__version__ = "0.1.0"

from .core.exceptions import (
    MessageHubError,
    MessageHubConnectionError,
    MessageHubDeliveryError,
    MessageHubCircuitBreakerError,
    MessageHubRetryError,
    ServiceUnavailable,
    ServiceNotFound,
    MessageValidationError,
    RoutingError,
    EventStoreError,
    RetryExhausted,
    TransactionError,
)

from .core.models.base import ServiceType, MessageType

__all__ = [
    "__version__",
    "MessageHubError",
    "MessageHubConnectionError",
    "MessageHubDeliveryError",
    "MessageHubCircuitBreakerError",
    "MessageHubRetryError",
    "ServiceUnavailable",
    "ServiceNotFound",
    "MessageValidationError",
    "RoutingError",
    "EventStoreError",
    "RetryExhausted",
    "TransactionError",
    "ServiceType",
    "MessageType",
]