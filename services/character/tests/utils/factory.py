"""Base test factory classes."""
from datetime import datetime, timezone
from typing import Any, Generic, Type, TypeVar
from uuid import uuid4

import factory
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class AsyncSQLAlchemyModelFactory(factory.Factory, Generic[ModelType]):
    """Base factory for SQLAlchemy models."""

    class Meta:
        abstract = True

    @classmethod
    def _create(
        cls,
        model_class: Type[ModelType],
        *args: Any,
        **kwargs: Any,
    ) -> ModelType:
        """Create a model instance."""
        session: AsyncSession = kwargs.pop("session")
        instance = model_class(*args, **kwargs)
        session.add(instance)
        return instance


class BaseFactory(AsyncSQLAlchemyModelFactory[ModelType]):
    """Base factory with common fields."""

    class Meta:
        abstract = True

    id = factory.LazyFunction(uuid4)
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    is_deleted = False


class SoftDeleteFactory(BaseFactory[ModelType]):
    """Base factory for models with soft delete."""

    class Meta:
        abstract = True

    is_deleted = False
    deleted_at = None


class ActiveModelFactory(BaseFactory[ModelType]):
    """Base factory for models with active status."""

    class Meta:
        abstract = True

    is_active = True
