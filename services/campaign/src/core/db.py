"""Database connection and session management."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.core.settings import settings


class Base(DeclarativeBase):
    """Base class for all models."""


class Database:
    """Database connection manager."""

    def __init__(self) -> None:
        self.engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    def init(self) -> None:
        """Initialize database connection."""
        if not self.engine:
            self.engine = create_async_engine(
                str(settings.database.dsn),
                echo=settings.database.echo,
                pool_size=settings.database.max_pool_size,
                max_overflow=settings.database.min_pool_size,
            )
            self._session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

    async def close(self) -> None:
        """Close database connection."""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self._session_factory = None

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session."""
        if not self._session_factory:
            raise RuntimeError("Database not initialized")

        session: AsyncSession = self._session_factory()
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()


# Global database instance
db = Database()

# Initialize database on import
db.init()
