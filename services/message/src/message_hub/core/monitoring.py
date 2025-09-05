from prometheus_client import Counter, Histogram, Gauge, Info, start_http_server
import structlog

logger = structlog.get_logger()

# Metrics
messages_total = Counter(
    'message_hub_messages_total',
    'Total messages processed',
    ['source', 'destination', 'type']
)

message_duration_seconds = Histogram(
    'message_hub_message_duration_seconds',
    'Time spent processing messages',
    ['source', 'destination', 'type'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

circuit_breaker_status = Gauge(
    'message_hub_circuit_breaker_status',
    'Circuit breaker status (0=closed, 1=half-open, 2=open)',
    ['service']
)

service_registry_info = Info(
    'message_hub_service_registry',
    'Service registry information'
)

queue_size = Gauge(
    'message_hub_queue_size',
    'Number of messages in queue',
    ['queue_name']
)

event_store_size = Gauge(
    'message_hub_event_store_size',
    'Number of events in store'
)

retry_count = Counter(
    'message_hub_retries_total',
    'Total number of message retries',
    ['source', 'destination']
)

error_count = Counter(
    'message_hub_errors_total',
    'Total number of errors',
    ['type', 'service']
)

async def setup_monitoring():
    """Initialize monitoring"""
    try:
        # Start metrics server on a different port
        start_http_server(8201)
        logger.info("Metrics server started", port=8201)
    except Exception as e:
        logger.error("Failed to start metrics server", error=str(e))
        raise

class MessageMetrics:
    """Context manager for message metrics"""
    def __init__(self, source: str, destination: str, message_type: str):
        self.source = source
        self.destination = destination
        self.message_type = message_type
        self.duration = message_duration_seconds.labels(
            source=source,
            destination=destination,
            type=message_type
        ).time()

    def __enter__(self):
        messages_total.labels(
            source=self.source,
            destination=self.destination,
            type=self.message_type
        ).inc()
        return self.duration.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration.__exit__(exc_type, exc_val, exc_tb)
        if exc_type is not None:
            error_count.labels(
                type=exc_type.__name__,
                service=self.destination
            ).inc()

def record_queue_size(queue_name: str, size: int):
    """Record queue size"""
    queue_size.labels(queue_name=queue_name).set(size)

def record_event_store_size(size: int):
    """Record event store size"""
    event_store_size.set(size)

def record_retry(source: str, destination: str):
    """Record retry attempt"""
    retry_count.labels(
        source=source,
        destination=destination
    ).inc()

def set_circuit_breaker_status(service: str, status: str):
    """Set circuit breaker status"""
    value = {
        'closed': 0,
        'half-open': 1,
        'open': 2
    }[status.lower()]
    circuit_breaker_status.labels(service=service).set(value)

def update_service_registry(services: dict):
    """Update service registry info"""
    service_registry_info.info({
        service: str(info)
        for service, info in services.items()
    })

async def get_metrics():
    """Get all metrics in Prometheus format"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi.responses import Response
    
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
