"""
Map generation core functionality.
"""

from typing import Dict, Any, List
from uuid import UUID

from .exceptions import ImageGenerationError
from ..models.map_request import (
    TacticalMapRequest, CampaignMapRequest,
    GridPoint, CharacterPosition
)

class MapGenerator:
    """Handles map generation using the GetImg.AI API."""

    def __init__(self, api_client):
        """Initialize with API client.
        
        Args:
            api_client: GetImg.AI API client instance
        """
        self.api_client = api_client

    def _validate_grid_size(self, width: int, height: int) -> None:
        """Validate grid dimensions.
        
        Args:
            width: Grid width
            height: Grid height
            
        Raises:
            ValueError: If dimensions are invalid
        """
        if width <= 0 or height <= 0:
            raise ValueError("Invalid grid size: dimensions must be positive")
        if width > 100 or height > 100:
            raise ValueError("Invalid grid size: maximum dimension is 100")

    def _validate_character_positions(
        self,
        characters: List[CharacterPosition],
        grid_width: int,
        grid_height: int
    ) -> None:
        """Validate character positions against grid bounds.
        
        Args:
            characters: List of character positions
            grid_width: Width of the grid
            grid_height: Height of the grid
            
        Raises:
            ValueError: If any position is invalid
        """
        for char in characters:
            if (char.position.x < 0 or char.position.x >= grid_width or
                char.position.y < 0 or char.position.y >= grid_height):
                raise ValueError(
                    f"Character position outside grid: ({char.position.x}, {char.position.y})"
                )

    async def generate_tactical_map(self, request: TacticalMapRequest) -> Dict[str, Any]:
        """Generate a tactical battle map.
        
        Args:
            request: Tactical map generation request
            
        Returns:
            Dict containing generated map data and metadata
            
        Raises:
            ImageGenerationError: If map generation fails
            ValueError: If request parameters are invalid
        """
        try:
            # Validate request
            self._validate_grid_size(request.grid_size.width, request.grid_size.height)
            if request.characters:
                self._validate_character_positions(
                    request.characters,
                    request.grid_size.width,
                    request.grid_size.height
                )

            # Generate base map with grid
            prompt = self._build_tactical_map_prompt(request)
            result = await self.api_client.generate_image(
                style="map",
                description=prompt,
                additional_details={
                    "grid_size": {
                        "width": request.grid_size.width,
                        "height": request.grid_size.height,
                        "scale": request.grid_size.scale
                    },
                    "lighting": request.lighting_conditions,
                    "weather": request.weather_effects,
                    "terrain": [
                        {
                            "type": feature.type,
                            "position": {"x": feature.position.x, "y": feature.position.y},
                            **feature.properties
                        }
                        for feature in request.terrain_features
                    ]
                }
            )

            # Add grid metadata
            result["grid_metadata"] = {
                "cells_x": request.grid_size.width,
                "cells_y": request.grid_size.height,
                "scale": request.grid_size.scale
            }

            # Add terrain data if present
            if request.terrain_features:
                result["terrain_data"] = {
                    "features_count": len(request.terrain_features),
                    "features": [
                        {
                            "type": f.type,
                            "position": {"x": f.position.x, "y": f.position.y},
                            "size": {"width": f.size.width, "height": f.size.height} if f.size else None,
                            **(f.properties or {})
                        }
                        for f in request.terrain_features
                    ]
                }

            # Add character positions if present
            if request.characters:
                result["character_positions"] = [
                    {
                        "id": str(char.character_id),
                        "position": {"x": char.position.x, "y": char.position.y},
                        "size": char.size,
                        "effects": char.status_effects
                    }
                    for char in request.characters
                ]

            # Add spell effects if present
            if request.spell_effects:
                result["spell_overlays"] = [
                    {
                        "type": effect.type,
                        "origin": {"x": effect.origin.x, "y": effect.origin.y},
                        "size": effect.size,
                        **effect.properties
                    }
                    for effect in request.spell_effects
                ]

            # Ensure metadata includes width/height/format for downstream
            if "metadata" not in result:
                result["metadata"] = {}
            result["metadata"].setdefault("width", result.get("metadata", {}).get("width", 1024))
            result["metadata"].setdefault("height", result.get("metadata", {}).get("height", 1024))
            result["metadata"].setdefault("format", result.get("metadata", {}).get("format", "PNG"))

            return result

        except ValueError as e:
            raise e
        except Exception as e:
            raise ImageGenerationError(f"Failed to generate map: {str(e)}") from e

    async def generate_campaign_map(self, request: CampaignMapRequest) -> Dict[str, Any]:
        """Generate a campaign/region map.
        
        Args:
            request: Campaign map generation request
            
        Returns:
            Dict containing generated map data and metadata
            
        Raises:
            ImageGenerationError: If map generation fails
            ValueError: If request parameters are invalid
        """
        try:
            # Validate request
            self._validate_grid_size(request.grid_size.width, request.grid_size.height)

            # Generate base map
            prompt = self._build_campaign_map_prompt(request)
            result = await self.api_client.generate_image(
                style=request.map_style,
                description=prompt,
                additional_details={
                    "grid_size": {
                        "width": request.grid_size.width,
                        "height": request.grid_size.height,
                        "scale": request.grid_size.scale
                    },
                    "region_name": request.region_name,
                    "region_type": request.region_type,
                    "points_of_interest": request.points_of_interest,
                    "terrain": [
                        {
                            "type": feature.type,
                            "position": {"x": feature.position.x, "y": feature.position.y},
                            **feature.properties
                        }
                        for feature in request.terrain_features
                    ]
                }
            )

            # Add metadata
            result["metadata"] = {
                "region_name": request.region_name,
                "region_type": request.region_type,
                "map_style": request.map_style
            }

            # Add points of interest
            result["points_of_interest"] = request.points_of_interest

            # Add party positions if present
            if request.characters:
                result["party_positions"] = [
                    {
                        "id": str(char.character_id),
                        "position": {"x": char.position.x, "y": char.position.y},
                        **(getattr(char, "properties", {}) or {})
                    }
                    for char in request.characters
                ]

            # Add region data if present
            if request.terrain_features:
                result["region_data"] = {}
                result["political_borders"] = []
                for feature in request.terrain_features:
                    if feature.type == "kingdom_border":
                        result["political_borders"].append({
                            "name": feature.properties.get("name"),
                            "style": feature.properties.get("border_style"),
                            "position": {"x": feature.position.x, "y": feature.position.y}
                        })
                        result["region_data"][feature.properties.get("name")] = {
                            "border_style": feature.properties.get("border_style")
                        }

            # Ensure metadata includes width/height/format for downstream
            if "metadata" not in result:
                result["metadata"] = {}
            result["metadata"].setdefault("width", result.get("metadata", {}).get("width", 1024))
            result["metadata"].setdefault("height", result.get("metadata", {}).get("height", 1024))
            result["metadata"].setdefault("format", result.get("metadata", {}).get("format", "PNG"))

            return result

        except ValueError as e:
            raise e
        except Exception as e:
            raise ImageGenerationError(f"Failed to generate map: {str(e)}") from e

    def _build_tactical_map_prompt(self, request: TacticalMapRequest) -> str:
        """Build prompt for tactical map generation."""
        prompt = f"Generate a {request.theme} tactical battle map with "
        prompt += f"a {request.grid_size.width}x{request.grid_size.height} grid. "
        
        if request.terrain_features:
            terrain_desc = ", ".join(f"{t.type}" for t in request.terrain_features)
            prompt += f"Include terrain features: {terrain_desc}. "
        
        if request.lighting_conditions != "bright":
            prompt += f"Apply {request.lighting_conditions} lighting conditions. "
        
        if request.weather_effects:
            weather = ", ".join(request.weather_effects)
            prompt += f"Include weather effects: {weather}. "
        
        return prompt

    def _build_campaign_map_prompt(self, request: CampaignMapRequest) -> str:
        """Build prompt for campaign map generation."""
        prompt = f"Generate a {request.map_style} style map of {request.region_name}, "
        prompt += f"a {request.region_type} region. "
        
        if request.terrain_features:
            terrain_types = set(t.type for t in request.terrain_features)
            terrain_desc = ", ".join(terrain_types)
            prompt += f"Include geographic features: {terrain_desc}. "
        
        if request.points_of_interest:
            poi_types = set(poi["type"] for poi in request.points_of_interest)
            poi_desc = ", ".join(poi_types)
            prompt += f"Mark locations of type: {poi_desc}. "
        
        return prompt
