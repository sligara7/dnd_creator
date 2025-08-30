"""
LLM Service Monitoring

Prometheus metrics and monitoring utilities.
"""

from prometheus_client import Counter, Histogram, generate_latest
from fastapi import FastAPI

class PrometheusMetrics:
    """Prometheus metrics collection for the LLM service."""
    
    def __init__(self, app: FastAPI):
        """Initialize metrics collectors."""
        self.app = app
        
        # Request counters
        self.generation_requests = Counter(
            "llm_generation_requests_total",
            "Total number of generation requests",
            ["type", "service"]
        )
        
        self.generation_errors = Counter(
            "llm_generation_errors_total",
            "Total number of generation errors",
            ["type", "service"]
        )
        
        # Latency histograms
        self.generation_latency = Histogram(
            "llm_generation_latency_seconds",
            "Generation request latency in seconds",
            ["type", "service"],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
        )
        
        # Token usage metrics
        self.token_usage = Counter(
            "llm_token_usage_total",
            "Total number of tokens used",
            ["type", "service"]
        )
    
    def record_generation_success(self, gen_type: str, service: str):
        """Record a successful generation request."""
        self.generation_requests.labels(type=gen_type, service=service).inc()
    
    def record_generation_failure(self, gen_type: str, service: str):
        """Record a failed generation request."""
        self.generation_errors.labels(type=gen_type, service=service).inc()
    
    def record_latency(self, gen_type: str, service: str, seconds: float):
        """Record request latency."""
        self.generation_latency.labels(type=gen_type, service=service).observe(seconds)
    
    def record_token_usage(self, gen_type: str, service: str, tokens: int):
        """Record token usage."""
        self.token_usage.labels(type=gen_type, service=service).inc(tokens)
    
    def get_metrics(self):
        """Get current metrics in Prometheus format."""
        return generate_latest()
