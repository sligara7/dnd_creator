"""
Tests for map generation functionality.
"""

import pytest
from uuid import UUID, uuid4
from image_service.models.map_request import (
    GridPoint, GridSize, TerrainFeature, SpellEffect,
    CharacterPosition, TacticalMapRequest, CampaignMapRequest
)
from image_service.core.exceptions import ImageGenerationError

@pytest.fixture
def mock_map_generator(mock_getimg_api):
    """Configure mock response for map generation."""
    async def mock_generate(*args, **kwargs):
        return {
            "image_data": b"fake_map_image_bytes",
            "metadata": {
                "width": 1024,
                "height": 1024,
                "format": "PNG",
                "grid": {
                    "cells_x": 20,
                    "cells_y": 20,
                    "scale": 5
                }
            }
        }
    mock_getimg_api.generate_image = mock_generate
    return mock_getimg_api

@pytest.mark.asyncio
class TestTacticalMapGeneration:
    async def test_basic_tactical_map(self, image_service, mock_map_generator):
        """Test basic tactical map generation."""
        request = TacticalMapRequest(
            theme="fantasy",
            grid_size=GridSize(width=20, height=20, scale=5),
            lighting_conditions="bright"
        )
        
        result = await image_service.generate_tactical_map(request)
        
        assert result.width == 1024
        assert result.height == 1024
        assert result.format == "PNG"
        assert result.grid_metadata["cells_x"] == 20
        assert result.grid_metadata["cells_y"] == 20
        assert result.grid_metadata["scale"] == 5

    async def test_tactical_map_with_terrain(self, image_service, mock_map_generator):
        """Test tactical map with terrain features."""
        request = TacticalMapRequest(
            theme="fantasy",
            grid_size=GridSize(width=20, height=20),
            terrain_features=[
                TerrainFeature(
                    type="forest",
                    position=GridPoint(x=5, y=5),
                    size=GridSize(width=3, height=3)
                ),
                TerrainFeature(
                    type="river",
                    position=GridPoint(x=0, y=10),
                    properties={"width": "10ft", "flow": "east"}
                )
            ]
        )
        
        result = await image_service.generate_tactical_map(request)
        assert result.terrain_data["features_count"] == 2
        assert "forest" in str(result.terrain_data["features"])
        assert "river" in str(result.terrain_data["features"])

    async def test_tactical_map_with_characters(self, image_service, mock_map_generator):
        """Test tactical map with character positions."""
        char_id_1 = uuid4()
        char_id_2 = uuid4()
        
        request = TacticalMapRequest(
            theme="fantasy",
            grid_size=GridSize(width=20, height=20),
            characters=[
                CharacterPosition(
                    character_id=char_id_1,
                    position=GridPoint(x=5, y=5),
                    size="medium"
                ),
                CharacterPosition(
                    character_id=char_id_2,
                    position=GridPoint(x=10, y=10),
                    size="large",
                    status_effects=["prone", "invisible"]
                )
            ]
        )
        
        result = await image_service.generate_tactical_map(request)
        
        assert len(result.character_positions) == 2
        assert str(char_id_1) in str(result.character_positions)
        assert str(char_id_2) in str(result.character_positions)
        assert "invisible" in str(result.character_positions)

    async def test_tactical_map_with_spell_effects(self, image_service, mock_map_generator):
        """Test tactical map with spell effect overlays."""
        request = TacticalMapRequest(
            theme="fantasy",
            grid_size=GridSize(width=20, height=20),
            spell_effects=[
                SpellEffect(
                    type="circle",
                    origin=GridPoint(x=10, y=10),
                    size=20,
                    properties={"spell": "fireball", "color": "red"}
                ),
                SpellEffect(
                    type="cone",
                    origin=GridPoint(x=5, y=5),
                    size=15,
                    properties={"spell": "burning_hands", "color": "orange"}
                )
            ]
        )
        
        result = await image_service.generate_tactical_map(request)
        
        assert len(result.spell_overlays) == 2
        assert "fireball" in str(result.spell_overlays)
        assert "burning_hands" in str(result.spell_overlays)

@pytest.mark.asyncio
class TestCampaignMapGeneration:
    async def test_basic_campaign_map(self, image_service, mock_map_generator):
        """Test basic campaign/region map generation."""
        request = CampaignMapRequest(
            theme="fantasy",
            grid_size=GridSize(width=30, height=30, scale=1),
            region_name="The Misty Vale",
            region_type="wilderness",
            points_of_interest=[
                {"type": "town", "name": "Riverside", "position": "10,15"},
                {"type": "dungeon", "name": "Ancient Ruins", "position": "20,25"}
            ]
        )
        
        result = await image_service.generate_campaign_map(request)
        
        assert result.width == 1024
        assert result.height == 1024
        assert "The Misty Vale" in str(result.map_metadata)
        assert len(result.points_of_interest) == 2
        assert "Riverside" in str(result.points_of_interest)
        assert "Ancient Ruins" in str(result.points_of_interest)

    async def test_campaign_map_with_party_tracking(self, image_service, mock_map_generator):
        """Test campaign map with party position tracking."""
        party_id = uuid4()
        request = CampaignMapRequest(
            theme="fantasy",
            grid_size=GridSize(width=30, height=30),
            region_name="The Misty Vale",
            region_type="wilderness",
            characters=[
                CharacterPosition(
                    character_id=party_id,
                    position=GridPoint(x=15, y=15),
                    properties={"type": "party", "members": 4}
                )
            ]
        )
        
        result = await image_service.generate_campaign_map(request)
        
        assert str(party_id) in str(result.party_positions)
        assert result.party_positions[0]["members"] == 4

    async def test_campaign_map_with_regions(self, image_service, mock_map_generator):
        """Test campaign map with multiple regions and borders."""
        request = CampaignMapRequest(
            theme="fantasy",
            grid_size=GridSize(width=40, height=40),
            region_name="The Disputed Lands",
            region_type="political",
            terrain_features=[
                TerrainFeature(
                    type="kingdom_border",
                    position=GridPoint(x=20, y=0),
                    properties={"name": "Northern Kingdom", "border_style": "solid"}
                ),
                TerrainFeature(
                    type="kingdom_border",
                    position=GridPoint(x=20, y=39),
                    properties={"name": "Southern Empire", "border_style": "dashed"}
                )
            ]
        )
        
        result = await image_service.generate_campaign_map(request)
        
        assert "Northern Kingdom" in str(result.region_data)
        assert "Southern Empire" in str(result.region_data)
        assert len(result.political_borders) == 2

@pytest.mark.asyncio
class TestMapGenerationErrors:
    async def test_invalid_grid_size(self, image_service, mock_map_generator):
        """Test error handling for invalid grid size."""
        with pytest.raises(ValueError) as exc_info:
            request = TacticalMapRequest(
                theme="fantasy",
                grid_size=GridSize(width=0, height=0)
            )
            await image_service.generate_tactical_map(request)
        assert "Invalid grid size" in str(exc_info.value)

    async def test_invalid_character_position(self, image_service, mock_map_generator):
        """Test error handling for invalid character position."""
        request = TacticalMapRequest(
            theme="fantasy",
            grid_size=GridSize(width=20, height=20),
            characters=[
                CharacterPosition(
                    character_id=uuid4(),
                    position=GridPoint(x=30, y=30),  # Outside grid
                    size="medium"
                )
            ]
        )
        
        with pytest.raises(ValueError) as exc_info:
            await image_service.generate_tactical_map(request)
        assert "Character position outside grid" in str(exc_info.value)

    async def test_api_failure_handling(self, image_service, mock_getimg_api):
        """Test handling of API failures."""
        async def mock_fail(*args, **kwargs):
            raise Exception("API Error")
        
        mock_getimg_api.generate_image = mock_fail
        
        with pytest.raises(ImageGenerationError) as exc_info:
            request = TacticalMapRequest(
                theme="fantasy",
                grid_size=GridSize(width=20, height=20)
            )
            await image_service.generate_tactical_map(request)
        assert "Failed to generate map" in str(exc_info.value)
