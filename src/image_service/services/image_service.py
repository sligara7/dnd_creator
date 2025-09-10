"""
Image Service main service class.
"""

from uuid import uuid4
from typing import Dict, Any, List
import json

from ..models.image import Image
from ..models.map_request import TacticalMapRequest, CampaignMapRequest
from ..models.map_result import MapImage
from ..core.image_generator import ImageGenerator
from ..core.portrait_generator import PortraitGenerator
from ..core.map_generator import MapGenerator
from ..repositories.image_repository import ImageRepository
from ..repositories.map_repository import MapRepository
from ..models.character import CharacterPortraitRequest

class ImageService:
    """Main service class for image operations."""
    
    def __init__(
        self,
        repository: ImageRepository,
        generator: ImageGenerator,
        map_repository: MapRepository = None,
        map_generator: MapGenerator = None,
        portrait_generator: PortraitGenerator = None
    ):
        """Initialize service with dependencies.
        
        Args:
            repository: Repository for image persistence
            generator: Service for image generation
        """
        self.repository = repository
        self.generator = generator
        self.map_repository = map_repository
        self.map_generator = map_generator
        self.portrait_generator = portrait_generator

    async def generate_character_portrait(self, request: CharacterPortraitRequest) -> str:
        """Generate a character portrait.
        
        Args:
            request: Portrait generation request
            
        Returns:
            ID of generated image
            
        Raises:
            ImageGenerationError: If generation fails
            ValueError: If request is invalid
        """
        if not self.portrait_generator:
            raise ValueError("Portrait generator not configured")

        # Generate the portrait
        result = await self.portrait_generator.generate_portrait(request)
        
        # Create image model
        image = Image(
            id=uuid4(),
            character_id=request.metadata.character_id,
            width=result["metadata"]["width"],
            height=result["metadata"]["height"],
            format=result["metadata"].get("format", "png"),
            data=result["data"],
            tags={
                "character_name": request.metadata.character_name,
                "theme": json.dumps(request.metadata.theme.model_dump()),
                "type": "portrait",
                **self._get_character_tags(request)
            }
        )
        
        # Persist image
        await self.repository.save(image)
        return str(image.id)

    async def generate_character_portraits(self, requests: List[CharacterPortraitRequest]) -> List[str]:
        """Generate multiple character portraits in batch.
        
        Args:
            requests: List of portrait requests
            
        Returns:
            List of generated image IDs
            
        Raises:
            ImageGenerationError: If generation fails
        """
        image_ids = []
        for request in requests:
            image_id = await self.generate_character_portrait(request)
            image_ids.append(image_id)
        return image_ids

    async def get_image_metadata(self, image_id: str) -> Image:
        """Get metadata for an image.
        
        Args:
            image_id: Image identifier
            
        Returns:
            Image metadata
            
        Raises:
            ImageNotFound: If image does not exist
        """
        return await self.repository.get(image_id)

    def _get_character_tags(self, request: CharacterPortraitRequest) -> Dict[str, str]:
        """Get tags for character portrait.
        
        Args:
            request: Portrait request
            
        Returns:
            Dictionary of tags
        """
        tags = {}

        if request.metadata.character_class:
            tags["class"] = request.metadata.character_class.value
        if request.metadata.character_race:
            tags["race"] = request.metadata.character_race.value
        if request.metadata.npc_type:
            tags["npc_type"] = request.metadata.npc_type.value
        if request.metadata.monster_type:
            tags["monster_type"] = request.metadata.monster_type.value
        if request.metadata.equipment:
            if request.metadata.equipment.armor:
                tags["armor"] = request.metadata.equipment.armor
            if request.metadata.equipment.weapon:
                tags["weapon"] = request.metadata.equipment.weapon

        return tags

    async def generate_tactical_map(self, request: TacticalMapRequest) -> MapImage:
        """Generate a tactical battle map.
        
        Args:
            request: Map generation request
            
        Returns:
            Generated map image
            
        Raises:
            ImageGenerationError: If generation fails
            ValueError: If request parameters are invalid
        """
        if not self.map_generator:
            raise ValueError("Map generator not configured")
        
        # Generate the map
        result = await self.map_generator.generate_tactical_map(request)
        
        # Create and persist map model
        map_image = MapImage(
            id=uuid4(),
            campaign_id=request.campaign_id,
            encounter_id=request.encounter_id,
            width=result["metadata"]["width"],
            height=result["metadata"]["height"],
            format=result["metadata"]["format"],
            data=result["image_data"],
            grid_metadata=result.get("grid_metadata"),
            map_metadata={
                key: value for key, value in result.items()
                if key not in ["image_data", "metadata", "grid_metadata"]
            }
        )
        
        await self.map_repository.save(map_image)
        return map_image

    async def generate_campaign_map(self, request: CampaignMapRequest) -> MapImage:
        """Generate a campaign/region map.
        
        Args:
            request: Map generation request
            
        Returns:
            Generated map image
            
        Raises:
            ImageGenerationError: If generation fails
            ValueError: If request parameters are invalid
        """
        if not self.map_generator:
            raise ValueError("Map generator not configured")
        
        # Generate the map
        result = await self.map_generator.generate_campaign_map(request)
        
        # Create and persist map model
        map_image = MapImage(
            id=uuid4(),
            campaign_id=request.campaign_id,
            width=result["metadata"]["width"],
            height=result["metadata"]["height"],
            format=result["metadata"]["format"],
            data=result["image_data"],
            grid_metadata=result.get("grid_metadata"),
            map_metadata={
                key: value for key, value in result.items()
                if key not in ["image_data", "metadata", "grid_metadata"]
            }
        )

        # Add region metadata
        map_image.map_metadata = {
            **(map_image.map_metadata or {}),
            "region_name": request.region_name,
            "region_type": request.region_type,
            "map_style": request.map_style
        }
        
        await self.map_repository.save(map_image)
        return map_image

    def _get_image_tags(self, metadata: Dict[str, Any]) -> Dict[str, str]:
        """Convert metadata to image tags.
        
        Args:
            metadata: Image generation metadata
            
        Returns:
            Dictionary of tag key/values
        """
        tags = {}

        if "theme" in metadata:
            tags["theme"] = json.dumps(metadata["theme"])

        # Convert any metadata fields to tags
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                tags[key] = str(value)
            elif isinstance(value, dict):
                tags[key] = json.dumps(value)

        return tags
