"""Tests for Campaign service integration."""
from datetime import datetime
import json
from typing import Dict
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from llm_service.api.campaign_integration import router
from llm_service.core.exceptions import EventHandlingError, IntegrationError
from llm_service.models.theme import ContentType, GenerationResult, ThemeContext
from llm_service.services.campaign_integration import (
    CampaignContent,
    CampaignContentType,
    CampaignEvent,
    CampaignEventType,
    CampaignService
)
from llm_service.services.campaign_events import CampaignEventHandler
from llm_service.services.generation import GenerationPipeline


@pytest.fixture
def app() -> FastAPI:
    """Create test application."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def campaign_id() -> UUID:
    """Create test campaign ID."""
    return uuid4()


@pytest.fixture
def theme_context() -> ThemeContext:
    """Create test theme context."""
    return ThemeContext(
        theme_id=uuid4(),
        name="Test Theme",
        type="traditional",
        genre="fantasy",
        tone="serious",
        elements={
            "key_words": ["heroic", "mystical"],
            "style_guide": {"narrative": "descriptive"},
            "character_traits": ["brave", "wise"],
            "world_elements": ["magic", "dragons"]
        }
    )


@pytest.fixture
def mock_campaign_service() -> MagicMock:
    """Create mock campaign service."""
    mock = MagicMock(spec=CampaignService)
    mock.get_campaign_content = AsyncMock()
    mock.update_campaign_content = AsyncMock()
    mock.validate_theme = AsyncMock()
    mock.create_plot_element = AsyncMock()
    mock.create_location = AsyncMock()
    mock.create_npc = AsyncMock()
    mock.notify_content_generation = AsyncMock()
    return mock


@pytest.fixture
def mock_generation_pipeline() -> MagicMock:
    """Create mock generation pipeline."""
    mock = MagicMock(spec=GenerationPipeline)
    mock.generate_content = AsyncMock()
    return mock


class TestCampaignIntegration:
    """Test campaign integration endpoints."""

    async def test_generate_content_success(
        self,
        client: TestClient,
        campaign_id: UUID,
        theme_context: ThemeContext,
        mock_campaign_service: MagicMock,
        mock_generation_pipeline: MagicMock
    ):
        """Test successful content generation."""
        # Setup mocks
        content_type = CampaignContentType.PLOT
        campaign_content = CampaignContent(
            campaign_id=campaign_id,
            content_type=content_type,
            theme_context=theme_context,
            existing_content={"plot": "Old plot"}
        )
        generation_result = GenerationResult(
            content="New content",
            metadata={
                "prompt_tokens": 100,
                "completion_tokens": 200,
                "total_tokens": 300,
                "generation_time_ms": 1000,
                "model_name": "gpt-5-nano",
                "cached": False
            },
            theme_context=theme_context,
            content_type=content_type
        )

        mock_campaign_service.get_campaign_content.return_value = campaign_content
        mock_generation_pipeline.generate_content.return_value = generation_result

        with patch(
            "llm_service.api.campaign_integration.get_campaign_service",
            return_value=mock_campaign_service
        ), patch(
            "llm_service.api.campaign_integration.get_generation_pipeline",
            return_value=mock_generation_pipeline
        ):
            response = client.post(
                f"/api/v2/campaign/{campaign_id}/generate/{content_type.value}",
                json=theme_context.dict()
            )

        assert response.status_code == 200
        assert response.json() == {"content": "New content"}

        # Verify service calls
        mock_campaign_service.get_campaign_content.assert_called_once_with(
            campaign_id,
            content_type
        )
        mock_generation_pipeline.generate_content.assert_called_once_with(
            content_type=content_type,
            theme_context=theme_context,
            existing_content=campaign_content.existing_content
        )
        mock_campaign_service.update_campaign_content.assert_called_once_with(
            campaign_id=campaign_id,
            content_type=content_type,
            content="New content",
            metadata={
                "model": "gpt-5-nano",
                "tokens": 300,
                "theme": theme_context.name
            }
        )

    async def test_validate_theme_success(
        self,
        client: TestClient,
        campaign_id: UUID,
        theme_context: ThemeContext,
        mock_campaign_service: MagicMock
    ):
        """Test successful theme validation."""
        mock_campaign_service.validate_theme.return_value = True

        with patch(
            "llm_service.api.campaign_integration.get_campaign_service",
            return_value=mock_campaign_service
        ):
            response = client.post(
                f"/api/v2/campaign/{campaign_id}/theme/validate",
                json=theme_context.dict()
            )

        assert response.status_code == 200
        assert response.json() == {"is_valid": True}

        mock_campaign_service.validate_theme.assert_called_once_with(
            campaign_id,
            theme_context
        )

    async def test_create_plot_element_success(
        self,
        client: TestClient,
        campaign_id: UUID,
        theme_context: ThemeContext,
        mock_campaign_service: MagicMock
    ):
        """Test successful plot element creation."""
        mock_response = {
            "id": str(uuid4()),
            "title": "Test Plot",
            "description": "Test description",
            "element_type": "quest"
        }
        mock_campaign_service.create_plot_element.return_value = mock_response

        with patch(
            "llm_service.api.campaign_integration.get_campaign_service",
            return_value=mock_campaign_service
        ):
            response = client.post(
                f"/api/v2/campaign/{campaign_id}/plot",
                json={
                    "title": "Test Plot",
                    "description": "Test description",
                    "element_type": "quest",
                    "theme_context": theme_context.dict() if theme_context else None
                }
            )

        assert response.status_code == 200
        assert response.json() == mock_response

        mock_campaign_service.create_plot_element.assert_called_once_with(
            campaign_id=campaign_id,
            title="Test Plot",
            description="Test description",
            element_type="quest",
            theme_context=theme_context
        )

    async def test_create_location_success(
        self,
        client: TestClient,
        campaign_id: UUID,
        theme_context: ThemeContext,
        mock_campaign_service: MagicMock
    ):
        """Test successful location creation."""
        mock_response = {
            "id": str(uuid4()),
            "name": "Test Location",
            "description": "Test description",
            "location_type": "dungeon"
        }
        mock_campaign_service.create_location.return_value = mock_response

        with patch(
            "llm_service.api.campaign_integration.get_campaign_service",
            return_value=mock_campaign_service
        ):
            response = client.post(
                f"/api/v2/campaign/{campaign_id}/location",
                json={
                    "name": "Test Location",
                    "description": "Test description",
                    "location_type": "dungeon",
                    "theme_context": theme_context.dict() if theme_context else None
                }
            )

        assert response.status_code == 200
        assert response.json() == mock_response

        mock_campaign_service.create_location.assert_called_once_with(
            campaign_id=campaign_id,
            name="Test Location",
            description="Test description",
            location_type="dungeon",
            theme_context=theme_context
        )

    async def test_create_npc_success(
        self,
        client: TestClient,
        campaign_id: UUID,
        theme_context: ThemeContext,
        mock_campaign_service: MagicMock
    ):
        """Test successful NPC creation."""
        mock_response = {
            "id": str(uuid4()),
            "name": "Test NPC",
            "description": "Test description",
            "role": "merchant"
        }
        mock_campaign_service.create_npc.return_value = mock_response

        with patch(
            "llm_service.api.campaign_integration.get_campaign_service",
            return_value=mock_campaign_service
        ):
            response = client.post(
                f"/api/v2/campaign/{campaign_id}/npc",
                json={
                    "name": "Test NPC",
                    "description": "Test description",
                    "role": "merchant",
                    "theme_context": theme_context.dict() if theme_context else None
                }
            )

        assert response.status_code == 200
        assert response.json() == mock_response

        mock_campaign_service.create_npc.assert_called_once_with(
            campaign_id=campaign_id,
            name="Test NPC",
            description="Test description",
            role="merchant",
            theme_context=theme_context
        )

    async def test_handle_events_success(
        self,
        client: TestClient,
        campaign_id: UUID,
        theme_context: ThemeContext,
        mock_campaign_service: MagicMock,
        mock_generation_pipeline: MagicMock
    ):
        """Test successful event handling."""
        event = CampaignEvent(
            event_type=CampaignEventType.THEME_TRANSITIONED,
            campaign_id=campaign_id,
            data={},
            theme_context=theme_context
        )

        with patch(
            "llm_service.api.campaign_integration.get_campaign_service",
            return_value=mock_campaign_service
        ), patch(
            "llm_service.api.campaign_integration.get_generation_pipeline",
            return_value=mock_generation_pipeline
        ):
            response = client.post(
                f"/api/v2/campaign/{campaign_id}/events",
                json=event.dict()
            )

        assert response.status_code == 200
        assert response.json() == {"status": "Event handled"}

    async def test_error_handling(
        self,
        client: TestClient,
        campaign_id: UUID,
        theme_context: ThemeContext,
        mock_campaign_service: MagicMock
    ):
        """Test error handling."""
        mock_campaign_service.validate_theme.side_effect = IntegrationError(
            "Service unavailable"
        )

        with patch(
            "llm_service.api.campaign_integration.get_campaign_service",
            return_value=mock_campaign_service
        ):
            response = client.post(
                f"/api/v2/campaign/{campaign_id}/theme/validate",
                json=theme_context.dict()
            )

        assert response.status_code == 400
        assert response.json() == {"detail": "Service unavailable"}
