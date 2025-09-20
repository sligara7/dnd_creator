"""
Tests for event router endpoints.
"""
from typing import List
import pytest
from httpx import AsyncClient
from fastapi import status

from audit_service.models.events import (
    Event,
    SecurityEvent,
    UserEvent,
    SystemEvent,
    ComplianceEvent
)

@pytest.mark.asyncio
async def test_create_event(client: AsyncClient, event: Event):
    """Test creating a basic event."""
    response = await client.post(
        "/api/v2/events",
        json=event.model_dump()
    )
    assert response.status_code == status.HTTP_201_CREATED
    created_event = Event(**response.json())
    assert created_event.service == event.service
    assert created_event.type == event.type
    assert created_event.action == event.action
    assert created_event.severity == event.severity
    assert created_event.outcome == event.outcome

@pytest.mark.asyncio
async def test_create_security_event(client: AsyncClient, security_event: SecurityEvent):
    """Test creating a security event."""
    response = await client.post(
        "/api/v2/events/security",
        json=security_event.model_dump()
    )
    assert response.status_code == status.HTTP_201_CREATED
    created_event = SecurityEvent(**response.json())
    assert created_event.auth_context == security_event.auth_context
    assert created_event.permissions == security_event.permissions
    assert created_event.risk_level == security_event.risk_level

@pytest.mark.asyncio
async def test_create_user_event(client: AsyncClient, user_event: UserEvent):
    """Test creating a user event."""
    response = await client.post(
        "/api/v2/events/user",
        json=user_event.model_dump()
    )
    assert response.status_code == status.HTTP_201_CREATED
    created_event = UserEvent(**response.json())
    assert created_event.user_id == user_event.user_id
    assert created_event.user_type == user_event.user_type
    assert created_event.session_data == user_event.session_data

@pytest.mark.asyncio
async def test_create_system_event(client: AsyncClient, system_event: SystemEvent):
    """Test creating a system event."""
    response = await client.post(
        "/api/v2/events/system",
        json=system_event.model_dump()
    )
    assert response.status_code == status.HTTP_201_CREATED
    created_event = SystemEvent(**response.json())
    assert created_event.component == system_event.component
    assert created_event.resource_id == system_event.resource_id
    assert created_event.operation == system_event.operation
    assert created_event.performance_impact == system_event.performance_impact

@pytest.mark.asyncio
async def test_create_compliance_event(client: AsyncClient, compliance_event: ComplianceEvent):
    """Test creating a compliance event."""
    response = await client.post(
        "/api/v2/events/compliance",
        json=compliance_event.model_dump()
    )
    assert response.status_code == status.HTTP_201_CREATED
    created_event = ComplianceEvent(**response.json())
    assert created_event.regulation == compliance_event.regulation
    assert created_event.compliance_status == compliance_event.compliance_status
    assert created_event.controls == compliance_event.controls
    assert created_event.data_categories == compliance_event.data_categories

@pytest.mark.asyncio
async def test_create_events_batch(client: AsyncClient, event_batch: List[Event]):
    """Test creating multiple events in a batch."""
    response = await client.post(
        "/api/v2/events/batch",
        json={"root": [event.model_dump() for event in event_batch]}
    )
    assert response.status_code == status.HTTP_201_CREATED
    created_events = [Event(**event) for event in response.json()]
    assert len(created_events) == len(event_batch)
    for created, original in zip(created_events, event_batch):
        assert created.service == original.service
        assert created.type == original.type
        assert created.action == original.action
        assert created.severity == original.severity
        assert created.outcome == original.outcome

@pytest.mark.asyncio
async def test_create_event_invalid_data(client: AsyncClient, event: Event):
    """Test creating an event with invalid data."""
    invalid_event = event.model_dump()
    invalid_event["severity"] = "invalid"  # Invalid severity level
    
    response = await client.post(
        "/api/v2/events",
        json=invalid_event
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_create_security_event_missing_fields(
    client: AsyncClient,
    security_event: SecurityEvent
):
    """Test creating a security event with missing required fields."""
    invalid_event = security_event.model_dump()
    del invalid_event["risk_level"]  # Required field
    
    response = await client.post(
        "/api/v2/events/security",
        json=invalid_event
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_create_events_batch_empty(client: AsyncClient):
    """Test creating an empty batch of events."""
    response = await client.post(
        "/api/v2/events/batch",
        json={"root": []}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_create_events_batch_partially_invalid(
    client: AsyncClient,
    event_batch: List[Event]
):
    """Test creating a batch with some invalid events."""
    events_data = [event.model_dump() for event in event_batch]
    events_data[0]["severity"] = "invalid"  # Make first event invalid
    
    response = await client.post(
        "/api/v2/events/batch",
        json={"root": events_data}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY