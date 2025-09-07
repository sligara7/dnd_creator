"""Core utilities for cache service."""

from .config import settings
from .exceptions import (
    CacheServiceError,
    CacheOperationError,
    CacheKeyError,
    CacheConnectionError,
    CacheConsistencyError,
    CacheOverflowError,
    CacheEvictionError,
    CircuitBreakerError,
    ReplicationError,
    InvalidKeyspaceError,
    BatchOperationError,
)

__all__ = [
    "settings",
    "CacheServiceError",
    "CacheOperationError",
    "CacheKeyError",
    "CacheConnectionError",
    "CacheConsistencyError",
    "CacheOverflowError",
    "CacheEvictionError",
    "CircuitBreakerError",
    "ReplicationError",
    "InvalidKeyspaceError",
    "BatchOperationError",
]
