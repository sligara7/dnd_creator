"""Test fixtures for storage service."""

import asyncio
from datetime import datetime, timezone
from typing import AsyncGenerator, Optional
from uuid import UUID, uuid4
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from storage.core.config import get_settings
from storage.core.database import Base, get_db
from storage.models.asset import Asset, AssetType
from storage.services.asset_service import AssetService


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create database engine for tests."""
    settings = get_settings()
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        future=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests."""
    async_session = sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def asset_service(db_session: AsyncSession) -> AssetService:
    """Create asset service for tests."""
    return AssetService(db_session)


@pytest.fixture
def test_app(db_session: AsyncSession) -> FastAPI:
    """Create FastAPI test application."""
    from storage.main import app
    
    async def get_test_db():
        yield db_session
    
    app.dependency_overrides[get_db] = get_test_db
    return app


@pytest.fixture
async def test_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    async with AsyncClient(
        app=test_app,
        base_url="http://test",
        headers={"X-API-Key": "test"}
    ) as client:
        yield client


@pytest.fixture
def test_asset() -> Asset:
    """Create test asset."""
    return Asset(
        id=uuid4(),
        name="test.png",
        service="test_service",
        owner_id=uuid4(),
        asset_type=AssetType.IMAGE,
        s3_key="test/123/test.png",
        s3_url="https://storage.test.com/test.png",
        size=1024,
        content_type="image/png",
        checksum="sha256:123",
        current_version=1,
        tags=["test"],
        metadata={"test": "data"},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
async def db_asset(db_session: AsyncSession, test_asset: Asset) -> Asset:
    """Create test asset in database."""
    db_session.add(test_asset)
    await db_session.commit()
    await db_session.refresh(test_asset)
    return test_asset