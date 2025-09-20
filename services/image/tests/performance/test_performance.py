"""Performance tests for image service."""

import asyncio
import json
import statistics
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient

from image_service.core.config import get_settings
from image_service.domain.models import (
    ImageType,
    ImageSubtype,
    PortraitStyle,
    ItemStyle,
    ItemProperties,
)

settings = get_settings()

# Constants
PERF_LOG_DIR = Path("./performance_logs")
PERF_LOG_DIR.mkdir(exist_ok=True)


class PerformanceMetrics:
    """Performance metrics collector."""

    def __init__(self):
        """Initialize metrics."""
        self.operations: Dict[str, List[float]] = {}
        self.errors: Dict[str, List[Dict[str, Any]]] = {}
        self.start_time = time.time()

    def add_operation(self, name: str, duration: float):
        """Add operation duration."""
        if name not in self.operations:
            self.operations[name] = []
        self.operations[name].append(duration)

    def add_error(self, name: str, error: Dict[str, Any]):
        """Add error details."""
        if name not in self.errors:
            self.errors[name] = []
        self.errors[name].append(error)

    def get_stats(self, name: str) -> Dict[str, float]:
        """Get statistics for operation."""
        if name not in self.operations:
            return {}
        durations = self.operations[name]
        return {
            "count": len(durations),
            "mean": statistics.mean(durations),
            "median": statistics.median(durations),
            "p95": statistics.quantiles(durations, n=20)[18],  # 95th percentile
            "min": min(durations),
            "max": max(durations),
            "errors": len(self.errors.get(name, [])),
        }

    def save_results(self, test_name: str):
        """Save results to file."""
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "duration": time.time() - self.start_time,
            "operations": {
                name: self.get_stats(name)
                for name in self.operations.keys()
            },
            "errors": self.errors,
        }

        file_path = PERF_LOG_DIR / f"{test_name}_{int(time.time())}.json"
        with open(file_path, "w") as f:
            json.dump(results, f, indent=2)


@pytest.fixture
async def metrics() -> PerformanceMetrics:
    """Create performance metrics collector."""
    return PerformanceMetrics()


@pytest.fixture
async def test_data() -> Dict[str, Any]:
    """Create test data."""
    return {
        "tactical_map": {
            "size": {"width": 2048, "height": 2048},
            "grid": {"enabled": True, "size": 50, "color": "#000000"},
            "theme": "fantasy",
            "features": ["forest", "mountains", "river"],
            "terrain": {"type": "grassland", "properties": {}},
        },
        "portrait": {
            "character_id": str(uuid4()),
            "theme": "fantasy",
            "style": PortraitStyle(
                pose="standing",
                background="tavern",
                lighting="warm",
            ).dict(),
            "equipment": {
                "visible": True,
                "items": [str(uuid4()) for _ in range(3)],
            },
        },
        "item": {
            "item_id": str(uuid4()),
            "type": "weapon",
            "theme": "fantasy",
            "style": ItemStyle(
                angle="front",
                lighting="dramatic",
                detail_level="high",
            ).dict(),
            "properties": ItemProperties(
                material="steel",
                magical_effects=["flaming", "frost"],
                wear_state="pristine",
            ).dict(),
        },
    }


async def measure_operation(
    metrics: PerformanceMetrics,
    name: str,
    coro: Any,
) -> Any:
    """Measure operation duration."""
    start = time.time()
    try:
        result = await coro
        duration = time.time() - start
        metrics.add_operation(name, duration)
        return result
    except Exception as e:
        duration = time.time() - start
        metrics.add_operation(name, duration)
        metrics.add_error(name, {"error": str(e), "duration": duration})
        raise


async def run_generation_test(
    client: AsyncClient,
    metrics: PerformanceMetrics,
    test_data: Dict[str, Any],
    operation: str,
    endpoint: str,
    iterations: int = 5,
) -> List[Dict[str, Any]]:
    """Run generation test for specified operation."""
    results = []
    for i in range(iterations):
        result = await measure_operation(
            metrics,
            f"{operation}_generation",
            client.post(endpoint, json=test_data[operation]),
        )
        results.append(result.json())
        # Sleep briefly to avoid rate limits
        await asyncio.sleep(0.5)
    return results


@pytest.mark.asyncio
async def test_tactical_map_generation(
    client: AsyncClient,
    metrics: PerformanceMetrics,
    test_data: Dict[str, Any],
):
    """Test tactical map generation performance."""
    maps = await run_generation_test(
        client,
        metrics,
        test_data,
        "tactical_map",
        "/api/v2/maps/tactical",
    )
    metrics.save_results("tactical_map_generation")

    # Verify performance requirements
    stats = metrics.get_stats("tactical_map_generation")
    assert stats["p95"] < 30.0, "Tactical map generation too slow"
    assert stats["errors"] == 0, "Errors during tactical map generation"


@pytest.mark.asyncio
async def test_portrait_generation(
    client: AsyncClient,
    metrics: PerformanceMetrics,
    test_data: Dict[str, Any],
):
    """Test portrait generation performance."""
    portraits = await run_generation_test(
        client,
        metrics,
        test_data,
        "portrait",
        "/api/v2/portraits",
    )
    metrics.save_results("portrait_generation")

    # Verify performance requirements
    stats = metrics.get_stats("portrait_generation")
    assert stats["p95"] < 15.0, "Portrait generation too slow"
    assert stats["errors"] == 0, "Errors during portrait generation"


@pytest.mark.asyncio
async def test_item_generation(
    client: AsyncClient,
    metrics: PerformanceMetrics,
    test_data: Dict[str, Any],
):
    """Test item generation performance."""
    items = await run_generation_test(
        client,
        metrics,
        test_data,
        "item",
        "/api/v2/items",
    )
    metrics.save_results("item_generation")

    # Verify performance requirements
    stats = metrics.get_stats("item_generation")
    assert stats["p95"] < 10.0, "Item generation too slow"
    assert stats["errors"] == 0, "Errors during item generation"


@pytest.mark.asyncio
async def test_cache_performance(
    client: AsyncClient,
    metrics: PerformanceMetrics,
):
    """Test cache performance."""
    # First, create test data
    create_response = await measure_operation(
        metrics,
        "cache_setup",
        client.post(
            "/api/v2/items",
            json={
                "item_id": str(uuid4()),
                "type": "weapon",
                "theme": "fantasy",
                "style": ItemStyle(
                    angle="front",
                    lighting="dramatic",
                    detail_level="high",
                ).dict(),
                "properties": ItemProperties(
                    material="steel",
                    magical_effects=["flaming"],
                    wear_state="pristine",
                ).dict(),
            },
        ),
    )
    item_id = create_response.json()["id"]

    # Now test cache performance
    hits = 0
    iterations = 100
    for _ in range(iterations):
        response = await measure_operation(
            metrics,
            "cache_get",
            client.get(f"/api/v2/items/{item_id}"),
        )
        # Check if response came from cache (should be indicated in headers)
        if response.headers.get("X-Cache-Hit") == "true":
            hits += 1
        await asyncio.sleep(0.1)  # Don't overwhelm the service

    metrics.save_results("cache_performance")

    # Calculate hit rate
    hit_rate = hits / iterations
    assert hit_rate > 0.90, f"Cache hit rate {hit_rate:.2%} below target 90%"


@pytest.mark.asyncio
async def test_api_latency(
    client: AsyncClient,
    metrics: PerformanceMetrics,
):
    """Test API endpoint latency."""
    # Test various endpoints
    endpoints = [
        ("GET", "/health"),
        ("GET", "/api/v2/themes"),
        ("GET", "/api/v2/images"),
    ]

    for method, endpoint in endpoints:
        for _ in range(50):  # 50 requests per endpoint
            await measure_operation(
                metrics,
                f"latency_{method}_{endpoint}",
                client.request(method, endpoint),
            )
            await asyncio.sleep(0.1)  # Rate limiting

    metrics.save_results("api_latency")

    # Check latency requirements
    for name, stats in metrics.operations.items():
        if name.startswith("latency_"):
            p95 = statistics.quantiles(stats, n=20)[18]
            assert p95 < 0.100, f"{name} P95 latency {p95:.3f}s exceeds 100ms target"


@pytest.mark.asyncio
async def test_concurrent_operations(
    client: AsyncClient,
    metrics: PerformanceMetrics,
    test_data: Dict[str, Any],
):
    """Test concurrent operation performance."""
    # Create a mix of operations
    async def run_operation(op_type: str):
        if op_type == "map":
            endpoint = "/api/v2/maps/tactical"
            data = test_data["tactical_map"]
        elif op_type == "portrait":
            endpoint = "/api/v2/portraits"
            data = test_data["portrait"]
        else:  # item
            endpoint = "/api/v2/items"
            data = test_data["item"]

        try:
            await measure_operation(
                metrics,
                f"concurrent_{op_type}",
                client.post(endpoint, json=data),
            )
        except Exception as e:
            metrics.add_error(f"concurrent_{op_type}", {"error": str(e)})

    # Run 5 of each operation type concurrently
    operations = (
        [run_operation("map")] * 5 +
        [run_operation("portrait")] * 5 +
        [run_operation("item")] * 5
    )

    await asyncio.gather(*operations)
    metrics.save_results("concurrent_operations")

    # Check results
    for op_type in ["map", "portrait", "item"]:
        stats = metrics.get_stats(f"concurrent_{op_type}")
        assert stats["errors"] == 0, f"Errors in concurrent {op_type} operations"
        # Concurrent operations might be slightly slower
        if op_type == "map":
            assert stats["p95"] < 35.0, "Concurrent map generation too slow"
        elif op_type == "portrait":
            assert stats["p95"] < 20.0, "Concurrent portrait generation too slow"
        else:  # item
            assert stats["p95"] < 15.0, "Concurrent item generation too slow"