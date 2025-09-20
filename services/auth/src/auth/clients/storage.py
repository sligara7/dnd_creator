"""Storage client for auth service."""
import logging
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

import httpx
from pydantic import BaseModel

from auth.core.config import get_settings
from auth.models.api import (
    ApiKeyCreate,
    ApiKeyResponse,
    ApiKeyUpdate,
    AuditLogCreate,
    AuditLogResponse,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
    SessionCreate,
    SessionResponse,
    SessionUpdate,
    UserCreate,
    UserResponse,
    UserUpdate
)
from auth.core.exceptions import StorageError

logger = logging.getLogger(__name__)

class StorageClient:
    """Client for interacting with the storage service's auth_db."""

    def __init__(self) -> None:
        """Initialize the storage client."""
        self.settings = get_settings()
        self.base_url = f"{self.settings.storage_service_url}/api/v2/auth_db"
        self.timeout = httpx.Timeout(10.0, connect=5.0)
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={"X-Service-Name": "auth_service"}
        )

    async def create_user(self, user: UserCreate) -> UserResponse:
        """Create new user.

        Args:
            user: User creation model

        Returns:
            Created user

        Raises:
            StorageError: If creation fails
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/users",
                json=user.model_dump()
            )
            response.raise_for_status()
            return UserResponse(**response.json())
        except Exception as e:
            logger.exception("Error creating user in storage service")
            raise StorageError(f"User creation failed: {str(e)}")

    async def get_user(self, user_id: UUID) -> Optional[UserResponse]:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User if found, None otherwise

        Raises:
            StorageError: If retrieval fails
        """
        try:
            response = await self.client.get(f"{self.base_url}/users/{user_id}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return UserResponse(**response.json())
        except Exception as e:
            logger.exception("Error getting user from storage service")
            raise StorageError(f"User retrieval failed: {str(e)}")

    async def update_user(self, user_id: UUID, update: UserUpdate) -> UserResponse:
        """Update user.

        Args:
            user_id: User ID
            update: User update model

        Returns:
            Updated user

        Raises:
            StorageError: If update fails
        """
        try:
            response = await self.client.put(
                f"{self.base_url}/users/{user_id}",
                json=update.model_dump()
            )
            response.raise_for_status()
            return UserResponse(**response.json())
        except Exception as e:
            logger.exception("Error updating user in storage service")
            raise StorageError(f"User update failed: {str(e)}")

    async def delete_user(self, user_id: UUID) -> None:
        """Delete user.

        Args:
            user_id: User ID

        Raises:
            StorageError: If deletion fails
        """
        try:
            response = await self.client.delete(f"{self.base_url}/users/{user_id}")
            response.raise_for_status()
        except Exception as e:
            logger.exception("Error deleting user in storage service")
            raise StorageError(f"User deletion failed: {str(e)}")

    async def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """Get user by username.

        Args:
            username: Username to search for

        Returns:
            User if found, None otherwise

        Raises:
            StorageError: If retrieval fails
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/users",
                params={"username": username}
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return UserResponse(**response.json())
        except Exception as e:
            logger.exception("Error getting user by username from storage service")
            raise StorageError(f"User retrieval failed: {str(e)}")

    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email.

        Args:
            email: Email to search for

        Returns:
            User if found, None otherwise

        Raises:
            StorageError: If retrieval fails
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/users",
                params={"email": email}
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return UserResponse(**response.json())
        except Exception as e:
            logger.exception("Error getting user by email from storage service")
            raise StorageError(f"User retrieval failed: {str(e)}")

    async def create_session(self, session: SessionCreate) -> SessionResponse:
        """Create new session.

        Args:
            session: Session creation model

        Returns:
            Created session

        Raises:
            StorageError: If creation fails
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/sessions",
                json=session.model_dump()
            )
            response.raise_for_status()
            return SessionResponse(**response.json())
        except Exception as e:
            logger.exception("Error creating session in storage service")
            raise StorageError(f"Session creation failed: {str(e)}")

    async def get_session(self, session_id: UUID) -> Optional[SessionResponse]:
        """Get session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session if found, None otherwise

        Raises:
            StorageError: If retrieval fails
        """
        try:
            response = await self.client.get(f"{self.base_url}/sessions/{session_id}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return SessionResponse(**response.json())
        except Exception as e:
            logger.exception("Error getting session from storage service")
            raise StorageError(f"Session retrieval failed: {str(e)}")

    async def update_session(
        self,
        session_id: UUID,
        update: SessionUpdate
    ) -> SessionResponse:
        """Update session.

        Args:
            session_id: Session ID
            update: Session update model

        Returns:
            Updated session

        Raises:
            StorageError: If update fails
        """
        try:
            response = await self.client.put(
                f"{self.base_url}/sessions/{session_id}",
                json=update.model_dump()
            )
            response.raise_for_status()
            return SessionResponse(**response.json())
        except Exception as e:
            logger.exception("Error updating session in storage service")
            raise StorageError(f"Session update failed: {str(e)}")

    async def delete_session(self, session_id: UUID) -> None:
        """Delete session.

        Args:
            session_id: Session ID

        Raises:
            StorageError: If deletion fails
        """
        try:
            response = await self.client.delete(f"{self.base_url}/sessions/{session_id}")
            response.raise_for_status()
        except Exception as e:
            logger.exception("Error deleting session in storage service")
            raise StorageError(f"Session deletion failed: {str(e)}")

    async def create_role(self, role: RoleCreate) -> RoleResponse:
        """Create new role.

        Args:
            role: Role creation model

        Returns:
            Created role

        Raises:
            StorageError: If creation fails
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/roles",
                json=role.model_dump()
            )
            response.raise_for_status()
            return RoleResponse(**response.json())
        except Exception as e:
            logger.exception("Error creating role in storage service")
            raise StorageError(f"Role creation failed: {str(e)}")

    async def get_role(self, role_id: UUID) -> Optional[RoleResponse]:
        """Get role by ID.

        Args:
            role_id: Role ID

        Returns:
            Role if found, None otherwise

        Raises:
            StorageError: If retrieval fails
        """
        try:
            response = await self.client.get(f"{self.base_url}/roles/{role_id}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return RoleResponse(**response.json())
        except Exception as e:
            logger.exception("Error getting role from storage service")
            raise StorageError(f"Role retrieval failed: {str(e)}")

    async def update_role(self, role_id: UUID, update: RoleUpdate) -> RoleResponse:
        """Update role.

        Args:
            role_id: Role ID
            update: Role update model

        Returns:
            Updated role

        Raises:
            StorageError: If update fails
        """
        try:
            response = await self.client.put(
                f"{self.base_url}/roles/{role_id}",
                json=update.model_dump()
            )
            response.raise_for_status()
            return RoleResponse(**response.json())
        except Exception as e:
            logger.exception("Error updating role in storage service")
            raise StorageError(f"Role update failed: {str(e)}")

    async def delete_role(self, role_id: UUID) -> None:
        """Delete role.

        Args:
            role_id: Role ID

        Raises:
            StorageError: If deletion fails
        """
        try:
            response = await self.client.delete(f"{self.base_url}/roles/{role_id}")
            response.raise_for_status()
        except Exception as e:
            logger.exception("Error deleting role in storage service")
            raise StorageError(f"Role deletion failed: {str(e)}")

    async def create_api_key(self, api_key: ApiKeyCreate) -> ApiKeyResponse:
        """Create new API key.

        Args:
            api_key: API key creation model

        Returns:
            Created API key

        Raises:
            StorageError: If creation fails
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api_keys",
                json=api_key.model_dump()
            )
            response.raise_for_status()
            return ApiKeyResponse(**response.json())
        except Exception as e:
            logger.exception("Error creating API key in storage service")
            raise StorageError(f"API key creation failed: {str(e)}")

    async def get_api_key(self, key_id: UUID) -> Optional[ApiKeyResponse]:
        """Get API key by ID.

        Args:
            key_id: API key ID

        Returns:
            API key if found, None otherwise

        Raises:
            StorageError: If retrieval fails
        """
        try:
            response = await self.client.get(f"{self.base_url}/api_keys/{key_id}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return ApiKeyResponse(**response.json())
        except Exception as e:
            logger.exception("Error getting API key from storage service")
            raise StorageError(f"API key retrieval failed: {str(e)}")

    async def update_api_key(
        self,
        key_id: UUID,
        update: ApiKeyUpdate
    ) -> ApiKeyResponse:
        """Update API key.

        Args:
            key_id: API key ID
            update: API key update model

        Returns:
            Updated API key

        Raises:
            StorageError: If update fails
        """
        try:
            response = await self.client.put(
                f"{self.base_url}/api_keys/{key_id}",
                json=update.model_dump()
            )
            response.raise_for_status()
            return ApiKeyResponse(**response.json())
        except Exception as e:
            logger.exception("Error updating API key in storage service")
            raise StorageError(f"API key update failed: {str(e)}")

    async def delete_api_key(self, key_id: UUID) -> None:
        """Delete API key.

        Args:
            key_id: API key ID

        Raises:
            StorageError: If deletion fails
        """
        try:
            response = await self.client.delete(f"{self.base_url}/api_keys/{key_id}")
            response.raise_for_status()
        except Exception as e:
            logger.exception("Error deleting API key in storage service")
            raise StorageError(f"API key deletion failed: {str(e)}")

    async def create_audit_log(self, audit_log: AuditLogCreate) -> AuditLogResponse:
        """Create new audit log entry.

        Args:
            audit_log: Audit log creation model

        Returns:
            Created audit log entry

        Raises:
            StorageError: If creation fails
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/audit_logs",
                json=audit_log.model_dump()
            )
            response.raise_for_status()
            return AuditLogResponse(**response.json())
        except Exception as e:
            logger.exception("Error creating audit log in storage service")
            raise StorageError(f"Audit log creation failed: {str(e)}")

    async def get_audit_logs(
        self,
        user_id: Optional[UUID] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLogResponse]:
        """Get audit log entries with filtering.

        Args:
            user_id: Optional user ID filter
            action: Optional action filter
            resource_type: Optional resource type filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            limit: Maximum number of records
            offset: Pagination offset

        Returns:
            List of audit log entries

        Raises:
            StorageError: If retrieval fails
        """
        try:
            params: Dict = {
                "limit": limit,
                "offset": offset
            }
            if user_id:
                params["user_id"] = str(user_id)
            if action:
                params["action"] = action
            if resource_type:
                params["resource_type"] = resource_type
            if start_time:
                params["start_time"] = start_time.isoformat()
            if end_time:
                params["end_time"] = end_time.isoformat()

            response = await self.client.get(
                f"{self.base_url}/audit_logs",
                params=params
            )
            response.raise_for_status()
            return [AuditLogResponse(**data) for data in response.json()]
        except Exception as e:
            logger.exception("Error getting audit logs from storage service")
            raise StorageError(f"Audit log retrieval failed: {str(e)}")

    async def cleanup(self) -> None:
        """Clean up client resources."""
        await self.client.aclose()