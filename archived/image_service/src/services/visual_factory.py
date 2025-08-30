"""
Visual content generation factory.
"""

from typing import Dict, Any, Optional, List
from uuid import UUID

from ..models.content import VisualContent, ContentType
from ..core.logging import get_logger

logger = get_logger(__name__)


class VisualFactory:
    """Factory for generating visual content."""
    
    def __init__(self, message_hub_client, getimg_client):
        """Initialize with required dependencies."""
        self.message_hub = message_hub_client
        self.getimg = getimg_client
    
    async def generate_portrait(
        self,
        subject_type: str,
        subject_id: UUID,
        preferences: Optional[Dict[str, Any]] = None
    ) -> VisualContent:
        """Generate a portrait."""
        try:
            # Get subject details
            subject_data = await self.message_hub.request(
                f"{subject_type}.get",
                {"id": str(subject_id)}
            )
            
            if not subject_data:
                raise ValueError(f"Subject {subject_type} not found")
            
            # Get portrait generation prompt from LLM
            prompt = await self.message_hub.request(
                "llm.generate_portrait_prompt",
                {
                    "subject": subject_data,
                    "preferences": preferences or {}
                }
            )
            
            if not prompt:
                raise ValueError("Failed to generate portrait prompt")
            
            # Generate image with GetImg.AI
            image = await self.getimg.generate(
                prompt=prompt,
                style=preferences.get("style", "realistic"),
                size=preferences.get("size", {"width": 512, "height": 512}),
                parameters=preferences.get("parameters", {})
            )
            
            if not image:
                raise ValueError("Failed to generate portrait")
            
            # Create content model
            content = VisualContent(
                type=ContentType.PORTRAIT,
                subject_type=subject_type,
                subject_id=subject_id,
                image_url=image["url"],
                prompt=prompt,
                metadata={
                    "style": preferences.get("style"),
                    "parameters": preferences.get("parameters")
                }
            )
            
            # Publish generation event
            await self.message_hub.publish(
                "image.portrait_generated",
                {
                    "content_id": str(content.id),
                    "subject_type": subject_type,
                    "subject_id": str(subject_id)
                }
            )
            
            return content
            
        except Exception as e:
            logger.error("Portrait generation failed", error=str(e))
            raise ValueError(f"Failed to generate portrait: {e}")
    
    async def generate_map(
        self,
        map_type: str,
        parameters: Dict[str, Any],
        theme: Optional[str] = None
    ) -> VisualContent:
        """Generate a map."""
        try:
            # Get map generation prompt from LLM
            prompt = await self.message_hub.request(
                "llm.generate_map_prompt",
                {
                    "type": map_type,
                    "parameters": parameters,
                    "theme": theme
                }
            )
            
            if not prompt:
                raise ValueError("Failed to generate map prompt")
            
            # Generate base map with GetImg.AI
            image = await self.getimg.generate(
                prompt=prompt,
                style="map",
                size=parameters.get("size", {"width": 1024, "height": 1024}),
                parameters={
                    "detail_level": "high",
                    "view": "top-down",
                    **parameters.get("style_params", {})
                }
            )
            
            if not image:
                raise ValueError("Failed to generate map")
            
            # Add grid overlay if tactical map
            if map_type == "tactical":
                image = await self._add_grid_overlay(
                    image["url"],
                    parameters.get("grid", {})
                )
            
            # Create content model
            content = VisualContent(
                type=ContentType.MAP,
                map_type=map_type,
                image_url=image["url"],
                prompt=prompt,
                metadata={
                    "theme": theme,
                    "parameters": parameters,
                    "grid": parameters.get("grid")
                }
            )
            
            # Publish generation event
            await self.message_hub.publish(
                "image.map_generated",
                {
                    "content_id": str(content.id),
                    "map_type": map_type,
                    "theme": theme
                }
            )
            
            return content
            
        except Exception as e:
            logger.error("Map generation failed", error=str(e))
            raise ValueError(f"Failed to generate map: {e}")
    
    async def generate_item_visual(
        self,
        item_id: UUID,
        preferences: Optional[Dict[str, Any]] = None
    ) -> VisualContent:
        """Generate item visualization."""
        try:
            # Get item details from catalog
            item_data = await self.message_hub.request(
                "catalog.get_item",
                {"item_id": str(item_id)}
            )
            
            if not item_data:
                raise ValueError("Item not found")
            
            # Get visualization prompt from LLM
            prompt = await self.message_hub.request(
                "llm.generate_item_prompt",
                {
                    "item": item_data,
                    "preferences": preferences or {}
                }
            )
            
            if not prompt:
                raise ValueError("Failed to generate item prompt")
            
            # Generate image with GetImg.AI
            image = await self.getimg.generate(
                prompt=prompt,
                style=preferences.get("style", "realistic"),
                size=preferences.get("size", {"width": 512, "height": 512}),
                parameters={
                    "detail_level": "high",
                    "view": preferences.get("view", "front"),
                    **preferences.get("parameters", {})
                }
            )
            
            if not image:
                raise ValueError("Failed to generate item visual")
            
            # Create content model
            content = VisualContent(
                type=ContentType.ITEM,
                subject_id=item_id,
                image_url=image["url"],
                prompt=prompt,
                metadata={
                    "style": preferences.get("style"),
                    "view": preferences.get("view"),
                    "parameters": preferences.get("parameters")
                }
            )
            
            # Publish generation event
            await self.message_hub.publish(
                "image.item_generated",
                {
                    "content_id": str(content.id),
                    "item_id": str(item_id)
                }
            )
            
            return content
            
        except Exception as e:
            logger.error("Item visualization failed", error=str(e))
            raise ValueError(f"Failed to generate item visual: {e}")
    
    async def apply_theme(
        self,
        content_id: UUID,
        theme: str,
        strength: float = 1.0,
        preserve: List[str] = None
    ) -> VisualContent:
        """Apply theme to existing visual content."""
        try:
            # Get existing content
            content = await self.message_hub.request(
                "image.get_content",
                {"content_id": str(content_id)}
            )
            
            if not content:
                raise ValueError("Content not found")
            
            # Get theme adaptation from LLM
            adaptation = await self.message_hub.request(
                "llm.adapt_visual_theme",
                {
                    "content": content,
                    "theme": theme,
                    "strength": strength,
                    "preserve": preserve or []
                }
            )
            
            if not adaptation:
                raise ValueError("Failed to adapt theme")
            
            # Generate themed image with GetImg.AI
            image = await self.getimg.style_transfer(
                image_url=content["image_url"],
                prompt=adaptation["prompt"],
                strength=strength,
                preserve_elements=preserve or []
            )
            
            if not image:
                raise ValueError("Failed to generate themed image")
            
            # Update content model
            content = VisualContent(**content)
            content.image_url = image["url"]
            content.metadata["theme"] = theme
            content.metadata["theme_strength"] = strength
            
            # Publish theme event
            await self.message_hub.publish(
                "image.theme_applied",
                {
                    "content_id": str(content_id),
                    "theme": theme,
                    "strength": strength
                }
            )
            
            return content
            
        except Exception as e:
            logger.error("Theme application failed", error=str(e))
            raise ValueError(f"Failed to apply theme: {e}")
    
    async def _add_grid_overlay(
        self,
        image_url: str,
        grid_params: Dict[str, Any]
    ) -> Dict[str, str]:
        """Add grid overlay to tactical map."""
        try:
            # Get grid overlay from GetImg.AI
            image = await self.getimg.add_grid(
                image_url=image_url,
                grid_size=grid_params.get("size", 32),
                color=grid_params.get("color", "#000000"),
                opacity=grid_params.get("opacity", 0.3)
            )
            
            return image
            
        except Exception as e:
            logger.error("Grid overlay failed", error=str(e))
            return {"url": image_url}  # Return original if overlay fails
