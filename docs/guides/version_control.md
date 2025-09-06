# Campaign Version Control System

## Overview

The campaign version control system provides Git-like version control for D&D campaigns, enabling branching storylines, state management, and campaign evolution tracking. It supports both traditional D&D campaigns and Antitheticon campaigns with identity deception networks.

## Architecture

The version control system consists of three main components:

1. **Version Control Service**: Manages campaign versions, branches, and merges
2. **State Tracking Service**: Validates state changes and tracks transitions
3. **Message Hub Integration**: Handles event publishing for cross-service coordination

### Key Models

```python
# Version model (commits)
class Version:
    id: UUID
    campaign_id: UUID
    branch_id: UUID
    parent_id: Optional[UUID]
    version_hash: str
    version_type: VersionType
    title: str
    message: str
    author: str
    content: Dict
    metadata: Dict
    created_at: datetime
    is_deleted: bool

# Branch model
class Branch:
    id: UUID
    campaign_id: UUID
    name: str
    branch_type: BranchType
    description: str
    base_version_hash: str
    created_at: datetime
    is_deleted: bool

# State transition model
class StateTransition:
    id: UUID
    campaign_id: UUID
    version_id: UUID
    from_state: Dict
    to_state: Dict
    transition_type: str
    reason: str
    created_at: datetime
```

## API Endpoints

### Version Management

```http
# Create new version
POST /api/v2/campaigns/{campaign_id}/versions?branch_id={branch_id}
Content-Type: application/json

{
    "content": {
        "name": "Campaign Name",
        "description": "Campaign description",
        "theme": "fantasy",
        "chapters": [],
        "npcs": [],
        "locations": []
    },
    "title": "Version title",
    "message": "Commit message",
    "author": "username"
}

# List versions
GET /api/v2/campaigns/{campaign_id}/versions
```

### Branch Management

```http
# Create new branch
POST /api/v2/campaigns/{campaign_id}/branches
Content-Type: application/json

{
    "name": "feature-branch",
    "branch_type": "player_choice",
    "description": "Branch description",
    "base_version_hash": "hash_of_base_version"
}

# List branches
GET /api/v2/campaigns/{campaign_id}/branches

# Merge branches
POST /api/v2/campaigns/{campaign_id}/branches/merge
Content-Type: application/json

{
    "source_branch_id": "uuid_of_source",
    "target_branch_id": "uuid_of_target",
    "author": "username",
    "message": "Merge message"
}
```

## Usage Examples

### Creating a Campaign Branch

```python
from uuid import UUID
from campaign_service.models.version import BranchType
from campaign_service.services.version_control import VersionControlService

async def create_player_choice_branch(
    campaign_id: UUID,
    base_version_hash: str,
    version_control: VersionControlService,
) -> None:
    # Create new branch
    branch = await version_control.create_branch(
        campaign_id=campaign_id,
        name="player-choice-1",
        branch_type=BranchType.PLAYER_CHOICE,
        description="Alternative path based on player choice",
        base_version_hash=base_version_hash,
    )

    # Create initial version in new branch
    version = await version_control.create_version(
        campaign_id=campaign_id,
        branch_id=branch.id,
        content={
            "name": "Campaign Name",
            "theme": "fantasy",
            "chapters": [
                {"id": "123", "title": "Alternative Chapter 1"}
            ]
        },
        title="Initial version",
        message="Created alternative path",
        author="dm@example.com",
    )
```

### Merging Branches

```python
async def merge_player_choice(
    campaign_id: UUID,
    source_branch_id: UUID,
    target_branch_id: UUID,
    version_control: VersionControlService,
) -> None:
    # Merge source branch into target
    merge_version = await version_control.merge_branches(
        campaign_id=campaign_id,
        source_branch_id=source_branch_id,
        target_branch_id=target_branch_id,
        author="dm@example.com",
        message="Merging player choice into main storyline",
    )
```

## State Validation

The system enforces several validation rules for state changes:

1. **Theme Consistency**: Campaign theme cannot be changed after initialization
2. **Required Fields**: Core campaign fields must always be present
3. **ID Preservation**: Entity IDs must be preserved across versions
4. **Content Validation**: New content must meet schema requirements
5. **Relationship Integrity**: References between entities must remain valid

Example validation:

```python
from campaign_service.services.state_tracking import StateTrackingService

async def validate_campaign_update(
    campaign_id: UUID,
    current_state: Dict,
    new_state: Dict,
    state_tracking: StateTrackingService,
) -> bool:
    try:
        # Validate state change
        is_valid = await state_tracking.validate_state_change(
            campaign_id=campaign_id,
            current_state=current_state,
            new_state=new_state,
        )
        return is_valid
    except ValidationError as e:
        print(f"Invalid state change: {e}")
        return False
```

## Events and Integration

The system publishes events through Message Hub for various operations:

### Version Control Events

1. `campaign.version_control_initialized`
   - Triggered when versioning is initialized for a campaign
   - Contains campaign ID, branch ID, and version ID

2. `campaign.version_created`
   - Triggered when a new version is created
   - Contains version details and parent information

3. `campaign.branches_merged`
   - Triggered when branches are merged
   - Contains source and target branch information

### State Tracking Events

1. `campaign.state_transition`
   - Triggered when campaign state changes
   - Contains old and new state details

2. `campaign.state_validation_failed`
   - Triggered when state validation fails
   - Contains validation error details

## Error Handling

The system defines several custom exceptions:

```python
class VersionControlError(Exception):
    """Base exception for version control operations."""
    pass

class ValidationError(Exception):
    """Raised when state validation fails."""
    pass

class StateError(Exception):
    """Raised for state transition errors."""
    pass

class MergeConflictError(VersionControlError):
    """Raised when branch merge conflicts occur."""
    pass
```

## Testing

The test suite covers all major components:

1. **Unit Tests**
   - Version control service operations
   - State validation and transitions
   - Model validations

2. **Integration Tests**
   - API endpoint functionality
   - Event publishing
   - Cross-service coordination

3. **Error Cases**
   - Invalid state changes
   - Merge conflicts
   - Missing dependencies

Example test:

```python
@pytest.mark.asyncio
async def test_validate_state_change(
    state_tracking: StateTrackingService,
):
    """Test state change validation."""
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
```
