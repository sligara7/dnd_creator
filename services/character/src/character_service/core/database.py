"""Database Configuration"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass

from character_service.core.config import settings

# Convert the database URL to an async URL
async_database_url = settings.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')

# Create async engine with connection pool settings
engine = create_async_engine(
    async_database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    future=True,
    echo=False  # Set to True for SQL query logging
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session."""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
