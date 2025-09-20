"""
Prometheus monitoring setup and metrics collection.
"""
from prometheus_client import Counter, Gauge, Histogram, REGISTRY
import prometheus_client

# Event processing metrics
EVENT_PROCESSING_TIME = Histogram(
    "audit_event_processing_seconds",
    "Time spent processing events",
    ["service", "event_type"]
)

EVENT_BATCH_SIZE = Histogram(
    "audit_event_batch_size",
    "Distribution of event batch sizes",
    ["service"]
)

EVENTS_TOTAL = Counter(
    "audit_events_total",
    "Total number of audit events processed",
    ["service", "event_type", "outcome"]
)

EVENTS_PENDING = Gauge(
    "audit_events_pending",
    "Number of events pending processing",
    ["service"]
)

# Storage metrics
STORAGE_OPERATIONS = Counter(
    "audit_storage_operations_total",
    "Total number of storage operations",
    ["operation", "backend", "outcome"]
)

STORAGE_OPERATION_TIME = Histogram(
    "audit_storage_operation_seconds",
    "Time spent on storage operations",
    ["operation", "backend"]
)

STORAGE_SIZE_BYTES = Gauge(
    "audit_storage_size_bytes",
    "Total storage size in bytes",
    ["backend"]
)

# Analysis metrics
ANALYSIS_JOBS = Counter(
    "audit_analysis_jobs_total",
    "Total number of analysis jobs",
    ["type", "outcome"]
)

ANALYSIS_JOB_TIME = Histogram(
    "audit_analysis_job_seconds",
    "Time spent on analysis jobs",
    ["type"]
)

ACTIVE_ANALYSES = Gauge(
    "audit_active_analyses",
    "Number of currently running analyses",
    ["type"]
)

# Error metrics
ERROR_COUNT = Counter(
    "audit_errors_total",
    "Total number of errors encountered",
    ["type", "service"]
)

# Health metrics
SERVICE_UP = Gauge(
    "audit_service_up",
    "Whether the service is up (1) or down (0)",
    ["component"]
)

async def setup_monitoring() -> None:
    """Initialize monitoring and start metrics server."""
    prometheus_client.start_http_server(8401)  # Start metrics server

async def get_metrics() -> bytes:
    """Get current metrics."""
    return prometheus_client.generate_latest(REGISTRY)