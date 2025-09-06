"""Tests for campaign factory endpoints."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from campaign.models.api.factory import (CampaignGenerationRequest,
                                    CampaignGenerationResponse,
                                    CampaignRefinementRequest,
                                    CampaignRefinementResponse,
                                    NPCGenerationRequest,
                                    NPCGenerationResponse,
                                    LocationGenerationRequest,
                                    LocationGenerationResponse,
                                    MapGenerationRequest,
                                    MapGenerationResponse,
                                    CampaignType,
                                    CampaignComplexity,
                                    CampaignLength,
                                    LevelRange,
                                    PlayerCount)
from campaign.routers.factory import router
from campaign.services.factory import CampaignFactory


@pytest.fixture
def app() -> FastAPI:
    """Create test FastAPI app with factory router."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_campaign_factory() -> Mock:
    """Create mock campaign factory."""
    return Mock(spec=CampaignFactory)


@pytest.fixture
def mock_campaign_factory_context(app: FastAPI, mock_campaign_factory: Mock):
    """Override campaign factory dependency for testing."""
    app.dependency_overrides[get_campaign_factory] = lambda: mock_campaign_factory
    yield mock_campaign_factory
    app.dependency_overrides = {}


class TestCampaignGeneration:
    """Test cases for campaign generation endpoints."""

    def test_generate_campaign_success(
        self, client: TestClient, mock_campaign_factory_context: Mock
    ):
        """Test successful campaign generation."""
        campaign_id = uuid4()
        request_data = {
            "campaign_type": CampaignType.TRADITIONAL,
            "complexity": CampaignComplexity.MODERATE,
            "length": CampaignLength.MEDIUM,
            "level_range": {"min": 1, "max": 10},
            "player_count": {"min": 3, "max": 5},
        }
        expected_response = {
            "campaign_id": str(campaign_id),
            "status": "success",
            "message": "Campaign generated successfully",
            "details": {
                "structure": {"key": "value"},
                "applied_themes": [],
            },
            "generated_content": {"key": "value"},
        }
        mock_campaign_factory_context.generate_campaign = AsyncMock(
            return_value=CampaignGenerationResponse(**expected_response)
        )

        response = client.post("/api/v2/factory/create", json=request_data)

        assert response.status_code == 200
        assert response.json() == expected_response

    def test_generate_campaign_error(
        self, client: TestClient, mock_campaign_factory_context: Mock
    ):
        """Test campaign generation error handling."""
        request_data = {
            "campaign_type": CampaignType.TRADITIONAL,
            "complexity": CampaignComplexity.MODERATE,
            "length": CampaignLength.MEDIUM,
            "level_range": {"min": 1, "max": 10},
            "player_count": {"min": 3, "max": 5},
        }
        mock_campaign_factory_context.generate_campaign = AsyncMock(
            side_effect=Exception("Generation error")
        )

        response = client.post("/api/v2/factory/create", json=request_data)

        assert response.status_code == 500
        assert "Generation error" in response.json()["detail"]


class TestCampaignRefinement:
    """Test cases for campaign refinement endpoints."""

    def test_refine_campaign_success(
        self, client: TestClient, mock_campaign_factory_context: Mock
    ):
        """Test successful campaign refinement."""
        campaign_id = uuid4()
        request_data = {
            "campaign_id": str(campaign_id),
            "refinement_type": "theme",
            "adjustments": {"key": "value"},
            "preserve": ["element1", "element2"],
        }
        expected_response = {
            "campaign_id": str(campaign_id),
            "status": "success",
            "message": "Campaign refined successfully",
            "changes": [{"key": "value"}],
            "preserved": ["element1", "element2"],
        }
        mock_campaign_factory_context.refine_campaign = AsyncMock(
            return_value=CampaignRefinementResponse(**expected_response)
        )

        response = client.post(
            f"/api/v2/campaigns/{campaign_id}/refine",
            json=request_data,
        )

        assert response.status_code == 200
        assert response.json() == expected_response

    def test_refine_campaign_not_found(
        self, client: TestClient, mock_campaign_factory_context: Mock
    ):
        """Test campaign refinement with non-existent campaign."""
        campaign_id = uuid4()
        request_data = {
            "campaign_id": str(campaign_id),
            "refinement_type": "theme",
            "adjustments": {"key": "value"},
        }
        mock_campaign_factory_context.refine_campaign = AsyncMock(
            side_effect=ValueError("Campaign not found")
        )

        response = client.post(
            f"/api/v2/campaigns/{campaign_id}/refine",
            json=request_data,
        )

        assert response.status_code == 404
        assert "Campaign not found" in response.json()["detail"]


class TestNPCGeneration:
    """Test cases for NPC generation endpoints."""

    def test_generate_npc_success(
        self, client: TestClient, mock_campaign_factory_context: Mock
    ):
        """Test successful NPC generation."""
        campaign_id = uuid4()
        npc_id = uuid4()
        request_data = {
            "campaign_id": str(campaign_id),
            "npc_type": "major",
            "role": "villain",
            "relationships": [{"type": "rival", "target": "player"}],
        }
        expected_response = {
            "npc_id": str(npc_id),
            "status": "success",
            "message": "NPC generated successfully",
            "npc_data": {"key": "value"},
            "relationships": [{"type": "rival", "target": "player"}],
            "theme_elements": ["dark", "mysterious"],
        }
        mock_campaign_factory_context.generate_npc = AsyncMock(
            return_value=NPCGenerationResponse(**expected_response)
        )

        response = client.post(
            f"/api/v2/campaigns/{campaign_id}/npcs",
            json=request_data,
        )

        assert response.status_code == 200
        assert response.json() == expected_response


class TestLocationGeneration:
    """Test cases for location generation endpoints."""

    def test_generate_location_success(
        self, client: TestClient, mock_campaign_factory_context: Mock
    ):
        """Test successful location generation."""
        campaign_id = uuid4()
        location_id = uuid4()
        request_data = {
            "campaign_id": str(campaign_id),
            "location_type": "settlement",
            "importance": "major",
            "connections": [{"type": "road", "target": "capital"}],
        }
        expected_response = {
            "location_id": str(location_id),
            "status": "success",
            "message": "Location generated successfully",
            "location_data": {"key": "value"},
            "connections": [{"type": "road", "target": "capital"}],
            "theme_elements": ["dark", "fortified"],
        }
        mock_campaign_factory_context.generate_location = AsyncMock(
            return_value=LocationGenerationResponse(**expected_response)
        )

        response = client.post(
            f"/api/v2/campaigns/{campaign_id}/locations",
            json=request_data,
        )

        assert response.status_code == 200
        assert response.json() == expected_response


class TestMapGeneration:
    """Test cases for map generation endpoints."""

    def test_generate_map_success(
        self, client: TestClient, mock_campaign_factory_context: Mock
    ):
        """Test successful map generation."""
        campaign_id = uuid4()
        map_id = uuid4()
        request_data = {
            "campaign_id": str(campaign_id),
            "map_type": "settlement",
            "scale": "detailed",
        }
        expected_response = {
            "map_id": str(map_id),
            "status": "success",
            "message": "Map generated successfully",
            "map_data": {"key": "value"},
            "image_url": "https://example.com/map.jpg",
            "features": [{"type": "landmark", "name": "Tower"}],
            "theme_elements": ["dark", "mysterious"],
        }
        mock_campaign_factory_context.generate_map = AsyncMock(
            return_value=MapGenerationResponse(**expected_response)
        )

        response = client.post(
            f"/api/v2/campaigns/{campaign_id}/maps",
            json=request_data,
        )

        assert response.status_code == 200
        assert response.json() == expected_response
