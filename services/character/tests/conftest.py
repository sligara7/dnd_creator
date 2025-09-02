"""Test configuration and fixtures."""
import asyncio
import os
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from rodi import Container

from character_service.api.v2.dependencies import get_container
from character_service.api.v2.models import (
    CharacterCreate,
    InventoryItemCreate,
    JournalEntryCreate,
)
from character_service.di.container import setup_test_di
from character_service.domain.models import CharacterData
from character_service.infrastructure.database import (
    get_session,
)

from character_service.config import Settings, get_settings
from character_service.db.base import Base
from character_service.db.session import get_session
from character_service.main import create_application

# Test database URL - ensure we use asyncpg driver
    db_url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/character_test",
    )
    TEST_DB_URL = db_url


# Settings override for testing
@pytest.fixture(scope="session")
def settings() -> Settings:
    """Override settings for testing."""
    return Settings(
        DATABASE_URL=TEST_DB_URL,
        ENVIRONMENT="test",
        DEBUG=True,
        TESTING=True,
    )


# Database setup
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for testing."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def db_engine(settings: Settings) -> AsyncEngine:
    """Create database engine."""
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
        pool_size=5,
        max_overflow=10,
    )
    return engine

@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_db(db_engine: AsyncEngine) -> AsyncGenerator[None, None]:
    """Initialize database tables."""
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def async_session_maker(db_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create session factory."""
    return async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


@pytest_asyncio.fixture(scope="function")
async def db_session(
    async_session_maker: async_sessionmaker[AsyncSession],
    initialize_db: None,
) -> AsyncGenerator[AsyncSession, None]:
    """Create database session."""
    async with async_session_maker() as session:
        yield session
        await session.rollback()


# Application setup
@pytest.fixture(scope="session")
def di_container(settings: Settings, async_session_maker: async_sessionmaker[AsyncSession]) -> Container:
    """Create dependency injection container for testing."""
    container = setup_test_di()
    return container

@pytest.fixture(scope="session")
def app(settings: Settings, di_container: Container) -> FastAPI:
    """Create FastAPI application for testing."""
    app = create_application()

    # Override dependencies
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_container] = lambda: di_container
    app.dependency_overrides[get_session] = lambda: get_session(di_container)

    return app


@pytest_asyncio.fixture(scope="function")
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# Test data factories
@pytest.fixture
def random_uuid() -> str:
    """Generate random UUID for testing."""
    return str(uuid4())

@pytest.fixture
def test_character_data() -> CharacterCreate:
    """Create test character data."""
    return CharacterCreate(
        name="Test Character",
        theme="traditional",
        user_id=uuid4(),
        campaign_id=uuid4(),
        character_data=CharacterData.create_default(),
    )

@pytest.fixture
def test_inventory_item_data() -> InventoryItemCreate:
    """Create test inventory item data."""
    return InventoryItemCreate(
        item_data={
            "name": "Test Item",
            "type": "weapon",
            "weight": 2,
            "cost": {"gold": 1, "silver": 0, "copper": 0},
            "damage": {
                "type": "slashing",
                "dice": {"count": 1, "size": 8},
            },
            "properties": ["versatile"],
        },
        quantity=1,
        equipped=False,
        container=None,
        notes="Test notes",
    )

@pytest.fixture
def test_journal_entry_data() -> JournalEntryCreate:
    """Create test journal entry data."""
    return JournalEntryCreate(
        entry_type="session_log",
        title="Test Entry",
        content="Test content",
        session_number=1,
    )


# Service fixtures
@pytest.fixture
def character_service(di_container: Container):
    """Get character service."""
    return di_container.resolve("CharacterService")

@pytest.fixture
def inventory_service(di_container: Container):
    """Get inventory service."""
    return di_container.resolve("InventoryService")

@pytest.fixture
def journal_service(di_container: Container):
    """Get journal service."""
    return di_container.resolve("JournalService")

@pytest.fixture
def theme_service(di_container: Container):
    """Get theme service."""
    return di_container.resolve("ThemeService")

# Database fixtures for specific entities
@pytest_asyncio.fixture(scope="function")
async def clean_db(db_session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Provide clean database session."""
    yield db_session
    # Clean up any data created during the test
    for table in reversed(Base.metadata.sorted_tables):
        await db_session.execute(table.delete())
    await db_session.commit()
