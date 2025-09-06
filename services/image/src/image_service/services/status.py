"""Task status tracking and progress reporting."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from image_service.core.config import get_settings
from image_service.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class TaskStatus(str, Enum):
    """Task status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class TaskStage(str, Enum):
    """Task processing stages."""
    QUEUED = "queued"
    STARTING = "starting"
    GENERATING_BASE = "generating_base"
    ENHANCING_FACE = "enhancing_face"
    APPLYING_STYLE = "applying_style"
    PROCESSING_IMAGE = "processing_image"
    SAVING = "saving"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskProgress:
    """Task progress information."""
    task_id: UUID
    status: TaskStatus
    stage: Optional[TaskStage]
    progress: float  # 0-100
    message: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    processing_time: Optional[float]  # seconds
    attempt: int
    error: Optional[str]
    result: Optional[Dict[str, Any]]


class TaskStatusTracker:
    """Task status and progress tracking."""

    def __init__(
        self,
        redis: Redis,
        db: AsyncSession,
        ttl: int = settings.QUEUE_TIMEOUT,
    ):
        """Initialize tracker."""
        self.redis = redis
        self.db = db
        self.ttl = ttl

        # Redis key prefixes
        self.status_prefix = "task:status:"
        self.stage_prefix = "task:stage:"
        self.progress_prefix = "task:progress:"
        self.error_prefix = "task:error:"
        self.result_prefix = "task:result:"

    async def track_task_start(
        self,
        task_id: UUID,
        task_type: str,
    ) -> None:
        """Track task start."""
        now = datetime.utcnow()
        progress = TaskProgress(
            task_id=task_id,
            status=TaskStatus.PROCESSING,
            stage=TaskStage.STARTING,
            progress=0.0,
            message="Task processing started",
            start_time=now,
            end_time=None,
            processing_time=None,
            attempt=1,
            error=None,
            result=None,
        )
        await self._save_progress(progress)

    async def track_task_progress(
        self,
        task_id: UUID,
        stage: TaskStage,
        progress: float,
        message: Optional[str] = None,
    ) -> None:
        """Track task progress."""
        current = await self.get_task_progress(task_id)
        if not current:
            logger.warning("Task not found", task_id=task_id)
            return

        current.stage = stage
        current.progress = progress
        current.message = message or current.message
        await self._save_progress(current)

    async def track_task_completion(
        self,
        task_id: UUID,
        result: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track task completion."""
        current = await self.get_task_progress(task_id)
        if not current:
            logger.warning("Task not found", task_id=task_id)
            return

        now = datetime.utcnow()
        current.status = TaskStatus.COMPLETED
        current.stage = TaskStage.COMPLETED
        current.progress = 100.0
        current.message = "Task completed successfully"
        current.end_time = now
        current.processing_time = (now - current.start_time).total_seconds()
        current.result = result
        await self._save_progress(current)

    async def track_task_failure(
        self,
        task_id: UUID,
        error: str,
        stage: Optional[TaskStage] = None,
        retry: bool = True,
    ) -> None:
        """Track task failure."""
        current = await self.get_task_progress(task_id)
        if not current:
            logger.warning("Task not found", task_id=task_id)
            return

        now = datetime.utcnow()
        current.status = TaskStatus.RETRYING if retry else TaskStatus.FAILED
        current.stage = stage or TaskStage.FAILED
        current.message = "Task failed" if not retry else "Task will be retried"
        current.end_time = now
        current.processing_time = (now - current.start_time).total_seconds()
        current.error = error
        await self._save_progress(current)

    async def get_task_progress(self, task_id: UUID) -> Optional[TaskProgress]:
        """Get task progress."""
        # Check if task exists
        status = await self.redis.get(f"{self.status_prefix}{task_id}")
        if not status:
            return None

        # Get all task data
        async with self.redis.pipeline() as pipe:
            await pipe.get(f"{self.status_prefix}{task_id}")
            await pipe.get(f"{self.stage_prefix}{task_id}")
            await pipe.get(f"{self.progress_prefix}{task_id}")
            await pipe.get(f"{self.error_prefix}{task_id}")
            await pipe.get(f"{self.result_prefix}{task_id}")
            data = await pipe.execute()

        return TaskProgress(
            task_id=task_id,
            status=TaskStatus(data[0].decode()),
            stage=TaskStage(data[1].decode()) if data[1] else None,
            progress=float(data[2] or 0),
            message=None,  # Not stored in Redis
            start_time=datetime.utcnow(),  # Not stored in Redis
            end_time=None,  # Not stored in Redis
            processing_time=None,  # Not stored in Redis
            attempt=1,  # Not stored in Redis
            error=data[3].decode() if data[3] else None,
            result=data[4].decode() if data[4] else None,
        )

    async def get_active_tasks(self) -> List[TaskProgress]:
        """Get all active tasks."""
        # Get all task IDs
        pattern = f"{self.status_prefix}*"
        keys = await self.redis.keys(pattern)
        task_ids = [
            UUID(key.decode().split(":")[-1])
            for key in keys
        ]

        # Get progress for each task
        tasks = []
        for task_id in task_ids:
            progress = await self.get_task_progress(task_id)
            if progress:
                tasks.append(progress)

        return tasks

    async def _save_progress(self, progress: TaskProgress) -> None:
        """Save task progress to Redis."""
        task_id = str(progress.task_id)

        # Save all task data
        async with self.redis.pipeline() as pipe:
            # Status
            await pipe.set(
                f"{self.status_prefix}{task_id}",
                progress.status.value,
                ex=self.ttl,
            )
            # Stage
            if progress.stage:
                await pipe.set(
                    f"{self.stage_prefix}{task_id}",
                    progress.stage.value,
                    ex=self.ttl,
                )
            # Progress
            await pipe.set(
                f"{self.progress_prefix}{task_id}",
                str(progress.progress),
                ex=self.ttl,
            )
            # Error
            if progress.error:
                await pipe.set(
                    f"{self.error_prefix}{task_id}",
                    progress.error,
                    ex=self.ttl,
                )
            # Result
            if progress.result:
                await pipe.set(
                    f"{self.result_prefix}{task_id}",
                    str(progress.result),
                    ex=self.ttl,
                )
            await pipe.execute()
