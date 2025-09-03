"""Database models for the LLM service."""
from typing import Any

from llm_service.core.database import Base
from llm_service.models.content import ImageContent, TextContent, Theme
from llm_service.models.job import ImageGenerationJob, Job, TextGenerationJob

__all__ = [
    "Base",
    "Job",
    "TextGenerationJob",
    "ImageGenerationJob",
    "TextContent",
    "ImageContent",
    "Theme",
]

# Tables in insertion order for proper foreign key handling
tables: list[type[Any]] = [
    Theme,
    TextContent,
    ImageContent,
    Job,
    TextGenerationJob,
    ImageGenerationJob,
]
