"""Service layer for chapter organization."""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

import structlog
from fastapi import BackgroundTasks

from ..core.exceptions import ChapterError, EventHandlingError
from ..models.chapter import (
    Chapter,
    ChapterOrganization,
    ChapterReference,
    ChapterSection,
    ChapterStatus,
    ChapterType,
    CreateChapterRequest,
    CreateSectionRequest,
    CreateStoryBeatRequest,
    StoryBeat,
    UpdateChapterRequest,
    UpdateSectionRequest,
    UpdateStoryBeatRequest,
)
from ..models.theme import ThemeContext
from .campaign_integration import CampaignService
from .generation import GenerationPipeline


class ChapterService:
    """Service for managing campaign chapters."""

    def __init__(
        self,
        campaign_service: CampaignService,
        generation_pipeline: GenerationPipeline,
        background_tasks: BackgroundTasks,
        logger: Optional[structlog.BoundLogger] = None
    ):
        """Initialize the service."""
        self.campaign_service = campaign_service
        self.generation_pipeline = generation_pipeline
        self.background_tasks = background_tasks
        self.logger = logger or structlog.get_logger()

    def _get_next_order(self, current_items: List[Any], item_type: str) -> int:
        """Get next order number in sequence."""
        if not current_items:
            return 1
        return max(item.order for item in current_items) + 1

    async def create_chapter(
        self,
        request: CreateChapterRequest,
        organization: ChapterOrganization
    ) -> Chapter:
        """Create a new chapter."""
        try:
            # Determine chapter order
            order = request.order
            if order is None:
                order = self._get_next_order(organization.chapters, "chapter")

            # Create chapter
            chapter = Chapter(
                chapter_id=uuid4(),
                campaign_id=request.campaign_id,
                title=request.title,
                description=request.description,
                chapter_type=request.chapter_type,
                status=ChapterStatus.DRAFT,
                order=order,
                theme_context=request.theme_context,
                prerequisites=request.prerequisites,
                metadata=request.metadata,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Update organization
            organization.chapters.append(chapter)
            organization.updated_at = datetime.utcnow()

            self.logger.info(
                "chapter_created",
                campaign_id=str(request.campaign_id),
                chapter_id=str(chapter.chapter_id),
                title=chapter.title
            )

            return chapter

        except Exception as e:
            self.logger.error(
                "chapter_creation_failed",
                campaign_id=str(request.campaign_id),
                error=str(e)
            )
            raise ChapterError(f"Failed to create chapter: {str(e)}")

    async def update_chapter(
        self,
        chapter_id: UUID,
        request: UpdateChapterRequest,
        organization: ChapterOrganization
    ) -> Chapter:
        """Update an existing chapter."""
        try:
            # Find chapter
            chapter = next(
                (c for c in organization.chapters if c.chapter_id == chapter_id),
                None
            )
            if not chapter:
                raise ChapterError(f"Chapter {chapter_id} not found")

            # Update fields
            if request.title is not None:
                chapter.title = request.title
            if request.description is not None:
                chapter.description = request.description
            if request.chapter_type is not None:
                chapter.chapter_type = request.chapter_type
            if request.status is not None:
                chapter.status = request.status
            if request.order is not None:
                chapter.order = request.order
            if request.theme_context is not None:
                chapter.theme_context = request.theme_context
            if request.prerequisites is not None:
                chapter.prerequisites = request.prerequisites
            if request.metadata is not None:
                chapter.metadata = request.metadata

            chapter.updated_at = datetime.utcnow()
            organization.updated_at = datetime.utcnow()

            self.logger.info(
                "chapter_updated",
                campaign_id=str(chapter.campaign_id),
                chapter_id=str(chapter_id),
                title=chapter.title
            )

            return chapter

        except Exception as e:
            self.logger.error(
                "chapter_update_failed",
                chapter_id=str(chapter_id),
                error=str(e)
            )
            raise ChapterError(f"Failed to update chapter: {str(e)}")

    async def delete_chapter(
        self,
        chapter_id: UUID,
        organization: ChapterOrganization
    ) -> None:
        """Delete a chapter."""
        try:
            # Find and remove chapter
            organization.chapters = [
                c for c in organization.chapters if c.chapter_id != chapter_id
            ]
            organization.updated_at = datetime.utcnow()

            self.logger.info(
                "chapter_deleted",
                chapter_id=str(chapter_id)
            )

        except Exception as e:
            self.logger.error(
                "chapter_deletion_failed",
                chapter_id=str(chapter_id),
                error=str(e)
            )
            raise ChapterError(f"Failed to delete chapter: {str(e)}")

    async def add_section(
        self,
        chapter_id: UUID,
        request: CreateSectionRequest,
        organization: ChapterOrganization
    ) -> ChapterSection:
        """Add a section to a chapter."""
        try:
            # Find chapter
            chapter = next(
                (c for c in organization.chapters if c.chapter_id == chapter_id),
                None
            )
            if not chapter:
                raise ChapterError(f"Chapter {chapter_id} not found")

            # Determine section order
            order = request.order
            if order is None:
                order = self._get_next_order(chapter.sections, "section")

            # Create section
            section = ChapterSection(
                section_id=uuid4(),
                title=request.title,
                description=request.description,
                order=order,
                theme_context=request.theme_context,
                requirements=request.requirements,
                metadata=request.metadata
            )

            # Update chapter
            chapter.sections.append(section)
            chapter.updated_at = datetime.utcnow()
            organization.updated_at = datetime.utcnow()

            self.logger.info(
                "section_added",
                chapter_id=str(chapter_id),
                section_id=str(section.section_id),
                title=section.title
            )

            return section

        except Exception as e:
            self.logger.error(
                "section_addition_failed",
                chapter_id=str(chapter_id),
                error=str(e)
            )
            raise ChapterError(f"Failed to add section: {str(e)}")

    async def update_section(
        self,
        chapter_id: UUID,
        section_id: UUID,
        request: UpdateSectionRequest,
        organization: ChapterOrganization
    ) -> ChapterSection:
        """Update a chapter section."""
        try:
            # Find chapter and section
            chapter = next(
                (c for c in organization.chapters if c.chapter_id == chapter_id),
                None
            )
            if not chapter:
                raise ChapterError(f"Chapter {chapter_id} not found")

            section = next(
                (s for s in chapter.sections if s.section_id == section_id),
                None
            )
            if not section:
                raise ChapterError(f"Section {section_id} not found")

            # Update fields
            if request.title is not None:
                section.title = request.title
            if request.description is not None:
                section.description = request.description
            if request.order is not None:
                section.order = request.order
            if request.theme_context is not None:
                section.theme_context = request.theme_context
            if request.requirements is not None:
                section.requirements = request.requirements
            if request.metadata is not None:
                section.metadata = request.metadata

            chapter.updated_at = datetime.utcnow()
            organization.updated_at = datetime.utcnow()

            self.logger.info(
                "section_updated",
                chapter_id=str(chapter_id),
                section_id=str(section_id),
                title=section.title
            )

            return section

        except Exception as e:
            self.logger.error(
                "section_update_failed",
                chapter_id=str(chapter_id),
                section_id=str(section_id),
                error=str(e)
            )
            raise ChapterError(f"Failed to update section: {str(e)}")

    async def delete_section(
        self,
        chapter_id: UUID,
        section_id: UUID,
        organization: ChapterOrganization
    ) -> None:
        """Delete a chapter section."""
        try:
            # Find chapter
            chapter = next(
                (c for c in organization.chapters if c.chapter_id == chapter_id),
                None
            )
            if not chapter:
                raise ChapterError(f"Chapter {chapter_id} not found")

            # Remove section
            chapter.sections = [
                s for s in chapter.sections if s.section_id != section_id
            ]
            chapter.updated_at = datetime.utcnow()
            organization.updated_at = datetime.utcnow()

            self.logger.info(
                "section_deleted",
                chapter_id=str(chapter_id),
                section_id=str(section_id)
            )

        except Exception as e:
            self.logger.error(
                "section_deletion_failed",
                chapter_id=str(chapter_id),
                section_id=str(section_id),
                error=str(e)
            )
            raise ChapterError(f"Failed to delete section: {str(e)}")

    async def add_story_beat(
        self,
        chapter_id: UUID,
        section_id: UUID,
        request: CreateStoryBeatRequest,
        organization: ChapterOrganization
    ) -> StoryBeat:
        """Add a story beat to a section."""
        try:
            # Find chapter and section
            chapter = next(
                (c for c in organization.chapters if c.chapter_id == chapter_id),
                None
            )
            if not chapter:
                raise ChapterError(f"Chapter {chapter_id} not found")

            section = next(
                (s for s in chapter.sections if s.section_id == section_id),
                None
            )
            if not section:
                raise ChapterError(f"Section {section_id} not found")

            # Determine beat order
            order = request.order
            if order is None:
                order = self._get_next_order(section.story_beats, "story_beat")

            # Create story beat
            beat = StoryBeat(
                beat_id=uuid4(),
                title=request.title,
                description=request.description,
                order=order,
                requirements=request.requirements,
                outcomes=request.outcomes,
                metadata=request.metadata
            )

            # Update section
            section.story_beats.append(beat)
            chapter.updated_at = datetime.utcnow()
            organization.updated_at = datetime.utcnow()

            self.logger.info(
                "story_beat_added",
                chapter_id=str(chapter_id),
                section_id=str(section_id),
                beat_id=str(beat.beat_id),
                title=beat.title
            )

            return beat

        except Exception as e:
            self.logger.error(
                "story_beat_addition_failed",
                chapter_id=str(chapter_id),
                section_id=str(section_id),
                error=str(e)
            )
            raise ChapterError(f"Failed to add story beat: {str(e)}")

    async def update_story_beat(
        self,
        chapter_id: UUID,
        section_id: UUID,
        beat_id: UUID,
        request: UpdateStoryBeatRequest,
        organization: ChapterOrganization
    ) -> StoryBeat:
        """Update a story beat."""
        try:
            # Find chapter, section, and beat
            chapter = next(
                (c for c in organization.chapters if c.chapter_id == chapter_id),
                None
            )
            if not chapter:
                raise ChapterError(f"Chapter {chapter_id} not found")

            section = next(
                (s for s in chapter.sections if s.section_id == section_id),
                None
            )
            if not section:
                raise ChapterError(f"Section {section_id} not found")

            beat = next(
                (b for b in section.story_beats if b.beat_id == beat_id),
                None
            )
            if not beat:
                raise ChapterError(f"Story beat {beat_id} not found")

            # Update fields
            if request.title is not None:
                beat.title = request.title
            if request.description is not None:
                beat.description = request.description
            if request.order is not None:
                beat.order = request.order
            if request.requirements is not None:
                beat.requirements = request.requirements
            if request.outcomes is not None:
                beat.outcomes = request.outcomes
            if request.metadata is not None:
                beat.metadata = request.metadata

            chapter.updated_at = datetime.utcnow()
            organization.updated_at = datetime.utcnow()

            self.logger.info(
                "story_beat_updated",
                chapter_id=str(chapter_id),
                section_id=str(section_id),
                beat_id=str(beat_id),
                title=beat.title
            )

            return beat

        except Exception as e:
            self.logger.error(
                "story_beat_update_failed",
                chapter_id=str(chapter_id),
                section_id=str(section_id),
                beat_id=str(beat_id),
                error=str(e)
            )
            raise ChapterError(f"Failed to update story beat: {str(e)}")

    async def delete_story_beat(
        self,
        chapter_id: UUID,
        section_id: UUID,
        beat_id: UUID,
        organization: ChapterOrganization
    ) -> None:
        """Delete a story beat."""
        try:
            # Find chapter and section
            chapter = next(
                (c for c in organization.chapters if c.chapter_id == chapter_id),
                None
            )
            if not chapter:
                raise ChapterError(f"Chapter {chapter_id} not found")

            section = next(
                (s for s in chapter.sections if s.section_id == section_id),
                None
            )
            if not section:
                raise ChapterError(f"Section {section_id} not found")

            # Remove beat
            section.story_beats = [
                b for b in section.story_beats if b.beat_id != beat_id
            ]
            chapter.updated_at = datetime.utcnow()
            organization.updated_at = datetime.utcnow()

            self.logger.info(
                "story_beat_deleted",
                chapter_id=str(chapter_id),
                section_id=str(section_id),
                beat_id=str(beat_id)
            )

        except Exception as e:
            self.logger.error(
                "story_beat_deletion_failed",
                chapter_id=str(chapter_id),
                section_id=str(section_id),
                beat_id=str(beat_id),
                error=str(e)
            )
            raise ChapterError(f"Failed to delete story beat: {str(e)}")

    async def generate_chapter_content(
        self,
        chapter: Chapter,
        organization: ChapterOrganization
    ) -> None:
        """Generate content for a chapter."""
        try:
            # Generate chapter description if not provided
            if not chapter.description:
                result = await self.generation_pipeline.generate_content(
                    content_type="chapter_description",
                    theme_context=chapter.theme_context,
                    existing_content={
                        "title": chapter.title,
                        "type": chapter.chapter_type.value,
                        "campaign_theme": organization.theme_context.name
                        if organization.theme_context else None
                    }
                )
                chapter.description = result.content

            # Generate section content
            for section in chapter.sections:
                if not section.description:
                    result = await self.generation_pipeline.generate_content(
                        content_type="section_description",
                        theme_context=section.theme_context or chapter.theme_context,
                        existing_content={
                            "title": section.title,
                            "chapter_title": chapter.title,
                            "chapter_type": chapter.chapter_type.value
                        }
                    )
                    section.description = result.content

            chapter.updated_at = datetime.utcnow()
            organization.updated_at = datetime.utcnow()

            self.logger.info(
                "chapter_content_generated",
                chapter_id=str(chapter.chapter_id),
                title=chapter.title
            )

        except Exception as e:
            self.logger.error(
                "chapter_content_generation_failed",
                chapter_id=str(chapter.chapter_id),
                error=str(e)
            )
            raise ChapterError(f"Failed to generate chapter content: {str(e)}")

    async def reorder_chapters(
        self,
        chapter_orders: Dict[UUID, int],
        organization: ChapterOrganization
    ) -> None:
        """Reorder chapters in a campaign."""
        try:
            # Update chapter orders
            for chapter in organization.chapters:
                if chapter.chapter_id in chapter_orders:
                    chapter.order = chapter_orders[chapter.chapter_id]
                    chapter.updated_at = datetime.utcnow()

            organization.updated_at = datetime.utcnow()

            self.logger.info(
                "chapters_reordered",
                campaign_id=str(organization.campaign_id),
                chapter_count=len(chapter_orders)
            )

        except Exception as e:
            self.logger.error(
                "chapter_reordering_failed",
                campaign_id=str(organization.campaign_id),
                error=str(e)
            )
            raise ChapterError(f"Failed to reorder chapters: {str(e)}")

    async def reorder_sections(
        self,
        chapter_id: UUID,
        section_orders: Dict[UUID, int],
        organization: ChapterOrganization
    ) -> None:
        """Reorder sections in a chapter."""
        try:
            # Find chapter
            chapter = next(
                (c for c in organization.chapters if c.chapter_id == chapter_id),
                None
            )
            if not chapter:
                raise ChapterError(f"Chapter {chapter_id} not found")

            # Update section orders
            for section in chapter.sections:
                if section.section_id in section_orders:
                    section.order = section_orders[section.section_id]

            chapter.updated_at = datetime.utcnow()
            organization.updated_at = datetime.utcnow()

            self.logger.info(
                "sections_reordered",
                chapter_id=str(chapter_id),
                section_count=len(section_orders)
            )

        except Exception as e:
            self.logger.error(
                "section_reordering_failed",
                chapter_id=str(chapter_id),
                error=str(e)
            )
            raise ChapterError(f"Failed to reorder sections: {str(e)}")

    async def reorder_story_beats(
        self,
        chapter_id: UUID,
        section_id: UUID,
        beat_orders: Dict[UUID, int],
        organization: ChapterOrganization
    ) -> None:
        """Reorder story beats in a section."""
        try:
            # Find chapter and section
            chapter = next(
                (c for c in organization.chapters if c.chapter_id == chapter_id),
                None
            )
            if not chapter:
                raise ChapterError(f"Chapter {chapter_id} not found")

            section = next(
                (s for s in chapter.sections if s.section_id == section_id),
                None
            )
            if not section:
                raise ChapterError(f"Section {section_id} not found")

            # Update beat orders
            for beat in section.story_beats:
                if beat.beat_id in beat_orders:
                    beat.order = beat_orders[beat.beat_id]

            chapter.updated_at = datetime.utcnow()
            organization.updated_at = datetime.utcnow()

            self.logger.info(
                "story_beats_reordered",
                chapter_id=str(chapter_id),
                section_id=str(section_id),
                beat_count=len(beat_orders)
            )

        except Exception as e:
            self.logger.error(
                "story_beat_reordering_failed",
                chapter_id=str(chapter_id),
                section_id=str(section_id),
                error=str(e)
            )
            raise ChapterError(f"Failed to reorder story beats: {str(e)}")
