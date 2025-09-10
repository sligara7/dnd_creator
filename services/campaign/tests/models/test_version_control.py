"""Tests for campaign version control models."""
from datetime import datetime, UTC
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError 
from sqlalchemy.orm import selectinload

from campaign_service.models.campaign import Campaign, CampaignType, CampaignState
from campaign_service.models.version_control import (
    Branch,
    BranchType,
    BranchState,
    Commit,
    Change,
)


@pytest.fixture
async def campaign(test_db):
    """Create a test campaign."""
    campaign = Campaign(
        name="Test Campaign",
        description="A test campaign",
        campaign_type=CampaignType.TRADITIONAL,
        state=CampaignState.DRAFT,
        creator_id=uuid4(),
        owner_id=uuid4(),
    )
    test_db.add(campaign)
    await test_db.flush()
    return campaign


async def test_branch_creation_root(test_db, campaign):
    """Test creating a root branch with no base branch."""
    # Create root branch (MAIN type, no base branch)
    root_branch = Branch(
        name="main",
        description="Main campaign branch",
        type=BranchType.MAIN,
        campaign_id=campaign.id,  # Reference the test campaign
        base_branch_id=None  # Root branch has no base
    )
    test_db.add(root_branch)
    await test_db.flush()

    assert root_branch.id is not None
    assert root_branch.base_branch_id is None
    assert root_branch.type == BranchType.MAIN
    assert root_branch.state == BranchState.ACTIVE
    assert root_branch.created_at is not None
    assert root_branch.updated_at is not None


async def test_branch_creation_feature(test_db, campaign):
    """Test creating a feature branch with a base branch."""
    # First create root branch
    root_branch = Branch(
        name="main",
        description="Main campaign branch",
        type=BranchType.MAIN,
        campaign_id=campaign.id,
        base_branch_id=None
    )
    test_db.add(root_branch)
    await test_db.flush()

    # Now create feature branch
    feature_branch = Branch(
        name="feature/new-quest",
        description="New quest line",
        type=BranchType.FEATURE,
        campaign_id=campaign.id,
        base_branch_id=root_branch.id
    )
    test_db.add(feature_branch)
    await test_db.flush()

    assert feature_branch.id is not None
    assert feature_branch.base_branch_id == root_branch.id
    assert feature_branch.type == BranchType.FEATURE
    assert feature_branch.state == BranchState.ACTIVE
    assert feature_branch.created_at is not None
    assert feature_branch.updated_at is not None


async def test_branch_self_reference_prevented(test_db, campaign):
    """Test that a branch cannot reference itself as its base branch."""
    # Create a branch first
    branch = Branch(
        name="test",
        description="Test branch",
        type=BranchType.FEATURE,
        campaign_id=campaign.id,
        base_branch_id=None
    )
    test_db.add(branch)
    await test_db.flush()

    # Try to set branch as its own base
    with pytest.raises(ValueError) as exc_info:
        branch.base_branch_id = branch.id

    assert str(exc_info.value) == "Branch cannot reference itself as base branch"


async def test_branch_name_validation(test_db, campaign):
    """Test branch name validation."""
    # Try to create branch with space in name
    with pytest.raises(ValueError) as exc_info:
        branch = Branch(
            name="invalid branch name",
            description="Test branch",
            type=BranchType.FEATURE,
            campaign_id=campaign.id,
            base_branch_id=None
        )
        test_db.add(branch)
        await test_db.flush()

    assert "Branch name cannot contain spaces" in str(exc_info.value)

    # Valid branch names should work
    valid_names = [
        "main",
        "feature/new-quest",
        "hotfix/bug-123",
        "release/v1.0.0"
    ]
    
    for name in valid_names:
        branch = Branch(
            name=name,
            description="Test branch",
            type=BranchType.FEATURE,
            campaign_id=campaign.id,
            base_branch_id=None
        )
        test_db.add(branch)
        await test_db.flush()
        assert branch.name == name


async def test_commit_creation(test_db, campaign):
    """Test creating a commit in a branch."""
    # Create root branch
    branch = Branch(
        name="main",
        description="Main campaign branch",
        type=BranchType.MAIN,
        campaign_id=campaign.id,
        base_branch_id=None
    )
    test_db.add(branch)
    await test_db.flush()

    # Create initial commit
    commit = Commit(
        message="Initial commit",
        branch_id=branch.id,
        parent_commit_id=None
    )
    test_db.add(commit)
    await test_db.flush()

    assert commit.id is not None
    assert commit.branch_id == branch.id
    assert commit.parent_commit_id is None
    assert commit.created_at is not None
    assert isinstance(commit.meta, dict)


async def test_commit_with_changes(test_db, campaign):
    """Test creating a commit with associated changes."""
    # Create branch and initial commit
    branch = Branch(
        name="main",
        description="Main branch",
        type=BranchType.MAIN,
        campaign_id=campaign.id,
        base_branch_id=None
    )
    test_db.add(branch)
    await test_db.flush()

    commit = Commit(
        message="Update NPC stats",
        branch_id=branch.id,
        parent_commit_id=None
    )
    test_db.add(commit)
    await test_db.flush()

    # Create change records
    changes = [
        Change(
            commit_id=commit.id,
            entity_id=uuid4(),
            entity_type="npc",
            field_name="stats",
            old_value={"strength": 10},
            new_value={"strength": 12}
        ),
        Change(
            commit_id=commit.id,
            entity_id=uuid4(),
            entity_type="npc",
            field_name="level",
            old_value={"level": 1},
            new_value={"level": 2}
        )
    ]
    
    for change in changes:
        test_db.add(change)
    await test_db.flush()

    # Verify relationships with eager loading
    query = select(Commit).options(selectinload(Commit.changes)).where(Commit.id == commit.id)
    result = await test_db.execute(query)
    db_commit = result.unique().scalar_one()
    
    assert len(db_commit.changes) == 2
    assert all(change.commit_id == commit.id for change in db_commit.changes)
    assert all(isinstance(change.created_at, datetime) for change in db_commit.changes)
