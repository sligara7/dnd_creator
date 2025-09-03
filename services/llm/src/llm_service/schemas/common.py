from datetime import datetime
from enum import Enum
from typing import Dict, Generic, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Status of a queued job."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Theme(BaseModel):
    """Theme configuration for content generation."""
    genre: str = Field(description="Genre for content generation (e.g., fantasy, sci-fi)")
    tone: str = Field(description="Tone for content (e.g., serious, humorous)")
    style: str = Field(description="Style of the content (e.g., descriptive, concise)")


class ContentMetadata(BaseModel):
    """Metadata for generated content."""
    request_id: UUID = Field(description="Unique identifier for the request")
    source_service: str = Field(description="Service that initiated the request")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    model_used: str = Field(description="Model used for generation")
    prompt_used: str = Field(description="Prompt used for generation")
    settings_used: Dict = Field(description="Settings used for generation")


T = TypeVar("T")


class JobResult(BaseModel, Generic[T]):
    """Result of a job execution."""
    job_id: UUID = Field(description="Unique identifier for the job")
    status: JobStatus
    result: Optional[T] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    metadata: Optional[ContentMetadata] = None


class QueueStats(BaseModel):
    """Queue statistics."""
    active: int = Field(description="Number of active jobs")
    waiting: int = Field(description="Number of waiting jobs")
    completed: int = Field(description="Number of completed jobs")


class APIErrorDetail(BaseModel):
    """Detailed error information."""
    code: str = Field(description="Error code")
    message: str = Field(description="Error message")
    details: Dict = Field(description="Additional error details")
