"""
Image generation core functionality.
"""

from typing import Dict, Any
from .exceptions import ImageGenerationError

class GetImgClient:
    """Client for interacting with GetImg.AI API."""

    async def generate_image(
        self,
        style: str,
        description: str,
        additional_details: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """Generate an image using GetImg.AI.
        
        Args:
            style: The style to generate the image in
            description: Basic description of what to generate
            additional_details: Additional prompt details
            
        Returns:
            Dict containing generated image data and metadata
            
        Raises:
            ImageGenerationError: If generation fails
        """
        raise NotImplementedError()

    async def enhance_image(self, image_data: bytes) -> bytes:
        """Enhance an existing image using GetImg.AI.
        
        Args:
            image_data: Raw image data to enhance
            
        Returns:
            Enhanced image data
            
        Raises:
            ImageGenerationError: If enhancement fails
        """
        raise NotImplementedError()

class ImageGenerator:
    """Handles image generation using configured provider."""
    
    def __init__(self, api_client: GetImgClient):
        """Initialize with API client.
        
        Args:
            api_client: GetImg.AI API client instance
        """
        self.api_client = api_client

    async def generate_portrait(
        self,
        style: str,
        description: str,
        prompt_details: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """Generate a character portrait.
        
        Args:
            style: Portrait style (realistic, anime, etc.)
            description: Basic character description
            prompt_details: Additional details for generation
            
        Returns:
            Dict containing generated image data and metadata
            
        Raises:
            ImageGenerationError: If portrait generation fails
        """
        try:
            return await self.api_client.generate_image(
                style=style,
                description=description,
                additional_details=prompt_details
            )
        except Exception as e:
            raise ImageGenerationError(f"Failed to generate portrait: {str(e)}") from e
