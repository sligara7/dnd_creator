"""Database connection and session management."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from auth_service.core.config import settings


class DatabaseManager:
    """Database connection manager."""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize database manager."""
        self.database_url = database_url or settings.get_database_url
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker] = None
    
    async def initialize(self) -> None:
        """Initialize database engine and session factory."""
        # Create async engine with proper configuration
        self.engine = create_async_engine(
            self.database_url.replace("postgresql://", "postgresql+asyncpg://"),
            echo=settings.DEBUG,
            future=True,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,
        )
        
        # Create session factory
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    
    async def close(self) -> None:
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.session_factory = None
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session."""
        if not self.session_factory:
            await self.initialize()
        
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> bool:
        """Check database health."""
        try:
            async with self.get_session() as session:
                result = await session.execute("SELECT 1")
                return result.scalar() == 1
        except Exception:
            return False


# Create global database manager instance
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with db_manager.get_session() as session:
        yield session


async def init_database() -> None:
    """Initialize database (create tables, etc.)."""
    from auth_service.models.base import Base
    
    # Import all models to ensure they're registered
    from auth_service.models import (
        User,
        Role,
        Permission,
        Session,
        ApiKey,
        AuditLog,
    )
    
    # Create all tables
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_database() -> None:
    """Seed database with initial data."""
    from auth_service.models.role import SYSTEM_ROLES, SYSTEM_PERMISSIONS
    from auth_service.repositories.role import RoleRepository
    
    async with db_manager.get_session() as session:
        role_repo = RoleRepository(session)
        
        # Create system permissions
        for perm_data in SYSTEM_PERMISSIONS:
            from auth_service.models.role import Permission
            perm = Permission(**perm_data)
            session.add(perm)
        
        # Create system roles
        for role_data in SYSTEM_ROLES:
            from auth_service.models.role import Role
            role = Role(**role_data)
            
            # Assign permissions based on role
            if role.name == "admin":
                # Admin gets all permissions
                perms = await session.execute(
                    "SELECT * FROM permissions"
                )
                role.permissions = perms.scalars().all()
            elif role.name == "dm":
                # DM gets campaign and character permissions
                perms = await session.execute(
                    "SELECT * FROM permissions WHERE resource IN ('campaign', 'character', 'image')"
                )
                role.permissions = perms.scalars().all()
            elif role.name == "player":
                # Player gets own character permissions
                perms = await session.execute(
                    "SELECT * FROM permissions WHERE resource = 'character' AND scope = 'own'"
                )
                role.permissions = perms.scalars().all()
            
            session.add(role)
        
        await session.commit()
