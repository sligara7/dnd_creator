"""
LLM Service Providers

Implementation of text and image generation providers.
"""

import httpx
from typing import Dict, Optional
import structlog
from openai import AsyncOpenAI
from diffusers import StableDiffusionPipeline

from .config import Settings
from .models import LLMModel, GenerationResponse

logger = structlog.get_logger()

class LLMProvider:
    """Central provider for all LLM operations."""
    
    def __init__(self, settings: Settings):
        """Initialize LLM providers with configuration."""
        self.settings = settings
        self.openai_client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.openai_timeout
        )
        
        # Initialize Stable Diffusion
        self.sd_client = httpx.AsyncClient(
            base_url=settings.sd_api_url,
            timeout=settings.sd_timeout
        )
        
        # Initialize rate limiters
        self._setup_rate_limiters()
    
    def _setup_rate_limiters(self):
        """Set up rate limiting for different operations."""
        # TODO: Implement rate limiting with Redis
        pass
    
    async def generate_text(self,
                          prompt: str,
                          context: Dict[str, any],
                          model: Optional[LLMModel] = None) -> GenerationResponse:
        """Generate text using the specified model."""
        model = model or self.settings.openai_model
        
        try:
            # Check rate limits
            # TODO: Implement rate limit checking
            
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": str(context.get("system", ""))},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return GenerationResponse(
                content=response.choices[0].message.content,
                model=model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                metadata={
                    "finish_reason": response.choices[0].finish_reason
                }
            )
            
        except Exception as e:
            logger.error("text_generation_failed",
                        model=model,
                        error=str(e))
            raise
    
    async def generate_image(self,
                           prompt: str,
                           style: Dict[str, any]) -> GenerationResponse:
        """Generate an image using Stable Diffusion."""
        try:
            # Check rate limits
            # TODO: Implement rate limit checking
            
            # Call Stable Diffusion API
            response = await self.sd_client.post("/sdapi/v1/txt2img", json={
                "prompt": prompt,
                "negative_prompt": style.get("negative_prompt", ""),
                "width": int(style.get("width", 1024)),
                "height": int(style.get("height", 1024)),
                "steps": int(style.get("steps", 50)),
                "cfg_scale": float(style.get("cfg_scale", 7.5))
            })
            response.raise_for_status()
            
            result = response.json()
            
            return GenerationResponse(
                content=result["images"][0],  # Base64 encoded image
                model="stable-diffusion-xl",
                usage={
                    "steps": style.get("steps", 50)
                },
                metadata={
                    "parameters": style,
                    "info": result.get("info", {})
                }
            )
            
        except Exception as e:
            logger.error("image_generation_failed",
                        error=str(e))
            raise
    
    async def check_health(self) -> bool:
        """Check if all LLM providers are accessible."""
        try:
            # Check OpenAI
            await self.openai_client.models.list()
            
            # Check Stable Diffusion
            response = await self.sd_client.get("/sdapi/v1/sd-models")
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            logger.error("provider_health_check_failed",
                        error=str(e))
            raise
