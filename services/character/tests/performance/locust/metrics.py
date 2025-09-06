"""Prometheus metrics for load testing."""
from typing import Dict, Any
from prometheus_client import Histogram, Counter, Gauge

# Request latency histogram with SRD thresholds
REQUEST_LATENCY = Histogram(
    "character_service_request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0],  # Covers all SRD thresholds
)

# Success/failure counters
REQUEST_SUCCESS = Counter(
    "character_service_request_success_total",
    "Total number of successful requests",
    ["method", "endpoint"],
)

REQUEST_FAILURE = Counter(
    "character_service_request_failure_total",
    "Total number of failed requests",
    ["method", "endpoint", "error_type"],
)

# Active users gauge
ACTIVE_USERS = Gauge(
    "character_service_active_users",
    "Number of active users",
)

# Response size metrics
RESPONSE_SIZE = Histogram(
    "character_service_response_size_bytes",
    "Response size in bytes",
    ["endpoint"],
    buckets=[100, 1000, 10000, 100000, 1000000],
)
