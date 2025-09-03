from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from llm_service.core.settings import Settings


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


class Database:
    """Database connection manager."""
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    def init(self) -> None:
        """Initialize database connection."""
        if not self.engine:
            self.engine = create_async_engine(
                str(self.settings.database.dsn),
                echo=self.settings.debug,
                pool_size=self.settings.database.max_pool_size,
                max_overflow=self.settings.database.min_pool_size,
                pool_recycle=self.settings.database.pool_recycle_seconds,
            )
            self._session_factory = async_sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
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

        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except:
                await session.rollback()
                raise
            finally:
                await session.close()


def get_db() -> Database:
    """Get database instance."""
    settings = Settings()
    db = Database(settings)
    db.init()
    return db
