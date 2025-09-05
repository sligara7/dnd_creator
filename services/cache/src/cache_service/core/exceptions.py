from datetime import datetime
from typing import Any, Dict, List, Optional


class CacheServiceError(Exception):
    """Base exception for Cache Service errors"""

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


class CacheOperationError(CacheServiceError):
    """Cache operation error"""

    def __init__(
        self,
        operation: str,
        key: str,
        error: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details.update({
            "operation": operation,
            "key": key,
        })
        super().__init__(
            message=f"Cache operation {operation} failed for key {key}: {error}",
            error_code="CACHE_OPERATION_ERROR",
            status_code=500,
            details=details,
        )


class CacheKeyError(CacheServiceError):
    """Cache key error"""

    def __init__(self, message: str, key: str):
        super().__init__(
            message=f"Cache key error: {message}",
            error_code="CACHE_KEY_ERROR",
            status_code=400,
            details={"key": key},
        )


class CacheConnectionError(CacheServiceError):
    """Cache connection error"""

    def __init__(
        self,
        node: str,
        error: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details["node"] = node
        super().__init__(
            message=f"Cache connection error for node {node}: {error}",
            error_code="CACHE_CONNECTION_ERROR",
            status_code=500,
            details=details,
        )


class CacheConsistencyError(CacheServiceError):
    """Cache consistency error"""

    def __init__(
        self,
        key: str,
        error: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details["key"] = key
        super().__init__(
            message=f"Cache consistency error for key {key}: {error}",
            error_code="CACHE_CONSISTENCY_ERROR",
            status_code=500,
            details=details,
        )


class CacheOverflowError(CacheServiceError):
    """Cache overflow error"""

    def __init__(self, message: str, used: int, limit: int):
        super().__init__(
            message=f"Cache overflow: {message}",
            error_code="CACHE_OVERFLOW_ERROR",
            status_code=500,
            details={
                "used": used,
                "limit": limit,
                "available": limit - used,
            },
        )


class CacheEvictionError(CacheServiceError):
    """Cache eviction error"""

    def __init__(
        self,
        policy: str,
        error: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details["policy"] = policy
        super().__init__(
            message=f"Cache eviction error with policy {policy}: {error}",
            error_code="CACHE_EVICTION_ERROR",
            status_code=500,
            details=details,
        )


class CircuitBreakerError(CacheServiceError):
    """Circuit breaker error"""

    def __init__(
        self,
        operation: str,
        node: str,
        threshold: int,
        failures: int,
    ):
        super().__init__(
            message=f"Circuit breaker open for {operation} on node {node}",
            error_code="CIRCUIT_BREAKER_ERROR",
            status_code=503,
            details={
                "operation": operation,
                "node": node,
                "threshold": threshold,
                "failures": failures,
            },
        )


class ReplicationError(CacheServiceError):
    """Replication error"""

    def __init__(
        self,
        primary: str,
        replica: str,
        error: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details.update({
            "primary": primary,
            "replica": replica,
        })
        super().__init__(
            message=f"Replication error: {error}",
            error_code="REPLICATION_ERROR",
            status_code=500,
            details=details,
        )


class InvalidKeyspaceError(CacheServiceError):
    """Invalid keyspace error"""

    def __init__(
        self,
        service: str,
        keyspace: str,
        allowed_keyspaces: List[str],
    ):
        super().__init__(
            message=f"Invalid keyspace {keyspace} for service {service}",
            error_code="INVALID_KEYSPACE_ERROR",
            status_code=400,
            details={
                "service": service,
                "keyspace": keyspace,
                "allowed_keyspaces": allowed_keyspaces,
            },
        )


class BatchOperationError(CacheServiceError):
    """Batch operation error"""

    def __init__(
        self,
        operation: str,
        total: int,
        failed: int,
        errors: List[Dict[str, Any]],
    ):
        super().__init__(
            message=f"Batch operation {operation} partially failed: {failed}/{total} operations failed",
            error_code="BATCH_OPERATION_ERROR",
            status_code=500,
            details={
                "operation": operation,
                "total": total,
                "failed": failed,
                "errors": errors,
            },
        )
