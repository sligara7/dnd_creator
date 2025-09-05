from datetime import datetime
from typing import Any, Dict, List, Optional


class MessageHubError(Exception):
    """Base exception for Message Hub errors"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()


class CircuitBreakerOpen(MessageHubError):
    """Raised when circuit breaker is open"""

    def __init__(self, service: str, timeout: int):
        super().__init__(
            message=f"Circuit breaker is open for service {service}",
            error_code="CIRCUIT_BREAKER_OPEN",
            status_code=503,
            details={
                "service": service,
                "timeout": timeout,
            },
        )


class ServiceNotFound(MessageHubError):
    """Raised when service is not found in registry"""

    def __init__(self, service: str):
        super().__init__(
            message=f"Service {service} not found",
            error_code="SERVICE_NOT_FOUND",
            status_code=404,
            details={"service": service},
        )


class ServiceUnavailable(MessageHubError):
    """Raised when service is unavailable"""

    def __init__(self, service: str, reason: str):
        super().__init__(
            message=f"Service {service} is unavailable: {reason}",
            error_code="SERVICE_UNAVAILABLE",
            status_code=503,
            details={
                "service": service,
                "reason": reason,
            },
        )


class MessageValidationError(MessageHubError):
    """Raised when message validation fails"""

    def __init__(self, errors: List[str]):
        super().__init__(
            message="Message validation failed",
            error_code="MESSAGE_VALIDATION_ERROR",
            status_code=400,
            details={"errors": errors},
        )


class RoutingError(MessageHubError):
    """Raised when message routing fails"""

    def __init__(self, source: str, destination: str, reason: str):
        super().__init__(
            message=f"Failed to route message from {source} to {destination}: {reason}",
            error_code="ROUTING_ERROR",
            status_code=500,
            details={
                "source": source,
                "destination": destination,
                "reason": reason,
            },
        )


class EventStoreError(MessageHubError):
    """Raised when event store operation fails"""

    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"Event store operation {operation} failed: {reason}",
            error_code="EVENT_STORE_ERROR",
            status_code=500,
            details={
                "operation": operation,
                "reason": reason,
            },
        )


class RetryExhausted(MessageHubError):
    """Raised when message retries are exhausted"""

    def __init__(
        self,
        source: str,
        destination: str,
        message_id: str,
        max_retries: int,
    ):
        super().__init__(
            message=f"Max retries ({max_retries}) exhausted for message {message_id}",
            error_code="RETRY_EXHAUSTED",
            status_code=500,
            details={
                "source": source,
                "destination": destination,
                "message_id": message_id,
                "max_retries": max_retries,
            },
        )


class TransactionError(MessageHubError):
    """Raised when transaction operation fails"""

    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"Transaction operation {operation} failed: {reason}",
            error_code="TRANSACTION_ERROR",
            status_code=500,
            details={
                "operation": operation,
                "reason": reason,
            },
        )
