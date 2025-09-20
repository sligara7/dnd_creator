"""
Event processor service for the Audit Service.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
import asyncio

import structlog
from prometheus_client import Counter, Histogram

from audit_service.core.exceptions import EventProcessingError
from audit_service.core.config import settings
from audit_service.models.events import Event, BatchEventUpload
from audit_service.models.enrichment import EventEnricher
from audit_service.core.monitoring import (
    EVENTS_TOTAL,
    EVENTS_PENDING,
    EVENT_PROCESSING_TIME,
    EVENT_BATCH_SIZE,
)

logger = structlog.get_logger()

class EventProcessor:
    """Event processing service."""
    
    def __init__(self) -> None:
        """Initialize the event processor."""
        self.logger = logger.bind(component="event_processor")
        self.enricher = EventEnricher()
        self._processing_queue: List[Event] = []
        self._pending_count: int = 0
        self._processed_count: int = 0
        self._is_running: bool = False
        self._processing_task: Optional[asyncio.Task] = None
    
    async def setup(self) -> None:
        """Set up the event processor."""
        self.logger.info("Setting up event processor")
        self._is_running = True
        self._processing_task = asyncio.create_task(self._process_queue())
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Cleaning up event processor")
        self._is_running = False
        if self._processing_task:
            await self._processing_task
    
    async def process_event(self, event: Event) -> None:
        """
        Process a single event.
        
        Args:
            event: Event to process
            
        Raises:
            EventProcessingError: If processing fails
        """
        try:
            # Update metrics
            self._pending_count += 1
            EVENTS_PENDING.labels(service=event.service).inc()
            
            # Start timing
            start_time = datetime.utcnow()
            
            # Enrich event
            enriched_event = self.enricher.enrich_event(event)
            
            # Add to processing queue
            self._processing_queue.append(enriched_event)
            
            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            EVENT_PROCESSING_TIME.labels(
                service=event.service,
                event_type=event.type
            ).observe(processing_time)
            
            EVENTS_TOTAL.labels(
                service=event.service,
                event_type=event.type,
                outcome="success"
            ).inc()
            
            self._processed_count += 1
            self._pending_count -= 1
            EVENTS_PENDING.labels(service=event.service).dec()
            
        except Exception as e:
            EVENTS_TOTAL.labels(
                service=event.service,
                event_type=event.type,
                outcome="error"
            ).inc()
            
            raise EventProcessingError(
                message="Event processing failed",
                event_id=str(event.id),
                details={"error": str(e)}
            )
    
    async def process_batch(self, batch: BatchEventUpload) -> None:
        """
        Process a batch of events.
        
        Args:
            batch: List of events to process
            
        Raises:
            EventProcessingError: If batch processing fails
        """
        try:
            # Update metrics
            batch_size = len(batch.root)
            EVENT_BATCH_SIZE.labels(service=batch.root[0].service).observe(batch_size)
            
            # Enrich and process all events
            enriched_events = self.enricher.enrich_batch(batch.root)
            self._processing_queue.extend(enriched_events)
            
            # Update counts
            self._pending_count += batch_size
            
        except Exception as e:
            raise EventProcessingError(
                message="Batch event processing failed",
                details={"error": str(e)}
            )
    
    async def _process_queue(self) -> None:
        """Process events from the queue."""
        while self._is_running:
            try:
                if not self._processing_queue:
                    await asyncio.sleep(1)
                    continue
                
                # Get next event
                event = self._processing_queue.pop(0)
                self.logger.debug(
                    "Processing event",
                    event_id=str(event.id),
                    event_type=event.type
                )
                
                # TODO: Send to Message Hub for persistence
                # This will be implemented in the Message Hub integration task
                
                # Add a small delay to avoid overwhelming the system
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(
                    "Error processing queue",
                    error=str(e)
                )
                await asyncio.sleep(1)
    
    async def health_check(self) -> bool:
        """Check service health."""
        return self._is_running
    
    def get_processed_count(self) -> int:
        """Get number of processed events."""
        return self._processed_count
    
    def get_pending_count(self) -> int:
        """Get number of pending events."""
        return self._pending_count