"""Event subscribers for campaign service."""
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ...core.logging import get_logger
from ...models.campaign import Campaign
from ...models.chapter import Chapter
from ...models.version import Version, Branch, MergeRequest
from ...services.campaign_factory import CampaignFactory
from ...services.chapter_service import ChapterService
from ...services.version_control import VersionControlService
from ...services.theme_service import ThemeService
from .events import (
    EventType,
    BaseEvent,
    CampaignEvent,
    ChapterEvent,
    VersionEvent,
    ThemeEvent,
)

logger = get_logger(__name__)


class EventSubscriber:
    """Base class for event subscribers."""

    def __init__(
        self,
        db: Session,
        campaign_factory: CampaignFactory,
        chapter_service: ChapterService,
        version_control: VersionControlService,
        theme_service: ThemeService,
    ):
        """Initialize with required dependencies."""
        self.db = db
        self.campaign_factory = campaign_factory
        self.chapter_service = chapter_service
        self.version_control = version_control
        self.theme_service = theme_service

    async def handle_campaign_created(self, event: CampaignEvent):
        """Handle campaign creation events."""
        try:
            # Update campaign catalog
            await self.campaign_factory.update_catalog(
                event.campaign_id,
                event.name,
                event.theme
            )

            # Generate initial content if needed
            if event.metadata and event.metadata.get("generate_content"):
                await self.campaign_factory.generate_initial_content(
                    event.campaign_id
                )

            logger.info(
                "Handled campaign creation",
                campaign_id=str(event.campaign_id),
                name=event.name
            )

        except Exception as e:
            logger.error(
                "Failed to handle campaign creation",
                error=str(e),
                campaign_id=str(event.campaign_id)
            )

    async def handle_campaign_updated(self, event: CampaignEvent):
        """Handle campaign update events."""
        try:
            # Update campaign catalog
            await self.campaign_factory.update_catalog(
                event.campaign_id,
                event.name,
                event.theme
            )

            # Update version if provided
            if event.version:
                campaign = self.db.query(Campaign).get(event.campaign_id)
                if campaign:
                    campaign.version = event.version
                    self.db.commit()

            logger.info(
                "Handled campaign update",
                campaign_id=str(event.campaign_id),
                name=event.name
            )

        except Exception as e:
            logger.error(
                "Failed to handle campaign update",
                error=str(e),
                campaign_id=str(event.campaign_id)
            )

    async def handle_chapter_created(self, event: ChapterEvent):
        """Handle chapter creation events."""
        try:
            # Update chapter relationships
            chapter = self.db.query(Chapter).get(event.chapter_id)
            if chapter:
                # Update campaign if this is the first chapter
                campaign = self.db.query(Campaign).get(event.campaign_id)
                if campaign and not campaign.current_chapter:
                    campaign.current_chapter = chapter.id
                    self.db.commit()

            logger.info(
                "Handled chapter creation",
                campaign_id=str(event.campaign_id),
                chapter_id=str(event.chapter_id)
            )

        except Exception as e:
            logger.error(
                "Failed to handle chapter creation",
                error=str(e),
                campaign_id=str(event.campaign_id),
                chapter_id=str(event.chapter_id)
            )

    async def handle_chapter_completed(self, event: ChapterEvent):
        """Handle chapter completion events."""
        try:
            # Generate next chapter suggestion if needed
            campaign = self.db.query(Campaign).get(event.campaign_id)
            if campaign and campaign.current_chapter == event.chapter_id:
                next_chapter = await self.chapter_service.suggest_next_chapter(
                    event.campaign_id,
                    event.chapter_id
                )
                if next_chapter:
                    campaign.current_chapter = next_chapter.id
                    self.db.commit()

            logger.info(
                "Handled chapter completion",
                campaign_id=str(event.campaign_id),
                chapter_id=str(event.chapter_id)
            )

        except Exception as e:
            logger.error(
                "Failed to handle chapter completion",
                error=str(e),
                campaign_id=str(event.campaign_id),
                chapter_id=str(event.chapter_id)
            )

    async def handle_version_created(self, event: VersionEvent):
        """Handle version creation events."""
        try:
            # Update branch head if needed
            branch = self.db.query(Branch).filter_by(
                campaign_id=event.campaign_id,
                name=event.branch
            ).first()

            if branch:
                branch.head = event.version_hash
                self.db.commit()

            logger.info(
                "Handled version creation",
                campaign_id=str(event.campaign_id),
                version=event.version_hash
            )

        except Exception as e:
            logger.error(
                "Failed to handle version creation",
                error=str(e),
                campaign_id=str(event.campaign_id),
                version=event.version_hash
            )

    async def handle_merge_completed(self, event: VersionEvent):
        """Handle merge completion events."""
        try:
            # Update merge request status
            merge_request = self.db.query(MergeRequest).filter_by(
                campaign_id=event.campaign_id,
                status="in_progress"
            ).first()

            if merge_request:
                merge_request.status = "completed"
                merge_request.merge_commit_hash = event.version_hash
                self.db.commit()

            logger.info(
                "Handled merge completion",
                campaign_id=str(event.campaign_id),
                version=event.version_hash
            )

        except Exception as e:
            logger.error(
                "Failed to handle merge completion",
                error=str(e),
                campaign_id=str(event.campaign_id),
                version=event.version_hash
            )

    async def handle_theme_validation(self, event: ThemeEvent):
        """Handle theme validation events."""
        try:
            # Update campaign theme status
            campaign = self.db.query(Campaign).get(event.campaign_id)
            if campaign:
                theme_status = "valid" if event.validation_result["is_valid"] else "invalid"
                campaign.theme_status = theme_status
                self.db.commit()

            logger.info(
                "Handled theme validation",
                campaign_id=str(event.campaign_id),
                theme_id=str(event.theme_id)
            )

        except Exception as e:
            logger.error(
                "Failed to handle theme validation",
                error=str(e),
                campaign_id=str(event.campaign_id),
                theme_id=str(event.theme_id)
            )
