"""Unit tests for campaign permissions and ownership validation."""
import pytest
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from campaign_service.models.campaign import Campaign, CampaignType, CampaignState
from campaign_service.services.permissions import CampaignPermissions
from campaign_service.exceptions import PermissionDeniedError


@pytest.fixture
async def campaign_permissions(test_db: AsyncSession) -> CampaignPermissions:
    """Create permissions service fixture."""
    return CampaignPermissions(test_db)


@pytest.fixture
async def test_campaign(test_db: AsyncSession) -> Campaign:
    """Create a test campaign."""
    campaign = Campaign(
        name="Test Campaign",
        description="A test campaign",
        campaign_type=CampaignType.TRADITIONAL,
        state=CampaignState.DRAFT,
        theme_data={},
        campaign_metadata={},
        creator_id=UUID("00000000-0000-0000-0000-000000000001"),
        owner_id=UUID("00000000-0000-0000-0000-000000000001"),
    )
    test_db.add(campaign)
    await test_db.flush()
    return campaign


@pytest.mark.asyncio
class TestCampaignPermissions:
    """Test campaign permissions and ownership validation."""
    
    async def test_campaign_ownership_validation(
        self,
        test_db: AsyncSession,
        campaign_permissions: CampaignPermissions,
        test_campaign: Campaign,
    ) -> None:
        """Test campaign ownership validation."""
        # Owner should have all permissions
        owner_id = test_campaign.owner_id
        assert await campaign_permissions.can_view(test_campaign.id, owner_id)
        assert await campaign_permissions.can_edit(test_campaign.id, owner_id)
        assert await campaign_permissions.can_delete(test_campaign.id, owner_id)
        
        # Non-owner should not have permissions
        other_user_id = UUID("00000000-0000-0000-0000-000000000002")
        assert not await campaign_permissions.can_edit(test_campaign.id, other_user_id)
        assert not await campaign_permissions.can_delete(test_campaign.id, other_user_id)
    
    async def test_campaign_creator_permissions(
        self,
        test_db: AsyncSession,
        campaign_permissions: CampaignPermissions,
        test_campaign: Campaign,
    ) -> None:
        """Test campaign creator permissions."""
        # Creator should have view and edit permissions
        creator_id = test_campaign.creator_id
        assert await campaign_permissions.can_view(test_campaign.id, creator_id)
        assert await campaign_permissions.can_edit(test_campaign.id, creator_id)
        
        # But creator should not have delete permission if not owner
        if creator_id != test_campaign.owner_id:
            assert not await campaign_permissions.can_delete(test_campaign.id, creator_id)
    
    async def test_campaign_sharing_permissions(
        self,
        test_db: AsyncSession,
        campaign_permissions: CampaignPermissions,
        test_campaign: Campaign,
    ) -> None:
        """Test campaign sharing permissions."""
        shared_user_id = UUID("00000000-0000-0000-0000-000000000003")
        
        # Initially user should not have access
        assert not await campaign_permissions.can_view(test_campaign.id, shared_user_id)
        
        # Add view permission
        await campaign_permissions.grant_permission(
            campaign_id=test_campaign.id,
            user_id=shared_user_id,
            permission="view",
        )
        assert await campaign_permissions.can_view(test_campaign.id, shared_user_id)
        assert not await campaign_permissions.can_edit(test_campaign.id, shared_user_id)
        
        # Add edit permission
        await campaign_permissions.grant_permission(
            campaign_id=test_campaign.id,
            user_id=shared_user_id,
            permission="edit",
        )
        assert await campaign_permissions.can_edit(test_campaign.id, shared_user_id)
        
        # Revoke permissions
        await campaign_permissions.revoke_permission(
            campaign_id=test_campaign.id,
            user_id=shared_user_id,
            permission="edit",
        )
        assert not await campaign_permissions.can_edit(test_campaign.id, shared_user_id)
        assert await campaign_permissions.can_view(test_campaign.id, shared_user_id)
    
    async def test_campaign_state_transition_permissions(
        self,
        test_db: AsyncSession,
        campaign_permissions: CampaignPermissions,
        test_campaign: Campaign,
    ) -> None:
        """Test permissions for campaign state transitions."""
        other_user_id = UUID("00000000-0000-0000-0000-000000000002")
        
        # Owner should be able to change state
        assert await campaign_permissions.can_change_state(
            test_campaign.id,
            test_campaign.owner_id,
            CampaignState.ACTIVE,
        )
        
        # Non-owner should not be able to change state
        assert not await campaign_permissions.can_change_state(
            test_campaign.id,
            other_user_id,
            CampaignState.ACTIVE,
        )
        
        # Add edit permission
        await campaign_permissions.grant_permission(
            campaign_id=test_campaign.id,
            user_id=other_user_id,
            permission="edit",
        )
        
        # User with edit permission should be able to change some states
        assert await campaign_permissions.can_change_state(
            test_campaign.id,
            other_user_id,
            CampaignState.PAUSED,
        )
        
        # But should not be able to mark as completed
        assert not await campaign_permissions.can_change_state(
            test_campaign.id,
            other_user_id,
            CampaignState.COMPLETED,
        )
    
    async def test_campaign_permission_error_handling(
        self,
        test_db: AsyncSession,
        campaign_permissions: CampaignPermissions,
        test_campaign: Campaign,
    ) -> None:
        """Test error handling for permission operations."""
        unauthorized_user_id = UUID("00000000-0000-0000-0000-000000000004")
        
        # Try to grant permission without authorization
        with pytest.raises(PermissionDeniedError):
            await campaign_permissions.grant_permission(
                campaign_id=test_campaign.id,
                user_id=unauthorized_user_id,
                permission="view",
                granter_id=unauthorized_user_id,  # Unauthorized user trying to grant
            )
        
        # Try to perform operation without permission
        with pytest.raises(PermissionDeniedError):
            await campaign_permissions.validate_operation(
                campaign_id=test_campaign.id,
                user_id=unauthorized_user_id,
                operation="edit",
            )
        
        # Try to change critical settings without ownership
        with pytest.raises(PermissionDeniedError):
            await campaign_permissions.validate_operation(
                campaign_id=test_campaign.id,
                user_id=unauthorized_user_id,
                operation="change_owner",
            )