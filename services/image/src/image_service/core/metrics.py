"""Metrics and monitoring for the image service."""

import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from prometheus_client import Counter, Gauge, Histogram, REGISTRY
from prometheus_client.metrics import MetricWrapperBase

from image_service.core.config import get_settings
from image_service.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Task metrics
TASKS_TOTAL = Counter(
    "image_tasks_total",
    "Total number of image generation tasks",
    ["type", "status"],
)

TASKS_IN_PROGRESS = Gauge(
    "image_tasks_in_progress",
    "Number of tasks currently being processed",
    ["type"],
)

TASK_PROCESSING_TIME = Histogram(
    "image_task_processing_seconds",
    "Time spent processing tasks",
    ["type", "stage"],
    buckets=[1, 5, 10, 30, 60, 120, 300],  # 1s to 5m
)

# Queue metrics
QUEUE_SIZE = Gauge(
    "image_queue_size",
    "Current size of task queues",
    ["queue"],
)

QUEUE_PROCESSING_TIME = Histogram(
    "image_queue_processing_seconds",
    "Time spent processing queue items",
    ["queue"],
    buckets=[0.001, 0.01, 0.1, 0.5, 1, 5, 10],  # 1ms to 10s
)

# API metrics
API_REQUESTS_TOTAL = Counter(
    "image_api_requests_total",
    "Total number of API requests",
    ["method", "endpoint", "status"],
)

API_REQUEST_DURATION = Histogram(
    "image_api_request_seconds",
    "API request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.1, 0.5, 1, 2.5, 5, 10],  # 10ms to 10s
)

# Cache metrics
CACHE_OPERATIONS = Counter(
    "image_cache_operations_total",
    "Total number of cache operations",
    ["operation", "status"],
)

CACHE_HIT_RATIO = Gauge(
    "image_cache_hit_ratio",
    "Cache hit ratio",
)

# GetImg.AI metrics
API_CALLS = Counter(
    "getimg_api_calls_total",
    "Total number of GetImg.AI API calls",
    ["operation", "status"],
)

API_LATENCY = Histogram(
    "getimg_api_latency_seconds",
    "GetImg.AI API latency in seconds",
    ["operation"],
    buckets=[0.1, 0.5, 1, 2.5, 5, 10, 30],  # 100ms to 30s
)

# Storage metrics
STORAGE_OPERATIONS = Counter(
    "image_storage_operations_total",
    "Total number of storage operations",
    ["operation", "status"],
)

STORAGE_SIZE = Gauge(
    "image_storage_size_bytes",
    "Total size of stored images in bytes",
)


class MetricsManager:
    """Manager for service metrics."""

    def __init__(self):
        """Initialize metrics manager."""
        self._cache_hits = 0
        self._cache_total = 0
        self._last_update = datetime.utcnow()

    def track_task(self, task_type: str, status: str) -> None:
        """Track task metrics."""
        TASKS_TOTAL.labels(type=task_type, status=status).inc()

    def track_task_start(self, task_type: str) -> None:
        """Track task start."""
        TASKS_IN_PROGRESS.labels(type=task_type).inc()

    def track_task_end(self, task_type: str) -> None:
        """Track task end."""
        TASKS_IN_PROGRESS.labels(type=task_type).dec()

    def track_processing_time(
        self,
        task_type: str,
        stage: str,
        duration: float,
    ) -> None:
        """Track task processing time."""
        TASK_PROCESSING_TIME.labels(
            type=task_type,
            stage=stage,
        ).observe(duration)

    def track_queue_size(self, queue: str, size: int) -> None:
        """Track queue size."""
        QUEUE_SIZE.labels(queue=queue).set(size)

    def track_queue_operation(self, queue: str, duration: float) -> None:
        """Track queue operation."""
        QUEUE_PROCESSING_TIME.labels(queue=queue).observe(duration)

    def track_api_request(
        self,
        method: str,
        endpoint: str,
        status: int,
        duration: float,
    ) -> None:
        """Track API request."""
        API_REQUESTS_TOTAL.labels(
            method=method,
            endpoint=endpoint,
            status=str(status),
        ).inc()
        API_REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint,
        ).observe(duration)

    def track_cache_operation(
        self,
        operation: str,
        hit: bool,
    ) -> None:
        """Track cache operation."""
        status = "hit" if hit else "miss"
        CACHE_OPERATIONS.labels(
            operation=operation,
            status=status,
        ).inc()

        # Update hit ratio
        self._cache_total += 1
        if hit:
            self._cache_hits += 1

        # Update ratio every minute
        now = datetime.utcnow()
        if now - self._last_update > timedelta(minutes=1):
            if self._cache_total > 0:
                ratio = self._cache_hits / self._cache_total
                CACHE_HIT_RATIO.set(ratio)
            self._last_update = now

    def track_api_call(
        self,
        operation: str,
        status: str,
        duration: float,
    ) -> None:
        """Track GetImg.AI API call."""
        API_CALLS.labels(
            operation=operation,
            status=status,
        ).inc()
        API_LATENCY.labels(operation=operation).observe(duration)

    def track_storage_operation(
        self,
        operation: str,
        status: str,
        size: Optional[int] = None,
    ) -> None:
        """Track storage operation."""
        STORAGE_OPERATIONS.labels(
            operation=operation,
            status=status,
        ).inc()
        if size is not None:
            STORAGE_SIZE.inc(size)


# Global metrics manager instance
metrics = MetricsManager()


def track_task_metrics(task_type: str) -> Callable:
    """Decorator to track task metrics."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.monotonic()
            metrics.track_task_start(task_type)

            try:
                result = await func(*args, **kwargs)
                metrics.track_task(task_type, "success")
                return result
            except Exception as e:
                metrics.track_task(task_type, "error")
                raise
            finally:
                duration = time.monotonic() - start_time
                metrics.track_processing_time(task_type, "total", duration)
                metrics.track_task_end(task_type)

        return wrapper

    return decorator


def track_queue_metrics(queue: str) -> Callable:
    """Decorator to track queue metrics."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.monotonic()

            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.monotonic() - start_time
                metrics.track_queue_operation(queue, duration)

        return wrapper

    return decorator


def track_api_metrics(method: str, endpoint: str) -> Callable:
    """Decorator to track API metrics."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.monotonic()

            try:
                result = await func(*args, **kwargs)
                duration = time.monotonic() - start_time
                metrics.track_api_request(method, endpoint, 200, duration)
                return result
            except Exception as e:
                duration = time.monotonic() - start_time
                metrics.track_api_request(method, endpoint, 500, duration)
                raise

        return wrapper

    return decorator
