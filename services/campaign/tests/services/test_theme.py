"""Unit tests for theme management service."""

import pytest
from datetime import datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from campaign.models.theme import Theme, ThemeType, ThemeTone, ThemeIntensity
from campaign.models.api.theme import ThemeCreate, ThemeUpdate
from campaign.services.theme import ThemeService


@pytest.fixture
async def theme_service(db_session: AsyncSession) -> ThemeService:
    """Create theme service instance for testing."""
    return ThemeService(db_session)


@pytest.fixture
async def test_theme_data() -> ThemeCreate:
    """Create test theme data."""
    return ThemeCreate(
        name="Dark Fantasy",
        description="A grim and gritty fantasy theme",
        type=ThemeType.FANTASY,
        tone=ThemeTone.DARK,
        intensity=ThemeIntensity.STRONG,
        attributes={
            "manifestation": "shadows and decay",
            "theme_words": ["darkness", "corruption", "despair"],
            "influence": "growing darkness",
        },
        validation_rules={
            "tone_match": {
                "type": "tone",
                "tone_words": ["dark", "grim", "foreboding"],
                "minimum_count": 2,
            },
            "required_elements": {
                "type": "required_words",
                "words": ["shadow", "dark", "corrupt"],
            },
        },
        generation_prompts={
            "base_prompts": [
                "Include dark and ominous descriptions",
                "Focus on decay and corruption",
            ],
            "location_prompts": [
                "Describe signs of decay and abandonment",
                "Include shadowy corners and dark secrets",
            ],
        },
        style_guide={
            "description": "Use dark and evocative language",
            "name": "Include dark or corrupted elements",
            "suggestions": [
                "Add more descriptions of decay",
                "Include more shadows and darkness",
            ],
        },
    )


@pytest.mark.asyncio
class TestThemeService:
    """Test cases for theme service."""

    async def test_create_theme(
        self, theme_service: ThemeService, test_theme_data: ThemeCreate
    ):
        """Test theme creation."""
        theme = await theme_service.create_theme(test_theme_data)

        assert theme is not None
        assert theme.name == test_theme_data.name
        assert theme.type == test_theme_data.type
        assert theme.tone == test_theme_data.tone
        assert theme.intensity == test_theme_data.intensity
        assert theme.attributes == test_theme_data.attributes
        assert theme.validation_rules == test_theme_data.validation_rules
        assert theme.generation_prompts == test_theme_data.generation_prompts
        assert theme.style_guide == test_theme_data.style_guide
        assert not theme.is_deleted
        assert theme.created_at is not None
        assert theme.updated_at is not None

    async def test_get_theme(
        self, theme_service: ThemeService, test_theme_data: ThemeCreate
    ):
        """Test retrieving a theme."""
        created_theme = await theme_service.create_theme(test_theme_data)
        fetched_theme = await theme_service.get_theme(created_theme.id)

        assert fetched_theme is not None
        assert fetched_theme.id == created_theme.id
        assert fetched_theme.name == test_theme_data.name

    async def test_get_nonexistent_theme(self, theme_service: ThemeService):
        """Test retrieving a non-existent theme."""
        theme = await theme_service.get_theme(uuid4())
        assert theme is None

    async def test_list_themes(
        self, theme_service: ThemeService, test_theme_data: ThemeCreate
    ):
        """Test listing themes with filters."""
        # Create test themes
        await theme_service.create_theme(test_theme_data)
        await theme_service.create_theme(ThemeCreate(
            name="Light Adventure",
            description="A light and heroic adventure theme",
            type=ThemeType.FANTASY,
            tone=ThemeTone.LIGHT,
            intensity=ThemeIntensity.MODERATE,
            attributes={},
            validation_rules={},
            generation_prompts={},
            style_guide={},
        ))

        # Test without filters
        themes = await theme_service.list_themes()
        assert len(themes) == 2

        # Test with type filter
        themes = await theme_service.list_themes(type_filter=ThemeType.FANTASY)
        assert len(themes) == 2

        # Test with tone filter
        themes = await theme_service.list_themes(tone_filter=ThemeTone.DARK)
        assert len(themes) == 1
        assert themes[0].name == "Dark Fantasy"

    async def test_update_theme(
        self, theme_service: ThemeService, test_theme_data: ThemeCreate
    ):
        """Test updating a theme."""
        created_theme = await theme_service.create_theme(test_theme_data)
        
        update_data = ThemeUpdate(
            name="Updated Dark Fantasy",
            description=test_theme_data.description,
            type=test_theme_data.type,
            tone=test_theme_data.tone,
            intensity=ThemeIntensity.OVERWHELMING,
            attributes=test_theme_data.attributes,
            validation_rules=test_theme_data.validation_rules,
            generation_prompts=test_theme_data.generation_prompts,
            style_guide=test_theme_data.style_guide,
        )

        updated_theme = await theme_service.update_theme(
            created_theme.id, update_data
        )

        assert updated_theme is not None
        assert updated_theme.name == "Updated Dark Fantasy"
        assert updated_theme.intensity == ThemeIntensity.OVERWHELMING
        assert updated_theme.updated_at > updated_theme.created_at

    async def test_update_nonexistent_theme(
        self, theme_service: ThemeService, test_theme_data: ThemeCreate
    ):
        """Test updating a non-existent theme."""
        update_data = ThemeUpdate(**test_theme_data.dict())
        updated_theme = await theme_service.update_theme(uuid4(), update_data)
        assert updated_theme is None

    async def test_delete_theme(
        self, theme_service: ThemeService, test_theme_data: ThemeCreate
    ):
        """Test deleting a theme."""
        created_theme = await theme_service.create_theme(test_theme_data)
        
        # Delete the theme
        success = await theme_service.delete_theme(created_theme.id)
        assert success

        # Verify theme is soft deleted
        theme = await theme_service.get_theme(created_theme.id)
        assert theme is None

        # Try to delete again
        success = await theme_service.delete_theme(created_theme.id)
        assert not success

    async def test_combine_themes(
        self, theme_service: ThemeService, test_theme_data: ThemeCreate
    ):
        """Test combining themes."""
        # Create two themes
        theme1 = await theme_service.create_theme(test_theme_data)
        theme2 = await theme_service.create_theme(ThemeCreate(
            name="Mystery",
            description="A mysterious and intriguing theme",
            type=ThemeType.MYSTERY,
            tone=ThemeTone.NEUTRAL,
            intensity=ThemeIntensity.MODERATE,
            attributes={},
            validation_rules={},
            generation_prompts={},
            style_guide={},
        ))

        # Combine themes
        success = await theme_service.combine_themes(
            theme1.id, theme2.id, weight=0.7
        )
        assert success

        # Get combinations
        combinations = await theme_service.get_theme_combinations(theme1.id)
        assert len(combinations) == 1
        theme, weight = combinations[0]
        assert theme.id == theme2.id
        assert weight == 0.7

    async def test_combine_nonexistent_themes(self, theme_service: ThemeService):
        """Test combining non-existent themes."""
        success = await theme_service.combine_themes(
            uuid4(), uuid4(), weight=0.5
        )
        assert not success


@pytest.mark.asyncio
class TestThemeValidation:
    """Test cases for theme validation."""

    async def test_validate_theme_compatibility(
        self, theme_service: ThemeService, test_theme_data: ThemeCreate
    ):
        """Test theme compatibility validation."""
        # Create two themes
        theme1 = await theme_service.create_theme(test_theme_data)
        theme2 = await theme_service.create_theme(ThemeCreate(
            name="Horror",
            description="A horrific theme",
            type=ThemeType.HORROR,
            tone=ThemeTone.DARK,
            intensity=ThemeIntensity.OVERWHELMING,
            attributes={},
            validation_rules={},
            generation_prompts={},
            style_guide={},
        ))

        # Validate compatibility
        result = await theme_service.validate_theme_compatibility(
            theme1.id, theme2.id
        )

        assert result.score >= 0.0 and result.score <= 1.0
        assert isinstance(result.is_valid, bool)
        assert isinstance(result.issues, list)
        assert isinstance(result.suggestions, list)

    async def test_validate_theme_content(
        self, theme_service: ThemeService, test_theme_data: ThemeCreate
    ):
        """Test content validation against theme."""
        theme = await theme_service.create_theme(test_theme_data)
        
        # Test content that matches theme
        matching_content = {
            "name": "Dark Tower",
            "description": "A corrupted tower full of shadows and dark secrets",
        }
        result = await theme_service.validate_theme_content({
            "theme_id": theme.id,
            "content": matching_content,
        })

        assert result.is_valid
        assert result.score >= 0.7
        assert len(result.issues) == 0

        # Test content that doesn't match theme
        non_matching_content = {
            "name": "Happy Garden",
            "description": "A bright and cheerful garden full of flowers",
        }
        result = await theme_service.validate_theme_content({
            "theme_id": theme.id,
            "content": non_matching_content,
        })

        assert not result.is_valid
        assert result.score <= 0.5
        assert len(result.issues) > 0
