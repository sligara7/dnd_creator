"""Integration tests for campaign content generation."""
import pytest
from httpx import AsyncClient

from llm_service.schemas.campaign import StoryElement, NPCRole, LocationType


@pytest.mark.asyncio
async def test_generate_story(client: AsyncClient):
    """Test story generation endpoint."""
    # Prepare request
    request = {
        "element_type": StoryElement.PLOT.value,
        "context": {
            "campaign_theme": "Epic Fantasy",
            "party_level": 5,
            "party_size": 4,
            "campaign_type": "sandbox",
            "setting": "Forgotten Realms",
            "length": "long",
        },
        "parameters": {
            "focus": "political intrigue",
            "complexity": "high",
        },
    }

    # Make request
    response = await client.post("/api/v2/campaign/story", json=request)
    assert response.status_code == 200

    # Validate response
    data = response.json()
    assert "content" in data
    assert "content_id" in data
    assert data["element_type"] == StoryElement.PLOT.value
    assert "summary" in data


@pytest.mark.asyncio
async def test_generate_npc(client: AsyncClient):
    """Test NPC generation endpoint."""
    # Prepare request
    request = {
        "role": NPCRole.QUEST_GIVER.value,
        "context": {
            "campaign_theme": "Dark Fantasy",
            "party_level": 7,
            "party_size": 5,
            "campaign_type": "linear",
            "setting": "Ravenloft",
            "length": "medium",
        },
        "traits": {
            "personality": "mysterious",
            "motivation": "revenge",
        },
    }

    # Make request
    response = await client.post("/api/v2/campaign/npc", json=request)
    assert response.status_code == 200

    # Validate response
    data = response.json()
    assert "name" in data
    assert "description" in data
    assert "personality" in data
    assert "motivations" in data
    assert data["role"] == NPCRole.QUEST_GIVER.value


@pytest.mark.asyncio
async def test_generate_location(client: AsyncClient):
    """Test location generation endpoint."""
    # Prepare request
    request = {
        "location_type": LocationType.DUNGEON.value,
        "context": {
            "campaign_theme": "Classic D&D",
            "party_level": 3,
            "party_size": 4,
            "campaign_type": "dungeon crawl",
            "setting": "Sword Coast",
            "length": "short",
        },
        "size": "medium",
        "purpose": "ancient temple",
        "features": ["traps", "puzzles", "undead"],
    }

    # Make request
    response = await client.post("/api/v2/campaign/location", json=request)
    assert response.status_code == 200

    # Validate response
    data = response.json()
    assert "name" in data
    assert "description" in data
    assert "points_of_interest" in data
    assert "occupants" in data
    assert "hooks" in data
    assert data["location_type"] == LocationType.DUNGEON.value


@pytest.mark.asyncio
async def test_content_validation(client: AsyncClient):
    """Test content validation integration."""
    # Generate story content
    story_request = {
        "element_type": StoryElement.QUEST.value,
        "context": {
            "campaign_theme": "High Fantasy",
            "party_level": 5,
            "party_size": 4,
            "campaign_type": "mixed",
            "setting": "Homebrew",
            "length": "medium",
        },
    }
    story_response = await client.post(
        "/api/v2/campaign/story",
        json=story_request,
    )
    assert story_response.status_code == 200
    story_data = story_response.json()

    # Validate generated content
    validation_request = {
        "content": story_data["content"],
        "content_type": "quest",
        "rules": [
            {
                "category": "quality",
                "name": "content_quality",
                "is_required": True,
            },
            {
                "category": "theme",
                "name": "theme_consistency",
                "is_required": True,
            },
        ],
        "theme": {
            "genre": "fantasy",
            "tone": "heroic",
            "style": "epic",
        },
    }

    validation_response = await client.post(
        "/api/v2/validation/content",
        json=validation_request,
    )
    assert validation_response.status_code == 200

    # Check validation results
    validation_data = validation_response.json()
    assert validation_data["passed"]  # All required rules should pass
    assert validation_data["overall_score"] >= 0.7  # Good quality threshold
