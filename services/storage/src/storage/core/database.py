"""Database configuration and session management."""

from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from storage.core.config import settings


# Create base class for models
Base = declarative_base()


class DatabaseManager:
    """Manage database connections and sessions."""

    def __init__(self, database_url: Optional[str] = None):
        """Initialize database manager."""
        self.database_url = database_url or settings.database_url
        self._engine: Optional[AsyncEngine] = None
        self._sessionmaker: Optional[async_sessionmaker] = None

    async def init(self) -> None:
        """Initialize database engine and session maker."""
        # Create engine with appropriate pool settings
        if settings.is_testing:
            # Use NullPool for testing to avoid connection issues
            self._engine = create_async_engine(
                self.database_url,
                echo=settings.database_echo,
                future=True,
                poolclass=NullPool,
            )
        else:
            self._engine = create_async_engine(
                self.database_url,
                echo=settings.database_echo,
                future=True,
                pool_size=settings.database_pool_size,
                max_overflow=settings.database_max_overflow,
                pool_timeout=30,
                pool_recycle=1800,
            )

        # Create session maker
        self._sessionmaker = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    async def close(self) -> None:
        """Close database connections."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None

    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        """Get database session as context manager."""
        if not self._sessionmaker:
            await self.init()

        async with self._sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    @asynccontextmanager
    async def begin_nested(self) -> AsyncIterator[AsyncSession]:
        """Begin nested transaction for testing."""
        if not self._sessionmaker:
            await self.init()

        async with self._sessionmaker() as session:
            async with session.begin_nested():
                yield session

    async def create_tables(self) -> None:
        """Create all database tables."""
        if not self._engine:
            await self.init()

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        """Drop all database tables."""
        if not self._engine:
            await self.init()

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


# Global database manager instance
db_manager = DatabaseManager()


async def get_db() -> AsyncIterator[AsyncSession]:
    """Dependency for getting database session."""
    async with db_manager.get_session() as session:
        yield session
