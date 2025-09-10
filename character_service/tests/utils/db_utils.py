"""Database utilities for testing."""
from typing import AsyncGenerator, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

class TestSessionManager:
    """Manages database sessions for testing."""
    
    def __init__(self, database_url: str):
        """Initialize the session manager.
        
        Args:
            database_url: The database URL to connect to
        """
        self.database_url = database_url
        self.engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[sessionmaker] = None

    async def init(self) -> None:
        """Initialize the database engine and session factory."""
        self.engine = create_async_engine(
            self.database_url,
            echo=False,
            future=True,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800
        )
        
        self._session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )

    async def close(self) -> None:
        """Close all connections."""
        if self.engine:
            await self.engine.dispose()

    def get_session(self) -> AsyncSession:
        """Get a new session.
        
        Returns:
            AsyncSession: A new database session
        """
        if not self._session_factory:
            raise RuntimeError("Session factory not initialized. Call init() first.")
        return self._session_factory()

    async def __aenter__(self) -> AsyncSession:
        """Enter the async context manager.
        
        Returns:
            AsyncSession: The database session
        """
        self.session = self.get_session()
        await self.session.begin_nested()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager."""
        if exc_type is not None:
            await self.session.rollback()
        await self.session.close()
