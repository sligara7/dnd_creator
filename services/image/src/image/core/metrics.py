"""Prometheus metrics for monitoring image generation tasks."""
import logging
from datetime import datetime
from typing import Optional

from prometheus_client import Counter, Gauge, Histogram
from prometheus_client.utils import INF

logger = logging.getLogger(__name__)

# Task operation metrics
TASK_OPERATIONS = Counter(
    "image_task_operations_total",
    "Number of task operations",
    ["operation", "task_type", "status"]
)

# Task timing metrics
TASK_PROCESSING_TIME = Histogram(
    "image_task_processing_seconds",
    "Time spent processing tasks",
    ["task_type"],
    buckets=(1, 5, 10, 30, 60, 120, 300, 600, INF)
)

TASK_QUEUE_TIME = Histogram(
    "image_task_queue_time_seconds",
    "Time tasks spend in queue",
    ["task_type", "priority"],
    buckets=(1, 5, 10, 30, 60, 120, 300, 600, INF)
)

# Queue state metrics
QUEUE_SIZE = Gauge(
    "image_queue_size",
    "Number of tasks in queue",
    ["priority"]
)

PROCESSING_TASKS = Gauge(
    "image_processing_tasks",
    "Number of tasks currently being processed",
    ["task_type"]
)

TASK_RETRIES = Counter(
    "image_task_retries_total",
    "Number of task retry attempts",
    ["task_type"]
)

# Resource metrics
WORKER_COUNT = Gauge(
    "image_worker_count",
    "Number of active task workers"
)

MEMORY_USAGE = Gauge(
    "image_memory_usage_bytes",
    "Memory usage of image service",
    ["component"]  # worker, redis, etc.
)

# Error metrics
TASK_ERRORS = Counter(
    "image_task_errors_total",
    "Number of task errors",
    ["task_type", "error_type"]
)

# Performance metrics
GENERATION_SPEED = Histogram(
    "image_generation_speed_pixels_per_second",
    "Image generation speed in pixels per second",
    ["task_type"],
    buckets=(100000, 250000, 500000, 1000000, 2500000, 5000000, INF)
)

CACHE_OPERATIONS = Counter(
    "image_cache_operations_total",
    "Number of cache operations",
    ["operation", "result"]  # get/set, hit/miss
)

# Batch metrics
BATCH_SIZE = Histogram(
    "image_batch_size",
    "Size of task batches",
    buckets=(2, 5, 10, 20, 50, 100, INF)
)

BATCH_PROCESSING_TIME = Histogram(
    "image_batch_processing_seconds",
    "Time spent processing task batches",
    buckets=(1, 5, 10, 30, 60, 120, 300, 600, INF)
)


def record_task_queued(task_type: str) -> None:
    """Record metrics for a newly queued task.

    Args:
        task_type: Type of task queued
    """
    TASK_OPERATIONS.labels(
        operation="queue",
        task_type=task_type,
        status="pending"
    ).inc()


def record_task_started(task_type: str, queue_time: float) -> None:
    """Record metrics for a task starting processing.

    Args:
        task_type: Type of task started
        queue_time: Time spent in queue (seconds)
    """
    TASK_OPERATIONS.labels(
        operation="start",
        task_type=task_type,
        status="processing"
    ).inc()
    TASK_QUEUE_TIME.labels(
        task_type=task_type,
        priority="normal"  # TODO: Get actual priority
    ).observe(queue_time)
    PROCESSING_TASKS.labels(task_type=task_type).inc()


def record_task_completed(
    task_type: str,
    processing_time: float,
    pixels: Optional[int] = None
) -> None:
    """Record metrics for a completed task.

    Args:
        task_type: Type of task completed
        processing_time: Time spent processing (seconds)
        pixels: Optional number of pixels generated
    """
    TASK_OPERATIONS.labels(
        operation="complete",
        task_type=task_type,
        status="completed"
    ).inc()
    TASK_PROCESSING_TIME.labels(task_type=task_type).observe(processing_time)
    PROCESSING_TASKS.labels(task_type=task_type).dec()

    if pixels is not None:
        pixels_per_second = pixels / processing_time
        GENERATION_SPEED.labels(task_type=task_type).observe(pixels_per_second)


def record_task_failed(task_type: str, error_type: str, retried: bool) -> None:
    """Record metrics for a failed task.

    Args:
        task_type: Type of task that failed
        error_type: Type of error encountered
        retried: Whether the task was queued for retry
    """
    status = "retried" if retried else "failed"
    TASK_OPERATIONS.labels(
        operation="fail",
        task_type=task_type,
        status=status
    ).inc()
    TASK_ERRORS.labels(
        task_type=task_type,
        error_type=error_type
    ).inc()
    if retried:
        TASK_RETRIES.labels(task_type=task_type).inc()
    PROCESSING_TASKS.labels(task_type=task_type).dec()


def record_queue_size(priority: str, size: int) -> None:
    """Record current queue size for a priority level.

    Args:
        priority: Priority level
        size: Current queue size
    """
    QUEUE_SIZE.labels(priority=priority).set(size)


def record_worker_count(count: int) -> None:
    """Record number of active workers.

    Args:
        count: Number of workers
    """
    WORKER_COUNT.set(count)


def record_memory_usage(component: str, bytes_used: int) -> None:
    """Record memory usage for a component.

    Args:
        component: Name of component
        bytes_used: Memory usage in bytes
    """
    MEMORY_USAGE.labels(component=component).set(bytes_used)


def record_cache_operation(operation: str, hit: bool) -> None:
    """Record a cache operation.

    Args:
        operation: Type of operation (get/set)
        hit: Whether operation was a cache hit
    """
    result = "hit" if hit else "miss"
    CACHE_OPERATIONS.labels(
        operation=operation,
        result=result
    ).inc()


def record_batch_processed(size: int, processing_time: float) -> None:
    """Record metrics for a processed batch.

    Args:
        size: Number of tasks in batch
        processing_time: Time spent processing batch (seconds)
    """
    BATCH_SIZE.observe(size)
    BATCH_PROCESSING_TIME.observe(processing_time)
