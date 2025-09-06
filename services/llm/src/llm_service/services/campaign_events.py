"""Event handlers for Campaign service integration."""
from typing import Any, Dict, Optional
from uuid import UUID

import structlog
from fastapi import BackgroundTasks

from ..core.exceptions import EventHandlingError
from .campaign_integration import (
    CampaignContent,
    CampaignContentType,
    CampaignEvent,
    CampaignEventType,
    CampaignService
)
from .generation import GenerationPipeline


class CampaignEventHandler:
    """Handler for Campaign service events."""

    def __init__(
        self,
        campaign_service: CampaignService,
        generation_pipeline: GenerationPipeline,
        background_tasks: BackgroundTasks,
        logger: Optional[structlog.BoundLogger] = None
    ):
        """Initialize event handler."""
        self.campaign_service = campaign_service
        self.generation_pipeline = generation_pipeline
        self.background_tasks = background_tasks
        self.logger = logger or structlog.get_logger()

    async def handle_campaign_event(
        self,
        event: CampaignEvent
    ) -> None:
        """Handle events from Campaign service."""
        try:
            if event.event_type == CampaignEventType.THEME_TRANSITIONED:
                await self._handle_theme_transition(
                    event.campaign_id,
                    event.theme_context
                )
            elif event.event_type == CampaignEventType.QUEST_ADDED:
                await self._handle_quest_addition(
                    event.campaign_id,
                    event.data,
                    event.theme_context
                )
            elif event.event_type == CampaignEventType.LOCATION_ADDED:
                await self._handle_location_addition(
                    event.campaign_id,
                    event.data,
                    event.theme_context
                )
            elif event.event_type == CampaignEventType.NPC_ADDED:
                await self._handle_npc_addition(
                    event.campaign_id,
                    event.data,
                    event.theme_context
                )
            else:
                self.logger.warning(
                    "unhandled_event_type",
                    event_type=event.event_type.value,
                    campaign_id=str(event.campaign_id)
                )

        except Exception as e:
            self.logger.error(
                "event_handling_failed",
                event_type=event.event_type.value,
                campaign_id=str(event.campaign_id),
                error=str(e)
            )
            raise EventHandlingError(f"Failed to handle event: {str(e)}")

    async def _handle_theme_transition(
        self,
        campaign_id: UUID,
        theme_context: Optional[Dict[str, Any]]
    ) -> None:
        """Handle theme transition events."""
        try:
            # Validate theme compatibility
            is_valid = await self.campaign_service.validate_theme(
                campaign_id,
                theme_context
            )
            if not is_valid:
                raise EventHandlingError("Theme validation failed")

            # Generate updated content for all content types
            content_types = [
                CampaignContentType.PLOT,
                CampaignContentType.QUEST,
                CampaignContentType.LOCATION,
                CampaignContentType.NPC,
                CampaignContentType.DIALOGUE
            ]
            
            for content_type in content_types:
                # Add to background tasks to handle asynchronously
                self.background_tasks.add_task(
                    self._generate_themed_content,
                    campaign_id,
                    content_type,
                    theme_context
                )

            self.logger.info(
                "theme_transition_queued",
                campaign_id=str(campaign_id),
                theme=theme_context.get("name") if theme_context else None,
                content_types=[ct.value for ct in content_types]
            )

        except Exception as e:
            self.logger.error(
                "theme_transition_failed",
                campaign_id=str(campaign_id),
                theme=theme_context.get("name") if theme_context else None,
                error=str(e)
            )
            raise EventHandlingError(f"Theme transition failed: {str(e)}")

    async def _handle_quest_addition(
        self,
        campaign_id: UUID,
        quest_data: Dict[str, Any],
        theme_context: Optional[Dict[str, Any]]
    ) -> None:
        """Handle quest addition events."""
        try:
            # Generate quest details
            content = await self._generate_quest_content(
                campaign_id,
                quest_data,
                theme_context
            )

            # Create quest plot elements
            await self.campaign_service.create_plot_element(
                campaign_id=campaign_id,
                title=quest_data["title"],
                description=content["description"],
                element_type="quest",
                theme_context=theme_context,
                metadata={
                    "objectives": content["objectives"],
                    "challenges": content["challenges"],
                    "rewards": content["rewards"]
                }
            )

            # Generate related NPCs and locations
            for npc in content.get("npcs", []):
                self.background_tasks.add_task(
                    self.campaign_service.create_npc,
                    campaign_id=campaign_id,
                    name=npc["name"],
                    description=npc["description"],
                    role=npc["role"],
                    theme_context=theme_context
                )

            for location in content.get("locations", []):
                self.background_tasks.add_task(
                    self.campaign_service.create_location,
                    campaign_id=campaign_id,
                    name=location["name"],
                    description=location["description"],
                    location_type=location["type"],
                    theme_context=theme_context
                )

            self.logger.info(
                "quest_content_generated",
                campaign_id=str(campaign_id),
                quest_title=quest_data["title"],
                theme=theme_context.get("name") if theme_context else None
            )

        except Exception as e:
            self.logger.error(
                "quest_generation_failed",
                campaign_id=str(campaign_id),
                quest_title=quest_data["title"],
                error=str(e)
            )
            raise EventHandlingError(f"Quest generation failed: {str(e)}")

    async def _handle_location_addition(
        self,
        campaign_id: UUID,
        location_data: Dict[str, Any],
        theme_context: Optional[Dict[str, Any]]
    ) -> None:
        """Handle location addition events."""
        try:
            # Generate location details
            content = await self._generate_location_content(
                campaign_id,
                location_data,
                theme_context
            )

            # Create location
            await self.campaign_service.create_location(
                campaign_id=campaign_id,
                name=location_data["name"],
                description=content["description"],
                location_type=location_data["type"],
                theme_context=theme_context,
                metadata={
                    "points_of_interest": content["points_of_interest"],
                    "secrets": content["secrets"],
                    "hooks": content["hooks"]
                }
            )

            # Generate related NPCs
            for npc in content.get("npcs", []):
                self.background_tasks.add_task(
                    self.campaign_service.create_npc,
                    campaign_id=campaign_id,
                    name=npc["name"],
                    description=npc["description"],
                    role=npc["role"],
                    theme_context=theme_context
                )

            self.logger.info(
                "location_content_generated",
                campaign_id=str(campaign_id),
                location_name=location_data["name"],
                theme=theme_context.get("name") if theme_context else None
            )

        except Exception as e:
            self.logger.error(
                "location_generation_failed",
                campaign_id=str(campaign_id),
                location_name=location_data["name"],
                error=str(e)
            )
            raise EventHandlingError(f"Location generation failed: {str(e)}")

    async def _handle_npc_addition(
        self,
        campaign_id: UUID,
        npc_data: Dict[str, Any],
        theme_context: Optional[Dict[str, Any]]
    ) -> None:
        """Handle NPC addition events."""
        try:
            # Generate NPC details
            content = await self._generate_npc_content(
                campaign_id,
                npc_data,
                theme_context
            )

            # Create NPC
            await self.campaign_service.create_npc(
                campaign_id=campaign_id,
                name=npc_data["name"],
                description=content["description"],
                role=npc_data["role"],
                theme_context=theme_context,
                metadata={
                    "personality": content["personality"],
                    "motivations": content["motivations"],
                    "secrets": content["secrets"],
                    "relationships": content["relationships"]
                }
            )

            # Generate related plot elements
            for plot in content.get("plot_hooks", []):
                self.background_tasks.add_task(
                    self.campaign_service.create_plot_element,
                    campaign_id=campaign_id,
                    title=plot["title"],
                    description=plot["description"],
                    element_type="npc_hook",
                    theme_context=theme_context
                )

            self.logger.info(
                "npc_content_generated",
                campaign_id=str(campaign_id),
                npc_name=npc_data["name"],
                theme=theme_context.get("name") if theme_context else None
            )

        except Exception as e:
            self.logger.error(
                "npc_generation_failed",
                campaign_id=str(campaign_id),
                npc_name=npc_data["name"],
                error=str(e)
            )
            raise EventHandlingError(f"NPC generation failed: {str(e)}")

    async def _generate_themed_content(
        self,
        campaign_id: UUID,
        content_type: CampaignContentType,
        theme_context: Dict[str, Any]
    ) -> None:
        """Generate themed content for campaign."""
        try:
            # Get existing campaign content
            campaign_content = await self.campaign_service.get_campaign_content(
                campaign_id,
                content_type
            )

            # Generate new content
            result = await self.generation_pipeline.generate_content(
                content_type=content_type,
                theme_context=theme_context,
                existing_content=campaign_content.existing_content
            )

            # Update campaign content
            await self.campaign_service.update_campaign_content(
                campaign_id=campaign_id,
                content_type=content_type,
                content=result.content,
                metadata={
                    "model": result.metadata.model_name,
                    "tokens": result.metadata.total_tokens,
                    "theme": theme_context.get("name") if theme_context else None
                }
            )

            # Notify about content generation
            await self.campaign_service.notify_content_generation(
                campaign_id=campaign_id,
                content_type=content_type,
                theme_context=theme_context
            )

            self.logger.info(
                "themed_content_generated",
                campaign_id=str(campaign_id),
                content_type=content_type.value,
                theme=theme_context.get("name") if theme_context else None
            )

        except Exception as e:
            self.logger.error(
                "themed_content_generation_failed",
                campaign_id=str(campaign_id),
                content_type=content_type.value,
                theme=theme_context.get("name") if theme_context else None,
                error=str(e)
            )
            # Log error but don't raise to allow other content types to proceed

    async def _generate_quest_content(
        self,
        campaign_id: UUID,
        quest_data: Dict[str, Any],
        theme_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate quest content."""
        try:
            result = await self.generation_pipeline.generate_content(
                content_type=CampaignContentType.QUEST,
                theme_context=theme_context,
                existing_content={
                    "title": quest_data["title"],
                    "type": quest_data["type"],
                    "level": quest_data.get("level", "any")
                }
            )

            # Parse the generated content
            # For now, returning placeholder structured data
            # TODO: Implement proper parsing
            return {
                "description": result.content,
                "objectives": ["Objective 1", "Objective 2"],
                "challenges": ["Challenge 1", "Challenge 2"],
                "rewards": ["Reward 1", "Reward 2"],
                "npcs": [],
                "locations": []
            }

        except Exception as e:
            raise EventHandlingError(f"Failed to generate quest content: {str(e)}")

    async def _generate_location_content(
        self,
        campaign_id: UUID,
        location_data: Dict[str, Any],
        theme_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate location content."""
        try:
            result = await self.generation_pipeline.generate_content(
                content_type=CampaignContentType.LOCATION,
                theme_context=theme_context,
                existing_content={
                    "name": location_data["name"],
                    "type": location_data["type"],
                    "size": location_data.get("size", "medium")
                }
            )

            # Parse the generated content
            # For now, returning placeholder structured data
            # TODO: Implement proper parsing
            return {
                "description": result.content,
                "points_of_interest": ["POI 1", "POI 2"],
                "secrets": ["Secret 1"],
                "hooks": ["Hook 1", "Hook 2"],
                "npcs": []
            }

        except Exception as e:
            raise EventHandlingError(f"Failed to generate location content: {str(e)}")

    async def _generate_npc_content(
        self,
        campaign_id: UUID,
        npc_data: Dict[str, Any],
        theme_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate NPC content."""
        try:
            result = await self.generation_pipeline.generate_content(
                content_type=CampaignContentType.NPC,
                theme_context=theme_context,
                existing_content={
                    "name": npc_data["name"],
                    "role": npc_data["role"],
                    "importance": npc_data.get("importance", "minor")
                }
            )

            # Parse the generated content
            # For now, returning placeholder structured data
            # TODO: Implement proper parsing
            return {
                "description": result.content,
                "personality": "Personality traits",
                "motivations": ["Motivation 1", "Motivation 2"],
                "secrets": ["Secret 1"],
                "relationships": {},
                "plot_hooks": []
            }

        except Exception as e:
            raise EventHandlingError(f"Failed to generate NPC content: {str(e)}")
