"""Test configuration and fixtures for Game Session Service."""

import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
import redis.asyncio as redis
from fastapi import FastAPI
from httpx import AsyncClient

from game_session.main import app
from game_session.infrastructure.websocket import WebSocketManager

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def test_app() -> AsyncGenerator[FastAPI, None]:
    """Get the FastAPI application for testing."""
    yield app

@pytest_asyncio.fixture
async def client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Get an async HTTP client for testing."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture
async def redis_client() -> AsyncGenerator[redis.Redis, None]:
    """Get a Redis client for testing."""
    client = redis.Redis(host="localhost", port=6379, db=0)
    yield client
    await client.close()

@pytest.fixture
def websocket_manager() -> WebSocketManager:
    """Get a WebSocket manager for testing."""
    return WebSocketManager()

@pytest.fixture
def mock_message_hub() -> MagicMock:
    """Get a mock Message Hub client."""
    return MagicMock()