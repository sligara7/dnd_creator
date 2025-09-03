import asyncio
import base64
from io import BytesIO
import json
from typing import Any, Dict, Optional

import httpx
from PIL import Image
import structlog

from llm_service.core.exceptions import ImageGenerationError
from llm_service.core.settings import Settings
from llm_service.schemas.image import (
    ImageEnhancementRequest,
    ImageModelConfig,
    ImageParameters,
    ImageSize,
    ImageToImageRequest,
    TextToImageRequest,
)


class GetImgAIClient:
    """Client for GetImg.AI API."""

    BASE_URL = "https://api.getimg.ai/v1"
    ENDPOINTS = {
        "text_to_image": "/text-to-image",
        "image_to_image": "/image-to-image",
        "face_enhance": "/face-enhance",
        "upscale": "/upscale",
        "style_transfer": "/style-transfer",
    }

    def __init__(self, settings: Settings, logger: Optional[structlog.BoundLogger] = None) -> None:
        self.settings = settings
        self.logger = logger or structlog.get_logger()

        # Create HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {settings.getimg_ai.api_key.get_secret_value()}",
                "Content-Type": "application/json",
            },
            timeout=settings.getimg_ai.request_timeout,
        )

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()

    def _validate_base64_image(self, image_data: str) -> None:
        """Validate base64 encoded image data."""
        try:
            # Try to decode and open image
            img_data = base64.b64decode(image_data)
            Image.open(BytesIO(img_data))
        except Exception as e:
            raise ValueError(f"Invalid base64 image data: {str(e)}")

    async def _handle_response(
        self, response: httpx.Response, error_context: str
    ) -> Dict[str, Any]:
        """Handle API response and errors."""
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise ImageGenerationError(
                message=f"Invalid response format: {error_context}",
                details={"status_code": response.status_code},
            )

        if response.status_code != 200:
            raise ImageGenerationError(
                message=f"API error: {error_context}",
                details={
                    "status_code": response.status_code,
                    "error": data.get("error", str(data)),
                },
            )

        return data

    async def _retry_request(
        self, func: Any, *args: Any, max_retries: int = 3, **kwargs: Any
    ) -> Any:
        """Retry request with exponential backoff."""
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except ImageGenerationError as e:
                if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                    delay = 2 ** attempt
                    self.logger.warning(
                        "rate_limit_retry",
                        attempt=attempt + 1,
                        delay=delay,
                        error=str(e),
                    )
                    await asyncio.sleep(delay)
                    continue
                raise
            except Exception as e:
                if attempt < max_retries - 1:
                    delay = 2 ** attempt
                    self.logger.warning(
                        "request_retry",
                        attempt=attempt + 1,
                        delay=delay,
                        error=str(e),
                    )
                    await asyncio.sleep(delay)
                    continue
                raise

        raise ImageGenerationError(
            message="Max retries exceeded",
            details={"max_retries": max_retries},
        )

    async def generate_image(self, request: TextToImageRequest) -> str:
        """Generate image from text prompt."""
        payload = {
            "prompt": request.prompt,
            "model": request.model.model_dump(),
            "negative_prompt": request.parameters.negative_prompt,
            "width": request.size.width,
            "height": request.size.height,
            "steps": request.model.steps,
            "cfg_scale": request.model.cfg_scale,
            "style_preset": request.parameters.style_preset,
            "seed": request.parameters.seed,
        }

        response = await self._retry_request(
            self.client.post,
            self.ENDPOINTS["text_to_image"],
            json=payload,
        )

        data = await self._handle_response(response, "text-to-image")
        return data["image"]

    async def transform_image(self, request: ImageToImageRequest) -> str:
        """Transform existing image."""
        # Validate source image
        self._validate_base64_image(request.source_image)

        payload = {
            "image": request.source_image,
            "prompt": request.prompt,
            "model": request.model.model_dump(),
            "negative_prompt": request.parameters.negative_prompt,
            "steps": request.model.steps,
            "cfg_scale": request.model.cfg_scale,
            "style_preset": request.parameters.style_preset,
            "seed": request.parameters.seed,
            "strength": request.strength,
        }

        response = await self._retry_request(
            self.client.post,
            self.ENDPOINTS["image_to_image"],
            json=payload,
        )

        data = await self._handle_response(response, "image-to-image")
        return data["image"]

    async def enhance_faces(self, image: str) -> str:
        """Enhance faces in image."""
        # Validate image
        self._validate_base64_image(image)

        response = await self._retry_request(
            self.client.post,
            self.ENDPOINTS["face_enhance"],
            json={"image": image},
        )

        data = await self._handle_response(response, "face-enhance")
        return data["image"]

    async def upscale_image(self, image: str, scale: float = 2.0) -> str:
        """Upscale image resolution."""
        # Validate image
        self._validate_base64_image(image)

        response = await self._retry_request(
            self.client.post,
            self.ENDPOINTS["upscale"],
            json={"image": image, "scale": scale},
        )

        data = await self._handle_response(response, "upscale")
        return data["image"]

    async def transfer_style(
        self, image: str, style: str, strength: float = 0.8
    ) -> str:
        """Apply style transfer to image."""
        # Validate image
        self._validate_base64_image(image)

        response = await self._retry_request(
            self.client.post,
            self.ENDPOINTS["style_transfer"],
            json={
                "image": image,
                "style": style,
                "strength": strength,
            },
        )

        data = await self._handle_response(response, "style-transfer")
        return data["image"]

    async def enhance_image(self, request: ImageEnhancementRequest) -> str:
        """Apply requested enhancements to image."""
        # Start with original image
        result = request.image

        for enhancement in request.enhancements:
            if enhancement == "face_fix":
                result = await self.enhance_faces(result)
            elif enhancement == "upscale":
                result = await self.upscale_image(
                    result,
                    scale=request.parameters.upscale_factor or 2.0,
                )
            elif enhancement == "style_transfer":
                if not request.parameters.style_preset:
                    raise ValueError("Style preset required for style transfer")
                result = await self.transfer_style(
                    result,
                    style=request.parameters.style_preset,
                    strength=request.parameters.strength or 0.8,
                )

        return result

    def create_thumbnail(
        self, image: str, size: tuple[int, int] = (256, 256)
    ) -> str:
        """Create thumbnail from base64 image."""
        try:
            # Decode base64 image
            img_data = base64.b64decode(image)
            img = Image.open(BytesIO(img_data))

            # Convert to RGB if needed
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # Save to bytes
            output = BytesIO()
            img.save(output, format="JPEG", quality=85)
            output.seek(0)

            # Encode as base64
            return base64.b64encode(output.read()).decode("utf-8")

        except Exception as e:
            self.logger.error("thumbnail_creation_failed", error=str(e))
            raise ImageGenerationError(
                message="Failed to create thumbnail",
                details={"error": str(e)},
            )
