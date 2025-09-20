"""Unit tests for character content generation."""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from llm_service.core.exceptions import ContentGenerationError
from llm_service.models.character_content import (
    BackgroundNarrative,
    CharacterArc,
    CharacterContentType,
    PersonalityTraits,
)
from llm_service.services.character_content import CharacterContentService


@pytest.fixture
def theme_service():
    """Theme service mock fixture."""
    return MagicMock()


@pytest.fixture
def openai_provider():
    """OpenAI provider mock fixture."""
    provider = AsyncMock()
    provider.setup = AsyncMock()
    provider.cleanup = AsyncMock()
    return provider


@pytest.fixture
def settings():
    """Settings mock fixture."""
    return MagicMock()


@pytest.fixture
def character_content_service(settings, openai_provider, theme_service):
    """Character content service fixture."""
    return CharacterContentService(settings, openai_provider, theme_service)


@pytest.fixture
def character_data():
    """Sample character data fixture."""
    return {
        "race": "High Elf",
        "class": "Wizard",
        "background": "Sage",
        "level": 1,
        "alignment": "Neutral Good",
    }


@pytest.fixture
def theme_context():
    """Sample theme context fixture."""
    return {
        "genre": "High Fantasy",
        "tone": "Epic",
        "setting": "Forgotten Realms",
    }


@pytest.fixture
def campaign_context():
    """Sample campaign context fixture."""
    return {
        "type": "Traditional",
        "current_arc": "Rise of the Dragon Cult",
        "party_level": 1,
    }


@pytest.mark.asyncio
async def test_generate_personality_traits_success(
    character_content_service,
    character_data,
    theme_context,
    campaign_context,
    openai_provider,
):
    """Test successful personality traits generation."""
    # Mock response
    mock_response = {
        "alignment_traits": {"lawful_chaotic": "Tends towards lawful"},
        "personality_characteristics": ["Studious", "Analytical"],
        "bonds": ["Devoted to arcane knowledge"],
        "ideals": ["Knowledge is power"],
        "flaws": ["Overconfident in magical ability"],
        "quirks": ["Always carries a lucky quill"],
    }
    openai_provider.generate_text.return_value = json.dumps(mock_response)

    # Generate traits
    result = await character_content_service.generate_personality_traits(
        character_data=character_data,
        theme_context=theme_context,
        campaign_context=campaign_context,
    )

    # Verify response
    assert isinstance(result, PersonalityTraits)
    assert result.alignment_traits == mock_response["alignment_traits"]
    assert result.personality_characteristics == mock_response["personality_characteristics"]
    assert result.bonds == mock_response["bonds"]
    assert result.ideals == mock_response["ideals"]
    assert result.flaws == mock_response["flaws"]
    assert result.quirks == mock_response["quirks"]


@pytest.mark.asyncio
async def test_generate_background_narrative_success(
    character_content_service,
    character_data,
    theme_context,
    campaign_context,
    openai_provider,
):
    """Test successful background narrative generation."""
    # Mock response
    mock_response = {
        "early_life": "Grew up in a prestigious elven academy",
        "defining_events": ["Discovery of magical talent", "First spell success"],
        "relationships": {"Master Eldeth": "Mentor and guide"},
        "motivations": ["Unlock ancient magical secrets"],
        "secrets": ["Found forbidden spellbook"],
    }
    openai_provider.generate_text.return_value = json.dumps(mock_response)

    # Generate background
    result = await character_content_service.generate_background_narrative(
        character_data=character_data,
        theme_context=theme_context,
        campaign_context=campaign_context,
    )

    # Verify response
    assert isinstance(result, BackgroundNarrative)
    assert result.early_life == mock_response["early_life"]
    assert result.defining_events == mock_response["defining_events"]
    assert result.relationships == mock_response["relationships"]
    assert result.motivations == mock_response["motivations"]
    assert result.secrets == mock_response["secrets"]


@pytest.mark.asyncio
async def test_generate_character_arc_success(
    character_content_service,
    character_data,
    theme_context,
    campaign_context,
    openai_provider,
):
    """Test successful character arc generation."""
    # Mock response
    mock_response = {
        "current_state": "Novice wizard seeking knowledge",
        "potential_developments": ["Master of Ancient Magic", "Arcane Researcher"],
        "growth_opportunities": ["Learn from ancient tomes", "Study with masters"],
        "challenges": ["Overcome fear of failure", "Balance power and wisdom"],
        "arc_themes": ["Knowledge vs Wisdom", "Power and Responsibility"],
    }
    openai_provider.generate_text.return_value = json.dumps(mock_response)

    # Generate arc
    result = await character_content_service.generate_character_arc(
        character_data=character_data,
        theme_context=theme_context,
        campaign_context=campaign_context,
    )

    # Verify response
    assert isinstance(result, CharacterArc)
    assert result.current_state == mock_response["current_state"]
    assert result.potential_developments == mock_response["potential_developments"]
    assert result.growth_opportunities == mock_response["growth_opportunities"]
    assert result.challenges == mock_response["challenges"]
    assert result.arc_themes == mock_response["arc_themes"]


@pytest.mark.asyncio
async def test_generate_personality_traits_error(
    character_content_service,
    character_data,
    theme_context,
    campaign_context,
    openai_provider,
):
    """Test error handling in personality traits generation."""
    openai_provider.generate_text.side_effect = Exception("API error")

    with pytest.raises(ContentGenerationError) as exc:
        await character_content_service.generate_personality_traits(
            character_data=character_data,
            theme_context=theme_context,
            campaign_context=campaign_context,
        )
    assert "Failed to generate personality traits" in str(exc.value)


@pytest.mark.asyncio
async def test_generate_background_narrative_error(
    character_content_service,
    character_data,
    theme_context,
    campaign_context,
    openai_provider,
):
    """Test error handling in background narrative generation."""
    openai_provider.generate_text.side_effect = Exception("API error")

    with pytest.raises(ContentGenerationError) as exc:
        await character_content_service.generate_background_narrative(
            character_data=character_data,
            theme_context=theme_context,
            campaign_context=campaign_context,
        )
    assert "Failed to generate background narrative" in str(exc.value)


@pytest.mark.asyncio
async def test_generate_character_arc_error(
    character_content_service,
    character_data,
    theme_context,
    campaign_context,
    openai_provider,
):
    """Test error handling in character arc generation."""
    openai_provider.generate_text.side_effect = Exception("API error")

    with pytest.raises(ContentGenerationError) as exc:
        await character_content_service.generate_character_arc(
            character_data=character_data,
            theme_context=theme_context,
            campaign_context=campaign_context,
        )
    assert "Failed to generate character arc" in str(exc.value)


@pytest.mark.asyncio
async def test_prompt_building(
    character_content_service,
    character_data,
    theme_context,
    campaign_context,
):
    """Test prompt building for different content types."""
    # Test personality traits prompt
    personality_prompt = character_content_service._build_personality_prompt(
        character_data,
        theme_context,
        campaign_context,
    )
    assert character_data["race"] in personality_prompt
    assert character_data["class"] in personality_prompt
    assert character_data["background"] in personality_prompt
    assert "alignment_traits" in personality_prompt
    assert "personality_characteristics" in personality_prompt

    # Test background narrative prompt
    background_prompt = character_content_service._build_background_prompt(
        character_data,
        theme_context,
        campaign_context,
    )
    assert character_data["race"] in background_prompt
    assert character_data["class"] in background_prompt
    assert character_data["background"] in background_prompt
    assert "early_life" in background_prompt
    assert "defining_events" in background_prompt

    # Test character arc prompt
    arc_prompt = character_content_service._build_arc_prompt(
        character_data,
        theme_context,
        campaign_context,
    )
    assert character_data["race"] in arc_prompt
    assert character_data["class"] in arc_prompt
    assert character_data["background"] in arc_prompt
    assert "current_state" in arc_prompt
    assert "potential_developments" in arc_prompt


@pytest.mark.asyncio
async def test_invalid_json_response(
    character_content_service,
    character_data,
    theme_context,
    campaign_context,
    openai_provider,
):
    """Test handling of invalid JSON response."""
    openai_provider.generate_text.return_value = "Invalid JSON"

    with pytest.raises(ContentGenerationError) as exc:
        await character_content_service.generate_personality_traits(
            character_data=character_data,
            theme_context=theme_context,
            campaign_context=campaign_context,
        )
    assert "Failed to parse personality traits" in str(exc.value)


@pytest.mark.asyncio
async def test_missing_required_fields(
    character_content_service,
    character_data,
    theme_context,
    campaign_context,
    openai_provider,
):
    """Test handling of missing required fields in response."""
    mock_response = {
        # Missing required fields
        "personality_characteristics": ["Studious"],
        "bonds": ["Devoted to knowledge"],
    }
    openai_provider.generate_text.return_value = json.dumps(mock_response)

    with pytest.raises(ContentGenerationError) as exc:
        await character_content_service.generate_personality_traits(
            character_data=character_data,
            theme_context=theme_context,
            campaign_context=campaign_context,
        )
    assert "Failed to parse personality traits" in str(exc.value)