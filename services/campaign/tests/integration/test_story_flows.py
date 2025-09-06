"""Integration tests for story management flows."""

import asyncio
from datetime import datetime
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from campaign.models.api.story import (ChapterCreate, NPCRelationshipCreate,
                                   PlotCreate, StoryArcCreate)
from campaign.services.story import StoryService


class TestStoryFlows:
    """Test cases for story management flows."""

    @pytest.fixture
    async def story_service(self, db_session: AsyncSession) -> StoryService:
        """Create story service instance for testing."""
        return StoryService(db_session)

    @pytest.fixture
    async def campaign_id(self, client: AsyncClient) -> UUID:
        """Create a test campaign and return its ID."""
        response = await client.post("/api/v2/campaigns", json={
            "title": "Test Campaign",
            "description": "A test campaign for story flows",
            "theme_type": "fantasy",
            "campaign_type": "traditional",
            "target_level_range": {"min": 1, "max": 20},
        })
        assert response.status_code == 200
        return UUID(response.json()["id"])

    async def test_create_campaign_story_flow(
        self,
        client: AsyncClient,
        campaign_id: UUID,
        story_service: StoryService,
    ):
        """Test the full story creation flow for a campaign."""
        # Create initial plot structure
        main_plot_data = PlotCreate(
            title="Main Plot",
            description="The primary story arc",
            is_major=True,
            status="active",
            campaign_id=campaign_id,
        )
        main_plot_response = await client.post(
            f"/api/v2/campaigns/{campaign_id}/plots",
            json=main_plot_data.dict(),
        )
        assert main_plot_response.status_code == 200
        main_plot_id = UUID(main_plot_response.json()["id"])

        # Create subplot connected to main plot
        subplot_data = PlotCreate(
            title="Subplot",
            description="A connected story thread",
            is_major=False,
            status="active",
            campaign_id=campaign_id,
            parent_plot_id=main_plot_id,
        )
        subplot_response = await client.post(
            f"/api/v2/campaigns/{campaign_id}/plots",
            json=subplot_data.dict(),
        )
        assert subplot_response.status_code == 200
        subplot_id = UUID(subplot_response.json()["id"])

        # Create story arc connecting plots
        arc_data = StoryArcCreate(
            title="Character Development Arc",
            description="Personal growth journey",
            arc_type="character",
            status="active",
            campaign_id=campaign_id,
            plot_ids=[main_plot_id, subplot_id],
        )
        arc_response = await client.post(
            f"/api/v2/campaigns/{campaign_id}/arcs",
            json=arc_data.dict(),
        )
        assert arc_response.status_code == 200
        arc_id = UUID(arc_response.json()["id"])

        # Create NPC relationships
        npc_id = uuid4()  # Would come from character service in real system
        character_id = uuid4()  # Would come from character service in real system
        relationship_data = NPCRelationshipCreate(
            npc_id=npc_id,
            character_id=character_id,
            relationship_type="mentor",
            strength=9,
            description="A wise guide for the main character",
            status="active",
            campaign_id=campaign_id,
        )
        relationship_response = await client.post(
            f"/api/v2/campaigns/{campaign_id}/relationships",
            json=relationship_data.dict(),
        )
        assert relationship_response.status_code == 200
        relationship_id = UUID(relationship_response.json()["id"])

        # Create chapters
        intro_chapter_data = ChapterCreate(
            title="Introduction",
            description="The story begins",
            order=1,
            chapter_type="introduction",
            status="planned",
            campaign_id=campaign_id,
            plot_ids=[main_plot_id],
        )
        intro_chapter_response = await client.post(
            f"/api/v2/campaigns/{campaign_id}/chapters",
            json=intro_chapter_data.dict(),
        )
        assert intro_chapter_response.status_code == 200
        intro_chapter_id = UUID(intro_chapter_response.json()["id"])

        development_chapter_data = ChapterCreate(
            title="Development",
            description="The plot thickens",
            order=2,
            chapter_type="development",
            status="planned",
            campaign_id=campaign_id,
            prerequisite_chapter_ids=[intro_chapter_id],
            plot_ids=[main_plot_id, subplot_id],
        )
        development_chapter_response = await client.post(
            f"/api/v2/campaigns/{campaign_id}/chapters",
            json=development_chapter_data.dict(),
        )
        assert development_chapter_response.status_code == 200
        development_chapter_id = UUID(development_chapter_response.json()["id"])

        # Verify story structure
        plots_response = await client.get(f"/api/v2/campaigns/{campaign_id}/plots")
        assert plots_response.status_code == 200
        plots = plots_response.json()
        assert len(plots) == 2
        assert any(plot["id"] == str(main_plot_id) for plot in plots)
        assert any(plot["id"] == str(subplot_id) for plot in plots)

        arcs_response = await client.get(f"/api/v2/campaigns/{campaign_id}/arcs")
        assert arcs_response.status_code == 200
        arcs = arcs_response.json()
        assert len(arcs) == 1
        assert arcs[0]["id"] == str(arc_id)

        relationships_response = await client.get(
            f"/api/v2/campaigns/{campaign_id}/relationships"
        )
        assert relationships_response.status_code == 200
        relationships = relationships_response.json()
        assert len(relationships) == 1
        assert relationships[0]["id"] == str(relationship_id)

        chapters_response = await client.get(f"/api/v2/campaigns/{campaign_id}/chapters")
        assert chapters_response.status_code == 200
        chapters = chapters_response.json()
        assert len(chapters) == 2
        assert any(chapter["id"] == str(intro_chapter_id) for chapter in chapters)
        assert any(chapter["id"] == str(development_chapter_id) for chapter in chapters)

    async def test_plot_evolution_flow(
        self,
        client: AsyncClient,
        campaign_id: UUID,
        story_service: StoryService,
    ):
        """Test evolving a plot through different states."""
        # Create initial plot
        plot_data = PlotCreate(
            title="Evolving Plot",
            description="A plot that will change",
            is_major=True,
            status="active",
            campaign_id=campaign_id,
        )
        plot_response = await client.post(
            f"/api/v2/campaigns/{campaign_id}/plots",
            json=plot_data.dict(),
        )
        assert plot_response.status_code == 200
        plot_id = UUID(plot_response.json()["id"])

        # Update plot as it develops
        updates = [
            {"status": "in_progress", "description": "The plot deepens"},
            {"status": "climax", "description": "Reaching the critical moment"},
            {"status": "resolved", "description": "The conclusion is reached"},
        ]

        for update in updates:
            response = await client.put(
                f"/api/v2/campaigns/{campaign_id}/plots/{plot_id}",
                json={"title": "Evolving Plot", **update},
            )
            assert response.status_code == 200
            assert response.json()["status"] == update["status"]
            assert response.json()["description"] == update["description"]

            # Verify the update is persisted
            get_response = await client.get(
                f"/api/v2/campaigns/{campaign_id}/plots/{plot_id}"
            )
            assert get_response.status_code == 200
            assert get_response.json()["status"] == update["status"]
            assert get_response.json()["description"] == update["description"]

    async def test_npc_relationship_development_flow(
        self,
        client: AsyncClient,
        campaign_id: UUID,
        story_service: StoryService,
    ):
        """Test developing NPC relationships over time."""
        npc_id = uuid4()
        character_id = uuid4()

        # Create initial relationship
        relationship_data = NPCRelationshipCreate(
            npc_id=npc_id,
            character_id=character_id,
            relationship_type="neutral",
            strength=5,
            description="Initial meeting",
            status="active",
            campaign_id=campaign_id,
        )
        relationship_response = await client.post(
            f"/api/v2/campaigns/{campaign_id}/relationships",
            json=relationship_data.dict(),
        )
        assert relationship_response.status_code == 200
        relationship_id = UUID(relationship_response.json()["id"])

        # Evolve relationship through different stages
        stages = [
            {
                "relationship_type": "friendly",
                "strength": 6,
                "description": "Growing trust",
                "status": "active",
            },
            {
                "relationship_type": "ally",
                "strength": 8,
                "description": "Strong alliance formed",
                "status": "active",
            },
            {
                "relationship_type": "rival",
                "strength": 4,
                "description": "Trust broken",
                "status": "strained",
            },
            {
                "relationship_type": "enemy",
                "strength": 2,
                "description": "Complete breakdown",
                "status": "broken",
            },
        ]

        for stage in stages:
            response = await client.put(
                f"/api/v2/campaigns/{campaign_id}/relationships/{relationship_id}",
                json={"npc_id": str(npc_id), "character_id": str(character_id), **stage},
            )
            assert response.status_code == 200
            assert response.json()["relationship_type"] == stage["relationship_type"]
            assert response.json()["strength"] == stage["strength"]
            assert response.json()["status"] == stage["status"]

            # Verify the update is persisted
            get_response = await client.get(
                f"/api/v2/campaigns/{campaign_id}/relationships/{relationship_id}"
            )
            assert get_response.status_code == 200
            assert get_response.json()["relationship_type"] == stage["relationship_type"]
            assert get_response.json()["strength"] == stage["strength"]
            assert get_response.json()["status"] == stage["status"]
