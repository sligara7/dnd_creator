"""Core metrics infrastructure."""

from dataclasses import dataclass
from typing import Dict, Optional
from prometheus_client import Counter, Gauge, Histogram, REGISTRY

@dataclass
class MetricDefinition:
    """Metric definition with metadata."""
    name: str
    description: str
    labels: Optional[list[str]] = None
    buckets: Optional[list[float]] = None

class MetricsRegistry:
    """Central metrics registry and management."""
    
    def __init__(self):
        """Initialize metrics registry."""
        self._counters: Dict[str, Counter] = {}
        self._gauges: Dict[str, Gauge] = {}
        self._histograms: Dict[str, Histogram] = {}

    def counter(self, definition: MetricDefinition) -> Counter:
        """Get or create a Counter metric."""
        if definition.name not in self._counters:
            self._counters[definition.name] = Counter(
                definition.name,
                definition.description,
                labelnames=definition.labels or []
            )
        return self._counters[definition.name]

    def gauge(self, definition: MetricDefinition) -> Gauge:
        """Get or create a Gauge metric."""
        if definition.name not in self._gauges:
            self._gauges[definition.name] = Gauge(
                definition.name,
                definition.description,
                labelnames=definition.labels or []
            )
        return self._gauges[definition.name]

    def histogram(self, definition: MetricDefinition) -> Histogram:
        """Get or create a Histogram metric."""
        if definition.name not in self._histograms:
            self._histograms[definition.name] = Histogram(
                definition.name,
                definition.description,
                labelnames=definition.labels or [],
                buckets=definition.buckets or Histogram.DEFAULT_BUCKETS
            )
        return self._histograms[definition.name]

    def unregister_all(self) -> None:
        """Unregister all metrics from the registry."""
        for counter in self._counters.values():
            REGISTRY.unregister(counter)
        for gauge in self._gauges.values():
            REGISTRY.unregister(gauge)
        for histogram in self._histograms.values():
            REGISTRY.unregister(histogram)
        
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()

# Global metrics registry instance
registry = MetricsRegistry()

# Standard service metrics
HTTP_REQUEST_DURATION = MetricDefinition(
    name="http_request_duration_seconds",
    description="HTTP request duration in seconds",
    labels=["method", "path", "status"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
)

HTTP_REQUESTS_TOTAL = MetricDefinition(
    name="http_requests_total",
    description="Total number of HTTP requests",
    labels=["method", "path", "status"]
)

ACTIVE_REQUESTS = MetricDefinition(
    name="active_requests",
    description="Number of currently active requests",
    labels=["method", "path"]
)