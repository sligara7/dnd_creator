from typing import Optional

import httpx
from image_service.core.config import settings
from image_service.core.exceptions import GenerationError


class GetImgClient:
    """Client for interacting with GetImg.AI API"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GETIMG_API_KEY
        self.base_url = settings.GETIMG_API_URL
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        size: tuple[int, int] = (1024, 1024),
        model: str = "stable-diffusion-v1-5",
        steps: int = 50,
        cfg_scale: float = 7.5,
        seed: Optional[int] = None,
        style_preset: Optional[str] = None,
    ) -> str:
        """Generate an image using Stable Diffusion"""
        try:
            response = await self.client.post(
                "/images/generations",
                json={
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "width": size[0],
                    "height": size[1],
                    "model": model,
                    "steps": steps,
                    "cfg_scale": cfg_scale,
                    "seed": seed,
                    "style_preset": style_preset,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["image"]["url"]
        except httpx.HTTPError as e:
            raise GenerationError(f"Failed to generate image: {str(e)}")

    async def upscale_image(
        self,
        image_url: str,
        scale: int = 2,
        model: str = "real-esrgan-4x",
    ) -> str:
        """Upscale an image"""
        try:
            response = await self.client.post(
                "/images/upscale",
                json={
                    "image_url": image_url,
                    "scale": scale,
                    "model": model,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["image"]["url"]
        except httpx.HTTPError as e:
            raise GenerationError(f"Failed to upscale image: {str(e)}")

    async def enhance_face(
        self,
        image_url: str,
        model: str = "gfpgan",
    ) -> str:
        """Enhance face in an image"""
        try:
            response = await self.client.post(
                "/images/face-enhance",
                json={
                    "image_url": image_url,
                    "model": model,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["image"]["url"]
        except httpx.HTTPError as e:
            raise GenerationError(f"Failed to enhance face: {str(e)}")

    async def apply_style_transfer(
        self,
        image_url: str,
        style: str,
        strength: float = 1.0,
    ) -> str:
        """Apply style transfer to an image"""
        try:
            response = await self.client.post(
                "/images/style-transfer",
                json={
                    "image_url": image_url,
                    "style": style,
                    "strength": strength,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["image"]["url"]
        except httpx.HTTPError as e:
            raise GenerationError(f"Failed to apply style: {str(e)}")

    def _build_map_prompt(
        self,
        theme: str,
        features: list[str],
        terrain: dict,
        is_tactical: bool = True,
    ) -> tuple[str, str]:
        """Build prompt for map generation"""
        base_prompt = f"A detailed {'tactical battle map' if is_tactical else 'campaign map'} "
        base_prompt += f"in {theme} style, featuring {', '.join(features)}. "
        base_prompt += f"The terrain is {terrain['type']} with {terrain.get('details', '')}."
        
        neg_prompt = "text, labels, watermark, signature, blurry, low quality"
        
        return base_prompt, neg_prompt

    def _build_portrait_prompt(
        self,
        character_details: dict,
        theme: str,
        style: dict,
    ) -> tuple[str, str]:
        """Build prompt for portrait generation"""
        base_prompt = f"A {character_details['race']} {character_details['class']} "
        base_prompt += f"in a {style['pose']} pose, wearing {character_details.get('armor', 'clothes')}. "
        base_prompt += f"{style['background']} background with {style['lighting']} lighting. "
        base_prompt += f"Style: {theme}."
        
        if equipment := character_details.get("equipment"):
            base_prompt += f" Equipped with {', '.join(equipment)}."
            
        neg_prompt = "deformed, distorted, low quality, blurry, nsfw"
        
        return base_prompt, neg_prompt

    def _build_item_prompt(
        self,
        item_details: dict,
        theme: str,
        style: dict,
        properties: dict,
    ) -> tuple[str, str]:
        """Build prompt for item image generation"""
        base_prompt = f"A {properties['material']} {item_details['type']} "
        base_prompt += f"viewed from {style['angle']}, with {style['lighting']} lighting "
        base_prompt += f"and {style['detail_level']} detail. "
        
        if magical_effects := properties.get("magical_effects"):
            base_prompt += f"Magical effects: {', '.join(magical_effects)}. "
            
        base_prompt += f"Style: {theme}."
        
        neg_prompt = "text, labels, watermark, blurry, low quality"
        
        return base_prompt, neg_prompt
