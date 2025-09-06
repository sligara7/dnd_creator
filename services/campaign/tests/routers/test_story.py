"""Unit tests for story management endpoints."""

from datetime import datetime
from typing import List
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from campaign.models.api.story import (ChapterCreate, ChapterResponse, ChapterUpdate,
                                   NPCRelationshipCreate, NPCRelationshipResponse,
                                   NPCRelationshipUpdate, PlotCreate,
                                   PlotResponse, PlotUpdate, StoryArcCreate,
                                   StoryArcResponse, StoryArcUpdate)
from campaign.routers.story import router
from campaign.services.story import StoryService


@pytest.fixture
def app() -> FastAPI:
    """Create test FastAPI app with story router."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_story_service() -> Mock:
    """Create mock story service."""
    return Mock(spec=StoryService)


@pytest.fixture
def mock_story_service_context(app: FastAPI, mock_story_service: Mock):
    """Override story service dependency for testing."""
    app.dependency_overrides[get_story_service] = lambda: mock_story_service
    yield mock_story_service
    app.dependency_overrides = {}


class TestPlotEndpoints:
    """Test cases for plot endpoints."""

    def test_create_plot_success(
        self, client: TestClient, mock_story_service_context: Mock
    ):
        """Test successful plot creation."""
        campaign_id = uuid4()
        plot_data = {
            "title": "Test Plot",
            "description": "A test plot",
            "is_major": True,
            "status": "active",
            "campaign_id": str(campaign_id),
        }
        expected_response = {
            **plot_data,
            "id": str(uuid4()),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "parent_plot_id": None,
            "chapter_id": None,
        }
        mock_story_service_context.create_plot = AsyncMock(
            return_value=PlotResponse(**expected_response)
        )

        response = client.post(f"/api/v2/campaigns/{campaign_id}/plots", json=plot_data)

        assert response.status_code == 200
        assert response.json() == expected_response

    def test_list_plots_success(
        self, client: TestClient, mock_story_service_context: Mock
    ):
        """Test successful plot listing."""
        campaign_id = uuid4()
        plots = [
            {
                "id": str(uuid4()),
                "title": f"Plot {i}",
                "description": f"Description {i}",
                "is_major": bool(i % 2),
                "status": "active",
                "campaign_id": str(campaign_id),
                "parent_plot_id": None,
                "chapter_id": None,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
            for i in range(3)
        ]
        mock_story_service_context.list_plots = AsyncMock(
            return_value=[PlotResponse(**plot) for plot in plots]
        )

        response = client.get(f"/api/v2/campaigns/{campaign_id}/plots")

        assert response.status_code == 200
        assert response.json() == plots


class TestStoryArcEndpoints:
    """Test cases for story arc endpoints."""

    def test_create_story_arc_success(
        self, client: TestClient, mock_story_service_context: Mock
    ):
        """Test successful story arc creation."""
        campaign_id = uuid4()
        arc_data = {
            "title": "Test Arc",
            "description": "A test arc",
            "arc_type": "character",
            "status": "active",
            "campaign_id": str(campaign_id),
            "plot_ids": [str(uuid4()) for _ in range(2)],
        }
        expected_response = {
            **arc_data,
            "id": str(uuid4()),
            "plots": [],  # Would contain full plot objects in real response
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        mock_story_service_context.create_story_arc = AsyncMock(
            return_value=StoryArcResponse(**expected_response)
        )

        response = client.post(f"/api/v2/campaigns/{campaign_id}/arcs", json=arc_data)

        assert response.status_code == 200
        assert response.json() == expected_response


class TestNPCRelationshipEndpoints:
    """Test cases for NPC relationship endpoints."""

    def test_create_npc_relationship_success(
        self, client: TestClient, mock_story_service_context: Mock
    ):
        """Test successful NPC relationship creation."""
        campaign_id = uuid4()
        relationship_data = {
            "npc_id": str(uuid4()),
            "character_id": str(uuid4()),
            "relationship_type": "ally",
            "strength": 8,
            "description": "A strong alliance",
            "status": "active",
            "campaign_id": str(campaign_id),
        }
        expected_response = {
            **relationship_data,
            "id": str(uuid4()),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        mock_story_service_context.create_npc_relationship = AsyncMock(
            return_value=NPCRelationshipResponse(**expected_response)
        )

        response = client.post(
            f"/api/v2/campaigns/{campaign_id}/relationships", json=relationship_data
        )

        assert response.status_code == 200
        assert response.json() == expected_response


class TestChapterEndpoints:
    """Test cases for chapter endpoints."""

    def test_create_chapter_success(
        self, client: TestClient, mock_story_service_context: Mock
    ):
        """Test successful chapter creation."""
        campaign_id = uuid4()
        chapter_data = {
            "title": "Test Chapter",
            "description": "A test chapter",
            "order": 1,
            "chapter_type": "introduction",
            "status": "planned",
            "campaign_id": str(campaign_id),
            "prerequisite_chapter_ids": [str(uuid4())],
            "plot_ids": [str(uuid4())],
        }
        expected_response = {
            **chapter_data,
            "id": str(uuid4()),
            "prerequisite_chapters": [],  # Would contain full chapter objects
            "plots": [],  # Would contain full plot objects
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        mock_story_service_context.create_chapter = AsyncMock(
            return_value=ChapterResponse(**expected_response)
        )

        response = client.post(f"/api/v2/campaigns/{campaign_id}/chapters", json=chapter_data)

        assert response.status_code == 200
        assert response.json() == expected_response

    def test_list_chapters_success(
        self, client: TestClient, mock_story_service_context: Mock
    ):
        """Test successful chapter listing."""
        campaign_id = uuid4()
        chapters = [
            {
                "id": str(uuid4()),
                "title": f"Chapter {i}",
                "description": f"Description {i}",
                "order": i,
                "chapter_type": "introduction",
                "status": "planned",
                "campaign_id": str(campaign_id),
                "prerequisite_chapters": [],
                "plots": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
            for i in range(3)
        ]
        mock_story_service_context.list_chapters = AsyncMock(
            return_value=[ChapterResponse(**chapter) for chapter in chapters]
        )

        response = client.get(f"/api/v2/campaigns/{campaign_id}/chapters")

        assert response.status_code == 200
        assert response.json() == chapters
