"""Chapter management service."""
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from ..core.ai import AIClient
from ..core.logging import get_logger
from ..models.campaign import Campaign
from ..models.chapter import Chapter
from ..models.content import ChapterNPC, ChapterLocation
from ..services.theme_service import ThemeService
from ..services.version_service import VersionService
from ..api.schemas.chapter import (
    ChapterType,
    ChapterStatus,
    CreateChapterRequest,
    UpdateChapterRequest,
)

logger = get_logger(__name__)


class ChapterService:
    """Service for managing campaign chapters."""

    def __init__(
        self,
        db: Session,
        ai_client: AIClient,
        theme_service: ThemeService,
        version_service: VersionService,
        message_hub_client,
    ):
        """Initialize with required dependencies."""
        self.db = db
        self.ai_client = ai_client
        self.theme_service = theme_service
        self.version_service = version_service
        self.message_hub = message_hub_client

    async def create_chapter(
        self,
        campaign_id: UUID,
        request: CreateChapterRequest,
    ) -> Tuple[UUID, Chapter]:
        """Create a new chapter."""
        try:
            # Validate campaign
            campaign = self.db.query(Campaign).get(campaign_id)
            if not campaign:
                raise ValueError("Campaign not found")

            # Get theme profile
            theme_profile = await self.theme_service.get_theme_profile(
                campaign.theme.primary,
                campaign.theme.secondary
            )

            # Calculate sequence number
            sequence = await self._calculate_sequence_number(
                campaign_id,
                request.chapter_type,
                request.dependencies
            )

            # Generate chapter content
            chapter_content = await self.ai_client.generate_chapter({
                "campaign_id": str(campaign_id),
                "title": request.title,
                "chapter_type": request.chapter_type,
                "theme": theme_profile.dict(),
                "sequence_number": sequence,
                "requirements": request.requirements.dict(),
                "dependencies": [str(dep) for dep in request.dependencies]
            })

            # Create chapter
            chapter = Chapter(
                campaign_id=campaign_id,
                title=request.title,
                type=request.chapter_type,
                sequence_number=sequence,
                theme=request.theme,
                min_level=request.requirements.level_range["min"],
                max_level=request.requirements.level_range["max"],
                min_party_size=request.requirements.party_size["min"],
                max_party_size=request.requirements.party_size["max"],
                content=chapter_content,
                status=ChapterStatus.DRAFT,
                version=self.version_service.create_initial_hash()
            )
            self.db.add(chapter)

            # Add dependencies
            if request.dependencies:
                await self._add_dependencies(chapter.id, request.dependencies)

            # Generate encounters
            encounters = await self.ai_client.generate_encounters({
                "chapter": chapter_content,
                "theme_profile": theme_profile.dict(),
                "requirements": request.requirements.dict()
            })
            chapter.encounters = encounters["encounters"]

            # Associate NPCs and locations
            await self._associate_content(
                chapter,
                chapter_content.get("npcs", []),
                chapter_content.get("locations", [])
            )

            self.db.commit()

            # Notify integrations
            await self.message_hub.publish(
                "campaign.chapter_created",
                {
                    "campaign_id": str(campaign_id),
                    "chapter_id": str(chapter.id),
                    "sequence": sequence,
                    "type": request.chapter_type
                }
            )

            return chapter.id, chapter

        except Exception as e:
            self.db.rollback()
            logger.error("Failed to create chapter", error=str(e))
            raise ValueError(f"Failed to create chapter: {e}")

    async def update_chapter(
        self,
        chapter_id: UUID,
        request: UpdateChapterRequest,
    ) -> Chapter:
        """Update an existing chapter."""
        try:
            # Get chapter
            chapter = self.db.query(Chapter).get(chapter_id)
            if not chapter:
                raise ValueError("Chapter not found")

            # Create new version
            new_version = self.version_service.create_version_hash(
                chapter.dict(),
                request.commit_message
            )

            # Update fields
            updates = request.dict(exclude_unset=True)
            for field, value in updates.items():
                if field != "commit_message" and hasattr(chapter, field):
                    setattr(chapter, field, value)

            chapter.version = new_version

            # Update dependencies if provided
            if request.dependencies is not None:
                await self._update_dependencies(
                    chapter.id,
                    request.dependencies
                )

            # Validate against theme
            campaign = self.db.query(Campaign).get(chapter.campaign_id)
            theme_profile = await self.theme_service.get_theme_profile(
                campaign.theme.primary,
                campaign.theme.secondary
            )
            validation = await self.ai_client.validate_theme(
                chapter.dict(),
                theme_profile.dict()
            )

            if not validation["is_valid"]:
                raise ValueError(
                    f"Theme validation failed: {validation['errors']}"
                )

            self.db.commit()

            # Notify integrations
            await self.message_hub.publish(
                "campaign.chapter_updated",
                {
                    "campaign_id": str(chapter.campaign_id),
                    "chapter_id": str(chapter.id),
                    "version": new_version,
                    "changes": list(updates.keys())
                }
            )

            return chapter

        except Exception as e:
            self.db.rollback()
            logger.error("Failed to update chapter", error=str(e))
            raise ValueError(f"Failed to update chapter: {e}")

    async def delete_chapter(self, chapter_id: UUID) -> None:
        """Delete a chapter."""
        try:
            chapter = self.db.query(Chapter).get(chapter_id)
            if not chapter:
                raise ValueError("Chapter not found")

            # Check for dependencies
            dependent_chapters = await self._get_dependent_chapters(chapter_id)
            if dependent_chapters:
                raise ValueError(
                    "Cannot delete chapter with dependencies: " +
                    ", ".join(str(c.id) for c in dependent_chapters)
                )

            # Archive instead of delete
            chapter.status = ChapterStatus.ARCHIVED
            self.db.commit()

            # Notify integrations
            await self.message_hub.publish(
                "campaign.chapter_archived",
                {
                    "campaign_id": str(chapter.campaign_id),
                    "chapter_id": str(chapter.id)
                }
            )

        except Exception as e:
            self.db.rollback()
            logger.error("Failed to delete chapter", error=str(e))
            raise ValueError(f"Failed to delete chapter: {e}")

    async def get_chapter_sequence(
        self,
        campaign_id: UUID,
        status: Optional[List[ChapterStatus]] = None
    ) -> List[Dict]:
        """Get ordered chapter sequence."""
        try:
            query = select(Chapter).where(
                Chapter.campaign_id == campaign_id
            )

            if status:
                query = query.where(Chapter.status.in_(status))

            chapters = self.db.execute(query).scalars().all()
            
            # Build dependency graph
            graph = {}
            for chapter in chapters:
                deps = await self._get_chapter_dependencies(chapter.id)
                graph[chapter.id] = [d.id for d in deps]

            # Topologically sort chapters
            sorted_chapters = self._topological_sort(graph)

            # Build sequence info
            sequence = []
            for chapter_id in sorted_chapters:
                chapter = next(c for c in chapters if c.id == chapter_id)
                sequence.append({
                    "id": chapter.id,
                    "title": chapter.title,
                    "type": chapter.type,
                    "status": chapter.status,
                    "sequence_number": chapter.sequence_number,
                    "dependencies": graph[chapter.id]
                })

            return sequence

        except Exception as e:
            logger.error("Failed to get chapter sequence", error=str(e))
            raise ValueError(f"Failed to get chapter sequence: {e}")

    async def reorder_chapters(
        self,
        campaign_id: UUID,
        new_order: List[UUID]
    ) -> List[Dict]:
        """Reorder chapters in a campaign."""
        try:
            # Validate chapters
            chapters = self.db.query(Chapter).filter(
                Chapter.id.in_(new_order)
            ).all()
            if len(chapters) != len(new_order):
                raise ValueError("Invalid chapter IDs in new order")

            # Update sequence numbers
            for idx, chapter_id in enumerate(new_order, 1):
                chapter = next(c for c in chapters if c.id == chapter_id)
                chapter.sequence_number = idx

            self.db.commit()

            # Get new sequence
            return await self.get_chapter_sequence(campaign_id)

        except Exception as e:
            self.db.rollback()
            logger.error("Failed to reorder chapters", error=str(e))
            raise ValueError(f"Failed to reorder chapters: {e}")

    async def _calculate_sequence_number(
        self,
        campaign_id: UUID,
        chapter_type: ChapterType,
        dependencies: List[UUID]
    ) -> int:
        """Calculate appropriate sequence number for new chapter."""
        # Get existing chapters
        chapters = self.db.query(Chapter).filter(
            Chapter.campaign_id == campaign_id
        ).all()

        if not chapters:
            return 1

        if dependencies:
            # Place after all dependencies
            dep_chapters = [c for c in chapters if c.id in dependencies]
            return max(c.sequence_number for c in dep_chapters) + 1

        # Place based on chapter type
        type_order = {
            ChapterType.INTRODUCTION: 0,
            ChapterType.EXPOSITION: 1,
            ChapterType.RISING_ACTION: 2,
            ChapterType.CLIMAX: 3,
            ChapterType.FALLING_ACTION: 4,
            ChapterType.RESOLUTION: 5,
            ChapterType.SIDE_QUEST: 6
        }

        target_pos = type_order[chapter_type]
        relevant_chapters = [
            c for c in chapters
            if type_order[ChapterType(c.type)] <= target_pos
        ]

        if not relevant_chapters:
            return len(chapters) + 1

        return max(c.sequence_number for c in relevant_chapters) + 1

    async def _add_dependencies(
        self,
        chapter_id: UUID,
        dependencies: List[UUID]
    ) -> None:
        """Add chapter dependencies."""
        chapter = self.db.query(Chapter).get(chapter_id)
        for dep_id in dependencies:
            dep = self.db.query(Chapter).get(dep_id)
            if not dep or dep.campaign_id != chapter.campaign_id:
                raise ValueError(f"Invalid dependency: {dep_id}")
            chapter.dependencies.append(dep)

    async def _update_dependencies(
        self,
        chapter_id: UUID,
        new_dependencies: List[UUID]
    ) -> None:
        """Update chapter dependencies."""
        chapter = self.db.query(Chapter).get(chapter_id)
        # Clear existing
        chapter.dependencies = []
        # Add new
        await self._add_dependencies(chapter_id, new_dependencies)

    async def _get_dependent_chapters(self, chapter_id: UUID) -> List[Chapter]:
        """Get chapters that depend on the given chapter."""
        return self.db.query(Chapter).filter(
            Chapter.dependencies.any(id=chapter_id)
        ).all()

    async def _get_chapter_dependencies(self, chapter_id: UUID) -> List[Chapter]:
        """Get dependencies for a chapter."""
        chapter = self.db.query(Chapter).get(chapter_id)
        return chapter.dependencies

    def _topological_sort(self, graph: Dict[UUID, List[UUID]]) -> List[UUID]:
        """Sort chapters based on dependencies."""
        sorted_list = []
        visited = set()
        temp = set()

        def visit(node: UUID):
            if node in temp:
                raise ValueError("Cycle detected in chapter dependencies")
            if node in visited:
                return
            temp.add(node)
            for dep in graph.get(node, []):
                visit(dep)
            temp.remove(node)
            visited.add(node)
            sorted_list.insert(0, node)

        for node in graph:
            if node not in visited:
                visit(node)

        return sorted_list

    async def _associate_content(
        self,
        chapter: Chapter,
        npcs: List[Dict],
        locations: List[Dict]
    ) -> None:
        """Associate NPCs and locations with chapter."""
        # Add NPCs
        for npc_data in npcs:
            npc_assoc = ChapterNPC(
                chapter_id=chapter.id,
                npc_id=npc_data["id"],
                role=npc_data["role"],
                significance=npc_data["significance"],
                location_id=npc_data.get("location_id"),
                interaction_points=npc_data.get("interaction_points", [])
            )
            self.db.add(npc_assoc)

        # Add locations
        for loc_data in locations:
            loc_assoc = ChapterLocation(
                chapter_id=chapter.id,
                location_id=loc_data["id"],
                role=loc_data["role"],
                significance=loc_data["significance"],
                description_override=loc_data.get("description_override"),
                state_changes=loc_data.get("state_changes", [])
            )
            self.db.add(loc_assoc)
