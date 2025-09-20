"""Shared pytest fixtures for cache service tests."""

import asyncio
import json
import os
from typing import AsyncGenerator, Dict, Any
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
import redis.asyncio as redis
from message_hub.client import MessageHubClient

# Test configuration
TEST_CONFIG = {
    "redis": {
        "url": os.getenv("TEST_REDIS_URL", "redis://localhost:6379/1"),
        "pool_size": 5,
        "timeout": 1.0
    },
    "message_hub": {
        "url": os.getenv("TEST_MESSAGE_HUB_URL", "amqp://localhost:5672"),
        "auth_key": "test-auth-key"
    }
}

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def redis_client() -> AsyncGenerator[redis.Redis, None]:
    """Create a Redis client for testing."""
    client = redis.Redis.from_url(
        TEST_CONFIG["redis"]["url"],
        max_connections=TEST_CONFIG["redis"]["pool_size"],
        socket_timeout=TEST_CONFIG["redis"]["timeout"]
    )
    try:
        await client.ping()
        yield client
    finally:
        await client.close()

@pytest.fixture
def mock_redis_client() -> MagicMock:
    """Create a mock Redis client."""
    mock = MagicMock()
    # Add common Redis method mocks
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=1)
    mock.exists = AsyncMock(return_value=True)
    mock.ping = AsyncMock(return_value=True)
    mock.close = AsyncMock()
    return mock

@pytest_asyncio.fixture
async def message_hub_client() -> AsyncGenerator[MessageHubClient, None]:
    """Create a Message Hub client for testing."""
    client = MessageHubClient(
        service_name="cache-service-test",
        rabbitmq_url=TEST_CONFIG["message_hub"]["url"],
        auth_key=TEST_CONFIG["message_hub"]["auth_key"]
    )
    try:
        await client.connect()
        yield client
    finally:
        await client.close()

@pytest.fixture
def mock_message_hub_client() -> MagicMock:
    """Create a mock Message Hub client."""
    mock = MagicMock()
    # Add common Message Hub method mocks
    mock.connect = AsyncMock()
    mock.close = AsyncMock()
    mock.publish_event = AsyncMock()
    mock.subscribe = AsyncMock()
    return mock

@pytest.fixture
def sample_cache_data() -> Dict[str, Any]:
    """Sample cache data for testing."""
    return {
        "key1": json.dumps({"value": "test1"}),
        "key2": json.dumps({"value": "test2"}),
        "prefix:key3": json.dumps({"value": "test3"}),
        "prefix:key4": json.dumps({"value": "test4"})
    }

@pytest_asyncio.fixture
async def populated_redis(redis_client, sample_cache_data):
    """Redis client pre-populated with sample data."""
    try:
        # Clear test database first
        await redis_client.flushdb()
        
        # Populate with sample data
        for key, value in sample_cache_data.items():
            await redis_client.set(key, value)
        
        yield redis_client
        
    finally:
        # Cleanup
        await redis_client.flushdb()

@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return {
        "redis": {
            "url": "redis://localhost:6379/1",
            "pool_size": 5,
            "timeout": 1.0,
            "max_retries": 3,
            "retry_interval": 1.0
        },
        "message_hub": {
            "url": "amqp://localhost:5672",
            "auth_key": "test-auth-key",
            "max_retries": 3,
            "retry_interval": 1.0
        },
        "service": {
            "name": "cache-service-test",
            "version": "1.0.0"
        }
    }