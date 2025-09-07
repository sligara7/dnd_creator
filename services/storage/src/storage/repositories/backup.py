"""Backup Repository for storage service."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.backup import BackupJob, BackupType, BackupStatus
from ..utils.logging import get_logger

logger = get_logger(__name__)


class BackupRepository:
    """Repository for backup operations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db
    
    async def create(self, backup_data: Dict[str, Any]) -> BackupJob:
        """Create a new backup job."""
        try:
            backup = BackupJob(**backup_data)
            self.db.add(backup)
            await self.db.flush()
            await self.db.refresh(backup)
            logger.info(f"Created backup job: {backup.id}")
            return backup
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            raise
    
    async def get(self, backup_id: UUID) -> Optional[BackupJob]:
        """Get backup by ID."""
        try:
            query = select(BackupJob).where(
                BackupJob.id == backup_id,
                BackupJob.is_deleted == False
            )
            result = await self.db.execute(query)
            backup = result.scalar_one_or_none()
            
            if backup:
                logger.debug(f"Retrieved backup: {backup_id}")
            else:
                logger.warning(f"Backup not found: {backup_id}")
            
            return backup
        except Exception as e:
            logger.error(f"Failed to get backup {backup_id}: {str(e)}")
            raise
    
    async def list(
        self,
        service: Optional[str] = None,
        backup_type: Optional[BackupType] = None,
        status: Optional[BackupStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[BackupJob]:
        """List backups with filters."""
        try:
            query = select(BackupJob).where(BackupJob.is_deleted == False)
            
            if service:
                query = query.where(BackupJob.service == service)
            
            if backup_type:
                query = query.where(BackupJob.backup_type == backup_type)
            
            if status:
                query = query.where(BackupJob.status == status)
            
            if start_date:
                query = query.where(BackupJob.started_at >= start_date)
            
            if end_date:
                query = query.where(BackupJob.started_at <= end_date)
            
            query = query.limit(limit).offset(offset)
            query = query.order_by(BackupJob.started_at.desc())
            
            result = await self.db.execute(query)
            backups = result.scalars().all()
            
            logger.debug(f"Listed {len(backups)} backups")
            return backups
        except Exception as e:
            logger.error(f"Failed to list backups: {str(e)}")
            raise
    
    async def update_status(
        self,
        backup_id: UUID,
        status: BackupStatus,
        details: Optional[Dict[str, Any]] = None
    ) -> Optional[BackupJob]:
        """Update backup job status."""
        try:
            updates = {
                'status': status,
                'updated_at': datetime.utcnow()
            }
            
            if status == BackupStatus.COMPLETED:
                updates['completed_at'] = datetime.utcnow()
            elif status == BackupStatus.FAILED:
                updates['failed_at'] = datetime.utcnow()
            
            if details:
                updates['metadata'] = details
            
            query = (
                update(BackupJob)
                .where(BackupJob.id == backup_id)
                .values(**updates)
                .returning(BackupJob)
            )
            
            result = await self.db.execute(query)
            updated_backup = result.scalar_one_or_none()
            
            if updated_backup:
                logger.info(f"Updated backup status: {backup_id} -> {status.value}")
            
            return updated_backup
        except Exception as e:
            logger.error(f"Failed to update backup status: {str(e)}")
            raise
    
    async def get_latest_successful(
        self,
        service: Optional[str] = None,
        backup_type: Optional[BackupType] = None
    ) -> Optional[BackupJob]:
        """Get the latest successful backup."""
        try:
            query = select(BackupJob).where(
                and_(
                    BackupJob.status == BackupStatus.COMPLETED,
                    BackupJob.is_deleted == False
                )
            )
            
            if service:
                query = query.where(BackupJob.service == service)
            
            if backup_type:
                query = query.where(BackupJob.backup_type == backup_type)
            
            query = query.order_by(BackupJob.completed_at.desc()).limit(1)
            
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get latest successful backup: {str(e)}")
            raise
    
    async def get_running_backups(self) -> List[BackupJob]:
        """Get all currently running backups."""
        try:
            query = select(BackupJob).where(
                and_(
                    BackupJob.status == BackupStatus.IN_PROGRESS,
                    BackupJob.is_deleted == False
                )
            )
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get running backups: {str(e)}")
            raise
    
    async def cleanup_old_backups(
        self,
        retention_days: int,
        service: Optional[str] = None
    ) -> int:
        """Clean up old backups based on retention policy."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            query = (
                update(BackupJob)
                .where(
                    and_(
                        BackupJob.completed_at < cutoff_date,
                        BackupJob.status == BackupStatus.COMPLETED,
                        BackupJob.is_deleted == False
                    )
                )
                .values(
                    is_deleted=True,
                    deleted_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            )
            
            if service:
                query = query.where(BackupJob.service == service)
            
            result = await self.db.execute(query)
            cleaned_count = result.rowcount
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old backups")
            
            return cleaned_count
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {str(e)}")
            raise
    
    async def get_backup_stats(
        self,
        service: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get backup statistics."""
        try:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # Base query
            base_conditions = [
                BackupJob.started_at >= since_date,
                BackupJob.is_deleted == False
            ]
            
            if service:
                base_conditions.append(BackupJob.service == service)
            
            # Get total backups
            total_query = select(func.count(BackupJob.id)).where(
                and_(*base_conditions)
            )
            total_result = await self.db.execute(total_query)
            total_backups = total_result.scalar() or 0
            
            # Get successful backups
            success_query = select(func.count(BackupJob.id)).where(
                and_(
                    *base_conditions,
                    BackupJob.status == BackupStatus.COMPLETED
                )
            )
            success_result = await self.db.execute(success_query)
            successful_backups = success_result.scalar() or 0
            
            # Get failed backups
            failed_query = select(func.count(BackupJob.id)).where(
                and_(
                    *base_conditions,
                    BackupJob.status == BackupStatus.FAILED
                )
            )
            failed_result = await self.db.execute(failed_query)
            failed_backups = failed_result.scalar() or 0
            
            # Get average duration for completed backups
            duration_query = select(
                func.avg(
                    func.extract('epoch', BackupJob.completed_at - BackupJob.started_at)
                )
            ).where(
                and_(
                    *base_conditions,
                    BackupJob.status == BackupStatus.COMPLETED,
                    BackupJob.completed_at != None
                )
            )
            duration_result = await self.db.execute(duration_query)
            avg_duration = duration_result.scalar()
            
            # Get total size backed up
            size_query = select(func.sum(BackupJob.size_bytes)).where(
                and_(
                    *base_conditions,
                    BackupJob.status == BackupStatus.COMPLETED
                )
            )
            size_result = await self.db.execute(size_query)
            total_size = size_result.scalar() or 0
            
            stats = {
                'period_days': days,
                'total_backups': total_backups,
                'successful_backups': successful_backups,
                'failed_backups': failed_backups,
                'success_rate': (successful_backups / total_backups * 100) if total_backups > 0 else 0,
                'average_duration_seconds': float(avg_duration) if avg_duration else 0,
                'total_size_bytes': total_size
            }
            
            logger.debug(f"Generated backup stats for {days} days")
            return stats
        except Exception as e:
            logger.error(f"Failed to get backup stats: {str(e)}")
            raise
    
    async def mark_stale_backups(self, timeout_hours: int = 24) -> int:
        """Mark stale in-progress backups as failed."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=timeout_hours)
            
            query = (
                update(BackupJob)
                .where(
                    and_(
                        BackupJob.status == BackupStatus.IN_PROGRESS,
                        BackupJob.started_at < cutoff_time,
                        BackupJob.is_deleted == False
                    )
                )
                .values(
                    status=BackupStatus.FAILED,
                    failed_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    metadata={'error': 'Backup timed out'}
                )
            )
            
            result = await self.db.execute(query)
            marked_count = result.rowcount
            
            if marked_count > 0:
                logger.warning(f"Marked {marked_count} stale backups as failed")
            
            return marked_count
        except Exception as e:
            logger.error(f"Failed to mark stale backups: {str(e)}")
            raise
