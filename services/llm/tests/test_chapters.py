"""Tests for chapter organization."""
from datetime import datetime, timezone
import json
from typing import Dict
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from llm_service.api.chapters import router
from llm_service.core.exceptions import ChapterError, IntegrationError
from llm_service.models.chapter import (
    Chapter,
    ChapterOrganization,
    ChapterSection,
    StoryBeat,
    ChapterStatus,
    ChapterType,
)
from llm_service.models.theme import ThemeContext
from llm_service.services.campaign_integration import CampaignService
from llm_service.services.chapter_service import ChapterService


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
def chapter_id() -> UUID:
    """Create test chapter ID."""
    return uuid4()


@pytest.fixture
def section_id() -> UUID:
    """Create test section ID."""
    return uuid4()


@pytest.fixture
def beat_id() -> UUID:
    """Create test story beat ID."""
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
    mock.get_chapter_organization = AsyncMock()
    mock.get_campaign_id = AsyncMock()
    return mock


@pytest.fixture
def mock_generation_pipeline() -> MagicMock:
    """Create mock generation pipeline."""
    mock = MagicMock()
    mock.generate_content = AsyncMock()
    return mock


class TestChapterAPI:
    """Test chapter API endpoints."""

    async def test_create_chapter_success(
        self,
        client: TestClient,
        campaign_id: UUID,
        theme_context: ThemeContext,
        mock_campaign_service: MagicMock
    ):
        """Test successful chapter creation."""
        # Setup test data
        request_data = {
            "campaign_id": str(campaign_id),
            "title": "Test Chapter",
            "description": "Test chapter description",
            "chapter_type": ChapterType.MAIN_QUEST.value,
            "theme_context": theme_context.dict() if theme_context else None
        }

        # Setup mock responses
        organization = ChapterOrganization(
            campaign_id=campaign_id,
            chapters=[],
            theme_context=theme_context
        )
        mock_campaign_service.get_chapter_organization.return_value = organization

        # Make request
        with patch(
            "llm_service.api.chapters.get_campaign_service",
            return_value=mock_campaign_service
        ):
            response = client.post(
                "/api/v2/chapters/",
                json=request_data
            )

        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Chapter"
        assert data["description"] == "Test chapter description"
        assert data["chapter_type"] == ChapterType.MAIN_QUEST.value
        assert data["status"] == ChapterStatus.DRAFT.value
        assert UUID(data["chapter_id"]) is not None

        # Verify service calls
        mock_campaign_service.get_chapter_organization.assert_called_once_with(
            campaign_id
        )

    async def test_update_chapter_success(
        self,
        client: TestClient,
        campaign_id: UUID,
        chapter_id: UUID,
        theme_context: ThemeContext,
        mock_campaign_service: MagicMock
    ):
        """Test successful chapter update."""
        # Setup test data
        request_data = {
            "title": "Updated Chapter",
            "description": "Updated description",
            "chapter_type": ChapterType.SIDE_QUEST.value,
            "status": ChapterStatus.IN_PROGRESS.value
        }

        # Setup mock responses
        chapter = Chapter(
            chapter_id=chapter_id,
            campaign_id=campaign_id,
            title="Original Title",
            description="Original description",
            chapter_type=ChapterType.MAIN_QUEST,
            status=ChapterStatus.DRAFT,
            order=1,
            theme_context=theme_context,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        organization = ChapterOrganization(
            campaign_id=campaign_id,
            chapters=[chapter],
            theme_context=theme_context
        )
        mock_campaign_service.get_campaign_id.return_value = campaign_id
        mock_campaign_service.get_chapter_organization.return_value = organization

        # Make request
        with patch(
            "llm_service.api.chapters.get_campaign_service",
            return_value=mock_campaign_service
        ):
            response = client.put(
                f"/api/v2/chapters/{chapter_id}",
                json=request_data
            )

        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Chapter"
        assert data["description"] == "Updated description"
        assert data["chapter_type"] == ChapterType.SIDE_QUEST.value
        assert data["status"] == ChapterStatus.IN_PROGRESS.value

        # Verify service calls
        mock_campaign_service.get_campaign_id.assert_called_once_with(chapter_id)
        mock_campaign_service.get_chapter_organization.assert_called_once_with(
            campaign_id
        )

    async def test_delete_chapter_success(
        self,
        client: TestClient,
        campaign_id: UUID,
        chapter_id: UUID,
        theme_context: ThemeContext,
        mock_campaign_service: MagicMock
    ):
        """Test successful chapter deletion."""
        # Setup mock responses
        chapter = Chapter(
            chapter_id=chapter_id,
            campaign_id=campaign_id,
            title="Test Chapter",
            description="Test description",
            chapter_type=ChapterType.MAIN_QUEST,
            status=ChapterStatus.DRAFT,
            order=1,
            theme_context=theme_context,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        organization = ChapterOrganization(
            campaign_id=campaign_id,
            chapters=[chapter],
            theme_context=theme_context
        )
        mock_campaign_service.get_campaign_id.return_value = campaign_id
        mock_campaign_service.get_chapter_organization.return_value = organization

        # Make request
        with patch(
            "llm_service.api.chapters.get_campaign_service",
            return_value=mock_campaign_service
        ):
            response = client.delete(f"/api/v2/chapters/{chapter_id}")

        # Check response
        assert response.status_code == 200
        assert response.json() == {"status": "Chapter deleted"}

        # Verify service calls
        mock_campaign_service.get_campaign_id.assert_called_once_with(chapter_id)
        mock_campaign_service.get_chapter_organization.assert_called_once_with(
            campaign_id
        )

    async def test_add_section_success(
        self,
        client: TestClient,
        campaign_id: UUID,
        chapter_id: UUID,
        theme_context: ThemeContext,
        mock_campaign_service: MagicMock
    ):
        """Test successful section addition."""
        # Setup test data
        request_data = {
            "title": "Test Section",
            "description": "Test section description",
            "theme_context": theme_context.dict() if theme_context else None
        }

        # Setup mock responses
        chapter = Chapter(
            chapter_id=chapter_id,
            campaign_id=campaign_id,
            title="Test Chapter",
            description="Test description",
            chapter_type=ChapterType.MAIN_QUEST,
            status=ChapterStatus.DRAFT,
            order=1,
            theme_context=theme_context,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        organization = ChapterOrganization(
            campaign_id=campaign_id,
            chapters=[chapter],
            theme_context=theme_context
        )
        mock_campaign_service.get_campaign_id.return_value = campaign_id
        mock_campaign_service.get_chapter_organization.return_value = organization

        # Make request
        with patch(
            "llm_service.api.chapters.get_campaign_service",
            return_value=mock_campaign_service
        ):
            response = client.post(
                f"/api/v2/chapters/{chapter_id}/sections",
                json=request_data
            )

        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Section"
        assert data["description"] == "Test section description"
        assert UUID(data["section_id"]) is not None

        # Verify service calls
        mock_campaign_service.get_campaign_id.assert_called_once_with(chapter_id)
        mock_campaign_service.get_chapter_organization.assert_called_once_with(
            campaign_id
        )

    async def test_add_story_beat_success(
        self,
        client: TestClient,
        campaign_id: UUID,
        chapter_id: UUID,
        section_id: UUID,
        theme_context: ThemeContext,
        mock_campaign_service: MagicMock
    ):
        """Test successful story beat addition."""
        # Setup test data
        request_data = {
            "title": "Test Beat",
            "description": "Test beat description",
            "requirements": {"req1": "test requirement"},
            "outcomes": {"outcome1": "test outcome"}
        }

        # Setup mock responses
        section = ChapterSection(
            section_id=section_id,
            title="Test Section",
            description="Test description",
            order=1,
            theme_context=theme_context
        )
        chapter = Chapter(
            chapter_id=chapter_id,
            campaign_id=campaign_id,
            title="Test Chapter",
            description="Test description",
            chapter_type=ChapterType.MAIN_QUEST,
            status=ChapterStatus.DRAFT,
            order=1,
            sections=[section],
            theme_context=theme_context,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        organization = ChapterOrganization(
            campaign_id=campaign_id,
            chapters=[chapter],
            theme_context=theme_context
        )
        mock_campaign_service.get_campaign_id.return_value = campaign_id
        mock_campaign_service.get_chapter_organization.return_value = organization

        # Make request
        with patch(
            "llm_service.api.chapters.get_campaign_service",
            return_value=mock_campaign_service
        ):
            response = client.post(
                f"/api/v2/chapters/{chapter_id}/sections/{section_id}/beats",
                json=request_data
            )

        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Beat"
        assert data["description"] == "Test beat description"
        assert data["requirements"] == {"req1": "test requirement"}
        assert data["outcomes"] == {"outcome1": "test outcome"}
        assert UUID(data["beat_id"]) is not None

        # Verify service calls
        mock_campaign_service.get_campaign_id.assert_called_once_with(chapter_id)
        mock_campaign_service.get_chapter_organization.assert_called_once_with(
            campaign_id
        )

    async def test_reorder_chapters_success(
        self,
        client: TestClient,
        campaign_id: UUID,
        chapter_id: UUID,
        theme_context: ThemeContext,
        mock_campaign_service: MagicMock
    ):
        """Test successful chapter reordering."""
        # Setup test data
        chapter_orders = {str(chapter_id): 2}

        # Setup mock responses
        chapter = Chapter(
            chapter_id=chapter_id,
            campaign_id=campaign_id,
            title="Test Chapter",
            description="Test description",
            chapter_type=ChapterType.MAIN_QUEST,
            status=ChapterStatus.DRAFT,
            order=1,
            theme_context=theme_context,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        organization = ChapterOrganization(
            campaign_id=campaign_id,
            chapters=[chapter],
            theme_context=theme_context
        )
        mock_campaign_service.get_chapter_organization.return_value = organization

        # Make request
        with patch(
            "llm_service.api.chapters.get_campaign_service",
            return_value=mock_campaign_service
        ):
            response = client.post(
                "/api/v2/chapters/reorder",
                params={"campaign_id": str(campaign_id)},
                json=chapter_orders
            )

        # Check response
        assert response.status_code == 200
        assert response.json() == {"status": "Chapters reordered"}

        # Verify service calls
        mock_campaign_service.get_chapter_organization.assert_called_once_with(
            campaign_id
        )

    async def test_error_handling(
        self,
        client: TestClient,
        campaign_id: UUID,
        chapter_id: UUID,
        mock_campaign_service: MagicMock
    ):
        """Test error handling."""
        # Setup mock responses
        mock_campaign_service.get_chapter_organization.side_effect = ChapterError(
            "Chapter not found"
        )

        # Make request
        with patch(
            "llm_service.api.chapters.get_campaign_service",
            return_value=mock_campaign_service
        ):
            response = client.get(
                f"/api/v2/chapters/{chapter_id}",
                params={"campaign_id": str(campaign_id)}
            )

        # Check response
        assert response.status_code == 400
        assert response.json() == {"detail": "Chapter not found"}

        # Verify service calls
        mock_campaign_service.get_chapter_organization.assert_called_once_with(
            campaign_id
        )
