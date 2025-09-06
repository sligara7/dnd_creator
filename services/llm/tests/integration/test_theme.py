"""Integration tests for theme analysis endpoints."""
import pytest
from httpx import AsyncClient

from llm_service.schemas.theme import ThemeCategory


@pytest.mark.asyncio
async def test_analyze_theme(client: AsyncClient):
    """Test theme analysis endpoint."""
    # Prepare request
    request = {
        "content": "A heroic tale of adventure and discovery in a mystical land.",
        "elements": ["tone", "mood", "setting"],
        "category_filter": [ThemeCategory.FANTASY.value],
    }

    # Make request
    response = await client.post("/api/v2/theme/analyze", json=request)
    assert response.status_code == 200

    # Validate response
    data = response.json()
    assert data["primary_category"] == ThemeCategory.FANTASY.value
    assert "elements" in data
    assert "overall_score" in data
    assert "summary" in data


@pytest.mark.asyncio
async def test_theme_compatibility(client: AsyncClient):
    """Test theme compatibility analysis."""
    # Prepare request
    request = {
        "content": "A dark tale of intrigue and mystery.",
        "current_theme": {
            "genre": "mystery",
            "tone": "dark",
            "style": "noir",
        },
        "target_theme": {
            "genre": "fantasy",
            "tone": "heroic",
            "style": "epic",
        },
    }

    # Make request
    response = await client.post("/api/v2/theme/analyze", json=request)
    assert response.status_code == 200

    # Validate response
    data = response.json()
    assert "compatibility" in data
    assert "score" in data["compatibility"]
    assert "conflicts" in data["compatibility"]
    assert "transition_steps" in data["compatibility"]


@pytest.mark.asyncio
async def test_theme_validation(client: AsyncClient):
    """Test theme validation for content."""
    # Prepare request
    request = {
        "content": "A lighthearted story about friendship.",
        "theme": {
            "genre": "comedy",
            "tone": "light",
            "style": "whimsical",
        },
        "validation_rules": [
            {
                "category": "theme",
                "name": "tone_consistency",
                "is_required": True,
            },
            {
                "category": "theme",
                "name": "style_alignment",
                "is_required": True,
            },
        ],
    }

    # Make request
    response = await client.post("/api/v2/validation/content", json=request)
    assert response.status_code == 200

    # Validate response
    data = response.json()
    assert "overall_score" in data
    assert "passed" in data
    assert "results" in data
    assert len(data["results"]) == len(request["validation_rules"])
