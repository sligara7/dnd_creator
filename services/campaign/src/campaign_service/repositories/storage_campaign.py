"""Storage-based campaign repository implementation."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from campaign_service.models.storage_campaign import Campaign, Chapter, CampaignState, CampaignType
from campaign_service.models.pagination import PaginationResult
from campaign_service.storage import StorageClient, StorageQuery
from campaign_service.repositories.storage_base import StorageBaseRepository


class CampaignRepository(StorageBaseRepository[Campaign]):
    """Campaign repository implementation using storage service."""
    
    def __init__(self, storage: StorageClient) -> None:
        """Initialize repository.
        
        Args:
            storage: Storage service client
        """
        super().__init__(storage, Campaign, "campaigns")
    
    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> PaginationResult[Campaign]:
        """Get campaigns with pagination and filtering.
        
        Args:
            page: Page number
            page_size: Page size
            filters: Optional filters
            
        Returns:
            Paginated campaign results
            
        Raises:
            StorageError: If query fails
        """
        # Add is_deleted filter
        filters = filters or {}
        if "is_deleted" not in filters:
            filters["is_deleted"] = False
            
        # Get total count
        total = await self.count(**filters)
            
        # Calculate pagination
        offset = (page - 1) * page_size
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        has_next = page < total_pages
        has_previous = page > 1
        
        # Get paginated results
        items = await self.get_all(
            skip=offset,
            limit=page_size,
            **filters,
        )
        
        return PaginationResult(
            items=items,
            total_items=total,
            total_pages=total_pages,
            page_number=page,
            page_size=page_size,
            has_next=has_next,
            has_previous=has_previous,
        )
    
    async def filter_by(
        self,
        states: Optional[List[CampaignState]] = None,
        campaign_types: Optional[List[CampaignType]] = None,
        owner_id: Optional[UUID] = None,
    ) -> List[Campaign]:
        """Filter campaigns by criteria.
        
        Args:
            states: Optional campaign states
            campaign_types: Optional campaign types
            owner_id: Optional owner ID
            
        Returns:
            Filtered campaigns
            
        Raises:
            StorageError: If query fails
        """
        filters = {"is_deleted": False}
        
        if states:
            filters["state"] = {"$in": [s.value for s in states]}
        if campaign_types:
            filters["campaign_type"] = {"$in": [t.value for t in campaign_types]}
        if owner_id:
            filters["owner_id"] = str(owner_id)
            
        return await self.get_all(**filters)
    
    async def filter_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Campaign]:
        """Filter campaigns by creation date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Campaigns within date range
            
        Raises:
            StorageError: If query fails
        """
        filters = {
            "is_deleted": False,
            "created_at": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat(),
            },
        }
        return await self.get_all(**filters)
    
    async def get_by_owner(
        self,
        owner_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Campaign]:
        """Get campaigns by owner.
        
        Args:
            owner_id: Owner ID
            skip: Records to skip
            limit: Max records
            
        Returns:
            Owner's campaigns
            
        Raises:
            StorageError: If query fails
        """
        return await self.get_all(
            skip=skip,
            limit=limit,
            owner_id=str(owner_id),
        )
    
    async def get_with_chapters(self, campaign_id: UUID) -> Optional[Campaign]:
        """Get campaign with chapters.
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Campaign with chapters if found
            
        Raises:
            StorageError: If query fails
        """
        # Get campaign
        campaign = await self.get(campaign_id)
        if not campaign:
            return None
            
        # Get chapters
        results = await self.storage.execute(
            StorageQuery.select(
                table="chapters",
                where={
                    "campaign_id": str(campaign_id),
                    "is_deleted": False,
                },
            )
        )
        
        # Add chapters to campaign
        campaign.chapters = [Chapter.model_validate(r) for r in results]
        return campaign


class ChapterRepository(StorageBaseRepository[Chapter]):
    """Chapter repository implementation."""
    
    def __init__(self, storage: StorageClient) -> None:
        """Initialize repository.
        
        Args:
            storage: Storage service client
        """
        super().__init__(storage, Chapter, "chapters")
    
    async def get_by_campaign(
        self,
        campaign_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Chapter]:
        """Get chapters by campaign.
        
        Args:
            campaign_id: Campaign ID
            skip: Records to skip
            limit: Max records
            
        Returns:
            Campaign chapters
            
        Raises:
            StorageError: If query fails
        """
        return await self.get_all(
            skip=skip,
            limit=limit,
            campaign_id=str(campaign_id),
        )
    
    async def get_prerequisites(
        self,
        chapter_id: UUID,
    ) -> List[Chapter]:
        """Get chapter prerequisites.
        
        Args:
            chapter_id: Chapter ID
            
        Returns:
            Prerequisite chapters
            
        Raises:
            StorageError: If query fails
        """
        # Get chapter
        chapter = await self.get(chapter_id)
        if not chapter:
            return []
            
        # Get prerequisites if any
        if not chapter.prerequisites:
            return []
            
        return await self.get_all(
            where={
                "id": {"$in": [str(p) for p in chapter.prerequisites]},
                "is_deleted": False,
            },
        )