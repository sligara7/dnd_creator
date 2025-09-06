"""Metrics Configuration"""

import time
from contextlib import contextmanager
from datetime import datetime
from prometheus_client import Counter, Histogram, Info, Gauge

# Initialize service info
SERVICE_INFO = Info(
    "character_service",
    "Character service information"
)
SERVICE_INFO.info({
    "version": "2.0.0",
    "service_name": "character_service"
})

# Request metrics
REQUEST_COUNT = Counter(
    "character_service_request_total",
    "Total number of requests processed",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "character_service_request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint"]
)

# Database metrics
DB_QUERY_LATENCY = Histogram(
    "character_service_db_query_latency_seconds",
    "Database query latency in seconds",
    ["operation"]
)

DB_CONNECTIONS = Gauge(
    "character_service_db_connections",
    "Number of active database connections"
)

# Character metrics
CHARACTER_COUNT = Gauge(
    "character_service_characters_total",
    "Total number of characters in the system"
)

CHARACTER_CREATION_LATENCY = Histogram(
    "character_service_character_creation_seconds",
    "Character creation latency in seconds"
)

# LLM Integration metrics
LLM_REQUEST_LATENCY = Histogram(
    "character_service_llm_request_latency_seconds",
    "LLM request latency in seconds",
    ["operation"]
)

LLM_TOKEN_USAGE = Counter(
    "character_service_llm_token_usage_total",
    "Total number of tokens used in LLM requests",
    ["operation"]
)

# Integration metrics
INTEGRATION_REQUEST_LATENCY = Histogram(
    "character_service_integration_request_latency_seconds",
    "Integration request latency in seconds",
    ["service", "operation"]
)

INTEGRATION_ERRORS = Counter(
    "character_service_integration_errors_total",
    "Total number of integration errors",
    ["service", "error_type"]
)

# System metrics
SYSTEM_MEMORY_USAGE = Gauge(
    "character_service_memory_usage_bytes",
    "Current memory usage in bytes"
)

SYSTEM_CPU_USAGE = Gauge(
    "character_service_cpu_usage_percent",
    "Current CPU usage percentage"
)

# Cache metrics
CACHE_HIT_COUNT = Counter(
    "character_service_cache_hits_total",
    "Total number of cache hits",
    ["cache_type"]
)

CACHE_MISS_COUNT = Counter(
    "character_service_cache_misses_total",
    "Total number of cache misses",
    ["cache_type"]
)

def track_request_metrics(endpoint: str, method: str, status: int, duration: float):
    """Track metrics for an HTTP request."""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)

def track_db_operation(operation: str, duration: float):
    """Track metrics for a database operation."""
    DB_QUERY_LATENCY.labels(operation=operation).observe(duration)

def track_character_creation(duration: float):
    """Track metrics for character creation."""
    CHARACTER_CREATION_LATENCY.observe(duration)
    CHARACTER_COUNT.inc()

def track_llm_request(operation: str, duration: float, tokens: int):
    """Track metrics for an LLM request."""
    LLM_REQUEST_LATENCY.labels(operation=operation).observe(duration)
    LLM_TOKEN_USAGE.labels(operation=operation).inc(tokens)

def track_integration_request(service: str, operation: str, duration: float, error: str = None):
    """Track metrics for an integration request."""
    INTEGRATION_REQUEST_LATENCY.labels(service=service, operation=operation).observe(duration)
    if error:
        INTEGRATION_ERRORS.labels(service=service, error_type=error).inc()

def track_cache_operation(cache_type: str, hit: bool):
    """Track metrics for a cache operation."""
    if hit:
        CACHE_HIT_COUNT.labels(cache_type=cache_type).inc()
    else:
        CACHE_MISS_COUNT.labels(cache_type=cache_type).inc()


# Event handling metrics
EVENT_HANDLING_DURATION = Histogram(
    "character_event_handling_duration_seconds",
    "Time spent handling events",
    ["event_type", "handler"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0),
)

EVENT_HANDLING_ERRORS = Counter(
    "character_event_handling_errors_total",
    "Number of errors during event handling",
    ["event_type", "handler", "error_type"],
)

EVENT_PROCESSING_COUNT = Counter(
    "character_event_processing_total",
    "Number of events processed",
    ["event_type", "handler", "status"],
)

# Message publishing metrics
MESSAGE_PUBLISH_DURATION = Histogram(
    "character_message_publish_duration_seconds",
    "Time spent publishing messages",
    ["message_type"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0),
)

MESSAGE_PUBLISH_ERRORS = Counter(
    "character_message_publish_errors_total",
    "Number of errors during message publishing",
    ["message_type", "error_type"],
)

MESSAGE_PUBLISH_COUNT = Counter(
    "character_message_publish_total",
    "Number of messages published",
    ["message_type", "status"],
)

# Event queue metrics
IN_FLIGHT_MESSAGES = Gauge(
    "character_in_flight_messages",
    "Number of messages currently being processed",
    ["message_type"],
)

BATCH_SIZE = Histogram(
    "character_message_batch_size",
    "Size of message batches",
    buckets=(1, 2, 5, 10, 20, 50, 100),
)

RETRY_COUNT = Counter(
    "character_message_retries_total",
    "Number of message retry attempts",
    ["message_type"],
)

QUEUE_SIZE = Gauge(
    "character_message_queue_size",
    "Current size of message queues",
    ["queue_name"],
)

QUEUE_LATENCY = Histogram(
    "character_message_queue_latency_seconds",
    "Time messages spend in queue before processing",
    ["queue_name"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)


@contextmanager
def track_event_handling(event_type: str, handler: str):
    """Track event handling duration and status."""
    start_time = time.monotonic()
    try:
        yield
        EVENT_PROCESSING_COUNT.labels(
            event_type=event_type,
            handler=handler,
            status="success",
        ).inc()
    except Exception as e:
        EVENT_HANDLING_ERRORS.labels(
            event_type=event_type,
            handler=handler,
            error_type=type(e).__name__,
        ).inc()
        EVENT_PROCESSING_COUNT.labels(
            event_type=event_type,
            handler=handler,
            status="error",
        ).inc()
        raise
    finally:
        duration = time.monotonic() - start_time
        EVENT_HANDLING_DURATION.labels(
            event_type=event_type,
            handler=handler,
        ).observe(duration)


@contextmanager
def track_message_publish(message_type: str):
    """Track message publishing duration and status."""
    start_time = time.monotonic()
    try:
        yield
        MESSAGE_PUBLISH_COUNT.labels(
            message_type=message_type,
            status="success",
        ).inc()
    except Exception as e:
        MESSAGE_PUBLISH_ERRORS.labels(
            message_type=message_type,
            error_type=type(e).__name__,
        ).inc()
        MESSAGE_PUBLISH_COUNT.labels(
            message_type=message_type,
            status="error",
        ).inc()
        raise
    finally:
        duration = time.monotonic() - start_time
        MESSAGE_PUBLISH_DURATION.labels(
            message_type=message_type,
        ).observe(duration)


@contextmanager
def track_in_flight_with_type(message_type: str):
    """Track in-flight message count with automatic cleanup."""
    IN_FLIGHT_MESSAGES.labels(message_type=message_type).inc()
    try:
        yield
    finally:
        IN_FLIGHT_MESSAGES.labels(message_type=message_type).dec()


def track_batch_size(size: int):
    """Track message batch size."""
    BATCH_SIZE.observe(size)


def track_retry(message_type: str):
    """Track message retry attempt."""
    RETRY_COUNT.labels(message_type=message_type).inc()


def track_queue_size(queue_name: str, size: int):
    """Track queue size."""
    QUEUE_SIZE.labels(queue_name=queue_name).set(size)


def track_queue_latency(queue_name: str, latency: float):
    """Track queue latency."""
    QUEUE_LATENCY.labels(queue_name=queue_name).observe(latency)
