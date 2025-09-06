"""Chapter service implementation."""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from campaign_service.core.config import get_settings
from campaign_service.core.exceptions import (
    ChapterNotFoundError,
    GenerationError,
    StateError,
    ValidationError,
)
from campaign_service.core.logging import get_logger
from campaign_service.models.campaign import Chapter, ChapterState
from campaign_service.repositories.campaign import ChapterRepository
from campaign_service.services.theme import ThemeService

settings = get_settings()
logger = get_logger(__name__)


class ChapterService:
    """Service for managing campaign chapters."""

    def __init__(
        self,
        db: AsyncSession,
        chapter_repo: ChapterRepository,
        theme_service: ThemeService,
        message_hub_client: Any,  # type: ignore
    ) -> None:
        """Initialize chapter service.

        Args:
            db (AsyncSession): Database session
            chapter_repo (ChapterRepository): Chapter repository
            theme_service (ThemeService): Theme service
            llm_client (Any): LLM client
            message_hub_client (Any): Message hub client
        """
        self.db = db
        self.chapter_repo = chapter_repo
        self.theme_service = theme_service
        self.message_hub = message_hub_client

    async def create_chapter(
        self,
        campaign_id: UUID,
        title: str,
        description: str,
        chapter_type: str,
        sequence_number: int,
        prerequisites: List[UUID],
        content: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
    ) -> Chapter:
        """Create a new chapter.

        Args:
            campaign_id (UUID): Campaign ID
            title (str): Chapter title
            description (str): Chapter description
            chapter_type (str): Chapter type
            sequence_number (int): Chapter sequence number
            prerequisites (List[UUID]): Prerequisite chapter IDs
            content (Optional[Dict], optional): Chapter content. Defaults to None.
            metadata (Optional[Dict], optional): Additional metadata. Defaults to None.

        Returns:
            Chapter: Created chapter

        Raises:
            ValidationError: If validation fails
            GenerationError: If content generation fails
        """
        try:
            # Validate prerequisites exist
            await self._validate_prerequisites(prerequisites)

            # Create chapter data
            chapter_data = {
                "campaign_id": campaign_id,
                "title": title,
                "description": description,
                "chapter_type": chapter_type,
                "sequence_number": sequence_number,
                "prerequisites": prerequisites,
                "state": ChapterState.DRAFT,
                "content": content or {},
                "metadata": metadata or {},
            }

            # Create chapter
            chapter = await self.chapter_repo.create(chapter_data)

            # Generate initial content if not provided
            if not content:
                await self._generate_chapter_content(chapter.id)

            # Publish creation event
            await self.message_hub.publish(
                "campaign.chapter.created",
                {
                    "campaign_id": str(campaign_id),
                    "chapter_id": str(chapter.id),
                },
            )

            return chapter

        except Exception as e:
            logger.error("Chapter creation failed", error=str(e))
            raise

    async def update_chapter(
        self,
        chapter_id: UUID,
        updates: Dict,
    ) -> Chapter:
        """Update a chapter.

        Args:
            chapter_id (UUID): Chapter ID
            updates (Dict): Update data

        Returns:
            Chapter: Updated chapter

        Raises:
            ChapterNotFoundError: If chapter not found
            ValidationError: If validation fails
        """
        try:
            # Get existing chapter
            chapter = await self.chapter_repo.get(chapter_id)
            if not chapter:
                raise ChapterNotFoundError(f"Chapter not found: {chapter_id}")

            # Validate state transition if state is being updated
            if "state" in updates:
                await self._validate_state_transition(chapter, updates["state"])

            # Update chapter
            updated_chapter = await self.chapter_repo.update(chapter_id, updates)
            if not updated_chapter:
                raise ChapterNotFoundError(f"Chapter not found: {chapter_id}")

            # Publish update event
            await self.message_hub.publish(
                "campaign.chapter.updated",
                {
                    "campaign_id": str(chapter.campaign_id),
                    "chapter_id": str(chapter_id),
                    "updates": list(updates.keys()),
                },
            )

            return updated_chapter

        except Exception as e:
            logger.error("Chapter update failed", error=str(e))
            raise

    async def delete_chapter(
        self,
        chapter_id: UUID,
    ) -> bool:
        """Delete a chapter.

        Args:
            chapter_id (UUID): Chapter ID

        Returns:
            bool: True if deleted

        Raises:
            ChapterNotFoundError: If chapter not found
            StateError: If chapter cannot be deleted
        """
        try:
            # Get chapter with campaign
            chapter = await self.chapter_repo.get(chapter_id)
            if not chapter:
                raise ChapterNotFoundError(f"Chapter not found: {chapter_id}")

            # Check if chapter can be deleted
            if await self._has_dependent_chapters(chapter_id):
                raise StateError("Cannot delete chapter with dependencies")

            # Delete chapter
            result = await self.chapter_repo.delete(chapter_id)

            if result:
                # Publish deletion event
                await self.message_hub.publish(
                    "campaign.chapter.deleted",
                    {
                        "campaign_id": str(chapter.campaign_id),
                        "chapter_id": str(chapter_id),
                    },
                )

            return result

        except Exception as e:
            logger.error("Chapter deletion failed", error=str(e))
            raise

    async def reorder_chapters(
        self,
        campaign_id: UUID,
        chapter_order: List[UUID],
    ) -> List[Chapter]:
        """Reorder chapters in a campaign.

        Args:
            campaign_id (UUID): Campaign ID
            chapter_order (List[UUID]): New chapter order

        Returns:
            List[Chapter]: Reordered chapters

        Raises:
            ValidationError: If validation fails
        """
        try:
            # Get all campaign chapters
            chapters = await self.chapter_repo.get_by_campaign(campaign_id)
            chapter_dict = {str(c.id): c for c in chapters}

            # Validate all chapters exist
            for chapter_id in chapter_order:
                if str(chapter_id) not in chapter_dict:
                    raise ValidationError(f"Chapter not found: {chapter_id}")

            # Update sequence numbers
            updated_chapters = []
            for idx, chapter_id in enumerate(chapter_order, 1):
                chapter = await self.chapter_repo.update(
                    chapter_id,
                    {"sequence_number": idx},
                )
                if chapter:
                    updated_chapters.append(chapter)

            # Publish reorder event
            await self.message_hub.publish(
                "campaign.chapters.reordered",
                {
                    "campaign_id": str(campaign_id),
                    "chapter_order": [str(id) for id in chapter_order],
                },
            )

            return updated_chapters

        except Exception as e:
            logger.error("Chapter reordering failed", error=str(e))
            raise

    async def _validate_prerequisites(self, prerequisites: List[UUID]) -> None:
        """Validate prerequisite chapters exist.

        Args:
            prerequisites (List[UUID]): Prerequisite chapter IDs

        Raises:
            ValidationError: If validation fails
        """
        for prereq_id in prerequisites:
            chapter = await self.chapter_repo.get(prereq_id)
            if not chapter:
                raise ValidationError(f"Prerequisite chapter not found: {prereq_id}")

    async def _validate_state_transition(
        self,
        chapter: Chapter,
        new_state: str,
    ) -> None:
        """Validate chapter state transition.

        Args:
            chapter (Chapter): Current chapter
            new_state (str): New state

        Raises:
            StateError: If transition is invalid
        """
        valid_transitions = {
            ChapterState.DRAFT: [ChapterState.READY],
            ChapterState.READY: [ChapterState.IN_PROGRESS, ChapterState.DRAFT],
            ChapterState.IN_PROGRESS: [ChapterState.COMPLETED, ChapterState.READY],
            ChapterState.COMPLETED: [ChapterState.IN_PROGRESS],
        }

        if new_state not in valid_transitions.get(chapter.state, []):
            raise StateError(
                f"Invalid state transition from {chapter.state} to {new_state}"
            )

    async def _has_dependent_chapters(self, chapter_id: UUID) -> bool:
        """Check if any chapters depend on this chapter.

        Args:
            chapter_id (UUID): Chapter ID

        Returns:
            bool: True if has dependencies
        """
        # Get all chapters that list this chapter as a prerequisite
        dependent_chapters = await self.chapter_repo.get_multi(
            prerequisites=[chapter_id]
        )
        return len(dependent_chapters) > 0

    async def _generate_chapter_content(self, chapter_id: UUID) -> None:
        """Generate initial chapter content.

        Args:
            chapter_id (UUID): Chapter ID

        Raises:
            GenerationError: If content generation fails
        """
        try:
            # Get chapter
            chapter = await self.chapter_repo.get(chapter_id)
            if not chapter:
                raise ChapterNotFoundError(f"Chapter not found: {chapter_id}")

            # Get campaign theme
            campaign_data = await self.message_hub.request(
                "campaign.get",
                {"campaign_id": str(chapter.campaign_id)},
            )

            # Generate content using LLM service
            content = await self.message_hub.request(
                "llm.generate_chapter_content",
                {
                    "title": chapter.title,
                    "description": chapter.description,
                    "chapter_type": chapter.chapter_type,
                    "sequence_number": chapter.sequence_number,
                    "theme": campaign_data["theme_data"],
                    "requirements": {
                        "maintain_theme_consistency": True,
                        "respect_prerequisites": True,
                        "include_plot_hooks": True,
                    },
                }
            )

            # Update chapter
            await self.chapter_repo.update(
                chapter_id,
                {
                    "content": content,
                    "metadata": {
                        **chapter.metadata,
                        "content_generated": True,
                        "generated_at": datetime.utcnow().isoformat(),
                    },
                },
            )

        except Exception as e:
            logger.error("Chapter content generation failed", error=str(e))
            raise GenerationError(f"Failed to generate chapter content: {e}")
