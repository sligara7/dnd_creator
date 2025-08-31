"""Database utilities for testing."""

from typing import AsyncGenerator, Any, Callable
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import Session
from sqlalchemy import event
from contextlib import asynccontextmanager

class TestSessionManager:
    """Manages test database sessions and transactions."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None
        
    async def init(self) -> None:
        """Initialize the test database engine and session factory."""
        self.engine = create_async_engine(
            self.database_url,
            echo=False,
            future=True,
            # Useful settings for testing
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800
        )
        
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False  # Explicit flush for tests
        )
    
    async def cleanup(self) -> None:
        """Cleanup database connections."""
        if self.engine:
            await self.engine.dispose()
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a test session with transaction rollback."""
        if not self.session_factory:
            raise RuntimeError("TestSessionManager not initialized")
            
        async with self.session_factory() as session:
            try:
                yield session
                await session.flush()
                # Don't commit - will be rolled back
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @asynccontextmanager
    async def begin_nested(self) -> AsyncGenerator[AsyncSession, None]:
        """Create a new nested transaction."""
        if not self.session_factory:
            raise RuntimeError("TestSessionManager not initialized")
            
        async with self.session_factory() as session:
            async with session.begin():
                savepoint = await session.begin_nested()
                try:
                    yield session
                except Exception:
                    await savepoint.rollback()
                    raise
                finally:
                    await session.close()

async def run_sync(session: AsyncSession, func: Callable[[Session], Any]) -> Any:
    """Run a synchronous function in async session."""
    return await session.run_sync(func)
