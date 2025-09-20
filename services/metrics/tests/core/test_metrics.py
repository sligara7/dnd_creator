"""Tests for core metrics functionality."""

import pytest
from prometheus_client import REGISTRY
from metrics_service.core.metrics import (
    MetricDefinition,
    MetricsRegistry,
    HTTP_REQUEST_DURATION,
    HTTP_REQUESTS_TOTAL,
    ACTIVE_REQUESTS
)

@pytest.fixture
def metrics_registry():
    """Create a fresh metrics registry for each test."""
    registry = MetricsRegistry()
    yield registry
    registry.unregister_all()

def test_counter_creation(metrics_registry):
    """Test counter metric creation."""
    definition = MetricDefinition(
        name="test_counter",
        description="Test counter",
        labels=["label1", "label2"]
    )
    
    counter = metrics_registry.counter(definition)
    assert counter._name == "test_counter"
    assert "label1" in counter._labelnames
    assert "label2" in counter._labelnames

def test_gauge_creation(metrics_registry):
    """Test gauge metric creation."""
    definition = MetricDefinition(
        name="test_gauge",
        description="Test gauge",
        labels=["label1"]
    )
    
    gauge = metrics_registry.gauge(definition)
    assert gauge._name == "test_gauge"
    assert "label1" in gauge._labelnames

def test_histogram_creation(metrics_registry):
    """Test histogram metric creation."""
    definition = MetricDefinition(
        name="test_histogram",
        description="Test histogram",
        labels=["label1"],
        buckets=[0.1, 0.5, 1.0]
    )
    
    histogram = metrics_registry.histogram(definition)
    assert histogram._name == "test_histogram"
    assert "label1" in histogram._labelnames
    assert set(histogram._buckets) == {0.1, 0.5, 1.0, float("inf")}

def test_metric_reuse(metrics_registry):
    """Test that metrics are reused when requested multiple times."""
    definition = MetricDefinition(
        name="test_counter",
        description="Test counter"
    )
    
    counter1 = metrics_registry.counter(definition)
    counter2 = metrics_registry.counter(definition)
    assert counter1 is counter2

def test_standard_metrics_exist():
    """Test that standard service metrics are properly defined."""
    assert HTTP_REQUEST_DURATION.name == "http_request_duration_seconds"
    assert HTTP_REQUESTS_TOTAL.name == "http_requests_total"
    assert ACTIVE_REQUESTS.name == "active_requests"