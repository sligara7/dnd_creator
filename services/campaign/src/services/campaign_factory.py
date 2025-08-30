"""
Campaign generation factory.
"""

from typing import Dict, Any, List, Optional
from uuid import UUID

from ..models.campaign import Campaign, Chapter, NPC
from ..core.logging import get_logger

logger = get_logger(__name__)


class CampaignFactory:
    """Factory for creating and evolving campaigns."""
    
    def __init__(self, message_hub_client):
        """Initialize with required dependencies."""
        self.message_hub = message_hub_client
    
    async def create_campaign(
        self,
        concept: str,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Campaign:
        """Create a new campaign based on concept."""
        try:
            # Get campaign generation from LLM
            generation = await self.message_hub.request(
                "llm.generate_campaign",
                {
                    "concept": concept,
                    "preferences": preferences or {}
                }
            )
            
            if not generation:
                raise ValueError("Failed to generate campaign")
                
            # Create campaign model
            campaign = Campaign(**generation)
            
            # Generate NPCs
            npcs = await self._generate_npcs(campaign.npc_concepts)
            campaign.npcs.extend(npcs)
            
            # Generate maps if enabled
            if preferences and preferences.get("generate_maps"):
                maps = await self._generate_maps(campaign)
                campaign.maps.extend(maps)
            
            # Add to catalog
            await self.message_hub.request(
                "catalog.add_campaign",
                {"campaign": campaign.dict()}
            )
            
            # Publish creation event
            await self.message_hub.publish(
                "campaign.created",
                {
                    "campaign_id": str(campaign.id),
                    "theme": campaign.theme
                }
            )
            
            return campaign
            
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
    
    async def _generate_npcs(self, concepts: List[str]) -> List[NPC]:
        """Generate NPCs based on concepts."""
        npcs = []
        for concept in concepts:
            try:
                # Get NPC generation from LLM
                generation = await self.message_hub.request(
                    "llm.generate_npc",
                    {"concept": concept}
                )
                
                if generation:
                    npc = NPC(**generation)
                    
                    # Generate portrait
                    portrait = await self.message_hub.request(
                        "image.generate_portrait",
                        {"npc": npc.dict()}
                    )
                    if portrait:
                        npc.portrait_url = portrait["url"]
                        
                    npcs.append(npc)
                    
            except Exception as e:
                logger.error(f"Failed to generate NPC for concept: {concept}", error=str(e))
                continue
                
        return npcs
    
    async def _generate_maps(self, campaign: Campaign) -> List[Dict[str, Any]]:
        """Generate maps for campaign."""
        maps = []
        try:
            # Generate world map
            world_map = await self.message_hub.request(
                "image.generate_map",
                {
                    "type": "world",
                    "campaign": campaign.dict()
                }
            )
            if world_map:
                maps.append(world_map)
            
            # Generate region maps
            for region in campaign.regions:
                region_map = await self.message_hub.request(
                    "image.generate_map",
                    {
                        "type": "region",
                        "region": region,
                        "campaign": campaign.dict()
                    }
                )
                if region_map:
                    maps.append(region_map)
                    
        except Exception as e:
            logger.error("Map generation failed", error=str(e))
            
        return maps
    
    async def _generate_chapter_maps(self, chapter: Chapter) -> List[Dict[str, Any]]:
        """Generate maps for a chapter."""
        maps = []
        try:
            for location in chapter.locations:
                location_map = await self.message_hub.request(
                    "image.generate_map",
                    {
                        "type": location["type"],
                        "location": location,
                        "theme": chapter.theme
                    }
                )
                if location_map:
                    maps.append(location_map)
                    
        except Exception as e:
            logger.error("Chapter map generation failed", error=str(e))
            
        return maps
