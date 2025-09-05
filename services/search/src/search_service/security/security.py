from typing import Dict, List, Optional, Set
from datetime import datetime
import json
from uuid import UUID
from enum import Enum

from fastapi import HTTPException, status, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError

from search_service.core.config import settings
from search_service.security.models import (
    Role,
    Permission,
    AccessLevel,
)


security = HTTPBearer()


class SecurityError(Exception):
    """Base class for security errors"""
    pass


class InvalidTokenError(SecurityError):
    """Raised when a token is invalid"""
    pass


class PermissionDeniedError(SecurityError):
    """Raised when a permission is denied"""
    pass


class SecurityService:
    """Service for handling security operations"""

    def __init__(self):
        """Initialize security service"""
        self.auth_public_key = settings.AUTH_PUBLIC_KEY
        self.encryption_key = settings.ENCRYPTION_KEY

    def verify_token(self, token: str) -> Dict[str, any]:
        """Verify JWT token and return claims"""
        try:
            return jwt.decode(
                token,
                self.auth_public_key,
                algorithms=["RS256"],
            )
        except JWTError as e:
            raise InvalidTokenError(f"Invalid token: {str(e)}")

    def get_user_roles(self, claims: Dict[str, any]) -> Set[Role]:
        """Get user roles from claims"""
        roles = claims.get("roles", [])
        return {Role(role) for role in roles}

    def get_user_permissions(self, roles: Set[Role]) -> Set[Permission]:
        """Get user permissions from roles"""
        permissions = set()
        for role in roles:
            if role == Role.ADMIN:
                permissions.update({
                    Permission.SEARCH_READ,
                    Permission.SEARCH_WRITE,
                    Permission.INDEX_READ,
                    Permission.INDEX_WRITE,
                    Permission.INDEX_DELETE,
                })
            elif role == Role.WRITER:
                permissions.update({
                    Permission.SEARCH_READ,
                    Permission.SEARCH_WRITE,
                    Permission.INDEX_READ,
                    Permission.INDEX_WRITE,
                })
            elif role == Role.READER:
                permissions.update({
                    Permission.SEARCH_READ,
                    Permission.INDEX_READ,
                })
        return permissions

    def get_user_access_levels(self, claims: Dict[str, any]) -> Set[AccessLevel]:
        """Get user access levels from claims"""
        access_levels = claims.get("access_levels", [])
        return {AccessLevel(level) for level in access_levels}

    def check_permission(
        self,
        token: str,
        required_permissions: Set[Permission],
    ) -> None:
        """Check if user has required permissions"""
        try:
            # Verify token and get claims
            claims = self.verify_token(token)

            # Get user roles and permissions
            roles = self.get_user_roles(claims)
            permissions = self.get_user_permissions(roles)

            # Check if user has all required permissions
            if not required_permissions.issubset(permissions):
                missing = required_permissions - permissions
                raise PermissionDeniedError(
                    f"Missing permissions: {', '.join(p.value for p in missing)}"
                )

        except SecurityError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            )

    def filter_documents_by_access(
        self,
        documents: List[Dict],
        access_levels: Set[AccessLevel],
    ) -> List[Dict]:
        """Filter documents based on user's access levels"""
        return [
            doc for doc in documents
            if AccessLevel(doc.get("access_level", "public")) in access_levels
        ]

    async def encrypt_field(self, value: str) -> str:
        """Encrypt sensitive field value"""
        from cryptography.fernet import Fernet
        
        f = Fernet(self.encryption_key)
        return f.encrypt(value.encode()).decode()

    async def decrypt_field(self, value: str) -> str:
        """Decrypt sensitive field value"""
        from cryptography.fernet import Fernet
        
        f = Fernet(self.encryption_key)
        return f.decrypt(value.encode()).decode()

    def get_document_query_filter(
        self,
        access_levels: Set[AccessLevel],
    ) -> Dict:
        """Get Elasticsearch query filter for document access control"""
        return {
            "terms": {
                "access_level": [level.value for level in access_levels]
            }
        }


# FastAPI dependency
async def get_security_service() -> SecurityService:
    """Get security service instance"""
    return SecurityService()


async def get_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    """Get and validate bearer token"""
    return credentials.credentials


async def check_search_permission(
    token: str = Depends(get_token),
    security_service: SecurityService = Depends(get_security_service),
):
    """Check if user has search permission"""
    security_service.check_permission(
        token,
        {Permission.SEARCH_READ}
    )


async def check_index_write_permission(
    token: str = Depends(get_token),
    security_service: SecurityService = Depends(get_security_service),
):
    """Check if user has index write permission"""
    security_service.check_permission(
        token,
        {Permission.INDEX_WRITE}
    )


async def check_index_delete_permission(
    token: str = Depends(get_token),
    security_service: SecurityService = Depends(get_security_service),
):
    """Check if user has index delete permission"""
    security_service.check_permission(
        token,
        {Permission.INDEX_DELETE}
    )
