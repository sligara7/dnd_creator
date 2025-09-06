"""State synchronization models."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID


class SyncState(str, Enum):
    """States for synchronization tracking."""

    SYNCED = "synced"  # State is in sync with campaign
    PENDING = "pending"  # Local changes pending sync
    CONFLICTED = "conflicted"  # Conflict detected
    ERROR = "error"  # Sync error occurred
    RECOVERING = "recovering"  # Recovering from error


class SyncDirection(str, Enum):
    """Direction of state synchronization."""

    INCOMING = "incoming"  # Campaign -> Character
    OUTGOING = "outgoing"  # Character -> Campaign
    BIDIRECTIONAL = "bidirectional"  # Full two-way sync


class FieldSyncMode(str, Enum):
    """Sync mode for individual fields."""

    FULL = "full"  # Full field value sync
    INCREMENTAL = "incremental"  # Incremental value updates
    MERGE = "merge"  # Merge conflict resolution


@dataclass
class SyncMetadata:
    """Metadata for state synchronization."""

    character_id: UUID
    campaign_id: UUID
    character_version: int  # Local character state version
    campaign_version: int  # Known campaign state version
    last_sync: datetime  # Last successful sync time
    last_error: Optional[datetime] = None  # Last sync error time
    error_count: int = 0  # Number of consecutive errors
    retries: int = 0  # Number of retry attempts


@dataclass
class SyncConfiguration:
    """Configuration for state synchronization."""

    sync_direction: SyncDirection
    field_modes: Dict[str, FieldSyncMode]  # Per-field sync modes
    conflict_strategy: str  # Strategy for conflict resolution
    sync_interval: int  # Sync interval in seconds
    retry_policy: Dict  # Retry configuration
    enabled: bool = True

    def __post_init__(self):
        """Set default retry policy."""
        if not self.retry_policy:
            self.retry_policy = {
                "max_retries": 3,
                "base_delay": 1.0,  # Base delay in seconds
                "max_delay": 60.0,  # Maximum delay in seconds
                "exponential_base": 2.0,  # Base for exponential backoff
            }


@dataclass
class StateVersion:
    """Version information for state synchronization."""

    version: int
    timestamp: datetime
    parent_version: Optional[int] = None
    campaign_version: Optional[int] = None
    changes: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class StateChange:
    """Represents a change in state."""

    character_id: UUID
    campaign_id: UUID
    field_path: str  # Dotted path to changed field
    old_value: Optional[Dict] = None
    new_value: Optional[Dict] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = "character"  # Source of change (character/campaign)
    sync_mode: FieldSyncMode = FieldSyncMode.FULL


@dataclass
class SyncMessage:
    """Message for state synchronization."""

    message_id: UUID
    character_id: UUID
    campaign_id: UUID
    character_version: int
    campaign_version: int
    changes: List[StateChange]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    parent_message_id: Optional[UUID] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class SyncConflict:
    """Represents a synchronization conflict."""

    character_id: UUID
    campaign_id: UUID
    field_path: str
    character_value: Dict
    campaign_value: Dict
    character_version: int
    campaign_version: int
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolution_strategy: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_value: Optional[Dict] = None


@dataclass
class SyncError:
    """Represents a synchronization error."""

    character_id: UUID
    campaign_id: UUID
    error_type: str
    error_message: str
    state_version: int
    campaign_version: int
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    retry_count: int = 0
    recovery_strategy: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class SyncSubscription:
    """Campaign state subscription."""

    character_id: UUID
    campaign_id: UUID
    fields: List[str]  # Fields to sync
    sync_mode: SyncDirection
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_update: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)
