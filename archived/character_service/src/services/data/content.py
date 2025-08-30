"""
Content coordination service.

This service manages and coordinates content from various sources:
- Official D&D content
- Custom user content
- Campaign-specific content
- Content validation and rules
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from .catalog import UnifiedCatalogService
from src.models.database_models import (
    UnifiedCatalogItem,
    ContentApproval,
    ContentRevision
)

logger = logging.getLogger(__name__)

class ContentCoordinationService:
    """Service for coordinating and managing game content."""
    
    def __init__(self, db: Session, catalog_service: Optional[UnifiedCatalogService] = None):
        self.db = db
        self.catalog_service = catalog_service or UnifiedCatalogService(db)
        
    async def submit_custom_content(self,
                                  content_type: str,
                                  content_data: Dict[str, Any],
                                  submitted_by: str,
                                  campaign_id: Optional[str] = None) -> str:
        """
        Submit custom content for approval.
        
        Args:
            content_type: Type of content being submitted
            content_data: The content data
            submitted_by: ID of the submitting user
            campaign_id: Optional campaign context
            
        Returns:
            ID of the submitted content
        """
        try:
            # Create catalog item first
            item_id = await self.catalog_service.create_custom_item(
                name=content_data.get("name", "Unnamed Content"),
                item_type=content_type,
                content_data=content_data,
                source_type="user_submitted",
                created_by=submitted_by
            )
            
            # Create revision record
            revision = ContentRevision(
                content_id=item_id,
                revision_number=1,
                content=content_data,
                submitted_by=submitted_by,
                submitted_at=datetime.utcnow(),
                campaign_id=campaign_id
            )
            
            # Create approval record
            approval = ContentApproval(
                content_id=item_id,
                status="pending",
                submitted_by=submitted_by,
                submitted_at=datetime.utcnow(),
                campaign_id=campaign_id
            )
            
            self.db.add(revision)
            self.db.add(approval)
            self.db.commit()
            
            logger.info(
                "custom_content_submitted",
                content_id=item_id,
                type=content_type,
                submitted_by=submitted_by
            )
            
            return item_id
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                "content_submission_failed",
                type=content_type,
                error=str(e)
            )
            raise
            
    async def update_custom_content(self,
                                  content_id: str,
                                  content_data: Dict[str, Any],
                                  updated_by: str) -> bool:
        """
        Update existing custom content.
        
        Args:
            content_id: ID of the content to update
            content_data: Updated content data
            updated_by: ID of the updating user
            
        Returns:
            True if update was successful
        """
        try:
            # Get current content
            content = self.db.query(UnifiedCatalogItem).get(content_id)
            if not content:
                return False
                
            # Get latest revision number
            latest_revision = self.db.query(ContentRevision)\
                .filter(ContentRevision.content_id == content_id)\
                .order_by(ContentRevision.revision_number.desc())\
                .first()
                
            new_revision_number = (latest_revision.revision_number + 1) if latest_revision else 1
            
            # Create new revision
            revision = ContentRevision(
                content_id=content_id,
                revision_number=new_revision_number,
                content=content_data,
                submitted_by=updated_by,
                submitted_at=datetime.utcnow()
            )
            
            # Update catalog item
            content.content = content_data
            content.updated_at = datetime.utcnow()
            
            self.db.add(revision)
            self.db.commit()
            
            logger.info(
                "custom_content_updated",
                content_id=content_id,
                revision=new_revision_number,
                updated_by=updated_by
            )
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                "content_update_failed",
                content_id=content_id,
                error=str(e)
            )
            raise
            
    async def approve_custom_content(self,
                                   content_id: str,
                                   approved_by: str,
                                   approval_notes: Optional[str] = None) -> bool:
        """
        Approve custom content for use.
        
        Args:
            content_id: ID of the content to approve
            approved_by: ID of the approving user
            approval_notes: Optional approval notes
            
        Returns:
            True if approval was successful
        """
        try:
            # Get approval record
            approval = self.db.query(ContentApproval)\
                .filter(ContentApproval.content_id == content_id)\
                .first()
                
            if not approval:
                return False
                
            # Update approval status
            approval.status = "approved"
            approval.approved_by = approved_by
            approval.approved_at = datetime.utcnow()
            approval.notes = approval_notes
            
            # Update catalog item source type
            content = self.db.query(UnifiedCatalogItem).get(content_id)
            if content:
                content.source_type = "approved_custom"
                
            self.db.commit()
            
            logger.info(
                "custom_content_approved",
                content_id=content_id,
                approved_by=approved_by
            )
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                "content_approval_failed",
                content_id=content_id,
                error=str(e)
            )
            raise
            
    def get_content_history(self, content_id: str) -> List[Dict[str, Any]]:
        """
        Get revision history for content.
        
        Args:
            content_id: ID of the content
            
        Returns:
            List of content revisions
        """
        try:
            revisions = self.db.query(ContentRevision)\
                .filter(ContentRevision.content_id == content_id)\
                .order_by(ContentRevision.revision_number.desc())\
                .all()
                
            return [
                {
                    "revision": rev.revision_number,
                    "content": rev.content,
                    "submitted_by": rev.submitted_by,
                    "submitted_at": rev.submitted_at.isoformat(),
                    "campaign_id": rev.campaign_id
                }
                for rev in revisions
            ]
            
        except Exception as e:
            logger.error(
                "content_history_fetch_failed",
                content_id=content_id,
                error=str(e)
            )
            raise
            
    def get_pending_approvals(self, campaign_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get content pending approval.
        
        Args:
            campaign_id: Optional campaign filter
            
        Returns:
            List of pending content approvals
        """
        try:
            query = self.db.query(ContentApproval)\
                .filter(ContentApproval.status == "pending")
                
            if campaign_id:
                query = query.filter(ContentApproval.campaign_id == campaign_id)
                
            approvals = query.all()
            
            pending = []
            for approval in approvals:
                content = self.db.query(UnifiedCatalogItem).get(approval.content_id)
                if not content:
                    continue
                    
                pending.append({
                    "id": str(approval.content_id),
                    "name": content.name,
                    "type": content.item_type,
                    "submitted_by": approval.submitted_by,
                    "submitted_at": approval.submitted_at.isoformat(),
                    "campaign_id": approval.campaign_id
                })
                
            return pending
            
        except Exception as e:
            logger.error(
                "pending_approvals_fetch_failed",
                campaign_id=campaign_id,
                error=str(e)
            )
            raise
