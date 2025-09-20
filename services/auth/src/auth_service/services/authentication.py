"""Authentication service for user login, logout, and session management."""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from uuid import UUID



from auth_service.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    TokenError,
    ValidationError
)
from auth_service.models.session import Session, SessionStatus
from auth_service.models.user import User, UserStatus
from auth_service.repositories.session import SessionRepository
from auth_service.repositories.user import UserRepository
from auth_service.security.jwt_service import JWTService
from auth_service.security.password import PasswordService
from auth_service.services.audit import AuditService


class AuthenticationService:
    """Service for authentication operations."""
    
    def __init__(
        self,
        db: AsyncSession,
        password_service: Optional[PasswordService] = None,
        jwt_service: Optional[JWTService] = None,
        audit_service: Optional[AuditService] = None
    ):
        """
        Initialize authentication service.
        
        Args:
            db: Database session
            password_service: Password hashing service
            jwt_service: JWT token service
            audit_service: Audit logging service
        """
        self.db = db
        self.user_repo = UserRepository(db)
        self.session_repo = SessionRepository(db)
        
        self.password_service = password_service or PasswordService()
        self.jwt_service = jwt_service or JWTService()
        self.audit_service = audit_service or AuditService(db)
        
        # Security settings
        self.max_login_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
    
    async def login(
        self,
        username: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_id: Optional[str] = None
    ) -> Tuple[str, str, Session]:
        """
        Authenticate user and create session.
        
        Args:
            username: Username or email
            password: Plain text password
            ip_address: Client IP address
            user_agent: Client user agent
            device_id: Optional device identifier
            
        Returns:
            Tuple of (access_token, refresh_token, session)
            
        Raises:
            AuthenticationError: If authentication fails
        """
        # Find user by username or email
        user = await self.user_repo.get_by_username_or_email(username)
        
        if not user:
            # Log failed attempt
            await self.audit_service.log_failed_login(
                username=username,
                ip_address=ip_address,
                reason="User not found"
            )
            raise AuthenticationError("Invalid credentials")
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            await self.audit_service.log_failed_login(
                username=username,
                ip_address=ip_address,
                reason="Account locked",
                user_id=user.id
            )
            raise AuthenticationError("Account is temporarily locked")
        
        # Check account status
        if user.status != UserStatus.ACTIVE:
            await self.audit_service.log_failed_login(
                username=username,
                ip_address=ip_address,
                reason=f"Account status: {user.status}",
                user_id=user.id
            )
            raise AuthenticationError(f"Account is {user.status}")
        
        # Verify password
        if not self.password_service.verify_password(password, user.password_hash):
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            # Lock account if max attempts exceeded
            if user.failed_login_attempts >= self.max_login_attempts:
                user.locked_until = datetime.now(timezone.utc) + self.lockout_duration
                await self.audit_service.log_account_locked(
                    user_id=user.id,
                    ip_address=ip_address,
                    reason="Max login attempts exceeded"
                )
            
            await self.db.commit()
            
            await self.audit_service.log_failed_login(
                username=username,
                ip_address=ip_address,
                reason="Invalid password",
                user_id=user.id
            )
            raise AuthenticationError("Invalid credentials")
        
        # Check if email is verified
        if not user.email_verified:
            await self.audit_service.log_failed_login(
                username=username,
                ip_address=ip_address,
                reason="Email not verified",
                user_id=user.id
            )
            raise AuthenticationError("Email verification required")
        
        # Check if password needs rehashing
        if self.password_service.needs_rehash(user.password_hash):
            user.password_hash = self.password_service.hash_password(password)
            user.password_updated_at = datetime.now(timezone.utc)
        
        # Reset failed attempts
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.now(timezone.utc)
        user.last_login_ip = ip_address
        
        # Create session
        session = await self.session_repo.create(
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            device_id=device_id
        )
        
        # Get user permissions
        permissions = user.get_permissions()
        roles = [role.name for role in user.roles]
        
        # Generate tokens
        access_token = self.jwt_service.generate_access_token(
            user_id=user.id,
            username=user.username,
            roles=roles,
            permissions=permissions,
            session_id=session.id
        )
        
        refresh_token = self.jwt_service.generate_refresh_token(
            user_id=user.id,
            session_id=session.id,
            device_id=device_id
        )
        
        # Store refresh token in session
        session.refresh_token = refresh_token
        
        await self.db.commit()
        
        # Log successful login
        await self.audit_service.log_successful_login(
            user_id=user.id,
            session_id=session.id,
            ip_address=ip_address
        )
        
        return access_token, refresh_token, session
    
    async def logout(
        self,
        access_token: str,
        refresh_token: Optional[str] = None
    ) -> bool:
        """
        Logout user and invalidate session.
        
        Args:
            access_token: Current access token
            refresh_token: Optional refresh token
            
        Returns:
            True if logout successful
        """
        try:
            # Decode access token
            payload = self.jwt_service.verify_token(access_token)
            session_id = UUID(payload.get("session_id"))
            user_id = UUID(payload["sub"])
            
            # Invalidate session
            session = await self.session_repo.get(session_id)
            if session:
                await self.session_repo.invalidate(session_id)
            
            # Revoke tokens
            self.jwt_service.revoke_token(access_token)
            if refresh_token:
                self.jwt_service.revoke_token(refresh_token)
            
            # Log logout
            await self.audit_service.log_logout(
                user_id=user_id,
                session_id=session_id
            )
            
            await self.db.commit()
            return True
            
        except (TokenError, ValueError) as e:
            # Log failed logout attempt
            await self.audit_service.log_event(
                event_type="logout_failed",
                details={"error": str(e)}
            )
            return False
    
    async def refresh_tokens(
        self,
        refresh_token: str,
        ip_address: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Refresh access and refresh tokens.
        
        Args:
            refresh_token: Current refresh token
            ip_address: Client IP address
            
        Returns:
            Tuple of (new_access_token, new_refresh_token)
            
        Raises:
            TokenError: If refresh token is invalid
        """
        # Verify refresh token
        payload = self.jwt_service.verify_token(refresh_token, token_type="refresh")
        
        user_id = UUID(payload["sub"])
        session_id = UUID(payload["session_id"])
        
        # Get session
        session = await self.session_repo.get(session_id)
        if not session or session.status != SessionStatus.ACTIVE:
            raise TokenError("Invalid session")
        
        # Verify session belongs to user
        if session.user_id != user_id:
            await self.audit_service.log_security_event(
                user_id=user_id,
                event_type="session_mismatch",
                details={"session_id": str(session_id)}
            )
            raise TokenError("Session mismatch")
        
        # Get user
        user = await self.user_repo.get(user_id)
        if not user or not user.is_active():
            raise TokenError("User not active")
        
        # Update session
        session.last_activity = datetime.now(timezone.utc)
        session.refresh_count += 1
        
        # Get permissions and roles
        permissions = user.get_permissions()
        roles = [role.name for role in user.roles]
        
        # Generate new tokens
        new_access_token = self.jwt_service.generate_access_token(
            user_id=user.id,
            username=user.username,
            roles=roles,
            permissions=permissions,
            session_id=session.id
        )
        
        new_refresh_token = self.jwt_service.generate_refresh_token(
            user_id=user.id,
            session_id=session.id,
            device_id=payload.get("device_id")
        )
        
        # Update refresh token in session
        session.refresh_token = new_refresh_token
        
        # Revoke old refresh token
        self.jwt_service.revoke_token(refresh_token)
        
        await self.db.commit()
        
        # Log token refresh
        await self.audit_service.log_event(
            event_type="token_refresh",
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address
        )
        
        return new_access_token, new_refresh_token
    
    async def validate_token(
        self,
        token: str,
        required_permissions: Optional[list[str]] = None,
        required_roles: Optional[list[str]] = None
    ) -> dict:
        """
        Validate access token and check permissions.
        
        Args:
            token: Access token to validate
            required_permissions: Required permissions
            required_roles: Required roles
            
        Returns:
            Token payload if valid
            
        Raises:
            TokenError: If token is invalid
            AuthorizationError: If permissions/roles insufficient
        """
        # Verify token
        payload = self.jwt_service.verify_token(token, token_type="access")
        
        # Check session if present
        if "session_id" in payload:
            session_id = UUID(payload["session_id"])
            session = await self.session_repo.get(session_id)
            
            if not session or session.status != SessionStatus.ACTIVE:
                raise TokenError("Invalid session")
            
            # Update last activity
            session.last_activity = datetime.now(timezone.utc)
            await self.db.commit()
        
        # Check required permissions
        if required_permissions:
            user_permissions = set(payload.get("permissions", []))
            required = set(required_permissions)
            
            if not required.issubset(user_permissions):
                missing = required - user_permissions
                raise AuthorizationError(f"Missing permissions: {missing}")
        
        # Check required roles
        if required_roles:
            user_roles = set(payload.get("roles", []))
            required = set(required_roles)
            
            if not required.intersection(user_roles):
                raise AuthorizationError(f"Missing required role: {required_roles}")
        
        return payload
    
    async def initiate_password_reset(
        self,
        email: str,
        ip_address: Optional[str] = None
    ) -> str:
        """
        Initiate password reset process.
        
        Args:
            email: User's email address
            ip_address: Client IP address
            
        Returns:
            Password reset token
        """
        user = await self.user_repo.get_by_email(email)
        
        if not user:
            # Don't reveal if user exists
            return secrets.token_urlsafe(32)
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        
        await self.db.commit()
        
        # Log password reset request
        await self.audit_service.log_event(
            event_type="password_reset_requested",
            user_id=user.id,
            ip_address=ip_address
        )
        
        return reset_token
    
    async def reset_password(
        self,
        reset_token: str,
        new_password: str,
        ip_address: Optional[str] = None
    ) -> bool:
        """
        Reset user password with token.
        
        Args:
            reset_token: Password reset token
            new_password: New password
            ip_address: Client IP address
            
        Returns:
            True if password reset successful
            
        Raises:
            ValidationError: If token invalid or expired
        """
        user = await self.user_repo.get_by_reset_token(reset_token)
        
        if not user:
            raise ValidationError("Invalid reset token")
        
        if user.password_reset_expires < datetime.now(timezone.utc):
            raise ValidationError("Reset token has expired")
        
        # Hash new password
        user.password_hash = self.password_service.hash_password(new_password)
        user.password_updated_at = datetime.now(timezone.utc)
        user.password_reset_token = None
        user.password_reset_expires = None
        
        # Invalidate all sessions for security
        await self.session_repo.invalidate_all_user_sessions(user.id)
        
        await self.db.commit()
        
        # Log password reset
        await self.audit_service.log_event(
            event_type="password_reset_completed",
            user_id=user.id,
            ip_address=ip_address
        )
        
        return True
