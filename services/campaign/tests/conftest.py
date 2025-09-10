"""Campaign service test configuration and fixtures."""
import asyncio
from typing import AsyncGenerator, Dict, Optional
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

class TestSessionManager:
    """Manages test database sessions."""

    def __init__(self, database_url: str) -> None:
        """Initialize the test session manager.
        
        Args:
            database_url: The database URL to connect to
        """
        self.database_url = database_url
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    async def init(self) -> None:
        """Initialize the database engine and session factory."""
        self.engine = create_async_engine(
            self.database_url,
            echo=False,
            future=True,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    async def close(self) -> None:
        """Close all database connections."""
        if self.engine:
            await self.engine.dispose()

    def get_session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get the session factory.
        
        Returns:
            The session factory
        
        Raises:
            RuntimeError: If init() has not been called
        """
        if not self.session_factory:
            raise RuntimeError("SessionManager not initialized. Call init() first.")
        return self.session_factory

    async def begin_nested(self) -> AsyncSession:
        """Begin a nested transaction.
        
        Returns:
            An async session with a nested transaction
        """
        if not self.session_factory:
            raise RuntimeError("SessionManager not initialized. Call init() first.")
        session = self.session_factory()
        await session.begin()
        await session.begin_nested()
        return session

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db_manager() -> AsyncGenerator[TestSessionManager, None]:
    """Create a test database session manager.
    
    Yields:
        TestSessionManager instance
    """
    # Use test database URL - this should be configured via environment variable
    database_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/campaign_test"
    manager = TestSessionManager(database_url)
    await manager.init()
    
    # Create all tables before running tests
    from campaign_service.models import Base
    async with manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Clear any existing tables
        await conn.run_sync(Base.metadata.create_all)
    
    yield manager
    await manager.close()

@pytest.fixture(scope="function")
async def test_db(db_manager: TestSessionManager) -> AsyncGenerator[AsyncSession, None]:
    """Create a new database session for a test.
    
    Args:
        db_manager: The test database manager
    
    Yields:
        An async session with an active nested transaction
    """
    session = await db_manager.begin_nested()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()
