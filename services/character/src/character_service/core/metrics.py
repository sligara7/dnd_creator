"""Metrics Configuration"""

from prometheus_client import Counter, Histogram, Info, Gauge
from datetime import datetime

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
