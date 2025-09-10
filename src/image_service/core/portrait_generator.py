"""
Portrait generation logic.
"""

from typing import Dict, Any, Optional
import json
from uuid import UUID

from ..models.character import (
    CharacterPortraitRequest,
    PortraitMetadata,
    EquipmentVisuals,
    ThemeStyle,
    PortraitSize
)
from .getimg import GetImgClient

class PortraitGenerator:
    """Generator for character portraits."""

    def __init__(self, api_client: GetImgClient):
        """Initialize generator with API client."""
        self.api = api_client

    async def generate_portrait(
        self,
        request: CharacterPortraitRequest
    ) -> Dict[str, Any]:
        """Generate a character portrait.
        
        Args:
            request: Portrait generation request
            
        Returns:
            Dictionary containing:
              - url: URL to generated image
              - data: Base64 encoded image data
              - metadata: Image metadata
            
        Raises:
            ValueError: If request is invalid
            ImageGenerationError: If generation fails
        """
        # Build the prompt based on request details
        prompt = self._build_portrait_prompt(request)

        # Get size dimensions
        width, height = request.size.dimensions()

        # Call API to generate image
        result = await self.api.generate_image(
            prompt=prompt,
            style=request.metadata.theme.art_style,
            width=width,
            height=height,
            negative_prompt=self._get_negative_prompt(request)
        )

        # Add request metadata
        result["metadata"].update({
            "art_style": request.metadata.theme.art_style,
            "theme": {
                "color_scheme": request.metadata.theme.color_scheme,
                "mood": request.metadata.theme.mood
            },
            "portrait_metadata": {
                key: value 
                for key, value in request.metadata.model_dump().items()
                if value is not None
            },
            "generation_metadata": {
                "size": request.size.value,
                "background": request.background_style,
                "pose": request.pose,
                "expression": request.expression,
                "lighting": request.lighting
            }
        })

        return result

    def _build_portrait_prompt(self, request: CharacterPortraitRequest) -> str:
        """Build a detailed prompt for portrait generation.
        
        Args:
            request: Portrait generation request
            
        Returns:
            Formatted prompt string
        """
        metadata = request.metadata
        prompt_parts = []

        # Basic character description
        if metadata.monster_type:
            prompt_parts.append(f"{metadata.character_name}, a {metadata.monster_type.value}")
        elif metadata.npc_type:
            prompt_parts.append(f"{metadata.character_name}, a {metadata.npc_type.value}")
        else:
            desc = f"{metadata.character_name}, a {metadata.character_race.value} "
            if metadata.character_class:
                desc += metadata.character_class.value
            prompt_parts.append(desc)

        # Equipment details
        if metadata.equipment:
            equipment_desc = self._build_equipment_description(metadata.equipment)
            if equipment_desc:
                prompt_parts.append(f"wearing {equipment_desc}")

        # Pose and expression
        prompt_parts.append(f"in a {request.pose} pose")
        prompt_parts.append(f"with a {request.expression} expression")

        # Background and lighting
        prompt_parts.append(f"with {request.background_style} background")
        prompt_parts.append(f"in {request.lighting} lighting")

        # Theme details
        theme = metadata.theme
        prompt_parts.append(f"in {theme.art_style} style")
        prompt_parts.append(f"with {theme.color_scheme} color scheme")
        prompt_parts.append(f"conveying a {theme.mood} mood")

        return ", ".join(prompt_parts)

    def _build_equipment_description(self, equipment: EquipmentVisuals) -> str:
        """Build description of character's equipment.
        
        Args:
            equipment: Equipment visuals
            
        Returns:
            Equipment description string
        """
        desc_parts = []

        if equipment.armor:
            desc_parts.append(equipment.armor)
        if equipment.weapon:
            desc_parts.append(f"wielding {equipment.weapon}")
        if equipment.shield:
            desc_parts.append(f"carrying {equipment.shield}")
        if equipment.accessories:
            acc_list = ", ".join(equipment.accessories[:-1])
            if acc_list:
                desc_parts.append(f"{acc_list} and {equipment.accessories[-1]}")
            else:
                desc_parts.append(equipment.accessories[0])

        return ", ".join(desc_parts)

    def _get_negative_prompt(self, request: CharacterPortraitRequest) -> str:
        """Get negative prompt to improve generation quality.
        
        Args:
            request: Portrait generation request
            
        Returns:
            Negative prompt string
        """
        # Common issues to avoid
        negatives = [
            "deformed",
            "distorted",
            "blurry",
            "low quality",
            "poorly drawn",
            "extra limbs",
            "missing limbs",
            "double face",
            "multiple faces",
            "malformed hands",
            "incorrect anatomy"
        ]

        # Style-specific negatives
        if request.metadata.theme.art_style == "realistic":
            negatives.extend([
                "cartoon",
                "anime",
                "caricature",
                "cel shading",
                "stylized"
            ])
        elif request.metadata.theme.art_style == "anime":
            negatives.extend([
                "photorealistic",
                "hyperrealistic",
                "oil painting",
                "western art style"
            ])

        return ", ".join(negatives)
