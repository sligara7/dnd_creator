"""Schemas for the LLM service."""
from llm_service.schemas.common import (
    APIErrorDetail,
    ContentMetadata,
    JobResult,
    JobStatus,
    QueueStats,
    Theme,
)
from llm_service.schemas.image import (
    GeneratedImage,
    ImageEnhancementRequest,
    ImageEnhancementType,
    ImageGenerationResponse,
    ImageJobResult,
    ImageModelConfig,
    ImageParameters,
    ImageSize,
    ImageToImageRequest,
    ImageType,
    TextToImageRequest,
)
from llm_service.schemas.text import (
    CampaignContext,
    CharacterContext,
    GeneratedText,
    ModelConfig,
    TextGenerationRequest,
    TextGenerationResponse,
    TextJobResult,
    TextType,
)
from llm_service.schemas.theme import (
    TextThemeRequest,
    TextThemeResponse,
    ThemePreset,
    ThemePresetList,
    ThemeStatistics,
    VisualThemeRequest,
    VisualThemeResponse,
)

__all__ = [
    # Common
    "APIErrorDetail",
    "ContentMetadata",
    "JobResult",
    "JobStatus",
    "QueueStats",
    "Theme",
    # Image
    "GeneratedImage",
    "ImageEnhancementRequest",
    "ImageEnhancementType",
    "ImageGenerationResponse",
    "ImageJobResult",
    "ImageModelConfig",
    "ImageParameters",
    "ImageSize",
    "ImageToImageRequest",
    "ImageType",
    "TextToImageRequest",
    # Text
    "CampaignContext",
    "CharacterContext",
    "GeneratedText",
    "ModelConfig",
    "TextGenerationRequest",
    "TextGenerationResponse",
    "TextJobResult",
    "TextType",
    # Theme
    "TextThemeRequest",
    "TextThemeResponse",
    "ThemePreset",
    "ThemePresetList",
    "ThemeStatistics",
    "VisualThemeRequest",
    "VisualThemeResponse",
]
