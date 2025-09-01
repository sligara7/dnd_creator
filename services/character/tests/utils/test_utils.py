"""Utility functions and classes for testing."""
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from typing import Any, Optional, Type, TypeVar
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


async def create_test_model(
    session: AsyncSession,
    model_class: Type[ModelType],
    **kwargs: Any,
) -> ModelType:
    """Create a model instance for testing."""
    # Generate UUID if not provided
    if "id" not in kwargs and hasattr(model_class, "id"):
        kwargs["id"] = uuid4()

    # Set timestamps if not provided
    now = datetime.now(timezone.utc)
    if "created_at" not in kwargs and hasattr(model_class, "created_at"):
        kwargs["created_at"] = now
    if "updated_at" not in kwargs and hasattr(model_class, "updated_at"):
        kwargs["updated_at"] = now

    # Set default values for common fields
    if "is_deleted" not in kwargs and hasattr(model_class, "is_deleted"):
        kwargs["is_deleted"] = False
    if "is_active" not in kwargs and hasattr(model_class, "is_active"):
        kwargs["is_active"] = True

    # Create instance
    instance = model_class(**kwargs)
    session.add(instance)
    await session.commit()
    await session.refresh(instance)
    return instance


async def get_model_by_id(
    session: AsyncSession,
    model_class: Type[ModelType],
    model_id: UUID,
    include_deleted: bool = False,
) -> Optional[ModelType]:
    """Get a model instance by ID."""
    query = select(model_class).where(model_class.id == model_id)
    if not include_deleted and hasattr(model_class, "is_deleted"):
        query = query.where(model_class.is_deleted.is_(False))
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def soft_delete_model(
    session: AsyncSession,
    model: ModelType,
) -> None:
    """Soft delete a model instance."""
    if not hasattr(model, "is_deleted"):
        raise ValueError(f"Model {model.__class__.__name__} does not support soft delete")

    model.is_deleted = True
    model.deleted_at = datetime.now(timezone.utc)
    await session.commit()


class AsyncSessionContext:
    """Context manager for database sessions in tests."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self) -> AsyncSession:
        return self.session

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.session.rollback()
