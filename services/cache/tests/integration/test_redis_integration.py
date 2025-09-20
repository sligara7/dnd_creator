"""Integration tests for Redis operations."""

import asyncio
import json
from typing import Dict, Any

import pytest
import redis.asyncio as redis
from cache_service.cache.operations import CacheOperations
from tests.utils import generate_test_key, generate_test_value, assert_json_equal

@pytest.mark.integration
class TestRedisIntegration:
    """Integration tests for Redis operations."""
    
    @pytest.fixture
    async def cache_ops(self, redis_client, mock_message_hub_client, mock_config):
        """Create CacheOperations instance with real Redis."""
        ops = CacheOperations(
            redis_client=redis_client,
            message_hub=mock_message_hub_client,
            config=mock_config
        )
        yield ops

    @pytest.mark.parametrize("value", [
        {"string": "test"},
        {"number": 123},
        {"boolean": True},
        {"null": None},
        {"array": [1, 2, 3]},
        {"nested": {"key": "value"}},
        {"mixed": {"array": [1, "two", 3.0, None, {"key": "value"}]}}
    ])
    async def test_set_and_get(self, cache_ops, value):
        """Test setting and getting different value types."""
        # Arrange
        key = generate_test_key()

        # Act
        await cache_ops.set(key, value)
        result = await cache_ops.get(key)

        # Assert
        assert result == value

    async def test_large_value(self, cache_ops):
        """Test handling large values (1MB)."""
        # Arrange
        key = generate_test_key()
        value = generate_test_value(1024 * 1024)  # 1MB

        # Act
        await cache_ops.set(key, json.loads(value))
        result = await cache_ops.get(key)

        # Assert
        assert_json_equal(json.dumps(result), json.loads(value))

    async def test_concurrent_operations(self, cache_ops):
        """Test concurrent cache operations."""
        # Arrange
        num_operations = 100
        keys = [generate_test_key() for _ in range(num_operations)]
        values = [{"value": i} for i in range(num_operations)]

        # Act
        # Set values concurrently
        await asyncio.gather(*(
            cache_ops.set(key, value)
            for key, value in zip(keys, values)
        ))

        # Get values concurrently
        results = await asyncio.gather(*(
            cache_ops.get(key)
            for key in keys
        ))

        # Assert
        assert results == values

    async def test_pattern_operations(self, cache_ops):
        """Test pattern-based operations."""
        # Arrange
        prefix = "test-pattern"
        num_keys = 10
        keys = [generate_test_key(prefix) for _ in range(num_keys)]
        values = [{"value": i} for i in range(num_keys)]

        # Set test data
        for key, value in zip(keys, values):
            await cache_ops.set(key, value)

        # Act
        # Get by pattern
        pattern_results = await cache_ops.get_pattern(f"{prefix}:*")

        # Delete by pattern
        deleted = await cache_ops.delete_pattern(f"{prefix}:*")

        # Verify deletion
        remaining = await cache_ops.get_pattern(f"{prefix}:*")

        # Assert
        assert len(pattern_results) == num_keys
        for key, value in zip(keys, values):
            assert pattern_results[key] == value

        assert deleted == num_keys
        assert len(remaining) == 0

    async def test_ttl_expiration(self, cache_ops):
        """Test TTL-based expiration."""
        # Arrange
        key = generate_test_key()
        value = {"test": "value"}
        ttl = 1  # 1 second

        # Act
        await cache_ops.set(key, value, ttl=ttl)
        
        # Check immediately
        result_before = await cache_ops.get(key)
        
        # Wait for expiration
        await asyncio.sleep(ttl + 0.1)
        
        # Check after expiration
        result_after = await cache_ops.get(key)

        # Assert
        assert result_before == value
        assert result_after is None

    async def test_increment_decrement(self, cache_ops):
        """Test increment and decrement operations."""
        # Arrange
        key = generate_test_key()

        # Act & Assert
        # Initial increment
        value = await cache_ops.increment(key)
        assert value == 1

        # Multiple increments
        for i in range(5):
            value = await cache_ops.increment(key)
            assert value == i + 2

        # Multiple decrements
        for i in range(3):
            value = await cache_ops.decrement(key)
            assert value == 4 - i

    @pytest.mark.parametrize("pattern,expected_count", [
        ("test:*", 2),
        ("test:key1", 1),
        ("nonexistent:*", 0),
        ("*", 4)  # All keys
    ])
    async def test_pattern_matching(self, populated_redis, cache_ops, pattern, expected_count):
        """Test pattern matching with different patterns."""
        # Act
        results = await cache_ops.get_pattern(pattern)

        # Assert
        assert len(results) == expected_count

    async def test_clear_namespace(self, cache_ops):
        """Test clearing an entire namespace."""
        # Arrange
        namespace = "test-namespace"
        num_keys = 5
        keys = [generate_test_key(namespace) for _ in range(num_keys)]
        values = [{"value": i} for i in range(num_keys)]

        # Set test data
        for key, value in zip(keys, values):
            await cache_ops.set(key, value)

        # Also set a key in a different namespace
        other_key = generate_test_key("other-namespace")
        await cache_ops.set(other_key, {"value": "other"})

        # Act
        # Clear namespace
        cleared = await cache_ops.delete_pattern(f"{namespace}:*")

        # Check both namespaces
        namespace_keys = await cache_ops.get_pattern(f"{namespace}:*")
        other_value = await cache_ops.get(other_key)

        # Assert
        assert cleared == num_keys
        assert len(namespace_keys) == 0
        assert other_value == {"value": "other"}

    async def test_concurrent_pattern_operations(self, cache_ops):
        """Test concurrent pattern-based operations."""
        # Arrange
        patterns = ["test1:*", "test2:*", "test3:*"]
        keys_per_pattern = 10

        # Create test data for each pattern
        test_data = {}
        for pattern in patterns:
            prefix = pattern[:-1]  # Remove * from pattern
            pattern_keys = [
                generate_test_key(prefix)
                for _ in range(keys_per_pattern)
            ]
            pattern_values = [
                {"value": f"{prefix}-{i}"}
                for i in range(keys_per_pattern)
            ]
            test_data[prefix] = list(zip(pattern_keys, pattern_values))

        # Set all test data
        await asyncio.gather(*(
            cache_ops.set(key, value)
            for pattern_data in test_data.values()
            for key, value in pattern_data
        ))

        # Act
        # Get all patterns concurrently
        pattern_results = await asyncio.gather(*(
            cache_ops.get_pattern(pattern)
            for pattern in patterns
        ))

        # Delete all patterns concurrently
        delete_results = await asyncio.gather(*(
            cache_ops.delete_pattern(pattern)
            for pattern in patterns
        ))

        # Assert
        # Verify each pattern returned correct number of results
        for results in pattern_results:
            assert len(results) == keys_per_pattern

        # Verify each pattern deletion count
        for deleted in delete_results:
            assert deleted == keys_per_pattern

        # Verify all patterns are now empty
        empty_results = await asyncio.gather(*(
            cache_ops.get_pattern(pattern)
            for pattern in patterns
        ))
        assert all(len(results) == 0 for results in empty_results)

    async def test_error_handling(self, cache_ops):
        """Test error handling with real Redis."""
        # Arrange
        key = generate_test_key()
        value = {"test": "value"}

        # Act & Assert
        # Test with invalid JSON
        with pytest.raises(TypeError):
            await cache_ops.set(key, object())  # Trying to serialize non-serializable object

        # Test with non-existent key
        result = await cache_ops.get("nonexistent-key")
        assert result is None

        # Test with invalid pattern
        with pytest.raises(redis.RedisError):
            await cache_ops.get_pattern("[invalid pattern")  # Invalid regex pattern