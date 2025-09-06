"""Integration tests for theme system flows."""

import pytest
from datetime import datetime
from uuid import UUID, uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from campaign.models.theme import ThemeType, ThemeTone, ThemeIntensity
from campaign.services.theme import ThemeService
from campaign.services.world_effect import WorldEffectService
from campaign.services.theme_integration import ThemeIntegrationService


@pytest.fixture
async def theme_service(db_session: AsyncSession) -> ThemeService:
    """Create theme service instance for testing."""
    return ThemeService(db_session)


@pytest.fixture
async def world_effect_service(db_session: AsyncSession) -> WorldEffectService:
    """Create world effect service instance for testing."""
    return WorldEffectService(db_session)


@pytest.fixture
async def theme_integration_service(
    db_session: AsyncSession, llm_client
) -> ThemeIntegrationService:
    """Create theme integration service instance for testing."""
    return ThemeIntegrationService(db_session, llm_client)


@pytest.fixture
async def campaign_id(client: AsyncClient) -> UUID:
    """Create a test campaign."""
    response = await client.post("/api/v2/campaigns", json={
        "title": "Test Campaign",
        "description": "A test campaign for theme flows",
        "campaign_type": "traditional",
    })
    return UUID(response.json()["id"])


@pytest.mark.asyncio
class TestThemeFlows:
    """Test cases for theme system flows."""

    async def test_theme_creation_and_validation_flow(
        self, client: AsyncClient
    ):
        """Test creating and validating a theme."""
        # Create a new theme
        theme_data = {
            "name": "Dark Fantasy",
            "description": "A grim and gritty fantasy theme",
            "type": ThemeType.FANTASY,
            "tone": ThemeTone.DARK,
            "intensity": ThemeIntensity.STRONG,
            "attributes": {
                "manifestation": "shadows and decay",
                "theme_words": ["darkness", "corruption", "despair"],
            },
            "validation_rules": {
                "tone_match": {
                    "type": "tone",
                    "tone_words": ["dark", "grim", "foreboding"],
                    "minimum_count": 2,
                },
            },
            "generation_prompts": {
                "base_prompts": [
                    "Include dark and ominous descriptions",
                ],
            },
            "style_guide": {
                "description": "Use dark and evocative language",
            },
        }

        response = await client.post("/api/v2/themes", json=theme_data)
        assert response.status_code == 200
        theme_id = UUID(response.json()["id"])

        # Validate matching content
        matching_content = {
            "name": "Shadowspire",
            "description": "A dark and foreboding tower, its walls seeping with corruption.",
        }
        response = await client.post("/api/v2/themes/validate", json={
            "theme_id": str(theme_id),
            "content": matching_content,
        })
        assert response.status_code == 200
        validation = response.json()
        assert validation["is_valid"]
        assert validation["score"] >= 0.7

        # Validate non-matching content
        non_matching_content = {
            "name": "Sunhaven",
            "description": "A bright and cheerful village full of happy people.",
        }
        response = await client.post("/api/v2/themes/validate", json={
            "theme_id": str(theme_id),
            "content": non_matching_content,
        })
        assert response.status_code == 200
        validation = response.json()
        assert not validation["is_valid"]
        assert validation["score"] <= 0.5
        assert len(validation["issues"]) > 0

    async def test_theme_combination_and_application_flow(
        self, client: AsyncClient
    ):
        """Test combining themes and applying them to content."""
        # Create two themes
        dark_fantasy = {
            "name": "Dark Fantasy",
            "type": ThemeType.FANTASY,
            "tone": ThemeTone.DARK,
            "intensity": ThemeIntensity.STRONG,
            "description": "A dark fantasy theme",
            "attributes": {},
            "validation_rules": {},
            "generation_prompts": {},
            "style_guide": {},
        }
        mystery = {
            "name": "Mystery",
            "type": ThemeType.MYSTERY,
            "tone": ThemeTone.NEUTRAL,
            "intensity": ThemeIntensity.MODERATE,
            "description": "A mystery theme",
            "attributes": {},
            "validation_rules": {},
            "generation_prompts": {},
            "style_guide": {},
        }

        response = await client.post("/api/v2/themes", json=dark_fantasy)
        assert response.status_code == 200
        theme1_id = UUID(response.json()["id"])

        response = await client.post("/api/v2/themes", json=mystery)
        assert response.status_code == 200
        theme2_id = UUID(response.json()["id"])

        # Combine themes
        response = await client.post("/api/v2/themes/combinations", json={
            "primary_theme_id": str(theme1_id),
            "secondary_theme_id": str(theme2_id),
            "weight": 0.7,
        })
        assert response.status_code == 200

        # Get combinations
        response = await client.get(f"/api/v2/themes/{theme1_id}/combinations")
        assert response.status_code == 200
        combinations = response.json()
        assert len(combinations) == 1

        # Apply combined theme to content
        content = {
            "name": "The Missing Shadow",
            "description": "A mysterious disappearance in a dark town.",
        }
        response = await client.post("/api/v2/themes/apply", json={
            "theme_id": str(theme1_id),
            "content": content,
            "parameters": {
                "secondary_theme_id": str(theme2_id),
                "combination_weight": 0.7,
            },
        })
        assert response.status_code == 200
        result = response.json()
        assert "modified_content" in result
        assert len(result["changes"]) > 0
        assert len(result["theme_elements"]) > 0

    async def test_world_effect_flow(
        self, client: AsyncClient, campaign_id: UUID
    ):
        """Test world effect creation and application."""
        # Create a theme
        theme_data = {
            "name": "Dark Fantasy",
            "type": ThemeType.FANTASY,
            "tone": ThemeTone.DARK,
            "intensity": ThemeIntensity.STRONG,
            "description": "A dark fantasy theme",
            "attributes": {
                "manifestation": "corruption and decay",
            },
            "validation_rules": {},
            "generation_prompts": {},
            "style_guide": {},
        }
        response = await client.post("/api/v2/themes", json=theme_data)
        assert response.status_code == 200
        theme_id = UUID(response.json()["id"])

        # Create a location
        location_data = {
            "name": "Ravenhollow",
            "description": "A small town surrounded by dark woods",
            "location_type": "settlement",
            "campaign_id": str(campaign_id),
            "attributes": {
                "size": "small",
                "population": 500,
            },
            "state": {
                "prosperity": 0.7,
                "safety": 0.8,
            },
        }
        response = await client.post(
            f"/api/v2/campaigns/{campaign_id}/locations",
            json=location_data,
        )
        assert response.status_code == 200
        location_id = UUID(response.json()["id"])

        # Create a world effect
        effect_data = {
            "theme_id": str(theme_id),
            "name": "Creeping Darkness",
            "description": "A supernatural darkness slowly corrupts the area",
            "effect_type": "environment",
            "parameters": {
                "state_changes": {
                    "safety": -0.2,
                    "corruption": 0.3,
                },
            },
            "conditions": {
                "required_attributes": {
                    "size": "small",
                },
                "required_state": {
                    "safety": 0.8,
                },
            },
            "impact_scale": 0.7,
            "duration": 30,
        }
        response = await client.post("/api/v2/themes/effects", json=effect_data)
        assert response.status_code == 200
        effect_id = UUID(response.json()["id"])

        # Apply effect to location
        response = await client.post(
            f"/api/v2/themes/effects/{effect_id}/apply/location/{location_id}"
        )
        assert response.status_code == 200

        # Verify effect application
        response = await client.get("/api/v2/themes/effects/active", params={
            "location_id": str(location_id),
        })
        assert response.status_code == 200
        active_effects = response.json()
        assert len(active_effects) == 1
        assert UUID(active_effects[0]["id"]) == effect_id

        # Get updated location state
        response = await client.get(
            f"/api/v2/campaigns/{campaign_id}/locations/{location_id}"
        )
        assert response.status_code == 200
        location = response.json()
        assert location["state"]["safety"] == 0.6  # Original 0.8 - 0.2
        assert location["state"]["corruption"] == 0.3

    async def test_theme_content_generation_flow(
        self, client: AsyncClient
    ):
        """Test generating themed content."""
        # Create a theme
        theme_data = {
            "name": "Dark Fantasy",
            "type": ThemeType.FANTASY,
            "tone": ThemeTone.DARK,
            "intensity": ThemeIntensity.STRONG,
            "description": "A dark fantasy theme",
            "attributes": {
                "manifestation": "corruption and decay",
                "theme_words": ["darkness", "shadow", "corruption"],
            },
            "validation_rules": {},
            "generation_prompts": {
                "location_prompts": [
                    "Include signs of decay",
                    "Add dark secrets",
                ],
            },
            "style_guide": {
                "description": "Use dark and foreboding language",
            },
        }
        response = await client.post("/api/v2/themes", json=theme_data)
        assert response.status_code == 200
        theme_id = UUID(response.json()["id"])

        # Generate a location
        response = await client.post(
            f"/api/v2/themes/{theme_id}/content/location",
            json={
                "parameters": {
                    "location_type": "settlement",
                    "size": "small",
                },
            },
        )
        assert response.status_code == 200
        location = response.json()
        assert "name" in location
        assert "description" in location
        assert location["location_type"] == "settlement"
        assert any(
            word in location["description"].lower()
            for word in ["dark", "shadow", "corruption"]
        )

        # Validate generated content
        response = await client.post("/api/v2/themes/validate", json={
            "theme_id": str(theme_id),
            "content": location,
        })
        assert response.status_code == 200
        validation = response.json()
        assert validation["is_valid"]
        assert validation["score"] >= 0.7
