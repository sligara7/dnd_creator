"""Load tests for cache service."""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Tuple
import statistics

import pytest
from cache_service.cache.operations import CacheOperations
from tests.utils import generate_test_key, generate_test_value

@pytest.mark.load
class TestCacheLoad:
    """Load test scenarios for cache service."""

    @pytest.fixture
    async def cache_ops(self, redis_client, mock_message_hub_client, mock_config):
        """Create CacheOperations instance."""
        ops = CacheOperations(
            redis_client=redis_client,
            message_hub=mock_message_hub_client,
            config=mock_config
        )
        yield ops

    async def measure_operation(
        self,
        operation: callable,
        *args,
        **kwargs
    ) -> float:
        """Measure operation execution time.

        Args:
            operation: Async function to measure
            args: Positional arguments for operation
            kwargs: Keyword arguments for operation

        Returns:
            Execution time in milliseconds
        """
        start = time.monotonic()
        await operation(*args, **kwargs)
        end = time.monotonic()
        return (end - start) * 1000  # Convert to ms

    def calculate_statistics(self, timings: List[float]) -> Dict[str, float]:
        """Calculate timing statistics.

        Args:
            timings: List of operation timings in milliseconds

        Returns:
            Dictionary with statistics
        """
        return {
            "min": min(timings),
            "max": max(timings),
            "mean": statistics.mean(timings),
            "median": statistics.median(timings),
            "p95": statistics.quantiles(timings, n=20)[18],  # 95th percentile
            "p99": statistics.quantiles(timings, n=100)[98]  # 99th percentile
        }

    async def run_concurrent_operations(
        self,
        operation: callable,
        num_operations: int,
        *args,
        **kwargs
    ) -> List[float]:
        """Run operations concurrently and measure timings.

        Args:
            operation: Async function to run
            num_operations: Number of concurrent operations
            args: Positional arguments for operation
            kwargs: Keyword arguments for operation

        Returns:
            List of operation timings in milliseconds
        """
        tasks = []
        for _ in range(num_operations):
            task = asyncio.create_task(
                self.measure_operation(operation, *args, **kwargs)
            )
            tasks.append(task)

        return await asyncio.gather(*tasks)

    async def test_concurrent_set_get(self, cache_ops):
        """Test concurrent set and get operations."""
        # Arrange
        num_operations = 1000
        keys = [generate_test_key() for _ in range(num_operations)]
        values = [{"value": f"test{i}"} for i in range(num_operations)]
        
        # Act
        print("\\nRunning concurrent set operations...")
        set_timings = await self.run_concurrent_operations(
            cache_ops.set,
            num_operations,
            *zip(keys, values)
        )

        print("\\nRunning concurrent get operations...")
        get_timings = await self.run_concurrent_operations(
            cache_ops.get,
            num_operations,
            *keys
        )

        # Assert & Report
        set_stats = self.calculate_statistics(set_timings)
        get_stats = self.calculate_statistics(get_timings)

        print("\\nSet Operation Statistics (ms):")
        for metric, value in set_stats.items():
            print(f"{metric}: {value:.2f}")

        print("\\nGet Operation Statistics (ms):")
        for metric, value in get_stats.items():
            print(f"{metric}: {value:.2f}")

        # Performance assertions
        assert set_stats["p95"] < 50  # 95% of sets under 50ms
        assert get_stats["p95"] < 20  # 95% of gets under 20ms

    async def test_large_value_performance(self, cache_ops):
        """Test performance with different value sizes."""
        # Arrange
        sizes = [1024, 10*1024, 100*1024, 1024*1024]  # 1KB to 1MB
        operations_per_size = 100

        results = {}
        for size in sizes:
            print(f"\\nTesting with {size/1024:.1f}KB values...")
            key = generate_test_key()
            value = json.loads(generate_test_value(size))

            # Act
            set_timings = await self.run_concurrent_operations(
                cache_ops.set,
                operations_per_size,
                key,
                value
            )

            get_timings = await self.run_concurrent_operations(
                cache_ops.get,
                operations_per_size,
                key
            )

            # Calculate & store statistics
            results[size] = {
                "set": self.calculate_statistics(set_timings),
                "get": self.calculate_statistics(get_timings)
            }

        # Report
        for size, stats in results.items():
            print(f"\\nResults for {size/1024:.1f}KB values:")
            print("Set Operations (ms):")
            for metric, value in stats["set"].items():
                print(f"{metric}: {value:.2f}")
            print("Get Operations (ms):")
            for metric, value in stats["get"].items():
                print(f"{metric}: {value:.2f}")

            # Assert reasonable performance degradation
            # Larger values should still be manageable
            assert stats["set"]["p95"] < 200  # 95% under 200ms
            assert stats["get"]["p95"] < 100  # 95% under 100ms

    async def test_pattern_matching_load(self, cache_ops):
        """Test pattern matching performance under load."""
        # Arrange
        num_patterns = 5
        keys_per_pattern = 1000
        patterns = [f"test{i}:*" for i in range(num_patterns)]
        
        # Create test data
        print("\\nCreating test data...")
        for pattern in patterns:
            prefix = pattern[:-1]
            for i in range(keys_per_pattern):
                key = f"{prefix}{i}"
                await cache_ops.set(key, {"value": f"test{i}"})

        # Act
        print("\\nTesting pattern operations...")
        pattern_timings = []
        for pattern in patterns:
            # Measure get_pattern
            timing = await self.measure_operation(
                cache_ops.get_pattern,
                pattern
            )
            pattern_timings.append(timing)

            # Measure delete_pattern
            timing = await self.measure_operation(
                cache_ops.delete_pattern,
                pattern
            )
            pattern_timings.append(timing)

        # Assert & Report
        stats = self.calculate_statistics(pattern_timings)
        print("\\nPattern Operation Statistics (ms):")
        for metric, value in stats.items():
            print(f"{metric}: {value:.2f}")

        # Pattern operations should be reasonable for this scale
        assert stats["p95"] < 500  # 95% under 500ms

    async def test_sustained_load(self, cache_ops):
        """Test sustained load over time."""
        # Arrange
        duration = 30  # seconds
        operations_per_second = 100
        print(f"\\nRunning sustained load test for {duration} seconds...")

        results: List[Tuple[str, float]] = []
        start_time = time.monotonic()

        # Act
        while time.monotonic() - start_time < duration:
            # Mix of operations
            operations = [
                ("set", generate_test_key(), {"value": "test"}),
                ("get", generate_test_key(), None),
                ("delete", generate_test_key(), None),
                ("increment", generate_test_key(), None)
            ]

            for op_type, key, value in operations:
                op_start = time.monotonic()
                if op_type == "set":
                    await cache_ops.set(key, value)
                elif op_type == "get":
                    await cache_ops.get(key)
                elif op_type == "delete":
                    await cache_ops.delete(key)
                elif op_type == "increment":
                    await cache_ops.increment(key)
                
                results.append((
                    op_type,
                    (time.monotonic() - op_start) * 1000
                ))

                # Rate limiting
                await asyncio.sleep(1 / operations_per_second)

        # Calculate statistics per operation type
        stats_by_type = {}
        for op_type in ["set", "get", "delete", "increment"]:
            timings = [
                t for ot, t in results
                if ot == op_type
            ]
            if timings:
                stats_by_type[op_type] = self.calculate_statistics(timings)

        # Report
        print("\\nSustained Load Statistics by Operation Type:")
        for op_type, stats in stats_by_type.items():
            print(f"\\n{op_type.upper()} Operations (ms):")
            for metric, value in stats.items():
                print(f"{metric}: {value:.2f}")

            # Assert sustained performance
            assert stats["p95"] < 100  # 95% under 100ms

    async def test_mixed_workload(self, cache_ops):
        """Test mixed workload performance."""
        # Arrange
        num_operations = 1000
        print(f"\\nRunning mixed workload test with {num_operations} operations...")

        # Prepare different operation types
        operations = []
        for i in range(num_operations):
            op_type = i % 4  # Distribute across 4 operation types
            key = generate_test_key()
            value = {"value": f"test{i}"}

            if op_type == 0:
                # Set operation
                operations.append(("set", cache_ops.set, key, value))
            elif op_type == 1:
                # Get operation
                operations.append(("get", cache_ops.get, key, None))
            elif op_type == 2:
                # Delete operation
                operations.append(("delete", cache_ops.delete, key, None))
            else:
                # Pattern operation
                pattern = f"{key[:8]}*"
                operations.append(
                    ("pattern", cache_ops.get_pattern, pattern, None)
                )

        # Act
        results: List[Tuple[str, float]] = []
        for op_type, func, key, value in operations:
            if value is not None:
                timing = await self.measure_operation(func, key, value)
            else:
                timing = await self.measure_operation(func, key)
            results.append((op_type, timing))

        # Calculate & Report
        stats_by_type = {}
        for op_type in ["set", "get", "delete", "pattern"]:
            timings = [
                t for ot, t in results
                if ot == op_type
            ]
            if timings:
                stats_by_type[op_type] = self.calculate_statistics(timings)

        print("\\nMixed Workload Statistics by Operation Type:")
        for op_type, stats in stats_by_type.items():
            print(f"\\n{op_type.upper()} Operations (ms):")
            for metric, value in stats.items():
                print(f"{metric}: {value:.2f}")

            # Assert reasonable performance for each type
            assert stats["p95"] < 150  # 95% under 150ms

    async def test_cache_size_impact(self, cache_ops):
        """Test performance impact of cache size."""
        # Arrange
        sizes = [1000, 10000, 100000]  # Number of items in cache
        ops_per_size = 100

        print("\\nTesting performance with different cache sizes...")
        results = {}

        for size in sizes:
            print(f"\\nPopulating cache with {size} items...")
            # Populate cache
            base_key = generate_test_key()
            for i in range(size):
                key = f"{base_key}:{i}"
                await cache_ops.set(key, {"value": f"test{i}"})

            # Measure operations
            print(f"Running operations with {size} items in cache...")
            test_key = f"{base_key}:{size//2}"  # Key in middle of range
            
            set_timings = await self.run_concurrent_operations(
                cache_ops.set,
                ops_per_size,
                test_key,
                {"value": "test"}
            )

            get_timings = await self.run_concurrent_operations(
                cache_ops.get,
                ops_per_size,
                test_key
            )

            pattern_timings = await self.run_concurrent_operations(
                cache_ops.get_pattern,
                ops_per_size,
                f"{base_key}:*"
            )

            # Store results
            results[size] = {
                "set": self.calculate_statistics(set_timings),
                "get": self.calculate_statistics(get_timings),
                "pattern": self.calculate_statistics(pattern_timings)
            }

        # Report
        for size, stats in results.items():
            print(f"\\nResults with {size} items in cache:")
            for op_type, op_stats in stats.items():
                print(f"{op_type.upper()} Operations (ms):")
                for metric, value in op_stats.items():
                    print(f"{metric}: {value:.2f}")

            # Assert reasonable scaling
            assert stats["set"]["p95"] < 100
            assert stats["get"]["p95"] < 50
            assert stats["pattern"]["p95"] < 1000