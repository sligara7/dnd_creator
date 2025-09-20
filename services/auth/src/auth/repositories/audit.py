"""Audit log repository for auth service."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from auth.clients.storage import StorageClient
from auth.core.exceptions import StorageError
from auth.models.api import AuditLogCreate, AuditLogResponse, AuditLogBase
from auth.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLogResponse, AuditLogCreate, AuditLogBase]):
    """Audit log repository."""

    def __init__(self, storage_client: StorageClient) -> None:
        """Initialize audit log repository.

        Args:
            storage_client: Storage service client
        """
        super().__init__(AuditLogResponse, storage_client)

    async def create(self, audit_log: AuditLogCreate) -> AuditLogResponse:
        """Create new audit log entry.

        Args:
            audit_log: Audit log entry creation model

        Returns:
            Created audit log entry

        Raises:
            StorageError: If creation fails
        """
        return await self.storage_client.create_audit_log(audit_log)

    async def get(self, log_id: UUID) -> Optional[AuditLogResponse]:
        """Get audit log entry by ID.

        Args:
            log_id: Audit log entry ID

        Returns:
            Audit log entry if found, None otherwise

        Raises:
            StorageError: If retrieval fails
        """
        raise NotImplementedError("Individual audit log retrieval not supported")

    async def list_logs(
        self,
        user_id: Optional[UUID] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLogResponse]:
        """List audit log entries with filtering.

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
        return await self.storage_client.get_audit_logs(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset
        )

    async def update(self, log_id: UUID, obj: AuditLogBase) -> Optional[AuditLogResponse]:
        """Update is not supported for audit logs.

        Args:
            log_id: Audit log entry ID
            obj: Update model

        Raises:
            NotImplementedError: Always
        """
        raise NotImplementedError("Audit log entries cannot be modified")

    async def delete(self, log_id: UUID) -> bool:
        """Delete is not supported for audit logs.

        Args:
            log_id: Audit log entry ID

        Raises:
            NotImplementedError: Always
        """
        raise NotImplementedError("Audit log entries cannot be deleted")