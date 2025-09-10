"""
GetImg.AI API client.
"""

import base64
import os
from typing import Dict, Any, Optional

import httpx

class ImageGenerationError(Exception):
    """Raised when image generation fails."""
    pass

class GetImgClient:
    """Client for interacting with GetImg.AI API."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.getimg.ai/v1"):
        """Initialize API client.
        
        Args:
            api_key: API key. If not provided, will try to read from GETIMG_API_KEY env var.
            base_url: Base URL for API requests.
        """
        self.api_key = api_key or os.getenv("GETIMG_API_KEY")
        if not self.api_key:
            raise ValueError("API key required")
        
        self.base_url = base_url
        self.session = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )

    async def generate_image(
        self,
        prompt: str,
        style: str = "realistic",
        width: int = 512,
        height: int = 512,
        steps: int = 50,
        seed: Optional[int] = None,
        negative_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate an image via the API.
        
        Args:
            prompt: Generation prompt
            style: Art style to use
            width: Image width
            height: Image height
            steps: Number of generation steps
            seed: Optional RNG seed
            negative_prompt: Optional negative prompt
            
        Returns:
            Dictionary containing:
              - url: URL to generated image
              - data: Base64 encoded image data
              - metadata: Image metadata
            
        Raises:
            ImageGenerationError: If generation fails
            ValueError: If parameters are invalid
        """
        try:
            # Input validation
            if width % 128 != 0 or height % 128 != 0:
                raise ValueError("Width and height must be multiples of 128")

            # Build request payload
            data = {
                "prompt": prompt,
                "style": style,
                "width": width,
                "height": height,
                "steps": steps,
                "negative_prompt": negative_prompt
            }
            if seed is not None:
                data["seed"] = seed

            # Call API
            response = await self.session.post("/images/generations", json=data)
            if response.status_code != 200:
                raise ImageGenerationError(f"Generation failed: {response.text}")

            result = response.json()
            if "images" not in result or not result["images"]:
                raise ImageGenerationError("No images in response")

            # Get first image
            image_data = result["images"][0]
            if "image" not in image_data:
                raise ImageGenerationError("No image data in response")

            # Extract metadata
            metadata = {
                "width": width,
                "height": height,
                "style": style,
                "steps": steps
            }
            if seed is not None:
                metadata["seed"] = seed
            if "metadata" in image_data:
                metadata.update(image_data["metadata"])

            return {
                "url": image_data.get("url", ""),
                "data": image_data["image"],  # Base64 data
                "metadata": metadata
            }

        except httpx.RequestError as e:
            raise ImageGenerationError(f"API request failed: {str(e)}")
        except Exception as e:
            if isinstance(e, ImageGenerationError):
                raise
            raise ImageGenerationError(f"Unexpected error: {str(e)}")

    async def generate_variations(
        self,
        image: str,  # Base64 encoded image data
        prompt: Optional[str] = None,
        variations: int = 1,
        style: str = "realistic"
    ) -> Dict[str, Any]:
        """Generate variations of an existing image.
        
        Args:
            image: Base64 encoded source image
            prompt: Optional prompt to guide variation
            variations: Number of variations to generate
            style: Art style to apply
            
        Returns:
            Dictionary containing generated variations
            
        Raises:
            ImageGenerationError: If generation fails
            ValueError: If parameters are invalid
        """
        try:
            if variations < 1:
                raise ValueError("Must generate at least one variation")

            # Build request data
            data = {
                "image": image,
                "variations": variations,
                "style": style
            }
            if prompt:
                data["prompt"] = prompt

            # Call API
            response = await self.session.post("/images/variations", json=data)
            if response.status_code != 200:
                raise ImageGenerationError(f"Variation failed: {response.text}")

            result = response.json()
            if "images" not in result or not result["images"]:
                raise ImageGenerationError("No variations in response")

            # Extract metadata
            metadata = {
                "style": style,
                "variations": variations
            }
            if "metadata" in result:
                metadata.update(result["metadata"])

            return {
                "images": result["images"],  # List of variations
                "metadata": metadata
            }

        except httpx.RequestError as e:
            raise ImageGenerationError(f"API request failed: {str(e)}")
        except Exception as e:
            if isinstance(e, ImageGenerationError):
                raise
            raise ImageGenerationError(f"Unexpected error: {str(e)}")

    async def close(self):
        """Close API client session."""
        if self.session:
            await self.session.aclose()
