"""Integration tests for campaign factory flows."""

import pytest
from uuid import UUID

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from campaign.models.api.factory import (CampaignType, CampaignComplexity,
                                    CampaignLength)
from campaign.services.factory import CampaignFactory


@pytest.fixture
async def factory_service(
    db_session: AsyncSession,
    llm_client,
    theme_service,
    world_effect_service,
) -> CampaignFactory:
    """Create factory service instance for testing."""
    return CampaignFactory(
        db=db_session,
        llm_service=llm_client,
        theme_service=theme_service,
        world_effect_service=world_effect_service,
    )


@pytest.mark.asyncio
class TestCampaignFactoryFlows:
    """Test cases for campaign factory flows."""

    async def test_campaign_generation_flow(
        self,
        client: AsyncClient,
        factory_service: CampaignFactory,
    ):
        """Test end-to-end campaign generation flow."""
        # Generate campaign
        campaign_data = {
            "title": "Test Campaign",
            "description": "A test campaign for factory flows",
            "campaign_type": CampaignType.TRADITIONAL,
            "complexity": CampaignComplexity.MODERATE,
            "length": CampaignLength.MEDIUM,
            "level_range": {"min": 1, "max": 10},
            "player_count": {"min": 3, "max": 5},
        }
        response = await client.post(
            "/api/v2/factory/create",
            json=campaign_data,
        )
        assert response.status_code == 200
        result = response.json()
        campaign_id = UUID(result["campaign_id"])

        # Refine campaign theme
        refinement_data = {
            "campaign_id": str(campaign_id),
            "refinement_type": "theme",
            "adjustments": {
                "tone": "darker",
                "elements": ["corruption", "mystery"],
            },
            "preserve": ["core_plot", "key_npcs"],
        }
        response = await client.post(
            f"/api/v2/campaigns/{campaign_id}/refine",
            json=refinement_data,
        )
        assert response.status_code == 200
        assert len(response.json()["changes"]) > 0

        # Generate NPCs
        npc_data = {
            "campaign_id": str(campaign_id),
            "npc_type": "major",
            "role": "villain",
            "relationships": [
                {"type": "rival", "target": "party_leader"},
                {"type": "mentor", "target": "minion"},
            ],
        }
        response = await client.post(
            f"/api/v2/campaigns/{campaign_id}/npcs",
            json=npc_data,
        )
        assert response.status_code == 200
        npc_result = response.json()
        assert len(npc_result["relationships"]) == 2

        # Generate locations
        location_data = {
            "campaign_id": str(campaign_id),
            "location_type": "settlement",
            "importance": "major",
            "connections": [
                {"type": "road", "target": "capital_city"},
                {"type": "river", "target": "port_town"},
            ],
        }
        response = await client.post(
            f"/api/v2/campaigns/{campaign_id}/locations",
            json=location_data,
        )
        assert response.status_code == 200
        location_result = response.json()
        location_id = UUID(location_result["location_id"])

        # Generate map for location
        map_data = {
            "campaign_id": str(campaign_id),
            "location_id": str(location_id),
            "map_type": "settlement",
            "scale": "detailed",
            "parameters": {
                "include_labels": True,
                "style": "parchment",
            },
        }
        response = await client.post(
            f"/api/v2/campaigns/{campaign_id}/maps",
            json=map_data,
        )
        assert response.status_code == 200
        map_result = response.json()
        assert map_result["image_url"]
        assert len(map_result["features"]) > 0

    async def test_themed_content_generation_flow(
        self,
        client: AsyncClient,
        factory_service: CampaignFactory,
    ):
        """Test generating themed content."""
        # Create campaign with theme
        campaign_data = {
            "title": "Dark Campaign",
            "description": "A dark fantasy campaign",
            "campaign_type": CampaignType.TRADITIONAL,
            "complexity": CampaignComplexity.COMPLEX,
            "length": CampaignLength.LONG,
            "level_range": {"min": 5, "max": 15},
            "player_count": {"min": 4, "max": 6},
            "theme_ids": [],  # Would include theme IDs
        }
        response = await client.post(
            "/api/v2/factory/create",
            json=campaign_data,
        )
        assert response.status_code == 200
        result = response.json()
        campaign_id = UUID(result["campaign_id"])
        theme_elements = result["details"]["applied_themes"]
        assert len(theme_elements) > 0

        # Generate themed NPCs
        npc_requests = [
            {
                "campaign_id": str(campaign_id),
                "npc_type": npc_type,
                "role": role,
            }
            for npc_type, role in [
                ("major", "quest_giver"),
                ("major", "villain"),
                ("minor", "merchant"),
                ("minor", "guard"),
            ]
        ]
        npcs = []
        for npc_data in npc_requests:
            response = await client.post(
                f"/api/v2/campaigns/{campaign_id}/npcs",
                json=npc_data,
            )
            assert response.status_code == 200
            npc_result = response.json()
            assert npc_result["theme_elements"]
            npcs.append(npc_result)

        # Generate themed locations
        location_requests = [
            {
                "campaign_id": str(campaign_id),
                "location_type": loc_type,
                "importance": importance,
            }
            for loc_type, importance in [
                ("settlement", "major"),
                ("dungeon", "major"),
                ("wilderness", "minor"),
                ("settlement", "minor"),
            ]
        ]
        locations = []
        for location_data in location_requests:
            response = await client.post(
                f"/api/v2/campaigns/{campaign_id}/locations",
                json=location_data,
            )
            assert response.status_code == 200
            location_result = response.json()
            assert location_result["theme_elements"]
            locations.append(location_result)

        # Generate maps for major locations
        for location in locations:
            if location.get("importance") == "major":
                map_data = {
                    "campaign_id": str(campaign_id),
                    "location_id": location["location_id"],
                    "map_type": location["location_type"],
                    "scale": "detailed",
                }
                response = await client.post(
                    f"/api/v2/campaigns/{campaign_id}/maps",
                    json=map_data,
                )
                assert response.status_code == 200
                map_result = response.json()
                assert map_result["theme_elements"]

        # Verify theme consistency
        all_theme_elements = (
            [elem for npc in npcs for elem in npc["theme_elements"]]
            + [elem for loc in locations for elem in loc["theme_elements"]]
        )
        assert len(set(all_theme_elements)) > 0  # Has theme elements
        assert len(all_theme_elements) > len(set(all_theme_elements))  # Has repetition

    async def test_campaign_refinement_flow(
        self,
        client: AsyncClient,
        factory_service: CampaignFactory,
    ):
        """Test iterative campaign refinement."""
        # Create initial campaign
        campaign_data = {
            "title": "Evolving Campaign",
            "description": "A campaign that will be refined",
            "campaign_type": CampaignType.TRADITIONAL,
            "complexity": CampaignComplexity.MODERATE,
            "length": CampaignLength.MEDIUM,
            "level_range": {"min": 1, "max": 10},
            "player_count": {"min": 4, "max": 4},
        }
        response = await client.post(
            "/api/v2/factory/create",
            json=campaign_data,
        )
        assert response.status_code == 200
        result = response.json()
        campaign_id = UUID(result["campaign_id"])

        # Series of refinements
        refinements = [
            {
                "type": "theme",
                "adjustments": {
                    "tone": "darker",
                    "elements": ["corruption"],
                },
                "preserve": ["core_plot"],
            },
            {
                "type": "content",
                "adjustments": {
                    "add_subplots": ["conspiracy", "betrayal"],
                    "expand_locations": ["capital_city"],
                },
                "preserve": ["character_arcs"],
            },
            {
                "type": "structure",
                "adjustments": {
                    "merge_chapters": [2, 3],
                    "add_chapter": {
                        "position": 4,
                        "focus": "revelation",
                    },
                },
                "preserve": ["pacing", "key_reveals"],
            },
        ]

        for refinement in refinements:
            request_data = {
                "campaign_id": str(campaign_id),
                "refinement_type": refinement["type"],
                "adjustments": refinement["adjustments"],
                "preserve": refinement["preserve"],
            }
            response = await client.post(
                f"/api/v2/campaigns/{campaign_id}/refine",
                json=request_data,
            )
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert len(result["changes"]) > 0
            assert all(
                elem in result["preserved"]
                for elem in refinement["preserve"]
            )
