"""Test fixtures for model tests."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from campaign_service.models.base import Base


@pytest.fixture
async def test_db() -> AsyncSession:
    """Create a test database session."""
    # Use PostgreSQL for tests
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/test_campaign",
        echo=False,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Create and yield a test session
    async with async_session() as session:
        yield session
        await session.rollback()
