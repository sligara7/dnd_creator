"""
Database Connection

Provides database connection and session management.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .config import Settings

settings = Settings()

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True
)

# Create async session factory
AsyncSessionFactory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session.
    
    Use as a FastAPI dependency:
    
    ```python
    @router.get("/items")
    async def get_items(session: AsyncSession = Depends(get_session)):
        ...
    ```
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initialize database schema."""
    from .event_store.models import Base
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
async def close_db():
    """Close database connections."""
    await engine.dispose()
