"""Chapter content management service."""
from typing import Dict, List, Optional, Set
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from ..core.ai import AIClient
from ..core.logging import get_logger
from ..models.campaign import Campaign
from ..models.chapter import Chapter
from ..models.content import NPC, Location, ChapterNPC, ChapterLocation
from ..services.theme_service import ThemeService

logger = get_logger(__name__)


class ChapterContent:
    """Service for managing chapter content."""

    def __init__(
        self,
        db: Session,
        ai_client: AIClient,
        theme_service: ThemeService,
        message_hub_client,
    ):
        """Initialize with required dependencies."""
        self.db = db
        self.ai_client = ai_client
        self.theme_service = theme_service
        self.message_hub = message_hub_client

    async def add_npc_to_chapter(
        self,
        chapter_id: UUID,
        npc_id: UUID,
        role: str,
        significance: str,
        location_id: Optional[UUID] = None,
        interaction_points: Optional[List[str]] = None
    ) -> ChapterNPC:
        """Add an NPC to a chapter."""
        try:
            chapter = self.db.query(Chapter).get(chapter_id)
            npc = self.db.query(NPC).get(npc_id)
            if not chapter or not npc:
                raise ValueError("Chapter or NPC not found")

            if npc.campaign_id != chapter.campaign_id:
                raise ValueError("NPC belongs to different campaign")

            # Validate location if provided
            if location_id:
                location = self.db.query(Location).get(location_id)
                if not location or location.campaign_id != chapter.campaign_id:
                    raise ValueError("Invalid location")

            assoc = ChapterNPC(
                chapter_id=chapter_id,
                npc_id=npc_id,
                role=role,
                significance=significance,
                location_id=location_id,
                interaction_points=interaction_points or []
            )
            self.db.add(assoc)
            self.db.commit()

            await self._validate_npc_usage(chapter_id, npc_id)

            await self.message_hub.publish(
                "campaign.chapter_npc_added",
                {
                    "campaign_id": str(chapter.campaign_id),
                    "chapter_id": str(chapter_id),
                    "npc_id": str(npc_id),
                    "role": role
                }
            )

            return assoc

        except Exception as e:
            self.db.rollback()
            logger.error("Failed to add NPC to chapter", error=str(e))
            raise ValueError(f"Failed to add NPC to chapter: {e}")

    async def update_npc_in_chapter(
        self,
        chapter_id: UUID,
        npc_id: UUID,
        updates: Dict
    ) -> ChapterNPC:
        """Update an NPC's role in a chapter."""
        try:
            assoc = self.db.query(ChapterNPC).filter(
                ChapterNPC.chapter_id == chapter_id,
                ChapterNPC.npc_id == npc_id
            ).first()
            if not assoc:
                raise ValueError("NPC not found in chapter")

            # Update fields
            for field, value in updates.items():
                if hasattr(assoc, field):
                    setattr(assoc, field, value)

            self.db.commit()

            await self._validate_npc_usage(chapter_id, npc_id)

            await self.message_hub.publish(
                "campaign.chapter_npc_updated",
                {
                    "chapter_id": str(chapter_id),
                    "npc_id": str(npc_id),
                    "updates": updates
                }
            )

            return assoc

        except Exception as e:
            self.db.rollback()
            logger.error("Failed to update NPC in chapter", error=str(e))
            raise ValueError(f"Failed to update NPC in chapter: {e}")

    async def remove_npc_from_chapter(
        self,
        chapter_id: UUID,
        npc_id: UUID
    ) -> None:
        """Remove an NPC from a chapter."""
        try:
            assoc = self.db.query(ChapterNPC).filter(
                ChapterNPC.chapter_id == chapter_id,
                ChapterNPC.npc_id == npc_id
            ).first()
            if not assoc:
                raise ValueError("NPC not found in chapter")

            self.db.delete(assoc)
            self.db.commit()

            await self.message_hub.publish(
                "campaign.chapter_npc_removed",
                {
                    "chapter_id": str(chapter_id),
                    "npc_id": str(npc_id)
                }
            )

        except Exception as e:
            self.db.rollback()
            logger.error("Failed to remove NPC from chapter", error=str(e))
            raise ValueError(f"Failed to remove NPC from chapter: {e}")

    async def add_location_to_chapter(
        self,
        chapter_id: UUID,
        location_id: UUID,
        role: str,
        significance: str,
        description_override: Optional[str] = None,
        state_changes: Optional[List[Dict]] = None
    ) -> ChapterLocation:
        """Add a location to a chapter."""
        try:
            chapter = self.db.query(Chapter).get(chapter_id)
            location = self.db.query(Location).get(location_id)
            if not chapter or not location:
                raise ValueError("Chapter or location not found")

            if location.campaign_id != chapter.campaign_id:
                raise ValueError("Location belongs to different campaign")

            assoc = ChapterLocation(
                chapter_id=chapter_id,
                location_id=location_id,
                role=role,
                significance=significance,
                description_override=description_override,
                state_changes=state_changes or []
            )
            self.db.add(assoc)
            self.db.commit()

            await self._validate_location_usage(chapter_id, location_id)

            await self.message_hub.publish(
                "campaign.chapter_location_added",
                {
                    "campaign_id": str(chapter.campaign_id),
                    "chapter_id": str(chapter_id),
                    "location_id": str(location_id),
                    "role": role
                }
            )

            return assoc

        except Exception as e:
            self.db.rollback()
            logger.error("Failed to add location to chapter", error=str(e))
            raise ValueError(f"Failed to add location to chapter: {e}")

    async def update_location_in_chapter(
        self,
        chapter_id: UUID,
        location_id: UUID,
        updates: Dict
    ) -> ChapterLocation:
        """Update a location's role in a chapter."""
        try:
            assoc = self.db.query(ChapterLocation).filter(
                ChapterLocation.chapter_id == chapter_id,
                ChapterLocation.location_id == location_id
            ).first()
            if not assoc:
                raise ValueError("Location not found in chapter")

            # Update fields
            for field, value in updates.items():
                if hasattr(assoc, field):
                    setattr(assoc, field, value)

            self.db.commit()

            await self._validate_location_usage(chapter_id, location_id)

            await self.message_hub.publish(
                "campaign.chapter_location_updated",
                {
                    "chapter_id": str(chapter_id),
                    "location_id": str(location_id),
                    "updates": updates
                }
            )

            return assoc

        except Exception as e:
            self.db.rollback()
            logger.error("Failed to update location in chapter", error=str(e))
            raise ValueError(f"Failed to update location in chapter: {e}")

    async def remove_location_from_chapter(
        self,
        chapter_id: UUID,
        location_id: UUID
    ) -> None:
        """Remove a location from a chapter."""
        try:
            assoc = self.db.query(ChapterLocation).filter(
                ChapterLocation.chapter_id == chapter_id,
                ChapterLocation.location_id == location_id
            ).first()
            if not assoc:
                raise ValueError("Location not found in chapter")

            self.db.delete(assoc)
            self.db.commit()

            await self.message_hub.publish(
                "campaign.chapter_location_removed",
                {
                    "chapter_id": str(chapter_id),
                    "location_id": str(location_id)
                }
            )

        except Exception as e:
            self.db.rollback()
            logger.error("Failed to remove location from chapter", error=str(e))
            raise ValueError(f"Failed to remove location from chapter: {e}")

    async def generate_chapter_encounters(
        self,
        chapter_id: UUID,
        requirements: Optional[Dict] = None
    ) -> List[Dict]:
        """Generate encounters for a chapter."""
        try:
            chapter = self.db.query(Chapter).get(chapter_id)
            if not chapter:
                raise ValueError("Chapter not found")

            campaign = self.db.query(Campaign).get(chapter.campaign_id)
            theme_profile = await self.theme_service.get_theme_profile(
                campaign.theme.primary,
                campaign.theme.secondary
            )

            encounters = await self.ai_client.generate_encounters({
                "chapter": chapter.dict(),
                "theme_profile": theme_profile.dict(),
                "requirements": requirements or {}
            })

            # Update chapter encounters
            chapter.encounters = encounters["encounters"]
            self.db.commit()

            await self.message_hub.publish(
                "campaign.chapter_encounters_generated",
                {
                    "chapter_id": str(chapter_id),
                    "encounter_count": len(encounters["encounters"])
                }
            )

            return encounters["encounters"]

        except Exception as e:
            self.db.rollback()
            logger.error("Failed to generate encounters", error=str(e))
            raise ValueError(f"Failed to generate encounters: {e}")

    async def _validate_npc_usage(
        self,
        chapter_id: UUID,
        npc_id: UUID
    ) -> None:
        """Validate NPC usage in chapter."""
        chapter = self.db.query(Chapter).get(chapter_id)
        npc = self.db.query(NPC).get(npc_id)

        # Get theme profile
        campaign = self.db.query(Campaign).get(chapter.campaign_id)
        theme_profile = await self.theme_service.get_theme_profile(
            campaign.theme.primary,
            campaign.theme.secondary
        )

        # Validate against theme
        validation = await self.ai_client.validate_theme(
            {
                "chapter": chapter.dict(),
                "npc": npc.dict()
            },
            theme_profile.dict()
        )

        if not validation["is_valid"]:
            logger.warning(
                "NPC usage may not fit theme",
                npc_id=str(npc_id),
                issues=validation["errors"]
            )

    async def _validate_location_usage(
        self,
        chapter_id: UUID,
        location_id: UUID
    ) -> None:
        """Validate location usage in chapter."""
        chapter = self.db.query(Chapter).get(chapter_id)
        location = self.db.query(Location).get(location_id)

        # Get theme profile
        campaign = self.db.query(Campaign).get(chapter.campaign_id)
        theme_profile = await self.theme_service.get_theme_profile(
            campaign.theme.primary,
            campaign.theme.secondary
        )

        # Validate against theme
        validation = await self.ai_client.validate_theme(
            {
                "chapter": chapter.dict(),
                "location": location.dict()
            },
            theme_profile.dict()
        )

        if not validation["is_valid"]:
            logger.warning(
                "Location usage may not fit theme",
                location_id=str(location_id),
                issues=validation["errors"]
            )
