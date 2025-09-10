"""
Shared database utilities and base classes.
"""

import os
from typing import AsyncGenerator, AsyncContextManager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from contextlib import asynccontextmanager

class Base(DeclarativeBase):
    """Base class for all database models."""

class TestSessionManager:
    """Manages database sessions for testing."""
    
    def __init__(self):
        """Initialize the session manager."""
        self.database_url = os.getenv(
            "TEST_DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
        )
        self.engine = None
        self._session_factory = None

    async def init(self) -> None:
        """Initialize the database engine and session factory."""
        try:
            self.engine = create_async_engine(
                self.database_url,
                echo=False,
                future=True,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                # Additional settings for test reliability
                pool_pre_ping=True,  # Verify connections before use
                isolation_level='READ COMMITTED'  # Consistent isolation level
            )
        except Exception as e:
            print(f"Error initializing test database engine: {e}")
            raise

        self._session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )

    @asynccontextmanager
    async def begin_nested(self):
        """Async context manager: yields a session inside a nested transaction."""
        if not self._session_factory:
            await self.init()

        session = self._session_factory()
        outer = await session.begin()
        try:
            await session.begin_nested()
            try:
                yield session
            finally:
                await session.rollback()
        finally:
            await session.close()

    async def cleanup(self) -> None:
        """Clean up database connections."""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self._session_factory = None
