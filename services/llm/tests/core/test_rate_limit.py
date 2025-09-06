"""Tests for rate limiting and caching functionality."""
import time
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from redis.asyncio import Redis

from llm_service.core.cache import RateLimiter, RedisCache
from llm_service.core.config import Settings
from llm_service.core.exceptions import RateLimitExceeded


@pytest.fixture
def settings():
    """Create test settings."""
    return Settings(
        REDIS_HOST="localhost",
        REDIS_PORT=6379,
        REDIS_DB=0,
        RATE_LIMIT_REQUESTS=100,
        RATE_LIMIT_PERIOD=60,
    )


@pytest.fixture
def mock_redis():
    """Create mock Redis client."""
    client = MagicMock(spec=Redis)
    client.incr = AsyncMock()
    client.expire = AsyncMock()
    client.get = AsyncMock()
    client.set = AsyncMock()
    client.delete = AsyncMock()
    client.exists = AsyncMock()
    return client


@pytest.fixture
def rate_limiter(settings, mock_redis):
    """Create rate limiter instance."""
    limiter = RateLimiter(mock_redis)
    limiter.settings = settings
    return limiter


@pytest.fixture
def redis_cache(settings, mock_redis):
    """Create Redis cache instance."""
    cache = RedisCache(mock_redis)
    cache.settings = settings
    return cache


@pytest.mark.asyncio
async def test_text_rate_limit(rate_limiter, mock_redis):
    """Test text generation rate limiting."""
    # Set up mock responses
    mock_redis.get.side_effect = [
        b"90",  # Below limit
        b"100",  # At limit
        b"110",  # Above limit
    ]

    # Test below limit
    await rate_limiter.check_text_limit("test")

    # Test at limit
    await rate_limiter.check_text_limit("test")

    # Test above limit
    with pytest.raises(RateLimitExceeded):
        await rate_limiter.check_text_limit("test")

    # Verify Redis calls
    assert mock_redis.get.call_count == 3
    assert mock_redis.incr.call_count == 2  # Not called when above limit


@pytest.mark.asyncio
async def test_image_rate_limit(rate_limiter, mock_redis):
    """Test image generation rate limiting."""
    # Set up mock responses
    mock_redis.get.side_effect = [
        b"8",  # Below limit
        b"10",  # At limit
        b"12",  # Above limit
    ]

    # Test below limit
    await rate_limiter.check_image_limit("test")

    # Test at limit
    await rate_limiter.check_image_limit("test")

    # Test above limit
    with pytest.raises(RateLimitExceeded):
        await rate_limiter.check_image_limit("test")

    # Verify Redis calls
    assert mock_redis.get.call_count == 3
    assert mock_redis.incr.call_count == 2  # Not called when above limit


@pytest.mark.asyncio
async def test_rate_limit_key_expiry(rate_limiter, mock_redis):
    """Test rate limit key expiration."""
    # Set up mock response
    mock_redis.get.return_value = None  # Key doesn't exist
    mock_redis.incr.return_value = 1

    # Check rate limit
    await rate_limiter.check_text_limit("test")

    # Verify expiration was set
    mock_redis.expire.assert_called_once()
    call_args = mock_redis.expire.call_args
    assert call_args[0][1] == rate_limiter.settings.RATE_LIMIT_PERIOD


@pytest.mark.asyncio
async def test_cache_operations(redis_cache, mock_redis):
    """Test basic cache operations."""
    key = "test_key"
    value = {"data": "test"}
    ttl = 300

    # Test cache set
    await redis_cache.set(key, value, ttl)
    mock_redis.set.assert_called_once_with(
        key,
        '{"data": "test"}',
        ex=ttl,
    )

    # Test cache get
    mock_redis.get.return_value = '{"data": "test"}'
    result = await redis_cache.get(key)
    assert result == value
    mock_redis.get.assert_called_once_with(key)

    # Test cache delete
    await redis_cache.delete(key)
    mock_redis.delete.assert_called_once_with(key)

    # Test cache exists
    mock_redis.exists.return_value = 1
    exists = await redis_cache.exists(key)
    assert exists is True
    mock_redis.exists.assert_called_once_with(key)


@pytest.mark.asyncio
async def test_cache_miss(redis_cache, mock_redis):
    """Test cache miss handling."""
    key = "missing_key"
    mock_redis.get.return_value = None

    result = await redis_cache.get(key)
    assert result is None
    mock_redis.get.assert_called_once_with(key)


@pytest.mark.asyncio
async def test_invalid_json_handling(redis_cache, mock_redis):
    """Test handling of invalid JSON in cache."""
    key = "invalid_json_key"
    mock_redis.get.return_value = "invalid json"

    result = await redis_cache.get(key)
    assert result is None
    mock_redis.get.assert_called_once_with(key)


@pytest.mark.asyncio
async def test_cache_with_prefix(redis_cache, mock_redis):
    """Test cache operations with key prefix."""
    key = "test_key"
    value = {"data": "test"}
    prefix = "prefix"
    ttl = 300

    # Set with prefix
    await redis_cache.set(key, value, ttl, prefix=prefix)
    mock_redis.set.assert_called_once_with(
        f"{prefix}:{key}",
        '{"data": "test"}',
        ex=ttl,
    )

    # Get with prefix
    mock_redis.get.return_value = '{"data": "test"}'
    result = await redis_cache.get(key, prefix=prefix)
    assert result == value
    mock_redis.get.assert_called_once_with(f"{prefix}:{key}")

    # Delete with prefix
    await redis_cache.delete(key, prefix=prefix)
    mock_redis.delete.assert_called_once_with(f"{prefix}:{key}")
