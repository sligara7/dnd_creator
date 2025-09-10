"""Test configuration and fixtures."""
import asyncio
import os
from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.models.base import Base
from .utils.db_utils import TestSessionManager

# Use a test database URL - this should be configured in environment
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/dnd_character_test"
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db_manager():
    """Create a test database session manager."""
    manager = TestSessionManager(TEST_DATABASE_URL)
    await manager.init()
    
    # Create all tables
    async with manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield manager
    
    # Drop all tables after tests
    async with manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await manager.close()

@pytest.fixture
async def db_session(db_manager) -> AsyncSession:
    """Create a new database session for a test."""
    async with db_manager as session:
        yield session
