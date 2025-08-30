"""
Message Hub Monitoring

Prometheus metrics and monitoring utilities.
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import FastAPI

class MessageHubMetrics:
    """Prometheus metrics collection for the message hub."""
    
    def __init__(self, app: FastAPI, circuit_breaker_manager=None):
        """Initialize metrics collectors."""
        self.app = app
        self.circuit_breaker_manager = circuit_breaker_manager
        
        # Message counters
        self.messages_total = Counter(
            "message_hub_messages_total",
            "Total number of messages processed",
            ["source", "destination", "type"]
        )
        
        self.message_errors = Counter(
            "message_hub_errors_total",
            "Total number of message processing errors",
            ["source", "destination", "type"]
        )
        
        # Service health metrics
        self.service_health = Gauge(
            "message_hub_service_health",
            "Current health status of services (1 = healthy, 0 = unhealthy)",
            ["service"]
        )
        
        self.service_latency = Histogram(
            "message_hub_service_latency_seconds",
            "Service health check latency in seconds",
            ["service"],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
        )
        
        # Circuit breaker metrics
        self.circuit_breaker_status = Gauge(
            "message_hub_circuit_breaker_status",
            "Circuit breaker status (1 = closed, 0 = open)",
            ["service"]
        )
        
        self.circuit_breaker_trips = Counter(
            "message_hub_circuit_breaker_trips_total",
            "Total number of circuit breaker trips",
            ["service"]
        )
    
    def record_message_success(self,
                             source: str,
                             destination: str,
                             message_type: str):
        """Record a successful message delivery."""
        self.messages_total.labels(
            source=source,
            destination=destination,
            type=message_type
        ).inc()
    
    def record_message_failure(self,
                             source: str,
                             destination: str,
                             message_type: str):
        """Record a failed message delivery."""
        self.message_errors.labels(
            source=source,
            destination=destination,
            type=message_type
        ).inc()
    
    def update_service_health(self, service: str, is_healthy: bool):
        """Update service health status."""
        self.service_health.labels(service=service).set(1 if is_healthy else 0)
    
    def record_service_latency(self, service: str, seconds: float):
        """Record service health check latency."""
        self.service_latency.labels(service=service).observe(seconds)
    
    def update_circuit_breaker(self, service: str, is_closed: bool):
        """Update circuit breaker status."""
        self.circuit_breaker_status.labels(service=service).set(1 if is_closed else 0)
    
    def record_circuit_breaker_trip(self, service: str):
        """Record a circuit breaker trip."""
        self.circuit_breaker_trips.labels(service=service).inc()
    
    def get_metrics(self):
        """Get current metrics in Prometheus format."""
        metrics = {
            "message_metrics": {
                "requests": {
                    metric.name: metric._value.get() 
                    for metric in [self.messages_total, self.message_errors]
                },
                "latency": self.message_latency._samples(),
            }
        }
        
        # Add circuit breaker metrics if available
        if self.circuit_breaker_manager:
            metrics["circuit_breakers"] = self.circuit_breaker_manager.get_metrics()
        
        return metrics
