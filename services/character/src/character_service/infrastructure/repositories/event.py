"""Repository for campaign events and impacts."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.domain.models import CampaignEvent, EventImpact
from character_service.infrastructure.models import models
from character_service.infrastructure.repositories.base import BaseRepository


class CampaignEventRepository(BaseRepository[CampaignEvent, models.CampaignEvent]):
    """Repository for campaign events."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository."""
        super().__init__(session, models.CampaignEvent, CampaignEvent)

    async def get_character_events(
        self,
        character_id: UUID,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[CampaignEvent]:
        """Get campaign events for a character."""
        query = select(models.CampaignEvent).where(
            models.CampaignEvent.character_id == character_id
        )

        if not include_deleted:
            query = query.where(models.CampaignEvent.is_deleted == False)

        query = query.order_by(models.CampaignEvent.timestamp.desc())
        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        return [self._to_domain(event) for event in result.scalars().all()]

    async def get_unapplied_events(
        self,
        character_id: UUID,
        limit: int = 100,
    ) -> List[CampaignEvent]:
        """Get unapplied events for a character."""
        query = select(models.CampaignEvent).where(
            models.CampaignEvent.character_id == character_id,
            models.CampaignEvent.is_deleted == False,
            models.CampaignEvent.applied == False,
        ).order_by(models.CampaignEvent.timestamp.asc())
        query = query.limit(limit)

        result = await self.db.execute(query)
        return [self._to_domain(event) for event in result.scalars().all()]

    async def mark_applied(
        self,
        event_id: UUID,
        applied: bool = True,
    ) -> bool:
        """Mark an event as applied."""
        result = await self.update(
            event_id,
            {
                "applied": applied,
                "applied_at": datetime.utcnow() if applied else None,
            }
        )
        return result is not None


class EventImpactRepository(BaseRepository[EventImpact, models.EventImpact]):
    """Repository for event impacts."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository."""
        super().__init__(session, models.EventImpact, EventImpact)

    async def get_event_impacts(
        self,
        event_id: UUID,
        include_reverted: bool = False,
    ) -> List[EventImpact]:
        """Get impacts for an event."""
        query = select(models.EventImpact).where(
            models.EventImpact.event_id == event_id,
        )

        if not include_reverted:
            query = query.where(models.EventImpact.is_reverted == False)

        query = query.order_by(models.EventImpact.created_at.asc())

        result = await self.db.execute(query)
        return [self._to_domain(impact) for impact in result.scalars().all()]

    async def get_character_impacts(
        self,
        character_id: UUID,
        include_reverted: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[EventImpact]:
        """Get impacts for a character."""
        query = select(models.EventImpact).where(
            models.EventImpact.character_id == character_id,
        )

        if not include_reverted:
            query = query.where(models.EventImpact.is_reverted == False)

        query = query.order_by(models.EventImpact.created_at.desc())
        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        return [self._to_domain(impact) for impact in result.scalars().all()]

    async def mark_applied(
        self,
        impact_id: UUID,
        applied: bool = True,
    ) -> bool:
        """Mark an impact as applied."""
        result = await self.update(
            impact_id,
            {
                "applied": applied,
                "applied_at": datetime.utcnow() if applied else None,
            }
        )
        return result is not None

    async def mark_reverted(
        self,
        impact_id: UUID,
        reversion_data: dict,
    ) -> bool:
        """Mark an impact as reverted."""
        result = await self.update(
            impact_id,
            {
                "is_reverted": True,
                "reverted_at": datetime.utcnow(),
                "reversion_data": reversion_data,
            }
        )
        return result is not None
