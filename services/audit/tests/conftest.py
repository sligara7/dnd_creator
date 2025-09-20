"""
Test fixtures for Audit Service testing.
"""
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator, Dict, List
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import FastAPI

from audit_service.models.events import (
    Event,
    SecurityEvent,
    UserEvent,
    SystemEvent,
    ComplianceEvent,
    Actor,
    Target,
    Context,
    EventData,
)
from audit_service.main import app
from audit_service.services import init_services, cleanup_services

@pytest.fixture(scope="session")
def app_fixture() -> FastAPI:
    """Get FastAPI app instance."""
    return app

@pytest_asyncio.fixture(scope="session")
async def client(app_fixture: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    await init_services()
    async with AsyncClient(
        app=app_fixture,
        base_url="http://test"
    ) as client:
        yield client
    await cleanup_services()

@pytest.fixture
def actor() -> Actor:
    """Create test actor."""
    return Actor(
        id="test_user",
        type="user",
        name="Test User"
    )

@pytest.fixture
def target() -> Target:
    """Create test target."""
    return Target(
        id="test_resource",
        type="resource",
        name="Test Resource"
    )

@pytest.fixture
def context() -> Context:
    """Create test context."""
    return Context(
        request_id="test_request",
        session_id="test_session",
        ip_address="127.0.0.1",
        user_agent="pytest",
        environment="test",
        source="test_service"
    )

@pytest.fixture
def event_data() -> EventData:
    """Create test event data."""
    return EventData(
        changes=[{
            "field": "name",
            "old_value": "Old Name",
            "new_value": "New Name",
            "change_type": "update"
        }],
        metadata={"test": "data"},
        sensitive=False,
        encrypted_fields=[]
    )

@pytest.fixture
def event(
    actor: Actor,
    target: Target,
    context: Context,
    event_data: EventData
) -> Event:
    """Create test event."""
    return Event(
        id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        service="test_service",
        type="test.event",
        action="test",
        actor=actor,
        target=target,
        context=context,
        data=event_data,
        severity="info",
        outcome="success",
        retention_period="30d"
    )

@pytest.fixture
def security_event(event: Event) -> SecurityEvent:
    """Create test security event."""
    return SecurityEvent(
        **event.model_dump(),
        auth_context={"method": "jwt"},
        permissions=["read", "write"],
        risk_level="low"
    )

@pytest.fixture
def user_event(event: Event) -> UserEvent:
    """Create test user event."""
    return UserEvent(
        **event.model_dump(),
        user_id="test_user",
        user_type="standard",
        session_data={"last_action": "login"}
    )

@pytest.fixture
def system_event(event: Event) -> SystemEvent:
    """Create test system event."""
    return SystemEvent(
        **event.model_dump(),
        component="test_component",
        resource_id="test_resource",
        operation="update",
        performance_impact="low"
    )

@pytest.fixture
def compliance_event(event: Event) -> ComplianceEvent:
    """Create test compliance event."""
    return ComplianceEvent(
        **event.model_dump(),
        regulation="GDPR",
        compliance_status="compliant",
        controls=["access_control", "data_protection"],
        data_categories=["personal", "sensitive"]
    )

@pytest.fixture
def event_batch(event: Event) -> List[Event]:
    """Create test event batch."""
    events = []
    for i in range(5):
        event_copy = Event(
            **event.model_dump(),
            id=uuid4(),
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=i)
        )
        events.append(event_copy)
    return events

@pytest.fixture
def event_search_params() -> Dict[str, str]:
    """Create test search parameters."""
    now = datetime.now(timezone.utc)
    return {
        "start_date": (now - timedelta(hours=1)).isoformat(),
        "end_date": now.isoformat(),
        "event_types": ["test.event"],
        "services": ["test_service"],
        "severity": "info"
    }