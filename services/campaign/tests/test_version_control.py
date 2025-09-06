"""Test suite for version control system."""
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from campaign_service.core.exceptions import StateError, ValidationError, VersionControlError
from campaign_service.models.version import Branch, BranchType, StateTransition, Version, VersionType
from campaign_service.repositories.campaign import CampaignRepository
from campaign_service.repositories.version import (
    BranchRepository,
    StateTransitionRepository,
    VersionRepository,
)
from campaign_service.services.state_tracking import StateTrackingService
from campaign_service.services.version_control import VersionControlService


@pytest.fixture
def message_hub_mock():
    """Mock message hub client."""
    return AsyncMock()


@pytest.fixture
async def version_control(
    db_session: AsyncSession,
    message_hub_mock: AsyncMock,
) -> VersionControlService:
    """Create version control service."""
    campaign_repo = CampaignRepository(db_session)
    version_repo = VersionRepository(db_session)
    branch_repo = BranchRepository(db_session)
    state_repo = StateTransitionRepository(db_session)

    return VersionControlService(
        db=db_session,
        campaign_repo=campaign_repo,
        version_repo=version_repo,
        branch_repo=branch_repo,
        state_repo=state_repo,
        message_hub_client=message_hub_mock,
    )


@pytest.fixture
async def state_tracking(
    db_session: AsyncSession,
    version_control: VersionControlService,
    message_hub_mock: AsyncMock,
) -> StateTrackingService:
    """Create state tracking service."""
    campaign_repo = CampaignRepository(db_session)
    version_repo = VersionRepository(db_session)
    state_repo = StateTransitionRepository(db_session)

    return StateTrackingService(
        db=db_session,
        campaign_repo=campaign_repo,
        version_repo=version_repo,
        state_repo=state_repo,
        version_control=version_control,
        message_hub_client=message_hub_mock,
    )


class TestVersionControlService:
    """Test version control service."""

    async def test_initialize_versioning(
        self,
        version_control: VersionControlService,
        message_hub_mock: AsyncMock,
    ):
        """Test initializing version control."""
        campaign_id = UUID("12345678-1234-5678-1234-567812345678")
        author = "test_user"
        initial_content = {
            "name": "Test Campaign",
            "description": "Test campaign description",
            "theme": "fantasy",
            "chapters": [],
            "npcs": [],
            "locations": [],
        }

        # Initialize versioning
        main_branch, initial_version = await version_control.initialize_campaign_versioning(
            campaign_id=campaign_id,
            initial_content=initial_content,
            author=author,
        )

        # Verify branch
        assert main_branch.name == "main"
        assert main_branch.branch_type == BranchType.MAIN
        assert main_branch.campaign_id == campaign_id
        assert not main_branch.is_deleted

        # Verify version
        assert initial_version.campaign_id == campaign_id
        assert initial_version.branch_id == main_branch.id
        assert initial_version.version_type == VersionType.SKELETON
        assert initial_version.content == initial_content
        assert initial_version.author == author
        assert not initial_version.is_deleted

        # Verify event published
        message_hub_mock.publish.assert_called_once_with(
            "campaign.version_control_initialized",
            {
                "campaign_id": str(campaign_id),
                "branch_id": str(main_branch.id),
                "version_id": str(initial_version.id),
                "author": author,
            },
        )

    async def test_create_version(
        self,
        version_control: VersionControlService,
        message_hub_mock: AsyncMock,
    ):
        """Test creating a version."""
        campaign_id = UUID("12345678-1234-5678-1234-567812345678")
        branch_id = UUID("87654321-8765-4321-8765-432187654321")
        author = "test_user"
        title = "Test Version"
        message = "Test commit message"
        content = {
            "name": "Test Campaign",
            "description": "Updated description",
            "theme": "fantasy",
            "chapters": [{"id": "123", "title": "Chapter 1"}],
            "npcs": [],
            "locations": [],
        }

        # Create version
        version = await version_control.create_version(
            campaign_id=campaign_id,
            branch_id=branch_id,
            content=content,
            title=title,
            message=message,
            author=author,
        )

        # Verify version
        assert version.campaign_id == campaign_id
        assert version.branch_id == branch_id
        assert version.title == title
        assert version.message == message
        assert version.author == author
        assert version.content == content
        assert not version.is_deleted

        # Verify event published
        message_hub_mock.publish.assert_called_once_with(
            "campaign.version_created",
            {
                "campaign_id": str(campaign_id),
                "version_id": str(version.id),
                "branch_id": str(branch_id),
                "type": VersionType.DRAFT.value,
                "author": author,
            },
        )

    async def test_merge_branches(
        self,
        version_control: VersionControlService,
        message_hub_mock: AsyncMock,
    ):
        """Test merging branches."""
        campaign_id = UUID("12345678-1234-5678-1234-567812345678")
        source_branch_id = UUID("11111111-1111-1111-1111-111111111111")
        target_branch_id = UUID("22222222-2222-2222-2222-222222222222")
        author = "test_user"
        message = "Merge test branch into main"

        # Create version
        merge_version = await version_control.merge_branches(
            campaign_id=campaign_id,
            source_branch_id=source_branch_id,
            target_branch_id=target_branch_id,
            author=author,
            message=message,
        )

        # Verify version
        assert merge_version.campaign_id == campaign_id
        assert merge_version.branch_id == target_branch_id
        assert merge_version.version_type == VersionType.MERGE
        assert merge_version.author == author
        assert merge_version.message == message
        assert not merge_version.is_deleted

        # Verify event published
        message_hub_mock.publish.assert_called_once_with(
            "campaign.branches_merged",
            {
                "campaign_id": str(campaign_id),
                "source_branch_id": str(source_branch_id),
                "target_branch_id": str(target_branch_id),
                "merge_version_id": str(merge_version.id),
                "author": author,
            },
        )


class TestStateTrackingService:
    """Test state tracking service."""

    async def test_validate_state_change(
        self,
        state_tracking: StateTrackingService,
    ):
        """Test validating state changes."""
        campaign_id = UUID("12345678-1234-5678-1234-567812345678")
        current_state = {
            "theme": "fantasy",
            "chapters": [{"id": "123", "title": "Chapter 1"}],
            "npcs": [],
            "locations": [],
        }
        new_state = {
            "theme": "fantasy",  # Same theme
            "chapters": [
                {"id": "123", "title": "Chapter 1"},  # Existing chapter
                {"id": "456", "title": "Chapter 2"},  # New chapter
            ],
            "npcs": [],
            "locations": [],
        }

        # Validate state change
        is_valid = await state_tracking.validate_state_change(
            campaign_id=campaign_id,
            current_state=current_state,
            new_state=new_state,
        )
        assert is_valid is True

        # Test theme change validation
        with pytest.raises(ValidationError):
            invalid_state = new_state.copy()
            invalid_state["theme"] = "cyberpunk"  # Changed theme
            await state_tracking.validate_state_change(
                campaign_id=campaign_id,
                current_state=current_state,
                new_state=invalid_state,
            )

        # Test required fields validation
        with pytest.raises(ValidationError):
            invalid_state = new_state.copy()
            del invalid_state["theme"]  # Missing required field
            await state_tracking.validate_state_change(
                campaign_id=campaign_id,
                current_state=current_state,
                new_state=invalid_state,
            )

    async def test_create_state_transition(
        self,
        state_tracking: StateTrackingService,
        message_hub_mock: AsyncMock,
    ):
        """Test creating state transitions."""
        campaign_id = UUID("12345678-1234-5678-1234-567812345678")
        version_id = UUID("87654321-8765-4321-8765-432187654321")
        from_state = {
            "theme": "fantasy",
            "chapters": [{"id": "123", "title": "Chapter 1"}],
            "npcs": [],
            "locations": [],
        }
        to_state = {
            "theme": "fantasy",
            "chapters": [
                {"id": "123", "title": "Chapter 1"},
                {"id": "456", "title": "Chapter 2"},
            ],
            "npcs": [],
            "locations": [],
        }

        # Create state transition
        transition = await state_tracking.create_state_transition(
            campaign_id=campaign_id,
            version_id=version_id,
            from_state=from_state,
            to_state=to_state,
            transition_type="update",
            reason="Added new chapter",
        )

        # Verify transition
        assert transition.campaign_id == campaign_id
        assert transition.version_id == version_id
        assert transition.from_state == from_state
        assert transition.to_state == to_state
        assert transition.transition_type == "update"
        assert transition.reason == "Added new chapter"

        # Verify event published
        message_hub_mock.publish.assert_called_once_with(
            "campaign.state_transition",
            {
                "campaign_id": str(campaign_id),
                "version_id": str(version_id),
                "transition_id": str(transition.id),
                "type": "update",
            },
        )


class TestVersionControlAPI:
    """Test version control API endpoints."""

    async def test_create_version_endpoint(self, test_client: AsyncClient):
        """Test version creation endpoint."""
        campaign_id = UUID("12345678-1234-5678-1234-567812345678")
        branch_id = UUID("87654321-8765-4321-8765-432187654321")
        request_data = {
            "content": {
                "name": "Test Campaign",
                "description": "Test description",
                "theme": "fantasy",
                "chapters": [],
                "npcs": [],
                "locations": [],
            },
            "title": "Initial version",
            "message": "Initial commit",
            "author": "test_user",
        }

        response = await test_client.post(
            f"/api/v2/campaigns/{campaign_id}/versions?branch_id={branch_id}",
            json=request_data,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["campaign_id"] == str(campaign_id)
        assert data["branch_id"] == str(branch_id)
        assert data["title"] == request_data["title"]
        assert data["message"] == request_data["message"]
        assert data["author"] == request_data["author"]
        assert data["content"] == request_data["content"]

    async def test_create_branch_endpoint(self, test_client: AsyncClient):
        """Test branch creation endpoint."""
        campaign_id = UUID("12345678-1234-5678-1234-567812345678")
        request_data = {
            "name": "feature-branch",
            "branch_type": "player_choice",
            "description": "Player choice branch",
            "base_version_hash": "a" * 64,
        }

        response = await test_client.post(
            f"/api/v2/campaigns/{campaign_id}/branches",
            json=request_data,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["campaign_id"] == str(campaign_id)
        assert data["name"] == request_data["name"]
        assert data["branch_type"] == request_data["branch_type"]
        assert data["description"] == request_data["description"]
        assert data["base_version_hash"] == request_data["base_version_hash"]

    async def test_merge_branches_endpoint(self, test_client: AsyncClient):
        """Test branch merge endpoint."""
        campaign_id = UUID("12345678-1234-5678-1234-567812345678")
        request_data = {
            "source_branch_id": str(UUID("11111111-1111-1111-1111-111111111111")),
            "target_branch_id": str(UUID("22222222-2222-2222-2222-222222222222")),
            "author": "test_user",
            "message": "Merge feature branch",
        }

        response = await test_client.post(
            f"/api/v2/campaigns/{campaign_id}/branches/merge",
            json=request_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["campaign_id"] == str(campaign_id)
        assert data["version_type"] == VersionType.MERGE.value
        assert data["author"] == request_data["author"]
        assert data["message"] == request_data["message"]
