"""Test database utilities that mirror production configuration."""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Test database URL
TEST_DATABASE_URL = os.getenv(
    "DATABASE_TEST_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/character_service_test"
)

# Create test engine - uses same configuration as production
engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    poolclass=StaticPool,  # Use static pool for tests to ensure isolation
)

# Create session factory - matches production configuration
TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_test_db():
    """Get test database session - mirrors production get_db dependency."""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_test_db():
    """Initialize test database with schema."""
    from character_service.core.database import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def cleanup_test_db():
    """Clean up test database."""
    from character_service.core.database import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
