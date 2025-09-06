from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry

# Create a custom registry
registry = CollectorRegistry()

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'path', 'service'],
    registry=registry
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'path', 'service'],
    registry=registry,
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Service health metrics
service_health_status = Gauge(
    'service_health_status',
    'Service health status (0=unhealthy, 1=degraded, 2=healthy)',
    ['service'],
    registry=registry
)

service_response_time = Gauge(
    'service_response_time',
    'Service response time in seconds',
    ['service'],
    registry=registry
)

# Rate limiting metrics
rate_limit_exceeded_total = Counter(
    'rate_limit_exceeded_total',
    'Total number of rate limit exceeded events',
    ['client_ip'],
    registry=registry
)

# Circuit breaker metrics
circuit_breaker_state = Gauge(
    'circuit_breaker_state',
    'Circuit breaker state (0=open, 1=half-open, 2=closed)',
    ['service'],
    registry=registry
)

circuit_breaker_failures = Counter(
    'circuit_breaker_failures',
    'Circuit breaker failure count',
    ['service'],
    registry=registry
)

# Error metrics
http_errors_total = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'path', 'service', 'status_code'],
    registry=registry
)

# Authentication metrics
auth_failures_total = Counter(
    'auth_failures_total',
    'Total authentication failures',
    ['auth_type'],  # jwt or api_key
    registry=registry
)

# Service discovery metrics
registered_services = Gauge(
    'registered_services',
    'Number of registered services',
    registry=registry
)
