"""
Campaign generation factory.
"""

from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from ..core.ai import AIClient
from ..core.logging import get_logger
from ..models.campaign import Campaign, Chapter, NPC
from ..services.ai.campaign_generation import CampaignGenerator
from ..services.theme_service import ThemeService
from ..services.version_service import VersionService
from ..services.map_service import MapService
from ..api.schemas.campaign import CreateCampaignRequest, Campaign as CampaignSchema
from ..api.schemas.theme import ThemeProfile

logger = get_logger(__name__)


class CampaignFactory:
    """Factory for creating and evolving campaigns."""
    
    def __init__(
        self,
        db: Session,
        ai_client: AIClient,
        message_hub_client: Any,
        theme_service: ThemeService,
        version_service: VersionService,
        map_service: MapService,
    ):
        """Initialize with required dependencies."""
        self.db = db
        self.ai_client = ai_client
        self.message_hub = message_hub_client
        self.theme_service = theme_service
        self.version_service = version_service
        self.map_service = map_service
        self.generator = CampaignGenerator(ai_client)
    
    async def create_campaign(
        self,
        request: CreateCampaignRequest
    ) -> Tuple[UUID, CampaignSchema]:
        """Create a new campaign based on concept."""
        try:
            # Get theme profile
            theme_profile = await self.theme_service.get_theme_profile(
                request.theme.primary,
                request.theme.secondary
            )

            # Generate campaign structure
            generated_campaign = await self.generator.generate_campaign_structure(
                request.concept,
                request.theme,
                theme_profile,
                request.preferences.complexity,
                (request.length.min_sessions, request.length.max_sessions)
            )

            # Create database model
            campaign = Campaign(
                name=request.name,
                concept=request.concept,
                complexity_level=request.preferences.complexity.value,
                moral_tone=request.preferences.moral_tone.value,
                violence_level=request.preferences.violence_level.value,
                min_sessions=request.length.min_sessions,
                max_sessions=request.length.max_sessions,
                version=self.version_service.create_initial_hash(),
                is_template=False
            )
            self.db.add(campaign)
            self.db.flush()

            # Generate theme integration
            theme_integration = await self.generator.generate_theme_integration(
                generated_campaign,
                theme_profile
            )

            # Generate story arcs
            arcs = await self.generator.generate_story_arc(
                generated_campaign,
                "main",
                request.length.min_sessions
            )

            # Generate plot branches
            branches = await self.generator.generate_plot_branches(
                generated_campaign,
                [arc["trigger_point"] for arc in arcs if "trigger_point" in arc],
                request.preferences.complexity
            )

            # Generate maps if requested
            if request.generation_flags.get("generate_maps", True):
                maps = await self.map_service.generate_campaign_maps(campaign)
                campaign.maps = maps

            # Create initial chapter if requested
            if request.generation_flags.get("generate_first_chapter", True):
                first_chapter = await self._generate_initial_chapter(
                    campaign.id,
                    generated_campaign,
                    theme_profile
                )
                # Set as current chapter
                campaign.current_chapter = first_chapter.id

            # Save to database
            self.db.commit()

            # Notify integrations
            await self.message_hub.request(
                "catalog.add_campaign",
                {"campaign": generated_campaign.dict()}
            )

            await self.message_hub.publish(
                "campaign.created",
                {
                    "campaign_id": str(campaign.id),
                    "theme": request.theme.dict()
                }
            )

            return campaign.id, generated_campaign
            
        except Exception as e:
            logger.error("Campaign creation failed", error=str(e))
            raise ValueError(f"Failed to create campaign: {e}")
            
    async def evolve_campaign(
        self,
        campaign_id: UUID,
        changes: Dict[str, Any]
    ) -> Campaign:
        """Evolve an existing campaign."""
        try:
            # Get current campaign
            campaign_data = await self.message_hub.request(
                "campaign.get",
                {"campaign_id": str(campaign_id)}
            )
            
            if not campaign_data:
                raise ValueError("Campaign not found")
                
            # Get evolution from LLM
            evolution = await self.message_hub.request(
                "llm.evolve_campaign",
                {
                    "campaign": campaign_data,
                    "changes": changes
                }
            )
            
            if not evolution:
                raise ValueError("Failed to evolve campaign")
                
            # Update campaign model
            campaign = Campaign(**evolution)
            
            # Update catalog
            await self.message_hub.request(
                "catalog.update_campaign",
                {
                    "campaign_id": str(campaign_id),
                    "campaign": campaign.dict()
                }
            )
            
            # Publish evolution event
            await self.message_hub.publish(
                "campaign.evolved",
                {
                    "campaign_id": str(campaign_id),
                    "changes": list(changes.keys())
                }
            )
            
            return campaign
            
        except Exception as e:
            logger.error("Campaign evolution failed", error=str(e))
            raise ValueError(f"Failed to evolve campaign: {e}")
            
    async def create_chapter(
        self,
        campaign_id: UUID,
        chapter_concept: str,
        previous_chapter_id: Optional[UUID] = None
    ) -> Chapter:
        """Create a new chapter for a campaign."""
        try:
            # Get campaign context
            campaign_data = await self.message_hub.request(
                "campaign.get",
                {"campaign_id": str(campaign_id)}
            )
            
            if not campaign_data:
                raise ValueError("Campaign not found")
            
            # Get previous chapter if specified
            previous_chapter = None
            if previous_chapter_id:
                previous_chapter = await self.message_hub.request(
                    "campaign.get_chapter",
                    {"chapter_id": str(previous_chapter_id)}
                )
            
            # Generate chapter
            generation = await self.message_hub.request(
                "llm.generate_chapter",
                {
                    "campaign": campaign_data,
                    "concept": chapter_concept,
                    "previous_chapter": previous_chapter
                }
            )
            
            if not generation:
                raise ValueError("Failed to generate chapter")
                
            # Create chapter model
            chapter = Chapter(**generation)
            
            # Add to catalog
            await self.message_hub.request(
                "catalog.add_chapter",
                {
                    "campaign_id": str(campaign_id),
                    "chapter": chapter.dict()
                }
            )
            
            # Generate maps if needed
            if chapter.requires_maps:
                maps = await self._generate_chapter_maps(chapter)
                chapter.maps.extend(maps)
            
            # Publish creation event
            await self.message_hub.publish(
                "campaign.chapter_created",
                {
                    "campaign_id": str(campaign_id),
                    "chapter_id": str(chapter.id)
                }
            )
            
            return chapter
            
        except Exception as e:
            logger.error("Chapter creation failed", error=str(e))
            raise ValueError(f"Failed to create chapter: {e}")
    
    async def _generate_initial_chapter(
        self,
        campaign_id: UUID,
        campaign_data: CampaignSchema,
        theme_profile: ThemeProfile
    ) -> Chapter:
        """Generate the first chapter of a campaign."""
        # Generate chapter content
        chapter_content = await self.ai_client.generate_chapter({
            "campaign": campaign_data.dict(),
            "chapter_number": 1,
            "chapter_type": "introduction",
            "theme_profile": theme_profile.dict(),
            "requirements": {
                "must_introduce_theme": True,
                "must_hook_players": True
            }
        })

        # Create chapter model
        chapter = Chapter(
            campaign_id=campaign_id,
            title=chapter_content["title"],
            summary=chapter_content["summary"],
            content=chapter_content,
            sequence_number=1,
            status="draft"
        )
        self.db.add(chapter)

        # Generate encounters
        encounters = await self.ai_client.generate_encounters({
            "chapter": chapter_content,
            "theme_profile": theme_profile.dict(),
            "requirements": {
                "difficulty": "introductory",
                "must_include_combat": True,
                "must_include_roleplay": True
            }
        })

        # Add encounters to chapter
        chapter.encounters = encounters["encounters"]

        # Generate maps if needed
        if chapter_content.get("locations"):
            maps = await self.map_service.generate_chapter_maps(chapter, campaign_id)
            chapter.maps = maps

        return chapter
