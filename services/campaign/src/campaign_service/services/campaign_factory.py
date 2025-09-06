"""Campaign factory service for generating and structuring campaigns."""
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from campaign_service.core.config import get_settings
from campaign_service.core.exceptions import GenerationError, ThemeValidationError
from campaign_service.core.logging import get_logger
from campaign_service.models.campaign import Campaign, CampaignState, CampaignType, Chapter, ChapterState, ChapterType
from campaign_service.repositories.campaign import CampaignRepository, ChapterRepository
from campaign_service.services.theme import ThemeService

settings = get_settings()
logger = get_logger(__name__)


class CampaignFactoryService:
    """Service for creating and structuring campaigns."""

    def __init__(
        self,
        db: AsyncSession,
        campaign_repo: CampaignRepository,
        chapter_repo: ChapterRepository,
        theme_service: ThemeService,
        message_hub_client: Any,  # type: ignore
    ) -> None:
        """Initialize service.

        Args:
            db (AsyncSession): Database session
            campaign_repo (CampaignRepository): Campaign repository
            chapter_repo (ChapterRepository): Chapter repository
            theme_service (ThemeService): Theme service
        """
        self.db = db
        self.campaign_repo = campaign_repo
        self.chapter_repo = chapter_repo
        self.theme_service = theme_service
        self.message_hub = message_hub_client

    async def create_campaign(
        self,
        name: str,
        description: str,
        campaign_type: CampaignType,
        creator_id: UUID,
        owner_id: UUID,
        theme_id: Optional[UUID] = None,
        metadata: Optional[Dict] = None,
    ) -> Campaign:
        """Create a new campaign.

        Args:
            name (str): Campaign name
            description (str): Campaign description
            campaign_type (CampaignType): Campaign type
            creator_id (UUID): Creator ID
            owner_id (UUID): Owner ID
            theme_id (Optional[UUID], optional): Theme ID. Defaults to None.
            metadata (Optional[Dict], optional): Additional metadata. Defaults to None.

        Returns:
            Campaign: Created campaign
        """
        # Create campaign data
        campaign_data = {
            "name": name,
            "description": description,
            "campaign_type": campaign_type,
            "creator_id": creator_id,
            "owner_id": owner_id,
            "state": CampaignState.DRAFT,
            "metadata": metadata or {},
        }

        # Add theme if provided
        if theme_id:
            theme_data = await self.theme_service.get_theme(theme_id)
            if theme_data:
                campaign_data["theme_id"] = theme_id
                campaign_data["theme_data"] = theme_data

        # Create campaign
        campaign = await self.campaign_repo.create(campaign_data)

        # Create initial chapter structure
        await self._create_initial_chapters(campaign.id)

        # Refresh campaign to include chapters
        return await self.campaign_repo.get_with_chapters(campaign.id)

    async def _create_initial_chapters(self, campaign_id: UUID) -> List[Chapter]:
        """Create initial chapter structure for a campaign.

        Args:
            campaign_id (UUID): Campaign ID

        Returns:
            List[Chapter]: Created chapters
        """
        # Define initial chapter structure
        chapters_data = [
            {
                "campaign_id": campaign_id,
                "title": "Introduction",
                "description": "Campaign introduction and setup",
                "chapter_type": ChapterType.INTRODUCTION,
                "state": ChapterState.DRAFT,
                "sequence_number": 1,
                "prerequisites": [],
                "content": {},
                "metadata": {},
            },
            {
                "campaign_id": campaign_id,
                "title": "Chapter 1",
                "description": "First story chapter",
                "chapter_type": ChapterType.STORY,
                "state": ChapterState.DRAFT,
                "sequence_number": 2,
                "prerequisites": [],  # Will be updated with introduction ID
                "content": {},
                "metadata": {},
            },
            {
                "campaign_id": campaign_id,
                "title": "Chapter 2",
                "description": "Second story chapter",
                "chapter_type": ChapterType.STORY,
                "state": ChapterState.DRAFT,
                "sequence_number": 3,
                "prerequisites": [],  # Will be updated with Chapter 1 ID
                "content": {},
                "metadata": {},
            },
        ]

        # Create chapters
        chapters = []
        for chapter_data in chapters_data:
            chapter = await self.chapter_repo.create(chapter_data)
            chapters.append(chapter)

        # Update prerequisites after creation
        await self._update_chapter_prerequisites(chapters)

        # Generate content for all chapters
        await self._generate_chapter_contents(chapters, campaign_id)

        return chapters

    async def _generate_chapter_contents(self, chapters: List[Chapter], campaign_id: UUID) -> None:
        """Generate content for all chapters.

        Args:
            chapters (List[Chapter]): List of chapters
            campaign_id (UUID): Campaign ID
        """
        try:
            # Get campaign data for context
            campaign = await self.campaign_repo.get(campaign_id)
            if not campaign:
                return

            # Get campaign theme
            theme_profile = await self.theme_service.get_theme_profile(str(campaign.theme_id))

            for chapter in chapters:
                try:
                    # Generate content using LLM
                    content = await self.llm.generate_chapter_content({
                        "chapter": chapter.to_dict(),
                        "theme": theme_profile,
                        "campaign_context": {
                            "name": campaign.name,
                            "description": campaign.description,
                            "type": campaign.campaign_type.value,
                            "state": campaign.state.value,
                        },
                        "requirements": {
                            "maintain_theme_consistency": True,
                            "respect_prerequisites": True,
                            "include_plot_hooks": True,
                        },
                    })

                    # Update chapter with generated content
                    await self.chapter_repo.update(
                        chapter.id,
                        {
                            "content": content,
                            "metadata": {
                                **chapter.metadata,
                                "content_generated": True,
                                "generated_at": datetime.utcnow().isoformat(),
                            },
                        },
                    )

                    # Add delay between generations to respect rate limits
                    await asyncio.sleep(1)

                except Exception as e:
                    logger.error(
                        "Chapter content generation failed",
                        chapter_id=str(chapter.id),
                        error=str(e)
                    )
                    # Continue with next chapter
                    continue

        except Exception as e:
            logger.error(
                "Failed to generate chapter contents",
                campaign_id=str(campaign_id),
                error=str(e)
            )
            # Let the error propagate up
            raise

    async def _update_chapter_prerequisites(self, chapters: List[Chapter]) -> None:
        """Update chapter prerequisites.

        Args:
            chapters (List[Chapter]): List of chapters
        """
        # Skip if less than 2 chapters
        if len(chapters) < 2:
            return

        # Update prerequisites for each chapter except the first one
        for i, chapter in enumerate(chapters[1:], start=1):
            # Get previous chapter's ID
            prev_chapter_id = chapters[i - 1].id

            # Update prerequisites
            await self.chapter_repo.update(
                chapter.id,
                {
                    "prerequisites": [prev_chapter_id],
                    "updated_at": datetime.utcnow(),
                },
            )
