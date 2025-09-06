"""Image generation task management models."""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Enum as SQLAEnum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSON, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from image.models.base import Base


class TaskStatus(str, Enum):
    """Status of a generation task."""
    PENDING = "pending"  # Task is queued but not started
    IN_PROGRESS = "in_progress"  # Task is actively being processed
    COMPLETED = "completed"  # Task completed successfully
    FAILED = "failed"  # Task failed and won't be retried
    CANCELLED = "cancelled"  # Task was cancelled by user/system


class TaskPriority(str, Enum):
    """Priority levels for generation tasks."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class TaskType(str, Enum):
    """Types of image generation tasks."""
    CHARACTER_PORTRAIT = "character_portrait"
    MAP = "map"
    ITEM = "item"
    OVERLAY = "overlay"
    BATCH = "batch"  # For batch processing parent tasks
    ENHANCEMENT = "enhancement"  # For post-processing tasks


class GenerationTask(Base):
    """Model for tracking image generation tasks."""

    __tablename__ = "generation_tasks"

    # Required by base class but explicitly defined for clarity
    id: Mapped[UUID] = mapped_column(
        PGUUID, primary_key=True, default=uuid4
    )

    # Task metadata
    type: Mapped[TaskType] = mapped_column(
        SQLAEnum(TaskType), nullable=False
    )
    status: Mapped[TaskStatus] = mapped_column(
        SQLAEnum(TaskStatus), nullable=False, default=TaskStatus.PENDING
    )
    priority: Mapped[TaskPriority] = mapped_column(
        SQLAEnum(TaskPriority), nullable=False, default=TaskPriority.NORMAL
    )

    # Task parameters and results
    parameters: Mapped[dict] = mapped_column(
        JSON, nullable=False
    )
    result: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True
    )

    # Processing metadata
    retries: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    max_retries: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )
    progress: Mapped[Optional[float]] = mapped_column(
        Integer, nullable=True  # Percentage complete (0-100)
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Soft delete support (from base class)
    is_deleted: Mapped[bool] = mapped_column(
        default=False, nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True
    )

    # Optional parent task for batch operations
    parent_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID, ForeignKey("generation_tasks.id"), nullable=True
    )
    parent: Mapped[Optional["GenerationTask"]] = relationship(
        "GenerationTask", remote_side=[id], backref="subtasks"
    )

    def __repr__(self) -> str:
        """Return string representation of the task."""
        return (f"<GenerationTask(id={self.id}, type={self.type}, "
                f"status={self.status}, priority={self.priority}>")


class TaskEvent(Base):
    """Model for tracking task lifecycle events."""

    __tablename__ = "task_events"

    # Required by base class but explicitly defined for clarity
    id: Mapped[UUID] = mapped_column(
        PGUUID, primary_key=True, default=uuid4
    )

    # Task reference
    task_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("generation_tasks.id"), nullable=False
    )
    task: Mapped[GenerationTask] = relationship(
        "GenerationTask", backref="events"
    )

    # Event details
    event_type: Mapped[str] = mapped_column(
        String, nullable=False
    )
    details: Mapped[dict] = mapped_column(
        JSON, nullable=False
    )

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    def __repr__(self) -> str:
        """Return string representation of the event."""
        return (f"<TaskEvent(id={self.id}, task_id={self.task_id}, "
                f"event_type={self.event_type}>")
