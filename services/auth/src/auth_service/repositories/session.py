"""Session repository for database operations."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.models.session import Session
from auth_service.repositories.base import BaseRepository


class SessionRepository(BaseRepository[Session]):
    """Repository for Session database operations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize session repository."""
        super().__init__(db, Session)
    
    async def create(
        self,
        user_id: UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_id: Optional[str] = None
    ) -> Session:
        """Create a new session."""
        return await super().create(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            device_id=device_id
        )
    
    async def invalidate(self, session_id: UUID) -> bool:
        """Invalidate a session."""
        return await self.soft_delete(session_id)
    
    async def invalidate_all_user_sessions(self, user_id: UUID) -> int:
        """Invalidate all sessions for a user."""
        # Stub implementation
        return 0
