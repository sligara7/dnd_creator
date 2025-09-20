"""
Event enrichment utilities for the Audit Service.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

import structlog

from audit_service.core.exceptions import EventProcessingError
from audit_service.models.events import Event, SecurityEvent, UserEvent, SystemEvent, ComplianceEvent

logger = structlog.get_logger()

class EventEnricher:
    """Event enrichment utilities."""

    def __init__(self) -> None:
        """Initialize the event enricher."""
        self.logger = logger.bind(component="event_enricher")
    
    def enrich_event(self, event: Event) -> Event:
        """
        Enrich an event with additional context and metadata.
        
        Args:
            event: The event to enrich
            
        Returns:
            The enriched event
            
        Raises:
            EventProcessingError: If enrichment fails
        """
        try:
            # Add standard enrichments
            self._enrich_timestamps(event)
            self._enrich_context(event)
            
            # Add specialized enrichments based on event type
            if isinstance(event, SecurityEvent):
                self._enrich_security_event(event)
            elif isinstance(event, UserEvent):
                self._enrich_user_event(event)
            elif isinstance(event, SystemEvent):
                self._enrich_system_event(event)
            elif isinstance(event, ComplianceEvent):
                self._enrich_compliance_event(event)
            
            return event
            
        except Exception as e:
            raise EventProcessingError(
                message="Event enrichment failed",
                event_id=str(event.id),
                details={"error": str(e)}
            )
    
    def _enrich_timestamps(self, event: Event) -> None:
        """Add timing information to event."""
        if not event.data.metadata.get("timing"):
            event.data.metadata["timing"] = {
                "received_at": datetime.utcnow().isoformat(),
                "processing_started": datetime.utcnow().isoformat()
            }
    
    def _enrich_context(self, event: Event) -> None:
        """Add additional context to event."""
        # Add correlation context
        if event.context.request_id:
            event.data.metadata["correlation"] = {
                "request_id": event.context.request_id,
                "session_id": event.context.session_id,
                "parent_event_id": event.data.metadata.get("parent_event_id")
            }
        
        # Add environment context
        if "environment_context" not in event.data.metadata:
            event.data.metadata["environment_context"] = {
                "environment": event.context.environment,
                "source": event.context.source
            }

    def _enrich_security_event(self, event: SecurityEvent) -> None:
        """Add security-specific enrichments."""
        if not event.data.metadata.get("security_context"):
            event.data.metadata["security_context"] = {
                "auth_method": event.auth_context.get("method"),
                "permissions": event.permissions,
                "risk_level": event.risk_level
            }

    def _enrich_user_event(self, event: UserEvent) -> None:
        """Add user activity specific enrichments."""
        if not event.data.metadata.get("user_context"):
            event.data.metadata["user_context"] = {
                "user_id": event.user_id,
                "user_type": event.user_type,
                "session_data": event.session_data or {}
            }

    def _enrich_system_event(self, event: SystemEvent) -> None:
        """Add system-specific enrichments."""
        if not event.data.metadata.get("system_context"):
            event.data.metadata["system_context"] = {
                "component": event.component,
                "resource_id": event.resource_id,
                "operation": event.operation,
                "performance_impact": event.performance_impact
            }

    def _enrich_compliance_event(self, event: ComplianceEvent) -> None:
        """Add compliance-specific enrichments."""
        if not event.data.metadata.get("compliance_context"):
            event.data.metadata["compliance_context"] = {
                "regulation": event.regulation,
                "compliance_status": event.compliance_status,
                "controls": event.controls,
                "data_categories": event.data_categories
            }

    def enrich_batch(self, events: List[Event]) -> List[Event]:
        """
        Enrich a batch of events.
        
        Args:
            events: List of events to enrich
            
        Returns:
            List of enriched events
            
        Raises:
            EventProcessingError: If batch enrichment fails
        """
        try:
            enriched_events = []
            for event in events:
                enriched_events.append(self.enrich_event(event))
            return enriched_events
            
        except Exception as e:
            raise EventProcessingError(
                message="Batch event enrichment failed",
                details={"error": str(e)}
            )