"""Monitoring and metrics for Cache Service."""

import asyncio
from typing import Dict, Any, Optional
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
)
from fastapi.responses import Response
import structlog

from .config import settings

logger = structlog.get_logger()

# Create custom registry
registry = CollectorRegistry()

# Define metrics
cache_operations = Counter(
    "cache_operations_total",
    "Total number of cache operations",
    ["operation", "status", "service"],
    registry=registry,
)

cache_latency = Histogram(
    "cache_operation_duration_seconds",
    "Cache operation latency",
    ["operation", "service"],
    registry=registry,
)

cache_hit_rate = Gauge(
    "cache_hit_rate",
    "Cache hit rate percentage",
    ["service"],
    registry=registry,
)

cache_memory_usage = Gauge(
    "cache_memory_usage_bytes",
    "Cache memory usage in bytes",
    ["node", "type"],
    registry=registry,
)

cache_keys_total = Gauge(
    "cache_keys_total",
    "Total number of keys in cache",
    ["node"],
    registry=registry,
)

cache_evictions = Counter(
    "cache_evictions_total",
    "Total number of cache evictions",
    ["policy", "node"],
    registry=registry,
)

cache_replication_lag = Gauge(
    "cache_replication_lag_seconds",
    "Replication lag in seconds",
    ["primary", "replica"],
    registry=registry,
)

circuit_breaker_state = Gauge(
    "circuit_breaker_state",
    "Circuit breaker state (0=closed, 1=open, 2=half-open)",
    ["operation", "node"],
    registry=registry,
)

batch_operations = Counter(
    "cache_batch_operations_total",
    "Total number of batch operations",
    ["operation", "status"],
    registry=registry,
)

batch_operation_size = Histogram(
    "cache_batch_operation_size",
    "Size of batch operations",
    ["operation"],
    registry=registry,
)

connection_pool_usage = Gauge(
    "cache_connection_pool_usage",
    "Connection pool usage",
    ["pool", "metric"],  # metric: active, idle, total
    registry=registry,
)


class MetricsCollector:
    """Metrics collector for cache service."""

    def __init__(self):
        self.enabled = settings.METRICS_ENABLED
        self.registry = registry
        self._setup_complete = False

    async def setup(self) -> None:
        """Setup metrics collection."""
        if not self.enabled:
            logger.info("Metrics collection disabled")
            return

        try:
            # Initialize metrics with default values
            for service in ["character", "campaign", "image", "llm"]:
                cache_hit_rate.labels(service=service).set(0.0)
            
            # Initialize circuit breaker states
            for operation in ["get", "set", "delete"]:
                for node in ["primary", "replica"]:
                    circuit_breaker_state.labels(operation=operation, node=node).set(0)
            
            self._setup_complete = True
            logger.info("Metrics collection initialized")
        except Exception as e:
            logger.error("Failed to setup metrics", error=str(e))
            self.enabled = False

    def record_operation(
        self,
        operation: str,
        status: str,
        service: str,
        duration: Optional[float] = None,
    ) -> None:
        """Record a cache operation."""
        if not self.enabled:
            return

        try:
            cache_operations.labels(
                operation=operation,
                status=status,
                service=service,
            ).inc()

            if duration is not None:
                cache_latency.labels(
                    operation=operation,
                    service=service,
                ).observe(duration)
        except Exception as e:
            logger.warning("Failed to record operation metric", error=str(e))

    def update_hit_rate(self, service: str, rate: float) -> None:
        """Update cache hit rate."""
        if not self.enabled:
            return

        try:
            cache_hit_rate.labels(service=service).set(rate)
        except Exception as e:
            logger.warning("Failed to update hit rate metric", error=str(e))

    def update_memory_usage(self, node: str, usage_type: str, bytes_used: int) -> None:
        """Update memory usage metrics."""
        if not self.enabled:
            return

        try:
            cache_memory_usage.labels(node=node, type=usage_type).set(bytes_used)
        except Exception as e:
            logger.warning("Failed to update memory usage metric", error=str(e))

    def update_key_count(self, node: str, count: int) -> None:
        """Update total key count."""
        if not self.enabled:
            return

        try:
            cache_keys_total.labels(node=node).set(count)
        except Exception as e:
            logger.warning("Failed to update key count metric", error=str(e))

    def record_eviction(self, policy: str, node: str) -> None:
        """Record a cache eviction."""
        if not self.enabled:
            return

        try:
            cache_evictions.labels(policy=policy, node=node).inc()
        except Exception as e:
            logger.warning("Failed to record eviction metric", error=str(e))

    def update_replication_lag(self, primary: str, replica: str, lag_seconds: float) -> None:
        """Update replication lag."""
        if not self.enabled:
            return

        try:
            cache_replication_lag.labels(primary=primary, replica=replica).set(lag_seconds)
        except Exception as e:
            logger.warning("Failed to update replication lag metric", error=str(e))

    def update_circuit_breaker(self, operation: str, node: str, state: int) -> None:
        """Update circuit breaker state."""
        if not self.enabled:
            return

        try:
            circuit_breaker_state.labels(operation=operation, node=node).set(state)
        except Exception as e:
            logger.warning("Failed to update circuit breaker metric", error=str(e))

    def record_batch_operation(
        self,
        operation: str,
        status: str,
        size: Optional[int] = None,
    ) -> None:
        """Record a batch operation."""
        if not self.enabled:
            return

        try:
            batch_operations.labels(operation=operation, status=status).inc()
            
            if size is not None:
                batch_operation_size.labels(operation=operation).observe(size)
        except Exception as e:
            logger.warning("Failed to record batch operation metric", error=str(e))

    def update_connection_pool(self, pool: str, active: int, idle: int, total: int) -> None:
        """Update connection pool metrics."""
        if not self.enabled:
            return

        try:
            connection_pool_usage.labels(pool=pool, metric="active").set(active)
            connection_pool_usage.labels(pool=pool, metric="idle").set(idle)
            connection_pool_usage.labels(pool=pool, metric="total").set(total)
        except Exception as e:
            logger.warning("Failed to update connection pool metric", error=str(e))

    async def get_metrics(self) -> Response:
        """Get Prometheus metrics."""
        if not self.enabled:
            return Response(content="Metrics disabled", status_code=503)

        try:
            metrics_data = generate_latest(self.registry)
            return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)
        except Exception as e:
            logger.error("Failed to generate metrics", error=str(e))
            return Response(content="Error generating metrics", status_code=500)


# Global metrics collector instance
metrics_collector = MetricsCollector()


async def setup_monitoring() -> None:
    """Setup monitoring and metrics collection."""
    await metrics_collector.setup()


async def get_metrics() -> Response:
    """Get current metrics."""
    return await metrics_collector.get_metrics()


def record_cache_operation(
    operation: str,
    status: str,
    service: str,
    duration: Optional[float] = None,
) -> None:
    """Record a cache operation metric."""
    metrics_collector.record_operation(operation, status, service, duration)


def update_cache_stats(stats: Dict[str, Any]) -> None:
    """Update cache statistics metrics."""
    if "hit_rate" in stats:
        for service, rate in stats["hit_rate"].items():
            metrics_collector.update_hit_rate(service, rate)
    
    if "memory" in stats:
        for node, memory_info in stats["memory"].items():
            metrics_collector.update_memory_usage(
                node, "used", memory_info.get("used", 0)
            )
            metrics_collector.update_memory_usage(
                node, "total", memory_info.get("total", 0)
            )
    
    if "keys" in stats:
        for node, count in stats["keys"].items():
            metrics_collector.update_key_count(node, count)
    
    if "replication_lag" in stats:
        for primary, replicas in stats["replication_lag"].items():
            for replica, lag in replicas.items():
                metrics_collector.update_replication_lag(primary, replica, lag)
