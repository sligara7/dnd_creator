"""Database session management.

This module provides utilities for managing SQLAlchemy database sessions
in the character service.
"""

from functools import lru_cache
import logging
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from ..core.config import get_settings

logger = logging.getLogger(__name__)

@lru_cache()
def get_engine() -> AsyncEngine:
    """Get SQLAlchemy engine instance.
    
    Returns:
        Async SQLAlchemy engine
    """
    settings = get_settings()
    
    # Create engine with appropriate URL
    if settings.is_sqlite:
        engine = create_async_engine(
            settings.effective_database_url,
            echo=settings.database_echo,
            # SQLite-specific settings
            connect_args={"check_same_thread": False},
            poolclass=settings.pool_class,
        )
    else:
        engine = create_async_engine(
            settings.effective_database_url,
            echo=settings.database_echo,
            # PostgreSQL-specific settings
            pool_size=settings.pool_size,
            max_overflow=settings.max_overflow,
            pool_timeout=settings.pool_timeout,
            pool_recycle=settings.pool_recycle,
        )
        
    logger.info(
        "Created database engine",
        is_sqlite=settings.is_sqlite,
        echo=settings.database_echo,
    )
        
    return engine

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get SQLAlchemy session.
    
    Yields:
        Async SQLAlchemy session
    """
    engine = get_engine()
    
    # Create sessionmaker
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

class DBSessionManager:
    """Session manager for database operations.
    
    This class provides a context manager interface for database sessions
    and transaction management.
    """
    
    def __init__(self):
        """Initialize session manager."""
        self.engine = get_engine()
        self._session_maker = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        self._session: Optional[AsyncSession] = None
        
    async def __aenter__(self) -> AsyncSession:
        """Enter async context and get session.
        
        Returns:
            Active database session
        """
        self._session = self._session_maker()
        return self._session
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context and clean up session.
        
        Args:
            exc_type: Exception type if error occurred
            exc_val: Exception instance if error occurred
            exc_tb: Exception traceback if error occurred
        """
        if self._session:
            if exc_type is not None:
                # Error occurred, rollback
                await self._session.rollback()
                logger.error(
                    "Rolling back database transaction",
                    error=str(exc_val),
                    error_type=exc_type.__name__,
                )
            else:
                # Success, commit
                await self._session.commit()
                
            # Always close session
            await self._session.close()
            self._session = None

class TransactionManager:
    """Transaction manager for atomic operations.
    
    This class provides a context manager interface for managing
    database transactions that should be atomic.
    """
    
    def __init__(self, session: AsyncSession):
        """Initialize transaction manager.
        
        Args:
            session: Active database session
        """
        self.session = session
        self._transaction = None
        
    async def __aenter__(self):
        """Enter async context and start transaction.
        
        Returns:
            Active transaction session
        """
        self._transaction = await self.session.begin_nested()
        return self.session
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context and clean up transaction.
        
        Args:
            exc_type: Exception type if error occurred
            exc_val: Exception instance if error occurred
            exc_tb: Exception traceback if error occurred
        """
        if exc_type is not None:
            # Error occurred, rollback transaction
            await self._transaction.rollback()
            logger.error(
                "Rolling back database transaction",
                error=str(exc_val),
                error_type=exc_type.__name__,
            )
        else:
            # Success, commit transaction
            await self._transaction.commit()

class DatabaseSessionError(Exception):
    """Raised when a database session error occurs."""
    pass

async def get_db_session() -> AsyncSession:
    """Get database session from current request.
    
    Returns:
        Active database session
        
    Raises:
        DatabaseSessionError: If no active session found
    """
    try:
        session = get_session()
        return session
    except Exception as e:
        raise DatabaseSessionError(f"Failed to get database session: {e}")
        
def get_db() -> AsyncSession:
    """FastAPI dependency for database session.
    
    Returns:
        Active database session
    """
    try:
        return get_db_session()
    except Exception as e:
        logger.error("Failed to get database session", error=str(e))
        raise
