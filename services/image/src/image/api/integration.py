"""API endpoints for service integration and event handling."""
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query, Response, status

from image.api.models import (
    BulkOperationResponse,
    EventNotification,
    ServiceEventResponse,
    StateUpdateRequest,
    SyncStatusResponse
)
from image.core.dependencies import get_event_service, get_sync_service
from image.core.errors import InvalidEventError, SyncError
from image.core.validation import validate_api_key, validate_event_type
from image.services.event import EventService
from image.services.sync import SyncService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/events",
    response_model=ServiceEventResponse,
    summary="Handle service events",
    response_description="Event processing result",
    status_code=status.HTTP_202_ACCEPTED
)
async def handle_event(
    event: EventNotification,
    x_request_id: str = Header(None),
    x_api_key: str = Header(...),
    event_service: EventService = Depends(get_event_service)
) -> dict:
    """Handle events from other services.

    This endpoint receives and processes events from other services
    in the system, such as character updates, theme changes, etc.

    Args:
        event: Event notification details
        x_request_id: Optional request ID for tracking
        x_api_key: API key for authentication
        event_service: Event processing service

    Returns:
        Event processing result

    Raises:
        InvalidEventError: If event type is invalid
    """
    # Validate API key
    validate_api_key(x_api_key, "events:write")

    # Validate event type
    validate_event_type(event.type)

    try:
        # Process event
        result = await event_service.process_event(
            event_type=event.type,
            payload=event.payload,
            source_service=event.source,
            request_id=x_request_id
        )

        return {
            "event_id": result.event_id,
            "status": result.status,
            "processed_at": result.processed_at,
            "results": result.results
        }

    except InvalidEventError:
        raise
    except Exception as e:
        logger.exception("Error processing event")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/events/{event_id}",
    response_model=ServiceEventResponse,
    summary="Get event status",
    response_description="Event processing status"
)
async def get_event_status(
    event_id: UUID = Path(..., description="Event ID"),
    x_api_key: str = Header(...),
    event_service: EventService = Depends(get_event_service)
) -> dict:
    """Get status of a processed event.

    Args:
        event_id: Event ID to check
        x_api_key: API key for authentication
        event_service: Event processing service

    Returns:
        Event status details
    """
    # Validate API key
    validate_api_key(x_api_key, "events:read")

    try:
        # Get event status
        result = await event_service.get_event_status(event_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event {event_id} not found"
            )

        return {
            "event_id": result.event_id,
            "status": result.status,
            "processed_at": result.processed_at,
            "results": result.results
        }

    except Exception as e:
        logger.exception("Error getting event status")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/sync/state",
    response_model=SyncStatusResponse,
    summary="Sync state with other services",
    response_description="State synchronization result"
)
async def sync_state(
    request: StateUpdateRequest,
    x_request_id: str = Header(None),
    x_api_key: str = Header(...),
    sync_service: SyncService = Depends(get_sync_service)
) -> dict:
    """Synchronize state with other services.

    This endpoint handles state synchronization requests from other services,
    ensuring consistency across the system.

    Args:
        request: State update details
        x_request_id: Optional request ID for tracking
        x_api_key: API key for authentication
        sync_service: State synchronization service

    Returns:
        Sync operation status

    Raises:
        SyncError: If sync operation fails
    """
    # Validate API key
    validate_api_key(x_api_key, "sync:write")

    try:
        # Process sync request
        result = await sync_service.sync_state(
            state_type=request.type,
            state_data=request.data,
            source_service=request.source,
            request_id=x_request_id
        )

        return {
            "sync_id": result.sync_id,
            "status": result.status,
            "synced_at": result.synced_at,
            "details": result.details
        }

    except SyncError:
        raise
    except Exception as e:
        logger.exception("Error syncing state")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/sync/status/{sync_id}",
    response_model=SyncStatusResponse,
    summary="Get sync operation status",
    response_description="State sync operation status"
)
async def get_sync_status(
    sync_id: UUID = Path(..., description="Sync operation ID"),
    x_api_key: str = Header(...),
    sync_service: SyncService = Depends(get_sync_service)
) -> dict:
    """Get status of a sync operation.

    Args:
        sync_id: Sync operation ID
        x_api_key: API key for authentication
        sync_service: State synchronization service

    Returns:
        Sync operation details
    """
    # Validate API key
    validate_api_key(x_api_key, "sync:read")

    try:
        # Get sync status
        result = await sync_service.get_sync_status(sync_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sync operation {sync_id} not found"
            )

        return {
            "sync_id": result.sync_id,
            "status": result.status,
            "synced_at": result.synced_at,
            "details": result.details
        }

    except Exception as e:
        logger.exception("Error getting sync status")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/bulk",
    response_model=BulkOperationResponse,
    summary="Execute bulk operations",
    response_description="Bulk operation result"
)
async def execute_bulk_operation(
    operation_ids: List[UUID] = Query(..., description="List of operation IDs to process"),
    x_request_id: str = Header(None),
    x_api_key: str = Header(...),
    sync_service: SyncService = Depends(get_sync_service)
) -> dict:
    """Execute bulk operations across services.

    This endpoint handles bulk operations that need to be coordinated
    across multiple services.

    Args:
        operation_ids: List of operation IDs to process
        x_request_id: Optional request ID for tracking
        x_api_key: API key for authentication
        sync_service: State synchronization service

    Returns:
        Bulk operation results
    """
    # Validate API key
    validate_api_key(x_api_key, "bulk:write")

    try:
        # Execute bulk operation
        result = await sync_service.execute_bulk_operations(
            operation_ids=operation_ids,
            request_id=x_request_id
        )

        return {
            "operation_id": result.operation_id,
            "status": result.status,
            "completed_at": result.completed_at,
            "results": result.results,
            "failed_operations": result.failed_operations
        }

    except Exception as e:
        logger.exception("Error executing bulk operation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/health/ready",
    response_model=dict,
    summary="Service readiness check",
    response_description="Service readiness status"
)
async def readiness_check(
    sync_service: SyncService = Depends(get_sync_service),
    event_service: EventService = Depends(get_event_service)
) -> dict:
    """Check if service is ready to handle requests.

    This endpoint verifies that all required service dependencies
    and integrations are functioning correctly.

    Args:
        sync_service: State synchronization service
        event_service: Event processing service

    Returns:
        Service readiness status
    """
    try:
        # Check service dependencies
        sync_ready = await sync_service.check_ready()
        event_ready = await event_service.check_ready()

        status = "ready" if sync_ready and event_ready else "not_ready"
        return {
            "status": status,
            "sync_service": "ready" if sync_ready else "not_ready",
            "event_service": "ready" if event_ready else "not_ready"
        }

    except Exception as e:
        logger.exception("Error checking service readiness")
        return {
            "status": "not_ready",
            "sync_service": "error",
            "event_service": "error",
            "error": str(e)
        }


@router.get(
    "/health/live",
    response_model=dict,
    summary="Service liveness check",
    response_description="Service liveness status"
)
async def liveness_check() -> dict:
    """Check if service is alive.

    This endpoint provides a basic liveness check to verify
    that the service is running and responding to requests.

    Returns:
        Service liveness status
    """
    return {"status": "alive"}
