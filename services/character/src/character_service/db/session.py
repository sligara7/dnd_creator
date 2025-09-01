"""Database session module."""
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from character_service.config import get_settings

# Lazily initialized engine and session factory to avoid import-time side effects
_engine = None
_async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def _ensure_async_driver(db_url: str) -> str:
    """Ensure the database URL uses an async driver.

    Prefer asyncpg for PostgreSQL. If the URL is already async, leave it.
    """
    if db_url.startswith("postgresql+asyncpg://"):
        return db_url
    # Normalize common postgres schemes to asyncpg
    if db_url.startswith("postgresql://"):
        return db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if db_url.startswith("postgres://"):
        return db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    return db_url


def _init_engine_and_factory() -> None:
    global _engine, _async_session_factory
    if _engine is not None and _async_session_factory is not None:
        return

    settings = get_settings()
    db_url = _ensure_async_driver(settings.DATABASE_URL)

    _engine = create_async_engine(
        db_url,
        echo=settings.DEBUG,
        future=True,
        pool_size=5,
        max_overflow=10,
    )

    _async_session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session.

    Initializes the engine/session factory lazily so tests can override settings
    before import-time side effects occur.
    """
    if _async_session_factory is None:
        _init_engine_and_factory()
    assert _async_session_factory is not None  # for type checkers
    async with _async_session_factory() as session:
        yield session
