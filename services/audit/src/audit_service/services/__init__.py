"""
Service initialization and management for the Audit Service.
"""
from typing import Optional

from audit_service.core.message_hub import MessageHubClient
from audit_service.services.event_processor import EventProcessor
from audit_service.services.archival_service import ArchivalService
from audit_service.services.analysis_service import AnalysisService
from audit_service.core.storage import StorageClient

# Global service instances
message_hub: Optional[MessageHubClient] = None
storage_client: Optional[StorageClient] = None
event_processor: Optional[EventProcessor] = None
archival_service: Optional[ArchivalService] = None
analysis_service: Optional[AnalysisService] = None

async def init_services() -> None:
    """Initialize all services."""
    global message_hub, storage_client, event_processor, archival_service, analysis_service
    
    # Initialize clients
    message_hub = MessageHubClient()
    await message_hub.setup()
    
    storage_client = StorageClient()
    await storage_client.setup()
    
    # Initialize other services
    event_processor = EventProcessor()
    await event_processor.setup()
    
    archival_service = ArchivalService()
    await archival_service.setup()
    
    analysis_service = AnalysisService()
    await analysis_service.setup()

async def cleanup_services() -> None:
    """Clean up resources."""
    if analysis_service:
        await analysis_service.cleanup()
    
    if archival_service:
        await archival_service.cleanup()
    
    if event_processor:
        await event_processor.cleanup()
    
    if storage_client:
        await storage_client.cleanup()
    
    if message_hub:
        await message_hub.cleanup()
