"""Tests for style and theme API endpoints."""

from datetime import datetime
from typing import Dict, List
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from redis.asyncio import Redis

from image_service.api.routes.styles import router as styles_router
from image_service.api.schemas.style import (
    StyleElement,
    StylePreset,
    StyleRequest,
    Theme,
    ThemeVariation,
)
from image_service.services.style import StyleService
from image_service.services.validation import StyleValidationService
from image_service.core.cache import CacheManager

# Test data
TEST_ELEMENTS = [
    StyleElement(
        category="architecture",
        name="castle",
        display_name="Castle",
        description="Medieval castle architecture",
        weight=1.0,
        modifiers={
            "style_strength": 0.8,
            "realism": 0.7,
        },
    ),
    StyleElement(
        category="clothing",
        name="royal",
        display_name="Royal Attire",
        description="Elegant royal clothing",
        weight=1.0,
        modifiers={
            "detail": 0.9,
            "authenticity": 0.8,
        },
    ),
]

TEST_THEME = Theme(
    name="medieval",
    display_name="Medieval Fantasy",
    description="Classic medieval fantasy setting",
    base_theme=None,
    properties={
        "color_scheme": "rich",
        "lighting": "dramatic",
        "atmosphere": "mystical",
    },
    elements=TEST_ELEMENTS,
)

TEST_VARIATION = ThemeVariation(
    name="dark_medieval",
    display_name="Dark Medieval",
    description="Darker take on medieval fantasy",
    base_theme="medieval",
    properties={
        "color_scheme": "dark",
        "lighting": "moody",
        "atmosphere": "ominous",
    },
    elements=TEST_ELEMENTS,
)

TEST_PRESET = StylePreset(
    name="castle_interior",
    display_name="Castle Interior",
    description="Interior of a medieval castle",
    category="architecture",
    elements=[TEST_ELEMENTS[0]],  # Castle architecture
    compatibility=["medieval", "dark_medieval"],
)


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    redis = AsyncMock(spec=Redis)
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=True)
    return redis


@pytest.fixture
def cache_manager(mock_redis):
    """Create a cache manager instance."""
    return CacheManager(mock_redis)


@pytest.fixture
def style_service(mock_redis):
    """Create a style service instance."""
    service = StyleService(mock_redis)
    # Mock theme and preset lists
    service.list_themes = AsyncMock(return_value=[TEST_THEME, TEST_VARIATION])
    service.list_style_presets = AsyncMock(return_value=[TEST_PRESET])
    service.get_theme = AsyncMock(side_effect=lambda name: {
        "medieval": TEST_THEME,
        "dark_medieval": TEST_VARIATION,
    }.get(name))
    service.get_preset = AsyncMock(return_value=TEST_PRESET)
    return service


@pytest.fixture
def validation_service():
    """Create a validation service instance."""
    return StyleValidationService()


@pytest.fixture
def test_app(style_service, validation_service, cache_manager):
    """Create test FastAPI application."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(styles_router)

    # Override service dependencies
    app.dependency_overrides = {
        "get_style_service": lambda: style_service,
        "get_validation_service": lambda: validation_service,
        "get_cache_manager": lambda: cache_manager,
    }
    return app


@pytest.fixture
def client(test_app):
    """Create test client."""
    return TestClient(test_app)


class TestStyleEndpoints:
    """Test style API endpoints."""

    def test_list_styles(self, client, style_service):
        """Test GET /api/v2/images/styles endpoint."""
        response = client.get("/api/v2/images/styles")
        assert response.status_code == 200

        data = response.json()
        # Check themes
        themes = data["visual_themes"]
        assert "medieval" in themes
        assert "dark_medieval" in themes
        assert themes["medieval"]["display_name"] == "Medieval Fantasy"

        # Check elements by category
        elements = data["style_elements"]
        assert "architecture" in elements
        assert "clothing" in elements
        assert elements["architecture"][0]["name"] == "castle"

        # Check compatibility matrix
        compat = data["compatibility"]
        assert "medieval" in compat
        assert compat["medieval"][0] == TEST_PRESET.name

    def test_get_theme(self, client, style_service):
        """Test GET /api/v2/images/themes/{theme_name} endpoint."""
        response = client.get("/api/v2/images/themes/medieval")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "medieval"
        assert data["display_name"] == "Medieval Fantasy"
        assert len(data["elements"]) == 2

    def test_get_theme_not_found(self, client, style_service):
        """Test getting non-existent theme."""
        style_service.get_theme.return_value = None
        response = client.get("/api/v2/images/themes/nonexistent")
        assert response.status_code == 404

    def test_get_preset(self, client, style_service):
        """Test GET /api/v2/images/presets/{preset_name} endpoint."""
        response = client.get("/api/v2/images/presets/castle_interior")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "castle_interior"
        assert data["category"] == "architecture"
        assert len(data["elements"]) == 1

    def test_get_preset_not_found(self, client, style_service):
        """Test getting non-existent preset."""
        style_service.get_preset.return_value = None
        response = client.get("/api/v2/images/presets/nonexistent")
        assert response.status_code == 404

    def test_validate_style(self, client, validation_service):
        """Test POST /api/v2/images/styles/validate endpoint."""
        style = StyleRequest(
            theme_name="medieval",
            preset_name="castle_interior",
            parameters={
                "style_strength": 0.8,
                "realism": 0.7,
            },
        )
        
        response = client.post(
            "/api/v2/images/styles/validate",
            json=style.dict(),
        )
        assert response.status_code == 200

        data = response.json()
        assert "issues" in data
        assert isinstance(data["issues"], list)

    def test_validate_style_invalid(self, client):
        """Test validation with invalid style request."""
        response = client.post(
            "/api/v2/images/styles/validate",
            json={
                "theme_name": "nonexistent",
                "preset_name": "invalid",
                "parameters": {"invalid": -1},
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_theme_list_cache(self, style_service, cache_manager):
        """Test theme list caching."""
        # First call should query service
        themes = await style_service.list_themes()
        assert style_service.list_themes.call_count == 1

        # Cache the themes
        await cache_manager.warmup_cache(themes=themes)

        # Second call should use cache
        cached = await cache_manager.get_theme("medieval")
        assert cached == TEST_THEME

    @pytest.mark.asyncio
    async def test_preset_list_cache(self, style_service, cache_manager):
        """Test preset list caching."""
        # First call should query service
        presets = await style_service.list_style_presets()
        assert style_service.list_style_presets.call_count == 1

        # Cache the presets
        await cache_manager.warmup_cache(presets=presets)

        # Second call should use cache
        cached = await cache_manager.get_preset("castle_interior")
        assert cached == TEST_PRESET
