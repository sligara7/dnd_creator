"""Backup Service for backup and restore operations."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, BinaryIO
from uuid import UUID
import tarfile
import io

from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.backup import BackupRepository
from ..repositories.asset import AssetRepository
from ..integrations.s3_client import S3StorageClient
from ..models.backup import BackupJob, BackupType, BackupStatus
from ..utils.logging import get_logger

logger = get_logger(__name__)


class BackupService:
    """Service for backup and restore operations."""
    
    def __init__(self, db: AsyncSession, s3_client: Optional[S3StorageClient] = None):
        """Initialize service with dependencies."""
        self.db = db
        self.backup_repo = BackupRepository(db)
        self.asset_repo = AssetRepository(db)
        self.s3_client = s3_client or S3StorageClient()
    
    async def create_backup(
        self,
        service: str,
        backup_type: BackupType = BackupType.FULL,
        description: Optional[str] = None
    ) -> BackupJob:
        """Create a new backup job."""
        try:
            # Check for running backups
            running = await self.backup_repo.get_running_backups()
            if running:
                for job in running:
                    if job.service == service:
                        raise ValueError(f"Backup already running for service {service}")
            
            # Create backup job record
            backup_data = {
                'service': service,
                'backup_type': backup_type,
                'status': BackupStatus.PENDING,
                'started_at': datetime.utcnow(),
                'metadata': {
                    'description': description,
                    'created_at': datetime.utcnow().isoformat()
                }
            }
            
            backup_job = await self.backup_repo.create(backup_data)
            await self.db.commit()
            
            # Start backup asynchronously
            asyncio.create_task(self._perform_backup(backup_job))
            
            logger.info(f"Created backup job {backup_job.id} for service {service}")
            return backup_job
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create backup: {str(e)}")
            raise
    
    async def _perform_backup(self, backup_job: BackupJob) -> None:
        """Perform the actual backup operation."""
        try:
            # Update status to in progress
            await self.backup_repo.update_status(
                backup_job.id,
                BackupStatus.IN_PROGRESS,
                {'started': datetime.utcnow().isoformat()}
            )
            await self.db.commit()
            
            # Get assets to backup
            if backup_job.backup_type == BackupType.INCREMENTAL:
                # Get assets modified since last backup
                last_backup = await self.backup_repo.get_latest_successful(
                    service=backup_job.service
                )
                if last_backup:
                    assets = await self._get_modified_assets(
                        backup_job.service,
                        last_backup.completed_at
                    )
                else:
                    # No previous backup, do full backup
                    assets = await self.asset_repo.list(service=backup_job.service)
            else:
                # Full backup
                assets = await self.asset_repo.list(service=backup_job.service)
            
            # Create backup archive
            backup_data = await self._create_backup_archive(assets)
            
            # Upload backup to S3
            backup_key = f"backups/{backup_job.service}/{backup_job.id}.tar.gz"
            await self.s3_client.upload(
                key=backup_key,
                data=backup_data,
                content_type='application/gzip',
                metadata={
                    'backup_id': str(backup_job.id),
                    'service': backup_job.service,
                    'type': backup_job.backup_type.value
                }
            )
            
            # Update backup job with success
            await self.backup_repo.update_status(
                backup_job.id,
                BackupStatus.COMPLETED,
                {
                    'assets_backed_up': len(assets),
                    'backup_key': backup_key,
                    'size_bytes': len(backup_data.getvalue()),
                    'completed': datetime.utcnow().isoformat()
                }
            )
            
            # Update size in backup job
            backup_job.size_bytes = len(backup_data.getvalue())
            backup_job.s3_key = backup_key
            
            await self.db.commit()
            logger.info(f"Backup {backup_job.id} completed successfully")
            
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            await self.backup_repo.update_status(
                backup_job.id,
                BackupStatus.FAILED,
                {'error': str(e)}
            )
            await self.db.commit()
    
    async def _get_modified_assets(
        self,
        service: str,
        since: datetime
    ) -> List:
        """Get assets modified since a given time."""
        # This would require filtering by updated_at in asset repository
        # For now, return all assets
        return await self.asset_repo.list(service=service)
    
    async def _create_backup_archive(self, assets: List) -> io.BytesIO:
        """Create a tar.gz archive of assets."""
        archive_buffer = io.BytesIO()
        
        with tarfile.open(fileobj=archive_buffer, mode='w:gz') as tar:
            # Add manifest
            manifest = {
                'version': '1.0',
                'created_at': datetime.utcnow().isoformat(),
                'asset_count': len(assets),
                'assets': []
            }
            
            for asset in assets:
                # Download asset data
                try:
                    file_data = await self.s3_client.download(asset.s3_key)
                    
                    # Create tarinfo
                    tarinfo = tarfile.TarInfo(name=f"assets/{asset.id}/{asset.name}")
                    tarinfo.size = asset.size
                    
                    # Add to archive
                    tar.addfile(tarinfo, file_data)
                    
                    # Add to manifest
                    manifest['assets'].append({
                        'id': str(asset.id),
                        'name': asset.name,
                        'size': asset.size,
                        'checksum': asset.checksum,
                        's3_key': asset.s3_key
                    })
                except Exception as e:
                    logger.error(f"Failed to backup asset {asset.id}: {str(e)}")
            
            # Add manifest to archive
            manifest_data = json.dumps(manifest, indent=2).encode()
            manifest_info = tarfile.TarInfo(name='manifest.json')
            manifest_info.size = len(manifest_data)
            tar.addfile(manifest_info, io.BytesIO(manifest_data))
        
        archive_buffer.seek(0)
        return archive_buffer
    
    async def restore_backup(
        self,
        backup_id: UUID,
        target_service: Optional[str] = None
    ) -> Dict[str, Any]:
        """Restore from a backup."""
        try:
            # Get backup job
            backup_job = await self.backup_repo.get(backup_id)
            if not backup_job:
                raise ValueError(f"Backup {backup_id} not found")
            
            if backup_job.status != BackupStatus.COMPLETED:
                raise ValueError(f"Backup {backup_id} is not completed")
            
            # Download backup archive
            archive_data = await self.s3_client.download(backup_job.s3_key)
            
            # Extract and restore
            restored_count = 0
            errors = []
            
            with tarfile.open(fileobj=archive_data, mode='r:gz') as tar:
                # Read manifest
                manifest_file = tar.extractfile('manifest.json')
                if manifest_file:
                    manifest = json.loads(manifest_file.read().decode())
                else:
                    raise ValueError("Backup manifest not found")
                
                # Restore each asset
                for asset_info in manifest['assets']:
                    try:
                        # Extract asset file
                        asset_path = f"assets/{asset_info['id']}/{asset_info['name']}"
                        asset_file = tar.extractfile(asset_path)
                        
                        if asset_file:
                            # Upload to S3
                            s3_key = asset_info['s3_key']
                            if target_service and target_service != backup_job.service:
                                # Change service in S3 key
                                s3_key = s3_key.replace(
                                    f"{backup_job.service}/",
                                    f"{target_service}/",
                                    1
                                )
                            
                            await self.s3_client.upload(
                                key=s3_key,
                                data=asset_file,
                                content_type='application/octet-stream'
                            )
                            
                            restored_count += 1
                    except Exception as e:
                        errors.append({
                            'asset_id': asset_info['id'],
                            'error': str(e)
                        })
            
            result = {
                'backup_id': str(backup_id),
                'restored_count': restored_count,
                'errors': errors,
                'success': len(errors) == 0
            }
            
            logger.info(f"Restored {restored_count} assets from backup {backup_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {str(e)}")
            raise
    
    async def verify_backup(self, backup_id: UUID) -> Dict[str, Any]:
        """Verify backup integrity."""
        try:
            backup_job = await self.backup_repo.get(backup_id)
            if not backup_job:
                raise ValueError(f"Backup {backup_id} not found")
            
            # Download and check archive
            try:
                archive_data = await self.s3_client.download(backup_job.s3_key)
                
                with tarfile.open(fileobj=archive_data, mode='r:gz') as tar:
                    # Check manifest
                    manifest_file = tar.extractfile('manifest.json')
                    if not manifest_file:
                        return {'valid': False, 'error': 'Manifest not found'}
                    
                    manifest = json.loads(manifest_file.read().decode())
                    
                    # Verify each asset
                    missing_assets = []
                    for asset_info in manifest['assets']:
                        asset_path = f"assets/{asset_info['id']}/{asset_info['name']}"
                        try:
                            tar.getmember(asset_path)
                        except KeyError:
                            missing_assets.append(asset_info['id'])
                    
                    return {
                        'valid': len(missing_assets) == 0,
                        'asset_count': len(manifest['assets']),
                        'missing_assets': missing_assets
                    }
                    
            except Exception as e:
                return {'valid': False, 'error': str(e)}
                
        except Exception as e:
            logger.error(f"Failed to verify backup: {str(e)}")
            raise
    
    async def list_backups(
        self,
        service: Optional[str] = None,
        backup_type: Optional[BackupType] = None,
        status: Optional[BackupStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[BackupJob]:
        """List backup jobs."""
        return await self.backup_repo.list(
            service=service,
            backup_type=backup_type,
            status=status,
            limit=limit,
            offset=offset
        )
    
    async def get_backup_stats(
        self,
        service: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get backup statistics."""
        return await self.backup_repo.get_backup_stats(service, days)
    
    async def cleanup_old_backups(
        self,
        retention_days: int,
        service: Optional[str] = None
    ) -> int:
        """Clean up old backups based on retention policy."""
        try:
            cleaned = await self.backup_repo.cleanup_old_backups(
                retention_days,
                service
            )
            
            if cleaned > 0:
                await self.db.commit()
                logger.info(f"Cleaned up {cleaned} old backups")
            
            return cleaned
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to cleanup backups: {str(e)}")
            raise
    
    async def schedule_backup(
        self,
        service: str,
        schedule: str,
        backup_type: BackupType = BackupType.FULL
    ) -> Dict[str, Any]:
        """Schedule recurring backups (placeholder for scheduler integration)."""
        # This would integrate with a scheduler like APScheduler
        # For now, return schedule info
        return {
            'service': service,
            'schedule': schedule,
            'backup_type': backup_type.value,
            'status': 'scheduled'
        }
