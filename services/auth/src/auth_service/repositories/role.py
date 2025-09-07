"""Role repository for database operations."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.models.role import Role
from auth_service.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Repository for Role database operations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize role repository."""
        super().__init__(db, Role)
    
    async def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        query = select(Role).where(
            Role.name == name,
            Role.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
