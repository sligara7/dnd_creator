"""Campaign service permission management and validation."""
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Set
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from campaign_service.models.campaign import Campaign, CampaignState
from campaign_service.exceptions import PermissionDeniedError

class PermissionType(Enum):
    """Permission types for campaign operations."""
    VIEW = auto()
    EDIT = auto()
    DELETE = auto()
    CHANGE_STATE = auto()
    MANAGE_PERMISSIONS = auto()
    CHANGE_OWNER = auto()

@dataclass
class CampaignPermission:
    """Campaign permission record."""
    campaign_id: UUID
    user_id: UUID
    permission_type: PermissionType
    granted_by: UUID
    granted_at: datetime

class CampaignPermissions:
    """Service for managing campaign permissions and authorization."""

    def __init__(self, db: AsyncSession):
        """Initialize the permissions service.
        
        Args:
            db: Database session for queries
        """
        self.db = db
    
    async def _get_campaign(self, campaign_id: UUID) -> Campaign:
        """Get campaign by ID.
        
        Args:
            campaign_id: Campaign UUID
            
        Returns:
            Campaign instance
            
        Raises:
            PermissionDeniedError: If campaign not found
        """
        result = await self.db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        if not campaign:
            raise PermissionDeniedError("Campaign not found")
        return campaign
    
    async def can_view(self, campaign_id: UUID, user_id: UUID) -> bool:
        """Check if user has view permission.
        
        Args:
            campaign_id: Campaign UUID
            user_id: User UUID
            
        Returns:
            True if user has permission
        """
        campaign = await self._get_campaign(campaign_id)
        if user_id in (campaign.owner_id, campaign.creator_id):
            return True
            
        result = await self.db.execute(
            select(CampaignPermission)
            .where(
                CampaignPermission.campaign_id == campaign_id,
                CampaignPermission.user_id == user_id,
                CampaignPermission.permission_type == PermissionType.VIEW,
            )
        )
        return bool(result.scalar_one_or_none())
    
    async def can_edit(self, campaign_id: UUID, user_id: UUID) -> bool:
        """Check if user has edit permission.
        
        Args:
            campaign_id: Campaign UUID
            user_id: User UUID
            
        Returns:
            True if user has permission
        """
        campaign = await self._get_campaign(campaign_id)
        if user_id in (campaign.owner_id, campaign.creator_id):
            return True
            
        result = await self.db.execute(
            select(CampaignPermission)
            .where(
                CampaignPermission.campaign_id == campaign_id,
                CampaignPermission.user_id == user_id,
                CampaignPermission.permission_type == PermissionType.EDIT,
            )
        )
        return bool(result.scalar_one_or_none())
    
    async def can_delete(self, campaign_id: UUID, user_id: UUID) -> bool:
        """Check if user has delete permission.
        
        Args:
            campaign_id: Campaign UUID
            user_id: User UUID
            
        Returns:
            True if user has permission
        """
        campaign = await self._get_campaign(campaign_id)
        return user_id == campaign.owner_id
    
    async def can_change_state(
        self,
        campaign_id: UUID,
        user_id: UUID,
        new_state: CampaignState,
    ) -> bool:
        """Check if user can transition to new state.
        
        Args:
            campaign_id: Campaign UUID
            user_id: User UUID
            new_state: Target campaign state
            
        Returns:
            True if state transition is allowed
        """
        campaign = await self._get_campaign(campaign_id)
        
        # Owner can make any state transition
        if user_id == campaign.owner_id:
            return True
            
        # Users with edit permission can transition between DRAFT/ACTIVE/PAUSED
        if await self.can_edit(campaign_id, user_id):
            allowed_transitions = {
                CampaignState.DRAFT: {CampaignState.ACTIVE},
                CampaignState.ACTIVE: {CampaignState.PAUSED},
                CampaignState.PAUSED: {CampaignState.ACTIVE},
            }
            return new_state in allowed_transitions.get(campaign.state, set())
            
        return False
    
    async def grant_permission(
        self,
        campaign_id: UUID,
        user_id: UUID,
        permission: str,
        granter_id: Optional[UUID] = None,
    ) -> None:
        """Grant permission to user.
        
        Args:
            campaign_id: Campaign UUID
            user_id: User to grant permission to
            permission: Permission to grant
            granter_id: User granting permission (must have MANAGE_PERMISSIONS)
            
        Raises:
            PermissionDeniedError: If granter lacks permission
        """
        campaign = await self._get_campaign(campaign_id)
        
        # Validate granter has permission to manage permissions
        if granter_id:
            if granter_id != campaign.owner_id:
                result = await self.db.execute(
                    select(CampaignPermission)
                    .where(
                        CampaignPermission.campaign_id == campaign_id,
                        CampaignPermission.user_id == granter_id,
                        CampaignPermission.permission_type == PermissionType.MANAGE_PERMISSIONS,
                    )
                )
                if not result.scalar_one_or_none():
                    raise PermissionDeniedError("No permission to manage permissions")
        
        # Create permission record
        permission_type = getattr(PermissionType, permission.upper())
        permission = CampaignPermission(
            campaign_id=campaign_id,
            user_id=user_id,
            permission_type=permission_type,
            granted_by=granter_id or campaign.owner_id,
            granted_at=datetime.utcnow(),
        )
        self.db.add(permission)
        await self.db.flush()
    
    async def revoke_permission(
        self,
        campaign_id: UUID,
        user_id: UUID,
        permission: str,
    ) -> None:
        """Revoke permission from user.
        
        Args:
            campaign_id: Campaign UUID
            user_id: User to revoke from
            permission: Permission to revoke
        """
        campaign = await self._get_campaign(campaign_id)
        
        # Cannot revoke from owner
        if user_id == campaign.owner_id:
            raise PermissionDeniedError("Cannot revoke owner permissions")
            
        permission_type = getattr(PermissionType, permission.upper())
        await self.db.execute(
            select(CampaignPermission)
            .where(
                CampaignPermission.campaign_id == campaign_id,
                CampaignPermission.user_id == user_id,
                CampaignPermission.permission_type == permission_type,
            )
            .delete()
        )
        await self.db.flush()
    
    async def validate_operation(
        self,
        campaign_id: UUID,
        user_id: UUID,
        operation: str,
    ) -> None:
        """Validate if user can perform operation.
        
        Args:
            campaign_id: Campaign UUID
            user_id: User UUID
            operation: Operation to validate
            
        Raises:
            PermissionDeniedError: If operation not allowed
        """
        if operation == "view" and not await self.can_view(campaign_id, user_id):
            raise PermissionDeniedError("No view permission")
        elif operation == "edit" and not await self.can_edit(campaign_id, user_id):
            raise PermissionDeniedError("No edit permission")
        elif operation == "delete" and not await self.can_delete(campaign_id, user_id):
            raise PermissionDeniedError("No delete permission")
        elif operation == "change_owner":
            campaign = await self._get_campaign(campaign_id)
            if user_id != campaign.owner_id:
                raise PermissionDeniedError("Must be owner to change ownership")