"""Tests for the cache manager."""

import json
import zlib
from unittest.mock import AsyncMock, patch

import pytest
from redis.asyncio import Redis

from image_service.api.schemas.style import StylePreset, StyleRequest, Theme
from image_service.core.cache import CacheManager


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


# Test data
TEST_THEME = Theme(
    name="test_theme",
    display_name="Test Theme",
    description="A test theme",
    base_theme=None,
    properties={
        "color_scheme": "dark",
        "lighting": "dramatic",
        "atmosphere": "mysterious",
    },
    elements=[],
)

TEST_PRESET = StylePreset(
    name="test_preset",
    display_name="Test Preset",
    description="A test preset",
    category="architecture",
    elements=[],
    compatibility=[],
)

TEST_STYLE = StyleRequest(
    theme_name="test_theme",
    preset_name="test_preset",
    parameters={},
)


class TestCacheManager:
    """Test the cache manager functionality."""

    @pytest.mark.asyncio
    async def test_get_cached_model_hit(self, cache_manager, mock_redis):
        """Test successful cache hit."""
        # Setup
        mock_redis.get.return_value = TEST_THEME.json().encode()

        # Execute
        result = await cache_manager.get_cached_model(
            "test_key",
            Theme,
            "theme",
        )

        # Verify
        assert result == TEST_THEME
        mock_redis.get.assert_called_once_with("style:theme:test_key")

    @pytest.mark.asyncio
    async def test_get_cached_model_compressed(self, cache_manager, mock_redis):
        """Test cache hit with compressed data."""
        # Setup
        compressed = zlib.compress(TEST_THEME.json().encode())
        mock_redis.get.return_value = compressed

        # Execute
        result = await cache_manager.get_cached_model(
            "test_key",
            Theme,
            "theme",
        )

        # Verify
        assert result == TEST_THEME

    @pytest.mark.asyncio
    async def test_get_cached_model_miss(self, cache_manager, mock_redis):
        """Test cache miss."""
        # Setup
        mock_redis.get.return_value = None

        # Execute
        result = await cache_manager.get_cached_model(
            "test_key",
            Theme,
            "theme",
        )

        # Verify
        assert result is None

    @pytest.mark.asyncio
    async def test_set_cached_model(self, cache_manager, mock_redis):
        """Test setting cache entries."""
        # Execute
        await cache_manager.set_cached_model(
            "test_key",
            TEST_THEME,
            "theme",
        )

        # Verify
        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args[0]
        assert call_args[0] == "style:theme:test_key"
        assert isinstance(call_args[1], (str, bytes))

    @pytest.mark.asyncio
    async def test_set_cached_model_compression(self, cache_manager, mock_redis):
        """Test compression for large data."""
        # Setup
        large_theme = TEST_THEME.copy()
        large_theme.description = "x" * 2000  # Force compression

        # Execute
        await cache_manager.set_cached_model(
            "test_key",
            large_theme,
            "theme",
            compress=True,
        )

        # Verify compression was used
        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args[0]
        assert isinstance(call_args[1], bytes)
        assert len(call_args[1]) < len(large_theme.json())

    @pytest.mark.asyncio
    async def test_invalidate(self, cache_manager, mock_redis):
        """Test cache invalidation."""
        # Execute
        await cache_manager.invalidate("test_key", "theme")

        # Verify
        mock_redis.delete.assert_called_once_with("style:theme:test_key")

    @pytest.mark.asyncio
    async def test_theme_operations(self, cache_manager):
        """Test theme-specific cache operations."""
        # Test set
        await cache_manager.set_theme(TEST_THEME)
        
        # Test get
        mock_redis.get.return_value = TEST_THEME.json().encode()
        theme = await cache_manager.get_theme(TEST_THEME.name)
        assert theme == TEST_THEME

    @pytest.mark.asyncio
    async def test_preset_operations(self, cache_manager, mock_redis):
        """Test preset-specific cache operations."""
        # Test set
        await cache_manager.set_preset(TEST_PRESET)

        # Test get
        mock_redis.get.return_value = TEST_PRESET.json().encode()
        preset = await cache_manager.get_preset(TEST_PRESET.name)
        assert preset == TEST_PRESET

    @pytest.mark.asyncio
    async def test_style_operations(self, cache_manager, mock_redis):
        """Test style-specific cache operations."""
        # Test data
        style_params = {"param1": "value1"}

        # Test set
        await cache_manager.set_style("test_hash", style_params)

        # Test get
        mock_redis.get.return_value = json.dumps(style_params).encode()
        result = await cache_manager.get_style("test_hash")
        assert result == style_params

    @pytest.mark.asyncio
    async def test_validation_cache(self, cache_manager, mock_redis):
        """Test validation result caching."""
        # Test data
        issues = ["issue1", "issue2"]
        context = {"ctx": "value"}

        # Cache validation result
        await cache_manager.cache_validation_result(
            TEST_STYLE,
            issues,
            context,
        )

        # Retrieve validation result
        mock_redis.get.return_value = json.dumps({"issues": issues}).encode()
        result = await cache_manager.get_validation_result(
            TEST_STYLE,
            context,
        )
        assert result == issues

    @pytest.mark.asyncio
    async def test_warmup_cache(self, cache_manager):
        """Test cache warm-up functionality."""
        # Execute
        await cache_manager.warmup_cache(
            themes=[TEST_THEME],
            presets=[TEST_PRESET],
        )

        # Verify calls were made
        assert cache_manager.redis.set.call_count == 2

    @pytest.mark.asyncio
    async def test_cleanup_expired(self, cache_manager, mock_redis):
        """Test expired cache cleanup."""
        # Setup
        mock_redis.keys.return_value = ["key1", "key2"]
        mock_redis.ttl.side_effect = [-1, 100]  # First key expired

        # Execute
        await cache_manager.cleanup_expired()

        # Verify
        assert mock_redis.delete.call_count == 1

    @pytest.mark.asyncio
    async def test_error_handling(self, cache_manager, mock_redis):
        """Test error handling in cache operations."""
        # Setup
        mock_redis.get.side_effect = Exception("Redis error")

        # Execute
        result = await cache_manager.get_cached_model(
            "test_key",
            Theme,
            "theme",
        )

        # Verify
        assert result is None  # Should return None on error
