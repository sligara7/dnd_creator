"""Tests for campaign version control models."""
import pytest
from datetime import datetime, UTC
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from campaign_service.models.version_control import (
    BranchType,
    BranchState,
    Branch,
    Commit,
    Change,
)

# Test Data Fixtures

@pytest.fixture
def branch_data():
    """Provide test data for a campaign branch."""
    # Create a root branch first (no base branch)
    root_branch = Branch(
        name="main",
        description="Main campaign branch",
        type=BranchType.MAIN,
        state=BranchState.ACTIVE,
        base_branch_id=None,  # Root branch has no parent
        campaign_id=UUID("00000000-0000-0000-0000-000000000002"),
        metadata={"author": "DM Steve"}
    )

    # Return feature branch data that references the root branch
    return {
        "name": "feature/new-quest-line",
        "description": "Adding a side quest branch",
        "type": BranchType.FEATURE,
        "state": BranchState.ACTIVE,
        "base_branch_id": root_branch.id,  # Reference the root branch
        "campaign_id": UUID("00000000-0000-0000-0000-000000000002"),
        "metadata": {
            "author": "DM Steve",
            "tags": ["side-quest", "level-5"],
        }
    }, root_branch

@pytest.fixture
def commit_data(request):
    """Provide test data for a commit."""
    # Use the root branch created in the branch_data fixture
    _, root_branch = request.getfixturevalue("branch_data")
    
    return {
        "message": "Added initial quest structure",
        "branch_id": root_branch.id,  # Use the root branch's ID
        "parent_commit_id": None,  # Initial commit
        "metadata": {
            "author": "DM Steve",
            "co-authors": ["DM Jane"],
            "affected_chapters": ["Chapter 1", "Chapter 2"],
        }
    }

@pytest.fixture
async def change_data(request, test_db):
    """Provide test data for content changes."""
    # Create initial branch and commit
    _, root_branch = request.getfixturevalue("branch_data")
    
    # Add root branch
    test_db.add(root_branch)
    await test_db.flush()
    
    # Create initial commit
    commit = Commit(
        message="Initial commit",
        branch_id=root_branch.id,
        parent_commit_id=None,
        metadata={}
    )
    test_db.add(commit)
    await test_db.flush()
    
    return {
        "commit_id": commit.id,  # Use the created commit's ID
        "entity_id": UUID("00000000-0000-0000-0000-000000000002"),
        "entity_type": "Chapter",
        "field_name": "content",
        "old_value": {
            "title": "The Old Beginning",
            "description": "Original chapter content",
        },
        "new_value": {
            "title": "A New Beginning",
            "description": "Updated chapter content",
        },
        "metadata": {
            "change_type": "update",
            "reason": "Improving chapter flow",
        }
    }


@pytest.mark.asyncio
class TestVersionControlModels:
    """Test version control model functionality."""
    
    async def test_branch_creation(self, test_db: AsyncSession, branch_data):
        """Test creating a new branch."""
        feature_data, root_branch = branch_data
        
        # Create root branch first
        test_db.add(root_branch)
        await test_db.flush()
        
        # Create feature branch
        feature_branch = Branch(**feature_data)
        test_db.add(feature_branch)
        await test_db.flush()

        # Verify fields
        assert isinstance(feature_branch.id, UUID)
        assert feature_branch.name == feature_data["name"]
        assert feature_branch.type == BranchType.FEATURE
        assert feature_branch.state == BranchState.ACTIVE
        assert feature_branch.base_branch_id == feature_data["base_branch_id"]
        assert feature_branch.campaign_id == feature_data["campaign_id"]
        assert feature_branch.meta == feature_data["metadata"]
        assert isinstance(feature_branch.created_at, datetime)
        assert feature_branch.created_at.tzinfo == UTC

    async def test_commit_creation(self, test_db: AsyncSession, branch_data, commit_data):
        # Create root branch first
        feature_data, root_branch = branch_data
        test_db.add(root_branch)
        await test_db.flush()
        """Test creating a new commit."""
        # Create commit
        commit = Commit(**commit_data)
        test_db.add(commit)
        await test_db.flush()

        # Verify fields
        assert isinstance(commit.id, UUID)
        assert commit.message == commit_data["message"]
        assert commit.branch_id == commit_data["branch_id"]
        assert commit.parent_commit_id == commit_data["parent_commit_id"]
        assert commit.meta == commit_data["metadata"]
        assert isinstance(commit.created_at, datetime)
        assert commit.created_at.tzinfo == UTC

    async def test_change_creation(self, test_db: AsyncSession, change_data):
        """Test creating a new change record."""
        # Create change
        change = Change(**change_data)
        test_db.add(change)
        await test_db.flush()

        # Verify fields
        assert isinstance(change.id, UUID)
        assert change.commit_id == change_data["commit_id"]
        assert change.entity_id == change_data["entity_id"]
        assert change.entity_type == change_data["entity_type"]
        assert change.field_name == change_data["field_name"]
        assert change.old_value == change_data["old_value"]
        assert change.new_value == change_data["new_value"]
        assert change.meta == change_data["metadata"]

    async def test_branch_commit_relationship(self, test_db: AsyncSession, branch_data, commit_data):
        """Test relationship between branches and commits."""
        # Create branch
        feature_data, root_branch = branch_data
        test_db.add(root_branch)
        await test_db.flush()

        # Create commit with original branch (root)
        commit = Commit(**commit_data)
        test_db.add(commit)
        await test_db.flush()

        # Test relationships
        assert commit in root_branch.commits
        assert commit.branch == root_branch

    async def test_commit_change_relationship(self, test_db: AsyncSession, commit_data, change_data):
        """Test relationship between commits and changes."""
        # Branch and commit should already be created by the fixtures

        # Create change
        change = Change(**change_data)
        test_db.add(change)
        await test_db.flush()

        # Test relationships
        assert change in commit.changes
        assert change.commit == commit

    async def test_branch_state_transitions(self, test_db: AsyncSession, branch_data):
        """Test branch state transitions."""
        # Create root branch first
        feature_data, root_branch = branch_data
        test_db.add(root_branch)
        await test_db.flush()
        
        # Create feature branch
        branch = Branch(**feature_data)
        test_db.add(branch)
        await test_db.flush()

        # Test state transitions
        branch.state = BranchState.MERGED
        await test_db.flush()
        assert branch.state == BranchState.MERGED

        branch.state = BranchState.ARCHIVED
        await test_db.flush()
        assert branch.state == BranchState.ARCHIVED

    async def test_branch_validation(self, test_db: AsyncSession, branch_data):
        """Test branch validation rules."""
        feature_data, root_branch = branch_data

        # Test invalid branch name
        invalid_data = feature_data.copy()
        invalid_data["name"] = "invalid space name"
        with pytest.raises(ValueError):
            Branch(**invalid_data)

        # Test invalid base branch reference (self-reference)
        branch = Branch(**{**branch_data, "name": "valid/name"})
        test_db.add(branch)
        await test_db.flush()
        
        with pytest.raises(ValueError):
            branch.base_branch_id = branch.id
