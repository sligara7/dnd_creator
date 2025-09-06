"""Campaign service integration layer."""
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
import structlog
from pydantic import BaseModel, Field

from ..core.config import Settings
from ..core.exceptions import IntegrationError
from ..models.theme import ContentType, ThemeContext


class CampaignEventType(str, Enum):
    """Types of campaign events."""
    STORY_GENERATED = "story_generated"
    PLOT_UPDATED = "plot_updated"
    QUEST_ADDED = "quest_added"
    THEME_APPLIED = "theme_applied"
    THEME_TRANSITIONED = "theme_transitioned"
    LOCATION_ADDED = "location_added"
    NPC_ADDED = "npc_added"


class CampaignContentType(str, Enum):
    """Types of campaign content."""
    PLOT = "plot"
    QUEST = "quest"
    LOCATION = "location"
    NPC = "npc"
    DIALOGUE = "dialogue"
    EVENT = "event"


class CampaignContent(BaseModel):
    """Campaign content for generation."""
    campaign_id: UUID = Field(description="Campaign ID")
    content_type: CampaignContentType = Field(description="Type of content")
    theme_context: Optional[ThemeContext] = Field(
        default=None,
        description="Theme context for generation"
    )
    existing_content: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Existing campaign content"
    )
    requirements: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Generation requirements"
    )


class CampaignEvent(BaseModel):
    """Event from Campaign service."""
    event_type: CampaignEventType = Field(description="Type of event")
    campaign_id: UUID = Field(description="Campaign ID")
    data: Dict[str, Any] = Field(description="Event data")
    theme_context: Optional[ThemeContext] = Field(
        default=None,
        description="Theme context if relevant"
    )


class CampaignService:
    """Service for interacting with Campaign service."""

    def __init__(
        self,
        settings: Settings,
        logger: Optional[structlog.BoundLogger] = None
    ):
        """Initialize the service."""
        self.settings = settings
        self.logger = logger or structlog.get_logger()
        self.base_url = settings.CAMPAIGN_SERVICE_URL
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=settings.CAMPAIGN_SERVICE_TIMEOUT
        )

    async def get_campaign_content(
        self,
        campaign_id: UUID,
        content_type: CampaignContentType
    ) -> CampaignContent:
        """Get campaign content for generation."""
        try:
            response = await self.client.get(
                f"/api/v2/campaigns/{campaign_id}/content",
                params={"content_type": content_type.value}
            )
            response.raise_for_status()
            
            data = response.json()
            return CampaignContent(
                campaign_id=campaign_id,
                content_type=content_type,
                theme_context=ThemeContext(**data["theme_context"])
                if data.get("theme_context") else None,
                existing_content=data.get("existing_content"),
                requirements=data.get("requirements")
            )
            
        except httpx.HTTPError as e:
            self.logger.error(
                "campaign_content_fetch_failed",
                campaign_id=str(campaign_id),
                content_type=content_type.value,
                error=str(e)
            )
            raise IntegrationError(
                f"Failed to fetch campaign content: {str(e)}"
            )

    async def update_campaign_content(
        self,
        campaign_id: UUID,
        content_type: CampaignContentType,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update campaign content after generation."""
        try:
            response = await self.client.put(
                f"/api/v2/campaigns/{campaign_id}/content",
                json={
                    "content_type": content_type.value,
                    "content": content,
                    "metadata": metadata or {}
                }
            )
            response.raise_for_status()
            
            self.logger.info(
                "campaign_content_updated",
                campaign_id=str(campaign_id),
                content_type=content_type.value
            )
            
        except httpx.HTTPError as e:
            self.logger.error(
                "campaign_content_update_failed",
                campaign_id=str(campaign_id),
                content_type=content_type.value,
                error=str(e)
            )
            raise IntegrationError(
                f"Failed to update campaign content: {str(e)}"
            )

    async def validate_theme(
        self,
        campaign_id: UUID,
        theme_context: ThemeContext
    ) -> bool:
        """Validate theme compatibility for campaign."""
        try:
            response = await self.client.post(
                f"/api/v2/campaigns/{campaign_id}/theme/validate",
                json=theme_context.dict()
            )
            response.raise_for_status()
            
            data = response.json()
            is_valid = data["is_valid"]
            
            self.logger.info(
                "theme_validation_complete",
                campaign_id=str(campaign_id),
                theme=theme_context.name,
                is_valid=is_valid
            )
            
            return is_valid
            
        except httpx.HTTPError as e:
            self.logger.error(
                "theme_validation_failed",
                campaign_id=str(campaign_id),
                theme=theme_context.name,
                error=str(e)
            )
            raise IntegrationError(
                f"Failed to validate theme: {str(e)}"
            )

    async def create_plot_element(
        self,
        campaign_id: UUID,
        title: str,
        description: str,
        element_type: str,
        theme_context: Optional[ThemeContext] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new plot element."""
        try:
            response = await self.client.post(
                f"/api/v2/campaigns/{campaign_id}/plot",
                json={
                    "title": title,
                    "description": description,
                    "type": element_type,
                    "theme_context": theme_context.dict() if theme_context else None,
                    "metadata": metadata or {}
                }
            )
            response.raise_for_status()
            
            self.logger.info(
                "plot_element_created",
                campaign_id=str(campaign_id),
                element_type=element_type,
                theme=theme_context.name if theme_context else None
            )
            
            return response.json()
            
        except httpx.HTTPError as e:
            self.logger.error(
                "plot_element_creation_failed",
                campaign_id=str(campaign_id),
                element_type=element_type,
                error=str(e)
            )
            raise IntegrationError(
                f"Failed to create plot element: {str(e)}"
            )

    async def create_location(
        self,
        campaign_id: UUID,
        name: str,
        description: str,
        location_type: str,
        theme_context: Optional[ThemeContext] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new location."""
        try:
            response = await self.client.post(
                f"/api/v2/campaigns/{campaign_id}/locations",
                json={
                    "name": name,
                    "description": description,
                    "type": location_type,
                    "theme_context": theme_context.dict() if theme_context else None,
                    "metadata": metadata or {}
                }
            )
            response.raise_for_status()
            
            self.logger.info(
                "location_created",
                campaign_id=str(campaign_id),
                location_type=location_type,
                theme=theme_context.name if theme_context else None
            )
            
            return response.json()
            
        except httpx.HTTPError as e:
            self.logger.error(
                "location_creation_failed",
                campaign_id=str(campaign_id),
                location_type=location_type,
                error=str(e)
            )
            raise IntegrationError(
                f"Failed to create location: {str(e)}"
            )

    async def create_npc(
        self,
        campaign_id: UUID,
        name: str,
        description: str,
        role: str,
        theme_context: Optional[ThemeContext] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new NPC."""
        try:
            response = await self.client.post(
                f"/api/v2/campaigns/{campaign_id}/npcs",
                json={
                    "name": name,
                    "description": description,
                    "role": role,
                    "theme_context": theme_context.dict() if theme_context else None,
                    "metadata": metadata or {}
                }
            )
            response.raise_for_status()
            
            self.logger.info(
                "npc_created",
                campaign_id=str(campaign_id),
                role=role,
                theme=theme_context.name if theme_context else None
            )
            
            return response.json()
            
        except httpx.HTTPError as e:
            self.logger.error(
                "npc_creation_failed",
                campaign_id=str(campaign_id),
                role=role,
                error=str(e)
            )
            raise IntegrationError(
                f"Failed to create NPC: {str(e)}"
            )

    async def notify_content_generation(
        self,
        campaign_id: UUID,
        content_type: CampaignContentType,
        theme_context: Optional[ThemeContext] = None
    ) -> None:
        """Notify Campaign service about content generation."""
        try:
            response = await self.client.post(
                f"/api/v2/campaigns/{campaign_id}/events",
                json={
                    "event_type": CampaignEventType.STORY_GENERATED.value,
                    "content_type": content_type.value,
                    "theme_context": theme_context.dict() if theme_context else None
                }
            )
            response.raise_for_status()
            
            self.logger.info(
                "content_generation_notified",
                campaign_id=str(campaign_id),
                content_type=content_type.value,
                theme=theme_context.name if theme_context else None
            )
            
        except httpx.HTTPError as e:
            self.logger.error(
                "content_generation_notification_failed",
                campaign_id=str(campaign_id),
                content_type=content_type.value,
                error=str(e)
            )
            # Non-critical error, log but don't raise
            self.logger.warning(
                "Failed to notify content generation",
                exc_info=e
            )
