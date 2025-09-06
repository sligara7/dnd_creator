"""Integration tests for text generation endpoints."""
import pytest
from httpx import AsyncClient

from llm_service.schemas.text import TextType


@pytest.mark.asyncio
async def test_generate_character_content(client: AsyncClient):
    """Test character content generation endpoint."""
    # Prepare request
    request = {
        "type": TextType.CHARACTER_BACKSTORY.value,
        "character_context": {
            "character_class": "Wizard",
            "character_race": "High Elf",
            "character_level": 5,
            "alignment": "Neutral Good",
            "background": "Sage",
        },
        "theme": {
            "genre": "high fantasy",
            "tone": "serious",
            "style": "descriptive",
        },
    }

    # Make request
    response = await client.post("/api/v2/text/character", json=request)
    assert response.status_code == 200

    # Validate response
    data = response.json()
    assert "content" in data
    assert "content_id" in data
    assert data["metadata"]["content_type"] == "character"


@pytest.mark.asyncio
async def test_generate_campaign_content(client: AsyncClient):
    """Test campaign content generation endpoint."""
    # Prepare request
    request = {
        "type": TextType.CAMPAIGN_PLOT.value,
        "campaign_context": {
            "campaign_theme": "Epic Fantasy",
            "party_level": 5,
            "party_size": 4,
            "duration": "long",
        },
        "theme": {
            "genre": "fantasy",
            "tone": "epic",
            "style": "narrative",
        },
    }

    # Make request
    response = await client.post("/api/v2/text/campaign", json=request)
    assert response.status_code == 200

    # Validate response
    data = response.json()
    assert "content" in data
    assert "content_id" in data
    assert data["metadata"]["content_type"] == "campaign"


@pytest.mark.asyncio
async def test_rate_limiting(client: AsyncClient):
    """Test rate limiting for text generation."""
    # Prepare request
    request = {
        "type": TextType.CHARACTER_BACKSTORY.value,
        "character_context": {
            "character_class": "Rogue",
            "character_race": "Halfling",
            "character_level": 3,
            "alignment": "Chaotic Good",
            "background": "Criminal",
        },
        "theme": {
            "genre": "fantasy",
            "tone": "light",
            "style": "humorous",
        },
    }

    # Make multiple requests quickly
    responses = await asyncio.gather(
        *[
            client.post("/api/v2/text/character", json=request)
            for _ in range(5)
        ],
        return_exceptions=True,
    )

    # Check that some requests were rate limited
    assert any(
        r.status_code == 429 if hasattr(r, "status_code") else False
        for r in responses
    )
