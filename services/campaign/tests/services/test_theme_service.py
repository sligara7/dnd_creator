"""Tests for campaign theme service."""
import pytest
from unittest.mock import AsyncMock, Mock
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from campaign_service.core.exceptions import ThemeNotFoundError, ThemeValidationError
from campaign_service.services.theme import ThemeService


@pytest.fixture
def mock_message_hub():
    """Create mock message hub client."""
    return AsyncMock()


@pytest.fixture
def theme_service(test_db: AsyncSession, mock_message_hub: AsyncMock):
    """Create theme service with mock dependencies."""
    return ThemeService(
        db=test_db,
        message_hub_client=mock_message_hub,
    )


@pytest.mark.asyncio
class TestThemeService:
    """Test theme service functionality."""
    
    async def test_get_theme_profile_primary_only(
        self,
        theme_service: ThemeService,
        mock_message_hub: AsyncMock,
    ) -> None:
        """Test getting theme profile with primary theme only."""
        # Mock theme data
        mock_message_hub.request.return_value = {
            "id": "dark_fantasy",
            "traits": ["gritty", "dark"],
            "elements": ["corruption", "moral_ambiguity"],
            "tone": "somber and brooding",
            "restrictions": ["no_lighthearted"],
        }
        
        # Get theme profile
        profile = await theme_service.get_theme_profile("dark_fantasy")
        
        # Verify correct profile construction
        assert profile["primary"] == "dark_fantasy"
        assert "gritty" in profile["traits"]
        assert "corruption" in profile["elements"]
        assert profile["tone"] == "somber and brooding"
        assert "no_lighthearted" in profile["restrictions"]
        
        # Verify message hub call
        mock_message_hub.request.assert_called_once_with(
            "catalog.get_theme",
            {"theme_id": "dark_fantasy"}
        )
    
    async def test_get_theme_profile_with_secondary(
        self,
        theme_service: ThemeService,
        mock_message_hub: AsyncMock,
    ) -> None:
        """Test getting theme profile with secondary theme."""
        # Mock theme data responses
        mock_message_hub.request.side_effect = [
            {  # Primary theme
                "id": "dark_fantasy",
                "traits": ["gritty", "dark"],
                "elements": ["corruption"],
                "tone": "somber",
                "restrictions": ["no_lighthearted"],
                "incompatible_themes": ["whimsical"],
            },
            {  # Secondary theme
                "id": "mystery",
                "traits": ["intriguing", "complex"],
                "elements": ["secrets"],
                "tone": "mysterious",
                "restrictions": ["no_straightforward"],
            },
            {  # Theme compatibility check
                "compatible": True,
                "details": "Themes complement each other",
            },
            {  # Tone blending
                "tone": "somber and mysterious",
            },
        ]
        
        # Get theme profile
        profile = await theme_service.get_theme_profile(
            "dark_fantasy",
            "mystery",
        )
        
        # Verify profile construction
        assert profile["primary"] == "dark_fantasy"
        assert profile["secondary"] == "mystery"
        assert len(profile["traits"]) == 4  # Combined traits
        assert "secrets" in profile["elements"]
        assert profile["tone"] == "somber and mysterious"
        assert len(profile["restrictions"]) == 2
        
        # Verify message hub calls
        assert mock_message_hub.request.call_count == 4
        assert mock_message_hub.request.call_args_list[0][0] == (
            "catalog.get_theme",
            {"theme_id": "dark_fantasy"},
        )
        assert mock_message_hub.request.call_args_list[1][0] == (
            "catalog.get_theme",
            {"theme_id": "mystery"},
        )
    
    async def test_theme_not_found_error(
        self,
        theme_service: ThemeService,
        mock_message_hub: AsyncMock,
    ) -> None:
        """Test error handling for non-existent theme."""
        # Mock theme not found
        mock_message_hub.request.return_value = None
        
        # Verify error raised
        with pytest.raises(ThemeNotFoundError):
            await theme_service.get_theme_profile("nonexistent_theme")
    
    async def test_incompatible_themes_error(
        self,
        theme_service: ThemeService,
        mock_message_hub: AsyncMock,
    ) -> None:
        """Test error for incompatible themes."""
        # Mock incompatible themes
        mock_message_hub.request.side_effect = [
            {  # Primary theme
                "id": "dark_fantasy",
                "traits": ["gritty"],
                "elements": ["corruption"],
                "tone": "somber",
                "restrictions": ["no_lighthearted"],
                "incompatible_themes": ["whimsical"],
            },
            {  # Secondary theme
                "id": "whimsical",
                "traits": ["light", "fun"],
                "elements": ["joy"],
                "tone": "playful",
                "restrictions": ["no_darkness"],
            },
        ]
        
        # Verify error raised
        with pytest.raises(ThemeValidationError):
            await theme_service.get_theme_profile(
                "dark_fantasy",
                "whimsical",
            )
    
    async def test_validate_theme_compatibility(
        self,
        theme_service: ThemeService,
        mock_message_hub: AsyncMock,
    ) -> None:
        """Test theme compatibility validation."""
        # Test data
        primary_theme = {
            "id": "dark_fantasy",
            "restrictions": ["no_lighthearted"],
            "incompatible_themes": ["whimsical"],
        }
        secondary_theme = {
            "id": "mystery",
            "restrictions": ["require_intrigue"],
        }
        
        # Mock LLM validation response
        mock_message_hub.request.return_value = {
            "compatible": True,
            "reason": "Themes complement each other well",
        }
        
        # Check compatibility
        result = await theme_service.validate_theme_compatibility(
            primary_theme,
            secondary_theme,
        )
        
        # Verify result
        assert result["compatible"]
        assert "complement" in result["reason"]
        
        # Verify LLM call
        mock_message_hub.request.assert_called_once_with(
            "llm.validate_theme_compatibility",
            {
                "primary_theme": primary_theme,
                "secondary_theme": secondary_theme,
                "requirements": {
                    "check_tone_clash": True,
                    "check_narrative_compatibility": True,
                    "check_setting_compatibility": True,
                },
            }
        )
    
    async def test_blend_theme_tones(
        self,
        theme_service: ThemeService,
        mock_message_hub: AsyncMock,
    ) -> None:
        """Test blending theme tones."""
        # Mock LLM response
        mock_message_hub.request.return_value = {
            "tone": "mysteriously dark and brooding",
        }
        
        # Blend tones
        result = await theme_service.blend_theme_tones(
            "dark and brooding",
            "mysterious and intriguing",
        )
        
        # Verify result
        assert result == "mysteriously dark and brooding"
        
        # Verify LLM call
        mock_message_hub.request.assert_called_once_with(
            "llm.blend_theme_tones",
            {
                "primary_tone": "dark and brooding",
                "secondary_tone": "mysterious and intriguing",
                "requirements": {
                    "maintain_primary_dominance": True,
                    "ensure_coherence": True,
                    "preserve_key_elements": True,
                },
            }
        )
    
    async def test_restriction_conflict_detection(
        self,
        theme_service: ThemeService,
    ) -> None:
        """Test detecting conflicting theme restrictions."""
        # Test conflicting restrictions
        assert theme_service._are_restrictions_conflicting(
            "no_magic",
            "require_magic",
        )
        assert theme_service._are_restrictions_conflicting(
            "require_darkness",
            "no_darkness",
        )
        
        # Test compatible restrictions
        assert not theme_service._are_restrictions_conflicting(
            "no_magic",
            "no_technology",
        )
        assert not theme_service._are_restrictions_conflicting(
            "require_intrigue",
            "require_mystery",
        )