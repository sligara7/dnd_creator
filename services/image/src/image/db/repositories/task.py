"""Task repository for database operations."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Select

from image.models.generation import GenerationTask, TaskPriority, TaskStatus


class TaskRepository:
    """Repository for managing task records in the database."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    def get_query(self) -> Select:
        """Get base query for tasks.

        Returns:
            SQLAlchemy select query
        """
        return select(GenerationTask).where(GenerationTask.is_deleted == False)

    async def get_by_id(
        self,
        task_id: UUID,
        query: Optional[Select] = None
    ) -> Optional[GenerationTask]:
        """Get task by ID.

        Args:
            task_id: Task ID
            query: Optional base query to use

        Returns:
            Task if found, otherwise None
        """
        if query is None:
            query = self.get_query()

        query = query.where(GenerationTask.id == task_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_ids(
        self,
        task_ids: List[UUID],
        query: Optional[Select] = None
    ) -> List[GenerationTask]:
        """Get multiple tasks by IDs.

        Args:
            task_ids: List of task IDs
            query: Optional base query to use

        Returns:
            List of found tasks
        """
        if query is None:
            query = self.get_query()

        query = query.where(GenerationTask.id.in_(task_ids))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(
        self,
        type: str,
        parameters: dict,
        priority: TaskPriority = TaskPriority.NORMAL,
        parent_id: Optional[UUID] = None,
    ) -> GenerationTask:
        """Create a new task.

        Args:
            type: Task type
            parameters: Task parameters
            priority: Task priority level
            parent_id: Optional parent task ID

        Returns:
            The created task
        """
        task = GenerationTask(
            type=type,
            parameters=parameters,
            priority=priority,
            parent_id=parent_id,
            status=TaskStatus.PENDING
        )
        self.session.add(task)
        await self.session.commit()
        return task

    async def update(
        self,
        task_id: UUID,
        **kwargs
    ) -> Optional[GenerationTask]:
        """Update task fields.

        Args:
            task_id: Task ID to update
            **kwargs: Fields to update

        Returns:
            Updated task if found, otherwise None
        """
        task = await self.get_by_id(task_id)
        if not task:
            return None

        for key, value in kwargs.items():
            setattr(task, key, value)

        await self.session.commit()
        return task

    async def delete(self, task_id: UUID) -> bool:
        """Soft delete a task.

        Args:
            task_id: Task ID to delete

        Returns:
            True if task was found and deleted, False otherwise
        """
        task = await self.get_by_id(task_id)
        if not task:
            return False

        task.soft_delete()
        await self.session.commit()
        return True

    async def get_subtasks(
        self,
        parent_id: UUID,
        include_completed: bool = True
    ) -> List[GenerationTask]:
        """Get all subtasks for a parent task.

        Args:
            parent_id: Parent task ID
            include_completed: Whether to include completed tasks

        Returns:
            List of subtasks
        """
        query = self.get_query().where(GenerationTask.parent_id == parent_id)
        if not include_completed:
            query = query.where(GenerationTask.status != TaskStatus.COMPLETED)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_by_status(self, status: TaskStatus) -> int:
        """Count tasks with a given status.

        Args:
            status: Task status to count

        Returns:
            Number of tasks with status
        """
        query = self.get_query().where(GenerationTask.status == status)
        result = await self.session.execute(query)
        return len(result.scalars().all())
