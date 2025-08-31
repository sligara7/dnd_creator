"""Test Configuration and Fixtures"""

import asyncio
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.core.database import get_db, Base
from character_service.main import app as character_app
from tests.utils.db import init_test_db, cleanup_test_db, get_test_db, TestingSessionLocal

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def init_db():
    """Initialize test database schema."""
    await init_test_db()
    yield
    await cleanup_test_db()

@pytest.fixture
def app() -> FastAPI:
    """Create test FastAPI application with production-like DI."""
    async def override_get_db():
        """Mirror production get_db behavior exactly."""
        async with TestingSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    character_app.dependency_overrides[get_db] = override_get_db
    yield character_app
    character_app.dependency_overrides.clear()

@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create test client."""
    return TestClient(app)

@pytest.fixture
async def db_session(init_db) -> AsyncSession:
    """Database session fixture for repository tests only.
    
    API tests should not use this - they should create/read via HTTP endpoints
    to match production behavior.
    """
    async with TestingSessionLocal() as session:
        async with session.begin():
            yield session
            await session.rollback()
