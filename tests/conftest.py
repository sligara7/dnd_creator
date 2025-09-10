"""
Integration Test Fixtures

This module provides shared test fixtures for integration tests between services.
All fixtures here are available to test modules in the integration test suite.
"""

import os
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from typing import AsyncGenerator, Dict
from uuid import UUID

# Database Fixtures

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_db():
    """Provide test database session with transaction isolation"""
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker
    
    # Use test database URL from environment
    DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test_db")
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    session = async_session()
    try:
        # Start transactions
        await session.begin()
        await session.begin_nested()
        yield session
        await session.rollback()
    finally:
        await session.close()

# Message Hub Fixtures

@pytest.fixture
def mock_message_hub():
    """Mock Message Hub for testing service integration"""
    with patch("shared.message_hub.MessageHub") as mock:
        # Configure basic mocked behavior
        mock.publish_event = MagicMock()
        mock.subscribe = MagicMock()
        mock.unsubscribe = MagicMock()
        yield mock

# Service Mocks

@pytest.fixture
def mock_character_service():
    """Mock Character Service for integration tests"""
    with patch("shared.services.character.CharacterService") as mock:
        mock.get_character = MagicMock()
        mock.update_character = MagicMock()
        yield mock

@pytest.fixture
def mock_campaign_service():
    """Mock Campaign Service for integration tests"""
    with patch("shared.services.campaign.CampaignService") as mock:
        mock.get_campaign = MagicMock()
        mock.update_campaign = MagicMock()
        yield mock

@pytest.fixture
def mock_image_service():
    """Mock Image Service for integration tests"""
    with patch("shared.services.image.ImageService") as mock:
        mock.generate_image = MagicMock()
        mock.get_image = MagicMock()
        yield mock

@pytest.fixture
def mock_llm_service():
    """Mock LLM Service for integration tests"""
    with patch("shared.services.llm.LLMService") as mock:
        mock.generate_content = MagicMock()
        yield mock

# Test Data Fixtures

@pytest.fixture
def test_character_data():
    """Sample character data for testing"""
    return {
        "id": UUID("12345678-1234-5678-1234-567812345678"),
        "name": "Test Character",
        "species": "Human",
        "class": "Fighter",
        "level": 1,
        "ability_scores": {
            "strength": 15,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 8
        }
    }

@pytest.fixture
def test_campaign_data():
    """Sample campaign data for testing"""
    return {
        "id": UUID("87654321-4321-8765-4321-876543210987"),
        "name": "Test Campaign",
        "concept": "A heroic fantasy adventure",
        "theme": {
            "primary": "High Fantasy",
            "secondary": "Political Intrigue"
        },
        "target_sessions": 5,
        "target_level_range": {
            "start": 1,
            "end": 5
        }
    }

@pytest.fixture
def test_map_request():
    """Sample map generation request for testing"""
    return {
        "type": "tactical",
        "grid_size": {"width": 20, "height": 20},
        "theme": "fantasy",
        "features": ["forest", "river", "cliff"],
        "overlay_data": {
            "characters": [
                {"id": "uuid", "position": {"x": 5, "y": 5}}
            ],
            "spell_effects": [
                {
                    "type": "circle",
                    "radius": 20,
                    "center": {"x": 10, "y": 10}
                }
            ]
        }
    }

# Event Testing Utilities

@pytest.fixture
def event_history():
    """Track published events during tests"""
    return []

@pytest.fixture
def track_events(event_history, mock_message_hub):
    """Record events published to Message Hub"""
    def _track_event(event_type: str, data: Dict):
        event_history.append({
            "type": event_type,
            "data": data
        })
    
    mock_message_hub.publish_event.side_effect = _track_event
    return mock_message_hub

# Cache Testing

@pytest.fixture
async def test_cache():
    """Provide test cache instance"""
    from shared.cache import Cache
    
    cache = Cache()
    await cache.connect()
    await cache.clear()  # Ensure clean state
    
    yield cache
    
    await cache.clear()  # Cleanup after test
    await cache.disconnect()

# Health Check Testing

@pytest.fixture
def mock_health_checks():
    """Mock health check responses"""
    with patch("shared.health.HealthCheck") as mock:
        mock.check_database = MagicMock(return_value=True)
        mock.check_cache = MagicMock(return_value=True)
        mock.check_message_hub = MagicMock(return_value=True)
        yield mock
