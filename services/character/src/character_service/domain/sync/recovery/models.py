"""Models for sync error handling and recovery."""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ErrorType(str, Enum):
    """Types of sync errors."""

    MESSAGE_HANDLING = "message_handling"
    STATE_SYNC = "state_sync"
    SUBSCRIPTION = "subscription"
    CONFLICT = "conflict" 
    NETWORK = "network"


class ErrorStatus(str, Enum):
    """Status of sync errors."""

    NEW = "new"
    RETRYING = "retrying"
    RESOLVED = "resolved"
    FAILED = "failed"


class RecoveryMetrics(BaseModel):
    """Metrics for sync error recovery."""

    error_count: int = 0
    resolved_count: int = 0
    retry_count: int = 0
    success_rate: float = 0.0
    avg_resolution_time: float = 0.0
    failures_by_type: Dict[str, int] = Field(default_factory=dict)


class SyncErrorLog(BaseModel):
    """Log entry for a sync error."""

    error_id: UUID
    character_id: UUID
    campaign_id: UUID
    error_type: ErrorType
    error_message: str
    status: ErrorStatus
    retry_count: int = 0
    max_retries: int = 5
    last_retry: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    resolution_details: Optional[str] = None
    state_version: int
    campaign_version: int
    metadata: Dict = Field(default_factory=dict)

    class Config:
        """Pydantic config."""

        use_enum_values = True
