"""Test fixtures for image service integration tests."""

import os
import pytest
import aio_pika
import redis
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.main import app
from src.core.config import get_settings
from src.services.message_hub import MessageHubClient
from src.services.storage import StorageClient
from src.services.theme import ThemeClient
from src.services.cache import CacheService

settings = get_settings()

@pytest.fixture
def test_client():
    """Create test client."""
    return TestClient(app)

@pytest.fixture
async def async_client():
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def message_hub_client():
    """Create MessageHub client with test configuration."""
    connection = await aio_pika.connect_robust(
        host=os.getenv("MESSAGE_HUB_HOST", "localhost"),
        port=int(os.getenv("MESSAGE_HUB_PORT", 5672)),
    )
    channel = await connection.channel()
    client = MessageHubClient(channel)
    yield client
    await connection.close()

@pytest.fixture
async def storage_client():
    """Create Storage client with test configuration."""
    client = StorageClient(
        host=os.getenv("STORAGE_SERVICE_HOST", "localhost"),
        port=int(os.getenv("STORAGE_SERVICE_PORT", 8001)),
    )
    yield client
    await client.close()

@pytest.fixture
async def theme_client():
    """Create Theme client with test configuration."""
    client = ThemeClient(
        host=os.getenv("THEME_SERVICE_HOST", "localhost"),
        port=int(os.getenv("THEME_SERVICE_PORT", 8002)),
    )
    yield client
    await client.close()

@pytest.fixture
async def cache_service():
    """Create Cache service with test configuration."""
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True,
    )
    cache = CacheService(redis_client)
    yield cache
    await redis_client.close()

@pytest.fixture
def test_theme_data():
    """Sample theme data for testing."""
    return {
        "id": "test-theme-1",
        "name": "Fantasy",
        "description": "High fantasy theme with magical elements",
        "style_attributes": {
            "color_palette": ["#2c3e50", "#e74c3c", "#3498db"],
            "lighting": "dramatic",
            "mood": "epic",
        },
    }

@pytest.fixture
def test_image_data():
    """Sample image generation request data."""
    return {
        "portrait": {
            "character_id": "test-char-1",
            "pose": "standing",
            "theme_id": "test-theme-1",
            "equipment": ["sword", "shield"],
            "style": {
                "lighting": "dramatic",
                "background": "castle",
                "mood": "heroic",
            },
        },
        "item": {
            "item_id": "test-item-1",
            "type": "weapon",
            "name": "Flaming Sword",
            "theme_id": "test-theme-1",
            "style": {
                "angle": "front",
                "lighting": "dramatic",
                "detail_level": "high",
            },
        },
        "map": {
            "location_id": "test-loc-1",
            "type": "dungeon",
            "size": {"width": 2048, "height": 2048},
            "theme_id": "test-theme-1",
            "features": ["traps", "treasure"],
            "style": {
                "lighting": "dark",
                "atmosphere": "foreboding",
            },
        },
    }

@pytest.fixture
async def setup_test_theme(theme_client, test_theme_data):
    """Set up test theme in the system."""
    await theme_client.create_theme(test_theme_data)
    yield test_theme_data
    await theme_client.delete_theme(test_theme_data["id"])

@pytest.fixture
async def clean_cache(cache_service):
    """Ensure cache is clean before and after tests."""
    await cache_service.clear_all()
    yield
    await cache_service.clear_all()