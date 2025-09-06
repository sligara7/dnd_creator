"""Repository for sync error handling and recovery."""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.domain.sync.recovery.models import (
    ErrorStatus,
    ErrorType,
    RecoveryMetrics,
    SyncErrorLog,
)
from character_service.infrastructure.database.models import (
    SyncErrorModel,
    SyncMetadataModel,
)


class SyncErrorRepository:
    """Repository for managing sync errors."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository.

        Args:
            db: Database session
        """
        self._db = db

    async def create(
        self,
        character_id: UUID,
        campaign_id: UUID,
        error_type: ErrorType,
        error_message: str,
        state_version: int,
        campaign_version: int,
        metadata: Optional[Dict] = None,
    ) -> SyncErrorLog:
        """Create new sync error log.

        Args:
            character_id: Character ID
            campaign_id: Campaign ID
            error_type: Type of error
            error_message: Error message
            state_version: Current state version
            campaign_version: Current campaign version
            metadata: Optional error metadata

        Returns:
            Created error log
        """
        error = SyncErrorModel(
            character_id=character_id,
            campaign_id=campaign_id,
            error_type=error_type.value,
            error_message=error_message,
            status=ErrorStatus.NEW.value,
            state_version=state_version,
            campaign_version=campaign_version,
            metadata=metadata or {},
        )
        self._db.add(error)
        await self._db.flush()
        await self._db.refresh(error)

        return self._to_domain(error)

    async def get(
        self,
        error_id: UUID,
    ) -> Optional[SyncErrorLog]:
        """Get sync error by ID.

        Args:
            error_id: Error ID

        Returns:
            Error log if found
        """
        query = select(SyncErrorModel).where(SyncErrorModel.id == error_id)
        result = await self._db.execute(query)
        error = result.scalar_one_or_none()
        if not error:
            return None

        return self._to_domain(error)

    async def update(
        self,
        error_id: UUID,
        status: Optional[ErrorStatus] = None,
        retry_count: Optional[int] = None,
        resolution_details: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """Update sync error.

        Args:
            error_id: Error ID
            status: New status
            retry_count: New retry count
            resolution_details: Resolution details
            metadata: Updated metadata

        Returns:
            Whether update was successful
        """
        values = {}
        if status:
            values["status"] = status.value
        if retry_count is not None:
            values["retry_count"] = retry_count
        if resolution_details:
            values["resolution_details"] = resolution_details
        if metadata:
            values["metadata"] = metadata
        if status == ErrorStatus.RESOLVED:
            values["resolved_at"] = datetime.utcnow()
        elif status == ErrorStatus.RETRYING:
            values["last_retry"] = datetime.utcnow()

        query = (
            update(SyncErrorModel)
            .where(SyncErrorModel.id == error_id)
            .values(**values)
        )
        result = await self._db.execute(query)
        return bool(result.rowcount)

    async def list_for_retry(
        self,
        batch_size: int = 10,
        retry_window: int = 300,  # 5 minutes
    ) -> List[SyncErrorLog]:
        """List errors ready for retry.

        Args:
            batch_size: Maximum number of errors to return
            retry_window: Minimum seconds since last retry

        Returns:
            List of error logs
        """
        retry_cutoff = datetime.utcnow() - timedelta(seconds=retry_window)
        query = (
            select(SyncErrorModel)
            .where(
                and_(
                    SyncErrorModel.status.in_([ErrorStatus.NEW.value, ErrorStatus.RETRYING.value]),
                    SyncErrorModel.retry_count < SyncErrorModel.max_retries,
                    SyncErrorModel.last_retry <= retry_cutoff,
                )
            )
            .order_by(
                desc(SyncErrorModel.created_at)
            )
            .limit(batch_size)
        )
        result = await self._db.execute(query)
        errors = result.scalars().all()
        return [self._to_domain(error) for error in errors]

    async def get_character_errors(
        self,
        character_id: UUID,
        campaign_id: Optional[UUID] = None,
        error_types: Optional[Set[ErrorType]] = None,
        include_resolved: bool = False,
    ) -> List[SyncErrorLog]:
        """Get errors for a character.

        Args:
            character_id: Character ID
            campaign_id: Optional campaign ID filter
            error_types: Optional error types to include
            include_resolved: Whether to include resolved errors

        Returns:
            List of error logs
        """
        filters = [SyncErrorModel.character_id == character_id]
        if campaign_id:
            filters.append(SyncErrorModel.campaign_id == campaign_id)
        if error_types:
            filters.append(SyncErrorModel.error_type.in_([t.value for t in error_types]))
        if not include_resolved:
            filters.append(SyncErrorModel.status != ErrorStatus.RESOLVED.value)

        query = (
            select(SyncErrorModel)
            .where(and_(*filters))
            .order_by(desc(SyncErrorModel.created_at))
        )
        result = await self._db.execute(query)
        errors = result.scalars().all()
        return [self._to_domain(error) for error in errors]

    async def get_metrics(
        self,
        character_id: Optional[UUID] = None,
        campaign_id: Optional[UUID] = None,
        window_hours: int = 24,
    ) -> RecoveryMetrics:
        """Get recovery metrics.

        Args:
            character_id: Optional character ID filter
            campaign_id: Optional campaign ID filter
            window_hours: Time window in hours

        Returns:
            Recovery metrics
        """
        filters = []
        if character_id:
            filters.append(SyncErrorModel.character_id == character_id)
        if campaign_id:
            filters.append(SyncErrorModel.campaign_id == campaign_id)

        window_start = datetime.utcnow() - timedelta(hours=window_hours)
        filters.append(SyncErrorModel.created_at >= window_start)

        # Get all matching errors
        query = select(SyncErrorModel).where(and_(*filters))
        result = await self._db.execute(query)
        errors = result.scalars().all()

        # Calculate metrics
        metrics = RecoveryMetrics()
        total_time = 0.0
        resolved_time = 0.0

        for error in errors:
            metrics.error_count += 1
            metrics.retry_count += error.retry_count
            error_type = error.error_type
            if error_type not in metrics.failures_by_type:
                metrics.failures_by_type[error_type] = 0
            
            if error.status == ErrorStatus.RESOLVED.value:
                metrics.resolved_count += 1
                if error.resolved_at:
                    resolved_time += (error.resolved_at - error.created_at).total_seconds()
            else:
                metrics.failures_by_type[error_type] += 1

        # Calculate rates and averages
        if metrics.error_count > 0:
            metrics.success_rate = metrics.resolved_count / metrics.error_count
        if metrics.resolved_count > 0:
            metrics.avg_resolution_time = resolved_time / metrics.resolved_count

        return metrics

    async def cleanup_old_errors(
        self,
        max_age_days: int = 30,
    ) -> int:
        """Clean up old resolved errors.

        Args:
            max_age_days: Maximum age in days

        Returns:
            Number of errors cleaned up
        """
        cutoff = datetime.utcnow() - timedelta(days=max_age_days)
        query = (
            update(SyncErrorModel)
            .where(
                and_(
                    SyncErrorModel.status == ErrorStatus.RESOLVED.value,
                    SyncErrorModel.resolved_at <= cutoff,
                )
            )
            .values(is_deleted=True)
        )
        result = await self._db.execute(query)
        return result.rowcount

    def _to_domain(self, model: SyncErrorModel) -> SyncErrorLog:
        """Convert database model to domain model.

        Args:
            model: Database model

        Returns:
            Domain model
        """
        return SyncErrorLog(
            error_id=model.id,
            character_id=model.character_id,
            campaign_id=model.campaign_id,
            error_type=ErrorType(model.error_type),
            error_message=model.error_message,
            status=ErrorStatus(model.status),
            retry_count=model.retry_count,
            max_retries=model.max_retries,
            last_retry=model.last_retry,
            created_at=model.created_at,
            resolved_at=model.resolved_at,
            resolution_details=model.resolution_details,
            state_version=model.state_version,
            campaign_version=model.campaign_version,
            metadata=model.metadata,
        )
