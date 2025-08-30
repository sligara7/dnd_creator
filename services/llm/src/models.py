"""
LLM Service Data Models

Pydantic models for request/response data validation.
"""

from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field

class ServiceType(str, Enum):
    """Available services that can request LLM operations."""
    CHARACTER = "character"
    CAMPAIGN = "campaign"
    IMAGE = "image"

class LLMModel(str, Enum):
    """Available LLM models."""
    GPT4 = "gpt-4"
    GPT35 = "gpt-3.5-turbo"
    CLAUDE = "claude-3"
    SDXL = "stable-diffusion-xl"

class TextGenerationRequest(BaseModel):
    """Request model for text generation."""
    service: ServiceType
    prompt: str = Field(..., description="The prompt for text generation")
    context: Dict[str, any] = Field(default_factory=dict,
                                  description="Additional context for generation")
    model: LLMModel = Field(default=LLMModel.GPT4,
                         description="The LLM model to use")
    max_tokens: Optional[int] = Field(default=None,
                                    description="Maximum tokens to generate")
    temperature: float = Field(default=0.7,
                             description="Sampling temperature")

class ImageGenerationRequest(BaseModel):
    """Request model for image generation."""
    service: ServiceType
    prompt: str = Field(..., description="The prompt for image generation")
    style: Dict[str, any] = Field(default_factory=dict,
                               description="Style parameters for generation")
    size: str = Field(default="1024x1024",
                     description="Output image size")
    format: str = Field(default="png",
                       description="Output image format")

class GenerationResponse(BaseModel):
    """Response model for generation requests."""
    content: str = Field(..., description="Generated content (text or image URL)")
    model: str = Field(..., description="Model used for generation")
    usage: Dict[str, int] = Field(default_factory=dict,
                               description="Token/resource usage information")
    metadata: Dict[str, any] = Field(default_factory=dict,
                                  description="Additional generation metadata")
