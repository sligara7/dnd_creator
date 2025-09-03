from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from llm_service.schemas.common import ContentMetadata, JobResult, Theme


class ImageType(str, Enum):
    """Type of image to generate."""
    CHARACTER_PORTRAIT = "character_portrait"
    ITEM_ILLUSTRATION = "item_illustration"
    LOCATION_VISUAL = "location_visual"
    MAP_BACKGROUND = "map_background"
    ENVIRONMENT_SCENE = "environment_scene"
    MAGICAL_EFFECT = "magical_effect"


class ImageSize(BaseModel):
    """Image dimensions."""
    width: int = Field(ge=256, le=2048, description="Image width in pixels")
    height: int = Field(ge=256, le=2048, description="Image height in pixels")


class ImageModelConfig(BaseModel):
    """Configuration for image generation model."""
    name: str = Field("stable-diffusion-v1-5", description="Model to use")
    cfg_scale: float = Field(7.5, ge=1.0, le=30.0, description="Classifier free guidance scale")
    steps: int = Field(30, ge=1, le=150, description="Number of inference steps")


class ImageParameters(BaseModel):
    """Additional parameters for image generation."""
    style_preset: Optional[str] = Field(None, description="Style preset to use")
    seed: Optional[int] = Field(None, description="Random seed for generation")
    negative_prompt: Optional[str] = Field(None, description="Things to exclude from generation")


class ImageEnhancementType(str, Enum):
    """Types of image enhancements."""
    UPSCALE = "upscale"
    FACE_FIX = "face_fix"
    STYLE_TRANSFER = "style_transfer"
    COLOR_CORRECTION = "color_correction"
    DETAIL_ENHANCEMENT = "detail_enhancement"


class EnhancementParameters(BaseModel):
    """Parameters for image enhancement."""
    upscale_factor: Optional[float] = Field(None, ge=1.0, le=4.0)
    face_restore_model: Optional[str] = None
    quality: Optional[str] = None
    preserve_original_size: bool = Field(True)


class TextToImageRequest(BaseModel):
    """Request for text-to-image generation."""
    type: ImageType
    prompt: str = Field(description="Text prompt for image generation")
    size: ImageSize = Field(default_factory=lambda: ImageSize(width=512, height=512))
    model: ImageModelConfig = Field(default_factory=ImageModelConfig)
    parameters: ImageParameters = Field(default_factory=ImageParameters)
    theme: Optional[Theme] = None


class ImageToImageRequest(BaseModel):
    """Request for image-to-image generation."""
    source_image: str = Field(description="Base64 encoded source image")
    prompt: str = Field(description="Text prompt for image modification")
    type: ImageType
    model: ImageModelConfig = Field(default_factory=ImageModelConfig)
    parameters: ImageParameters = Field(default_factory=ImageParameters)
    strength: float = Field(0.8, ge=0.0, le=1.0, description="How much to transform the image")
    preserve_composition: bool = Field(True)


class ImageEnhancementRequest(BaseModel):
    """Request for image enhancement."""
    image: str = Field(description="Base64 encoded image to enhance")
    enhancements: List[ImageEnhancementType]
    parameters: EnhancementParameters = Field(default_factory=EnhancementParameters)


class GeneratedImage(BaseModel):
    """Generated or processed image."""
    image_data: str = Field(description="Base64 encoded image data")
    metadata: ContentMetadata
    image_id: UUID
    parent_image_id: Optional[UUID] = None
    thumbnail: Optional[str] = None
    parameters_used: Dict = Field(description="Parameters used for generation")


class ImageGenerationResponse(BaseModel):
    """Response containing generated image."""
    result: GeneratedImage
    alternative_results: Optional[list[GeneratedImage]] = None


class ImageJobResult(JobResult[GeneratedImage]):
    """Result of an image generation job."""
    pass
