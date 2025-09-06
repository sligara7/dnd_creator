"""Campaign content generation service."""
from uuid import UUID, uuid4
from typing import Dict, List, Optional

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from llm_service.core.exceptions import ContentGenerationError
from llm_service.core.cache import RateLimiter
from llm_service.core.events import MessageHubClient
from llm_service.services.openai import OpenAIClient
from llm_service.services.validation import ValidationService
from llm_service.schemas.campaign import (
    StoryElement,
    StoryRequest,
    StoryContent,
    NPCRequest,
    NPCContent,
    LocationRequest,
    LocationContent,
)


class CampaignContentService:
    """Service for generating campaign content."""

    def __init__(
        self,
        openai: OpenAIClient,
        rate_limiter: RateLimiter,
        message_hub: MessageHubClient,
        validation_service: ValidationService,
        db: AsyncSession,
        logger: Optional[structlog.BoundLogger] = None,
    ) -> None:
        self.openai = openai
        self.rate_limiter = rate_limiter
        self.message_hub = message_hub
        self.validation_service = validation_service
        self.db = db
        self.logger = logger or structlog.get_logger()

    def _create_story_prompt(self, request: StoryRequest) -> str:
        """Create prompt for story content generation."""
        prompt = f"""Generate {request.element_type.value} content for a D&D campaign:

Campaign Context:
- Theme: {request.context.campaign_theme}
- Type: {request.context.campaign_type}
- Setting: {request.context.setting}
- Party Level: {request.context.party_level}
- Party Size: {request.context.party_size}
- Length: {request.context.length}"""

        if request.parameters:
            prompt += "\n\nAdditional Parameters:"
            for key, value in request.parameters.items():
                prompt += f"\n- {key}: {value}"

        prompt += "\n\nProvide:\n"
        if request.element_type == StoryElement.PLOT:
            prompt += "1. Main plot points\n2. Key NPCs\n3. Major locations\n4. Story hooks"
        elif request.element_type == StoryElement.QUEST:
            prompt += "1. Quest objectives\n2. Challenges\n3. Rewards\n4. Possible outcomes"
        elif request.element_type == StoryElement.SCENE:
            prompt += "1. Scene description\n2. Key events\n3. NPC interactions\n4. Environment"
        elif request.element_type == StoryElement.DIALOGUE:
            prompt += "1. Conversation flow\n2. Key information\n3. NPC personality\n4. Player hooks"
        else:
            prompt += "1. Detailed description\n2. Key elements\n3. Integration points"

        return prompt

    def _create_npc_prompt(self, request: NPCRequest) -> str:
        """Create prompt for NPC generation."""
        prompt = f"""Generate an NPC for a D&D campaign:

NPC Role: {request.role.value}

Campaign Context:
- Theme: {request.context.campaign_theme}
- Setting: {request.context.setting}
- Party Level: {request.context.party_level}"""

        if request.traits:
            prompt += "\n\nRequired Traits:"
            for trait, value in request.traits.items():
                prompt += f"\n- {trait}: {value}"

        if request.relationships:
            prompt += "\n\nRelationships:"
            for char, rel in request.relationships.items():
                prompt += f"\n- {char}: {rel}"

        prompt += "\n\nProvide:\n1. Name and title\n2. Physical description\n3. Personality\n4. Motivations and goals\n5. Secrets and hooks"
        return prompt

    def _create_location_prompt(self, request: LocationRequest) -> str:
        """Create prompt for location generation."""
        prompt = f"""Generate a {request.location_type.value} location for a D&D campaign:

Location Details:
- Size: {request.size}
- Purpose: {request.purpose}

Campaign Context:
- Theme: {request.context.campaign_theme}
- Setting: {request.context.setting}
- Party Level: {request.context.party_level}"""

        if request.occupants:
            prompt += "\n\nNotable Occupants:"
            for occupant in request.occupants:
                prompt += f"\n- {occupant}"

        if request.features:
            prompt += "\n\nRequired Features:"
            for feature in request.features:
                prompt += f"\n- {feature}"

        prompt += "\n\nProvide:\n1. Name and description\n2. Points of interest\n3. Current occupants\n4. Secrets and mysteries\n5. Story hooks"
        return prompt

async def generate_story(self, request: StoryRequest) -> StoryContent:
        """Generate story content."""
        try:
            # Generate story content
            prompt = self._create_story_prompt(request)
            text, usage = await self.openai.generate_text(prompt)

            # Parse generated content
            from .campaign_parser import parse_story_content
            parsed = parse_story_content(text, request.element_type)

            # Create database model
            from ..models.campaign import StoryContent as StoryModel
            story = StoryModel(
                content_type=request.element_type.value,
                campaign_id=request.context.campaign_id,
                parent_id=request.parent_element_id,
                title=parsed.title,
                description=parsed.description,
                summary=parsed.summary,
                plot_points=parsed.plot_points,
                npc_references=parsed.npcs,
                location_references=parsed.locations,
                hooks=parsed.hooks,
                theme_context=request.context.dict(),
                metadata={
                    "model_used": "gpt-4",
                    "token_usage": usage.model_dump(),
                    "campaign_type": request.context.campaign_type,
                },
            )

            # Save to database
            self.db.add(story)
            await self.db.commit()
            await self.db.refresh(story)

            # Publish event
            await self.message_hub.publish_event({
                "type": "story_content_generated",
                "content_id": str(story.id),
                "element_type": story.content_type,
                "campaign_id": str(story.campaign_id),
            })

            # Convert to response model
            return StoryContent(
                content_id=story.id,
                element_type=request.element_type,
                content=parsed.description,
                metadata=story.metadata,
                parent_element_id=story.parent_id,
                summary=story.summary,
                plot_points=story.plot_points,
                npcs=[{"name": npc["name"], "description": npc["description"]} for npc in story.npc_references],
                locations=[{"name": loc["name"], "description": loc["description"]} for loc in story.location_references],
                hooks=story.hooks
            )

        except Exception as e:
            self.logger.error(
                "story_generation_failed",
                error=str(e),
                element_type=request.element_type.value,
            )
            raise ContentGenerationError(
                message=f"Story generation failed: {str(e)}",
                details={
                    "element_type": request.element_type.value,
                    "campaign_type": request.context.campaign_type,
                },
            )
        """Generate story content."""
        try:
            # Generate story content
            prompt = self._create_story_prompt(request)
            text, usage = await self.openai.generate_text(prompt)

            # Create content
            content = StoryContent(
                content_id=uuid4(),
                element_type=request.element_type,
                content=text,
                metadata={
                    "model_used": "gpt-4",
                    "token_usage": usage.model_dump(),
                    "campaign_type": request.context.campaign_type,
                },
                parent_element_id=request.parent_element_id,
                summary="Generated story content",  # TODO: Generate summary
            )

            # Save to database
            # TODO: Implement database persistence

            # Publish event
            await self.message_hub.publish_event({
                "type": "story_content_generated",
                "content_id": str(content.content_id),
                "element_type": content.element_type.value,
            })

            return content

        except Exception as e:
            self.logger.error(
                "story_generation_failed",
                error=str(e),
                element_type=request.element_type.value,
            )
            raise ContentGenerationError(
                message=f"Story generation failed: {str(e)}",
                details={
                    "element_type": request.element_type.value,
                    "campaign_type": request.context.campaign_type,
                },
            )

async def generate_npc(self, request: NPCRequest) -> NPCContent:
        """Generate NPC content."""
        try:
            # Generate NPC content
            prompt = self._create_npc_prompt(request)
            text, usage = await self.openai.generate_text(prompt)

            # Parse generated content
            from .campaign_parser import parse_npc_content
            parsed = parse_npc_content(text)

            # Create database model
            from ..models.campaign import NPCContent as NPCModel
            npc = NPCModel(
                content_type='npc',
                campaign_id=request.context.campaign_id,
                parent_id=request.parent_element_id if hasattr(request, 'parent_element_id') else None,
                title=parsed.title or parsed.name,
                name=parsed.name,
                title=parsed.title,
                description=parsed.description,
                personality=parsed.personality,
                motivations=parsed.motivations,
                secrets=parsed.secrets,
                relationships=parsed.relationships,
                summary=parsed.summary,
                theme_context=request.context.dict(),
                metadata={
                    "model_used": "gpt-4",
                    "token_usage": usage.model_dump(),
                    "campaign_type": request.context.campaign_type,
                    "npc_role": request.role.value,
                },
            )

            # Save to database
            self.db.add(npc)
            await self.db.commit()
            await self.db.refresh(npc)

            # Publish event
            await self.message_hub.publish_event({
                "type": "npc_generated",
                "npc_id": str(npc.id),
                "campaign_id": str(npc.campaign_id),
                "role": request.role.value,
            })

            # Convert to response model
            return NPCContent(
                content_id=npc.id,
                name=npc.name,
                title=npc.title,
                role=request.role,
                description=npc.description,
                personality=npc.personality,
                motivations=npc.motivations,
                secrets=npc.secrets,
                relationships=npc.relationships,
                metadata=npc.metadata,
            )

        except Exception as e:
            self.logger.error(
                "npc_generation_failed",
                error=str(e),
                role=request.role.value,
            )
            raise ContentGenerationError(
                message=f"NPC generation failed: {str(e)}",
                details={"role": request.role.value},
            )
        """Generate NPC content."""
        try:
            # Generate NPC content
            prompt = self._create_npc_prompt(request)
            text, usage = await self.openai.generate_text(prompt)

            # TODO: Parse response to extract structured NPC data
            # For now, using placeholder data
            npc = NPCContent(
                content_id=uuid4(),
                name="Generated NPC",  # TODO: Extract from response
                role=request.role,
                description="Physical description",  # TODO: Extract
                personality="Personality traits",  # TODO: Extract
                motivations=["Motivation 1", "Motivation 2"],  # TODO: Extract
                secrets=["Secret 1"] if request.role != "neutral" else None,
                relationships=request.relationships or {},
                metadata={
                    "model_used": "gpt-4",
                    "token_usage": usage.model_dump(),
                    "campaign_theme": request.context.campaign_theme,
                },
            )

            # Save to database
            # TODO: Implement database persistence

            # Publish event
            await self.message_hub.publish_event({
                "type": "npc_generated",
                "npc_id": str(npc.content_id),
                "role": npc.role.value,
            })

            return npc

        except Exception as e:
            self.logger.error(
                "npc_generation_failed",
                error=str(e),
                role=request.role.value,
            )
            raise ContentGenerationError(
                message=f"NPC generation failed: {str(e)}",
                details={"role": request.role.value},
            )

async def generate_location(self, request: LocationRequest) -> LocationContent:
        """Generate location content."""
        try:
            # Generate location content
            prompt = self._create_location_prompt(request)
            text, usage = await self.openai.generate_text(prompt)

            # Parse generated content
            from .campaign_parser import parse_location_content
            parsed = parse_location_content(text)

            # Create database model
            from ..models.campaign import LocationContent as LocationModel
            location = LocationModel(
                content_type='location',
                campaign_id=request.context.campaign_id,
                parent_id=request.parent_element_id if hasattr(request, 'parent_element_id') else None,
                title=parsed.name,
                name=parsed.name,
                description=parsed.description,
                points_of_interest=parsed.points_of_interest,
                occupants=parsed.occupants,
                secrets=parsed.secrets,
                hooks=parsed.hooks,
                summary=parsed.summary,
                theme_context=request.context.dict(),
                metadata={
                    "model_used": "gpt-4",
                    "token_usage": usage.model_dump(),
                    "campaign_type": request.context.campaign_type,
                    "location_type": request.location_type.value,
                    "size": request.size,
                    "purpose": request.purpose,
                },
            )

            # Save to database
            self.db.add(location)
            await self.db.commit()
            await self.db.refresh(location)

            # Publish event
            await self.message_hub.publish_event({
                "type": "location_generated",
                "location_id": str(location.id),
                "campaign_id": str(location.campaign_id),
                "location_type": location.metadata["location_type"],
            })

            # Convert to response model
            return LocationContent(
                content_id=location.id,
                name=location.name,
                location_type=request.location_type,
                description=location.description,
                points_of_interest=location.points_of_interest,
                occupants=location.occupants,
                secrets=location.secrets,
                hooks=location.hooks,
                metadata=location.metadata,
            )

        except Exception as e:
            self.logger.error(
                "location_generation_failed",
                error=str(e),
                location_type=request.location_type.value,
            )
            raise ContentGenerationError(
                message=f"Location generation failed: {str(e)}",
                details={"location_type": request.location_type.value},
            )
        """Generate location content."""
        try:
            # Generate location content
            prompt = self._create_location_prompt(request)
            text, usage = await self.openai.generate_text(prompt)

            # TODO: Parse response to extract structured location data
            # For now, using placeholder data
            location = LocationContent(
                content_id=uuid4(),
                name="Generated Location",  # TODO: Extract from response
                location_type=request.location_type,
                description=text,
                points_of_interest=request.features or ["Feature 1"],  # TODO: Extract
                occupants=request.occupants or ["Occupant 1"],  # TODO: Extract
                secrets=["Secret 1"],  # TODO: Extract
                hooks=["Hook 1", "Hook 2"],  # TODO: Extract
                metadata={
                    "model_used": "gpt-4",
                    "token_usage": usage.model_dump(),
                    "campaign_theme": request.context.campaign_theme,
                },
            )

            # Save to database
            # TODO: Implement database persistence

            # Publish event
            await self.message_hub.publish_event({
                "type": "location_generated",
                "location_id": str(location.content_id),
                "location_type": location.location_type.value,
            })

            return location

        except Exception as e:
            self.logger.error(
                "location_generation_failed",
                error=str(e),
                location_type=request.location_type.value,
            )
            raise ContentGenerationError(
                message=f"Location generation failed: {str(e)}",
                details={"location_type": request.location_type.value},
            )

    async def initialize(self) -> None:
        """Initialize service resources."""
        pass

    async def cleanup(self) -> None:
        """Clean up service resources."""
        pass
