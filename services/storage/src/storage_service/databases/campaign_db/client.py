"""Campaign database client."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from .models import Campaign, Chapter


class CampaignDBClient:
    """Client for campaign database operations."""

    def __init__(self, storage_client):
        """Initialize the client.

        Args:
            storage_client: The storage service client
        """
        self.storage = storage_client

    async def get_campaign(self, id: UUID) -> Optional[Dict]:
        """Get a campaign by ID.

        Args:
            id: Campaign UUID

        Returns:
            Campaign data or None if not found
        """
        return await self.storage.read(
            "campaign_db",
            "campaigns",
            {"id": id, "is_deleted": False}
        )

    async def list_campaigns(self, owner_id: UUID, limit: int = 100) -> List[Dict]:
        """List campaigns for an owner.

        Args:
            owner_id: Owner's UUID
            limit: Maximum number of campaigns to return

        Returns:
            List of campaign data
        """
        return await self.storage.read(
            "campaign_db",
            "campaigns",
            {
                "owner_id": owner_id,
                "is_deleted": False
            },
            limit=limit,
            order_by=["-created_at"]
        )

    async def create_campaign(self, campaign: Dict) -> Dict:
        """Create a new campaign.

        Args:
            campaign: Campaign data

        Returns:
            Created campaign data
        """
        return await self.storage.write(
            "campaign_db",
            "campaigns",
            campaign
        )

    async def update_campaign(self, id: UUID, data: Dict) -> Optional[Dict]:
        """Update a campaign.

        Args:
            id: Campaign UUID
            data: Updated campaign data

        Returns:
            Updated campaign data or None if not found
        """
        data["updated_at"] = datetime.utcnow()
        return await self.storage.update(
            "campaign_db",
            "campaigns",
            {"id": id, "is_deleted": False},
            data
        )

    async def delete_campaign(self, id: UUID) -> bool:
        """Soft delete a campaign.

        Args:
            id: Campaign UUID

        Returns:
            True if campaign was deleted
        """
        result = await self.storage.update(
            "campaign_db",
            "campaigns",
            {"id": id, "is_deleted": False},
            {
                "is_deleted": True,
                "deleted_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        )
        return result is not None

    async def get_chapter(self, id: UUID) -> Optional[Dict]:
        """Get a chapter by ID.

        Args:
            id: Chapter UUID

        Returns:
            Chapter data or None if not found
        """
        return await self.storage.read(
            "campaign_db",
            "chapters",
            {"id": id, "is_deleted": False}
        )

    async def list_chapters(self, campaign_id: UUID) -> List[Dict]:
        """List chapters for a campaign.

        Args:
            campaign_id: Campaign UUID

        Returns:
            List of chapter data
        """
        return await self.storage.read(
            "campaign_db",
            "chapters",
            {
                "campaign_id": campaign_id,
                "is_deleted": False
            },
            order_by=["sequence_number"]
        )

    async def create_chapter(self, chapter: Dict) -> Dict:
        """Create a new chapter.

        Args:
            chapter: Chapter data

        Returns:
            Created chapter data
        """
        return await self.storage.write(
            "campaign_db",
            "chapters",
            chapter
        )

    async def update_chapter(self, id: UUID, data: Dict) -> Optional[Dict]:
        """Update a chapter.

        Args:
            id: Chapter UUID
            data: Updated chapter data

        Returns:
            Updated chapter data or None if not found
        """
        data["updated_at"] = datetime.utcnow()
        return await self.storage.update(
            "campaign_db",
            "chapters",
            {"id": id, "is_deleted": False},
            data
        )

    async def delete_chapter(self, id: UUID) -> bool:
        """Soft delete a chapter.

        Args:
            id: Chapter UUID

        Returns:
            True if chapter was deleted
        """
        result = await self.storage.update(
            "campaign_db",
            "chapters",
            {"id": id, "is_deleted": False},
            {
                "is_deleted": True,
                "deleted_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        )
        return result is not None