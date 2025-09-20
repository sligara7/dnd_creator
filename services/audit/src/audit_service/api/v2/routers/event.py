"""
Event management router for the Audit Service.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from audit_service.core.exceptions import (
    EventProcessingError,
    EventValidationError,
    StorageError
)
from audit_service.models.events import (
    Event,
    SecurityEvent,
    UserEvent,
    SystemEvent,
    ComplianceEvent,
    BatchEventUpload
)
from audit_service.services.event_processor import EventProcessor

router = APIRouter(
    prefix="/api/v2/events",
    tags=["events"]
)

async def get_event_processor() -> EventProcessor:
    """Dependency for getting event processor instance."""
    processor = EventProcessor()
    try:
        await processor.setup()
        yield processor
    finally:
        await processor.cleanup()

@router.post(
    "",
    response_model=Event,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new audit event",
    description="Create a new audit event in the system"
)
async def create_event(
    event: Event,
    processor: EventProcessor = Depends(get_event_processor)
) -> Event:
    """Create a new audit event."""
    try:
        await processor.process_event(event)
        return event
    except EventValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except EventProcessingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post(
    "/security",
    response_model=SecurityEvent,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new security event",
    description="Create a new security-related audit event"
)
async def create_security_event(
    event: SecurityEvent,
    processor: EventProcessor = Depends(get_event_processor)
) -> SecurityEvent:
    """Create a new security event."""
    try:
        await processor.process_event(event)
        return event
    except (EventValidationError, EventProcessingError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST if isinstance(e, EventValidationError)
            else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post(
    "/user",
    response_model=UserEvent,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user event",
    description="Create a new user activity audit event"
)
async def create_user_event(
    event: UserEvent,
    processor: EventProcessor = Depends(get_event_processor)
) -> UserEvent:
    """Create a new user event."""
    try:
        await processor.process_event(event)
        return event
    except (EventValidationError, EventProcessingError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST if isinstance(e, EventValidationError)
            else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post(
    "/system",
    response_model=SystemEvent,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new system event",
    description="Create a new system-level audit event"
)
async def create_system_event(
    event: SystemEvent,
    processor: EventProcessor = Depends(get_event_processor)
) -> SystemEvent:
    """Create a new system event."""
    try:
        await processor.process_event(event)
        return event
    except (EventValidationError, EventProcessingError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST if isinstance(e, EventValidationError)
            else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post(
    "/compliance",
    response_model=ComplianceEvent,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new compliance event",
    description="Create a new compliance-related audit event"
)
async def create_compliance_event(
    event: ComplianceEvent,
    processor: EventProcessor = Depends(get_event_processor)
) -> ComplianceEvent:
    """Create a new compliance event."""
    try:
        await processor.process_event(event)
        return event
    except (EventValidationError, EventProcessingError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST if isinstance(e, EventValidationError)
            else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post(
    "/batch",
    response_model=List[Event],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple audit events",
    description="Create multiple audit events in a single batch"
)
async def create_events_batch(
    events: BatchEventUpload,
    processor: EventProcessor = Depends(get_event_processor)
) -> List[Event]:
    """Create multiple events in a batch."""
    try:
        await processor.process_batch(events)
        return events.events
    except (EventValidationError, EventProcessingError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST if isinstance(e, EventValidationError)
            else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )