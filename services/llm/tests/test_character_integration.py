"""Tests for Character service integration."""
from datetime import datetime
import json
from typing import Dict
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from llm_service.api.character import router
from llm_service.core.exceptions import EventHandlingError, IntegrationError
from llm_service.models.theme import ContentType, GenerationResult, ThemeContext
from llm_service.services.character import (
    CharacterContent,
    CharacterEventType,
    CharacterService
)
from llm_service.services.events import EventHandler
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
def character_id() -> UUID:
    """Create test character ID."""
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
def mock_character_service() -> MagicMock:
    """Create mock character service."""
    mock = MagicMock(spec=CharacterService)
    mock.get_character_content = AsyncMock()
    mock.update_character_content = AsyncMock()
    mock.validate_theme = AsyncMock()
    mock.notify_content_generation = AsyncMock()
    return mock


@pytest.fixture
def mock_generation_pipeline() -> MagicMock:
    """Create mock generation pipeline."""
    mock = MagicMock(spec=GenerationPipeline)
    mock.generate_content = AsyncMock()
    return mock


class TestCharacterIntegration:
    """Test character integration endpoints."""

    async def test_generate_content_success(
        self,
        client: TestClient,
        character_id: UUID,
        theme_context: ThemeContext,
        mock_character_service: MagicMock,
        mock_generation_pipeline: MagicMock
    ):
        """Test successful content generation."""
        # Setup mocks
        content_type = ContentType.CHARACTER_BACKSTORY
        character_content = CharacterContent(
            character_id=character_id,
            content_type=content_type,
            theme_context=theme_context,
            existing_content={"backstory": "Old content"}
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

        mock_character_service.get_character_content.return_value = character_content
        mock_generation_pipeline.generate_content.return_value = generation_result

        with patch(
            "llm_service.api.character.get_character_service",
            return_value=mock_character_service
        ), patch(
            "llm_service.api.character.get_generation_pipeline",
            return_value=mock_generation_pipeline
        ):
            response = client.post(
                f"/api/v2/character/{character_id}/generate/{content_type.value}",
                json=theme_context.dict()
            )

        assert response.status_code == 200
        assert response.json() == {"content": "New content"}

        # Verify service calls
        mock_character_service.get_character_content.assert_called_once_with(
            character_id,
            content_type
        )
        mock_generation_pipeline.generate_content.assert_called_once_with(
            content_type=content_type,
            theme_context=theme_context,
            existing_content=character_content.existing_content
        )
        mock_character_service.update_character_content.assert_called_once_with(
            character_id=character_id,
            content_type=content_type,
            content="New content"
        )

    async def test_validate_theme_success(
        self,
        client: TestClient,
        character_id: UUID,
        theme_context: ThemeContext,
        mock_character_service: MagicMock
    ):
        """Test successful theme validation."""
        mock_character_service.validate_theme.return_value = True

        with patch(
            "llm_service.api.character.get_character_service",
            return_value=mock_character_service
        ):
            response = client.post(
                f"/api/v2/character/{character_id}/theme/validate",
                json=theme_context.dict()
            )

        assert response.status_code == 200
        assert response.json() == {"is_valid": True}

        mock_character_service.validate_theme.assert_called_once_with(
            character_id,
            theme_context
        )

    async def test_handle_theme_transition_success(
        self,
        client: TestClient,
        character_id: UUID,
        theme_context: ThemeContext,
        mock_character_service: MagicMock,
        mock_generation_pipeline: MagicMock
    ):
        """Test successful theme transition."""
        mock_character_service.validate_theme.return_value = True

        with patch(
            "llm_service.api.character.get_character_service",
            return_value=mock_character_service
        ), patch(
            "llm_service.api.character.get_generation_pipeline",
            return_value=mock_generation_pipeline
        ):
            response = client.post(
                f"/api/v2/character/{character_id}/theme/transition",
                json=theme_context.dict()
            )

        assert response.status_code == 200
        assert response.json() == {"status": "Theme transition queued"}

    async def test_handle_events_success(
        self,
        client: TestClient,
        character_id: UUID,
        theme_context: ThemeContext,
        mock_character_service: MagicMock,
        mock_generation_pipeline: MagicMock
    ):
        """Test successful event handling."""
        event_data = {
            "content_type": ContentType.CHARACTER_BACKSTORY.value,
            "content": "Old content"
        }

        with patch(
            "llm_service.api.character.get_character_service",
            return_value=mock_character_service
        ), patch(
            "llm_service.api.character.get_generation_pipeline",
            return_value=mock_generation_pipeline
        ):
            response = client.post(
                f"/api/v2/character/{character_id}/events/handle",
                json={
                    "event_type": CharacterEventType.NARRATIVE_ADDED.value,
                    "data": event_data,
                    "theme_context": theme_context.dict() if theme_context else None
                }
            )

        assert response.status_code == 200
        assert response.json() == {"status": "Event handled"}

    async def test_error_handling(
        self,
        client: TestClient,
        character_id: UUID,
        theme_context: ThemeContext,
        mock_character_service: MagicMock
    ):
        """Test error handling."""
        mock_character_service.validate_theme.side_effect = IntegrationError(
            "Service unavailable"
        )

        with patch(
            "llm_service.api.character.get_character_service",
            return_value=mock_character_service
        ):
            response = client.post(
                f"/api/v2/character/{character_id}/theme/validate",
                json=theme_context.dict()
            )

        assert response.status_code == 400
        assert response.json() == {"detail": "Service unavailable"}
