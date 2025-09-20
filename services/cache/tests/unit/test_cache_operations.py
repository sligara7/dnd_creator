"""Unit tests for cache operations."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from cache_service.cache.operations import CacheOperations
from tests.utils import generate_test_key, generate_test_value, assert_json_equal

@pytest.mark.unit
class TestCacheOperations:
    """Test cache operations."""

    @pytest.fixture
    async def cache_ops(self, mock_redis_client, mock_message_hub_client, mock_config):
        """Create CacheOperations instance with mocked dependencies."""
        ops = CacheOperations(
            redis_client=mock_redis_client,
            message_hub=mock_message_hub_client,
            config=mock_config
        )
        yield ops

    async def test_get_existing_key(self, cache_ops, mock_redis_client):
        """Test getting an existing key."""
        # Arrange
        key = generate_test_key()
        expected_value = {"test": "value"}
        mock_redis_client.get.return_value = json.dumps(expected_value)

        # Act
        result = await cache_ops.get(key)

        # Assert
        assert result == expected_value
        mock_redis_client.get.assert_awaited_once_with(key)

    async def test_get_missing_key(self, cache_ops, mock_redis_client):
        """Test getting a non-existent key."""
        # Arrange
        key = generate_test_key()
        mock_redis_client.get.return_value = None

        # Act
        result = await cache_ops.get(key)

        # Assert
        assert result is None
        mock_redis_client.get.assert_awaited_once_with(key)

    async def test_set_key(self, cache_ops, mock_redis_client, mock_message_hub_client):
        """Test setting a key."""
        # Arrange
        key = generate_test_key()
        value = {"test": "value"}

        # Act
        await cache_ops.set(key, value)

        # Assert
        mock_redis_client.set.assert_awaited_once_with(
            key,
            json.dumps(value)
        )
        mock_message_hub_client.publish_event.assert_awaited_once()

    async def test_delete_existing_key(self, cache_ops, mock_redis_client, mock_message_hub_client):
        """Test deleting an existing key."""
        # Arrange
        key = generate_test_key()
        mock_redis_client.delete.return_value = 1

        # Act
        result = await cache_ops.delete(key)

        # Assert
        assert result is True
        mock_redis_client.delete.assert_awaited_once_with(key)
        mock_message_hub_client.publish_event.assert_awaited_once()

    async def test_delete_missing_key(self, cache_ops, mock_redis_client, mock_message_hub_client):
        """Test deleting a non-existent key."""
        # Arrange
        key = generate_test_key()
        mock_redis_client.delete.return_value = 0

        # Act
        result = await cache_ops.delete(key)

        # Assert
        assert result is False
        mock_redis_client.delete.assert_awaited_once_with(key)
        mock_message_hub_client.publish_event.assert_not_awaited()

    async def test_exists(self, cache_ops, mock_redis_client):
        """Test checking key existence."""
        # Arrange
        key = generate_test_key()
        mock_redis_client.exists.return_value = True

        # Act
        result = await cache_ops.exists(key)

        # Assert
        assert result is True
        mock_redis_client.exists.assert_awaited_once_with(key)

    async def test_get_pattern(self, cache_ops, mock_redis_client):
        """Test getting keys by pattern."""
        # Arrange
        pattern = "test:*"
        keys = [generate_test_key("test") for _ in range(3)]
        values = [{"value": f"test{i}"} for i in range(3)]
        
        mock_redis_client.keys = AsyncMock(return_value=keys)
        mock_redis_client.mget = AsyncMock(
            return_value=[json.dumps(v) for v in values]
        )

        # Act
        result = await cache_ops.get_pattern(pattern)

        # Assert
        assert len(result) == 3
        mock_redis_client.keys.assert_awaited_once_with(pattern)
        mock_redis_client.mget.assert_awaited_once_with(keys)
        
        for key, value in zip(keys, values):
            assert result[key] == value

    async def test_delete_pattern(
        self,
        cache_ops,
        mock_redis_client,
        mock_message_hub_client
    ):
        """Test deleting keys by pattern."""
        # Arrange
        pattern = "test:*"
        keys = [generate_test_key("test") for _ in range(3)]
        mock_redis_client.keys = AsyncMock(return_value=keys)
        mock_redis_client.delete = AsyncMock(return_value=len(keys))

        # Act
        count = await cache_ops.delete_pattern(pattern)

        # Assert
        assert count == len(keys)
        mock_redis_client.keys.assert_awaited_once_with(pattern)
        mock_redis_client.delete.assert_awaited_once_with(*keys)
        mock_message_hub_client.publish_event.assert_awaited_once()

    async def test_set_with_ttl(self, cache_ops, mock_redis_client):
        """Test setting a key with TTL."""
        # Arrange
        key = generate_test_key()
        value = {"test": "value"}
        ttl = 3600  # 1 hour

        # Act
        await cache_ops.set(key, value, ttl=ttl)

        # Assert
        mock_redis_client.setex.assert_awaited_once_with(
            key,
            ttl,
            json.dumps(value)
        )

    async def test_increment(self, cache_ops, mock_redis_client):
        """Test incrementing a counter."""
        # Arrange
        key = generate_test_key()
        mock_redis_client.incr = AsyncMock(return_value=1)

        # Act
        result = await cache_ops.increment(key)

        # Assert
        assert result == 1
        mock_redis_client.incr.assert_awaited_once_with(key)

    async def test_decrement(self, cache_ops, mock_redis_client):
        """Test decrementing a counter."""
        # Arrange
        key = generate_test_key()
        mock_redis_client.decr = AsyncMock(return_value=0)

        # Act
        result = await cache_ops.decrement(key)

        # Assert
        assert result == 0
        mock_redis_client.decr.assert_awaited_once_with(key)

    @pytest.mark.parametrize("error", [
        Exception("Generic error"),
        redis.ConnectionError("Connection error"),
        redis.TimeoutError("Timeout error")
    ])
    async def test_error_handling(self, cache_ops, mock_redis_client, error):
        """Test error handling for Redis operations."""
        # Arrange
        key = generate_test_key()
        mock_redis_client.get.side_effect = error

        # Act/Assert
        with pytest.raises(type(error)):
            await cache_ops.get(key)