"""User repository for database operations."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, or_, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth_service.models.user import User, UserStatus
from auth_service.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User database operations."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize user repository.
        
        Args:
            db: Database session
        """
        super().__init__(db, User)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User if found, None otherwise
        """
        query = select(User).where(
            and_(
                User.username == username,
                User.is_deleted == False
            )
        ).options(
            selectinload(User.roles),
            selectinload(User.sessions),
            selectinload(User.api_keys)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: Email to search for
            
        Returns:
            User if found, None otherwise
        """
        query = select(User).where(
            and_(
                User.email == email,
                User.is_deleted == False
            )
        ).options(
            selectinload(User.roles),
            selectinload(User.sessions),
            selectinload(User.api_keys)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_username_or_email(self, username_or_email: str) -> Optional[User]:
        """
        Get user by username or email.
        
        Args:
            username_or_email: Username or email to search for
            
        Returns:
            User if found, None otherwise
        """
        query = select(User).where(
            and_(
                or_(
                    User.username == username_or_email,
                    User.email == username_or_email
                ),
                User.is_deleted == False
            )
        ).options(
            selectinload(User.roles),
            selectinload(User.sessions),
            selectinload(User.api_keys)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_reset_token(self, reset_token: str) -> Optional[User]:
        """
        Get user by password reset token.
        
        Args:
            reset_token: Password reset token
            
        Returns:
            User if found, None otherwise
        """
        query = select(User).where(
            and_(
                User.password_reset_token == reset_token,
                User.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_verification_token(self, verification_token: str) -> Optional[User]:
        """
        Get user by email verification token.
        
        Args:
            verification_token: Email verification token
            
        Returns:
            User if found, None otherwise
        """
        query = select(User).where(
            and_(
                User.email_verification_token == verification_token,
                User.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_active_users(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[User]:
        """
        Get active users.
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            List of active users
        """
        query = select(User).where(
            and_(
                User.status == UserStatus.ACTIVE,
                User.is_deleted == False
            )
        ).limit(limit).offset(offset).options(
            selectinload(User.roles)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_users_by_role(self, role_name: str) -> List[User]:
        """
        Get users with a specific role.
        
        Args:
            role_name: Name of the role
            
        Returns:
            List of users with the role
        """
        query = select(User).join(User.roles).where(
            and_(
                User.is_deleted == False,
                User.roles.any(name=role_name)
            )
        ).options(
            selectinload(User.roles)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def search_users(
        self,
        search_term: str,
        limit: int = 50
    ) -> List[User]:
        """
        Search users by username, email, or full name.
        
        Args:
            search_term: Search term
            limit: Maximum number of results
            
        Returns:
            List of matching users
        """
        search_pattern = f"%{search_term}%"
        
        query = select(User).where(
            and_(
                or_(
                    User.username.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    User.full_name.ilike(search_pattern)
                ),
                User.is_deleted == False
            )
        ).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_last_login(
        self,
        user_id: UUID,
        ip_address: Optional[str] = None
    ) -> bool:
        """
        Update user's last login time and IP.
        
        Args:
            user_id: User's UUID
            ip_address: Login IP address
            
        Returns:
            True if updated successfully
        """
        query = update(User).where(
            and_(
                User.id == user_id,
                User.is_deleted == False
            )
        ).values(
            last_login=datetime.utcnow(),
            last_login_ip=ip_address,
            updated_at=datetime.utcnow()
        )
        
        result = await self.db.execute(query)
        return result.rowcount > 0
    
    async def lock_user(
        self,
        user_id: UUID,
        locked_until: datetime
    ) -> bool:
        """
        Lock user account until specified time.
        
        Args:
            user_id: User's UUID
            locked_until: Time until account is locked
            
        Returns:
            True if locked successfully
        """
        query = update(User).where(
            and_(
                User.id == user_id,
                User.is_deleted == False
            )
        ).values(
            locked_until=locked_until,
            updated_at=datetime.utcnow()
        )
        
        result = await self.db.execute(query)
        return result.rowcount > 0
    
    async def unlock_user(self, user_id: UUID) -> bool:
        """
        Unlock user account.
        
        Args:
            user_id: User's UUID
            
        Returns:
            True if unlocked successfully
        """
        query = update(User).where(
            and_(
                User.id == user_id,
                User.is_deleted == False
            )
        ).values(
            locked_until=None,
            failed_login_attempts=0,
            updated_at=datetime.utcnow()
        )
        
        result = await self.db.execute(query)
        return result.rowcount > 0
    
    async def verify_email(self, user_id: UUID) -> bool:
        """
        Mark user's email as verified.
        
        Args:
            user_id: User's UUID
            
        Returns:
            True if verified successfully
        """
        query = update(User).where(
            and_(
                User.id == user_id,
                User.is_deleted == False
            )
        ).values(
            email_verified=True,
            email_verification_token=None,
            status=UserStatus.ACTIVE,
            updated_at=datetime.utcnow()
        )
        
        result = await self.db.execute(query)
        return result.rowcount > 0
    
    async def count_active_users(self) -> int:
        """
        Count total active users.
        
        Returns:
            Number of active users
        """
        query = select(func.count(User.id)).where(
            and_(
                User.status == UserStatus.ACTIVE,
                User.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar() or 0
