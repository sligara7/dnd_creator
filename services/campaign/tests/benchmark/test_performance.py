"""Performance benchmark tests for campaign service."""
import asyncio
import pytest
from datetime import datetime, timedelta
from typing import List, Dict, Any
from uuid import UUID, uuid4

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from campaign_service.models.campaign import Campaign, CampaignState
from campaign_service.services.factory import CampaignFactory
from campaign_service.services.story import StoryService
from campaign_service.services.theme import ThemeService


logger = structlog.get_logger()


@pytest.fixture
async def factory_service(
    test_db: AsyncSession,
    mock_message_hub: AsyncMock,
) -> CampaignFactory:
    """Create campaign factory service."""
    return CampaignFactory(
        db=test_db,
        message_hub=mock_message_hub,
    )


@pytest.fixture
async def story_service(
    test_db: AsyncSession,
    mock_message_hub: AsyncMock,
) -> StoryService:
    """Create story service."""
    return StoryService(
        db=test_db,
        message_hub=mock_message_hub,
    )


@pytest.fixture
async def theme_service(
    test_db: AsyncSession,
    mock_message_hub: AsyncMock,
) -> ThemeService:
    """Create theme service."""
    return ThemeService(
        db=test_db,
        message_hub_client=mock_message_hub,
    )


@pytest.fixture
async def test_campaigns(
    test_db: AsyncSession,
) -> List[Campaign]:
    """Create multiple test campaigns."""
    campaigns = []
    for i in range(10):
        campaign = Campaign(
            name=f"Performance Test Campaign {i}",
            description="A campaign for performance testing",
            creator_id=UUID("00000000-0000-0000-0000-000000000001"),
            owner_id=UUID("00000000-0000-0000-0000-000000000001"),
            state=CampaignState.DRAFT,
            theme_data={},
        )
        test_db.add(campaign)
        campaigns.append(campaign)
    await test_db.flush()
    return campaigns


async def time_operation(operation: str, coro: Any) -> float:
    """Time an async operation.
    
    Args:
        operation: Operation name for logging
        coro: Coroutine to time
        
    Returns:
        Operation duration in seconds
    """
    start = datetime.now()
    try:
        await coro
    except Exception as e:
        logger.error(
            "Operation failed",
            operation=operation,
            error=str(e),
        )
        raise
    duration = (datetime.now() - start).total_seconds()
    logger.info(
        "Operation completed",
        operation=operation,
        duration=duration,
    )
    return duration


@pytest.mark.benchmark
class TestCampaignServicePerformance:
    """Performance benchmark tests."""
    
    async def test_campaign_skeleton_generation(
        self,
        factory_service: CampaignFactory,
        mock_message_hub: AsyncMock,
    ) -> None:
        """Test campaign skeleton generation performance.
        
        SRD Requirement: < 30 seconds
        """
        # Setup mock responses
        mock_message_hub.request.side_effect = [
            {"theme": "dark_fantasy", "elements": ["corruption", "intrigue"]},
            {"chapters": [{"id": str(uuid4()), "title": f"Chapter {i}"} for i in range(10)]},
        ]
        
        # Time skeleton generation
        duration = await time_operation(
            "campaign_skeleton_generation",
            factory_service.generate_campaign_skeleton(
                theme="dark_fantasy",
                complexity="moderate",
                length={"min": 5, "max": 10},
            ),
        )
        
        # Verify SRD requirement
        assert duration < 30, f"Campaign skeleton generation took {duration} seconds"
    
    async def test_chapter_generation(
        self,
        factory_service: CampaignFactory,
        story_service: StoryService,
        mock_message_hub: AsyncMock,
        test_campaigns: List[Campaign],
    ) -> None:
        """Test chapter generation performance.
        
        SRD Requirement: < 60 seconds
        """
        campaign = test_campaigns[0]
        
        # Setup mock responses
        mock_message_hub.request.return_value = {
            "chapter": {
                "title": "Test Chapter",
                "content": "Generated chapter content",
                "npcs": [{"id": str(uuid4()), "name": f"NPC {i}"} for i in range(5)],
                "locations": [{"id": str(uuid4()), "name": f"Location {i}"} for i in range(3)],
            }
        }
        
        # Time chapter generation
        duration = await time_operation(
            "chapter_generation",
            factory_service.generate_chapter(
                campaign_id=campaign.id,
                chapter_number=1,
                theme="dark_fantasy",
                requirements={"encounters": 2, "npcs": 5},
            ),
        )
        
        # Verify SRD requirement
        assert duration < 60, f"Chapter generation took {duration} seconds"
    
    async def test_chapter_scaling(
        self,
        factory_service: CampaignFactory,
        story_service: StoryService,
        mock_message_hub: AsyncMock,
        test_campaigns: List[Campaign],
    ) -> None:
        """Test chapter scaling performance.
        
        SRD Requirement: Support 50+ chapters
        """
        campaign = test_campaigns[0]
        chapters = 50
        
        # Setup mock responses
        mock_message_hub.request.return_value = {
            "chapter": {
                "title": "Test Chapter",
                "content": "Generated chapter content",
                "npcs": [{"id": str(uuid4()), "name": "NPC"}],
                "locations": [{"id": str(uuid4()), "name": "Location"}],
            }
        }
        
        # Generate chapters concurrently
        start = datetime.now()
        tasks = [
            factory_service.generate_chapter(
                campaign_id=campaign.id,
                chapter_number=i,
                theme="dark_fantasy",
                requirements={"encounters": 1, "npcs": 1},
            )
            for i in range(chapters)
        ]
        await asyncio.gather(*tasks)
        duration = (datetime.now() - start).total_seconds()
        
        # Calculate metrics
        avg_time = duration / chapters
        logger.info(
            "Chapter scaling metrics",
            total_chapters=chapters,
            total_duration=duration,
            avg_chapter_time=avg_time,
        )
        
        # Verify reasonable scaling
        assert avg_time < 2, f"Average chapter generation time {avg_time} seconds is too high"
    
    async def test_concurrent_generation(
        self,
        factory_service: CampaignFactory,
        story_service: StoryService,
        mock_message_hub: AsyncMock,
        test_campaigns: List[Campaign],
    ) -> None:
        """Test concurrent campaign generation.
        
        SRD Requirement: 10+ concurrent generations
        """
        concurrent_campaigns = 10
        
        # Setup mock responses
        mock_message_hub.request.return_value = {
            "campaign": {
                "title": "Generated Campaign",
                "theme": "dark_fantasy",
                "chapters": [{"id": str(uuid4()), "title": "Chapter"}],
            }
        }
        
        # Time concurrent generation
        start = datetime.now()
        tasks = [
            factory_service.generate_campaign_content(
                campaign_id=campaign.id,
                theme="dark_fantasy",
                complexity="moderate",
                length={"min": 3, "max": 5},
            )
            for campaign in test_campaigns[:concurrent_campaigns]
        ]
        await asyncio.gather(*tasks)
        duration = (datetime.now() - start).total_seconds()
        
        # Calculate metrics
        avg_time = duration / concurrent_campaigns
        logger.info(
            "Concurrent generation metrics",
            campaigns=concurrent_campaigns,
            total_duration=duration,
            avg_campaign_time=avg_time,
        )
        
        # Verify reasonable concurrent performance
        assert avg_time < 5, f"Average concurrent generation time {avg_time} seconds is too high"
    
    async def test_theme_application_performance(
        self,
        theme_service: ThemeService,
        mock_message_hub: AsyncMock,
        test_campaigns: List[Campaign],
    ) -> None:
        """Test theme application performance."""
        campaign = test_campaigns[0]
        
        # Setup mock responses
        mock_message_hub.request.return_value = {
            "theme": {
                "id": "dark_fantasy",
                "traits": ["gritty", "dark"],
                "elements": ["corruption", "intrigue"],
                "tone": "dark and brooding",
                "restrictions": ["no_lighthearted"],
            }
        }
        
        # Time theme application
        duration = await time_operation(
            "theme_application",
            theme_service.get_theme_profile("dark_fantasy"),
        )
        
        # Verify reasonable performance
        assert duration < 1, f"Theme application took {duration} seconds"
    
    async def test_memory_usage(
        self,
        factory_service: CampaignFactory,
        story_service: StoryService,
        mock_message_hub: AsyncMock,
        test_campaigns: List[Campaign],
    ) -> None:
        """Test memory usage under load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate significant content
        mock_message_hub.request.return_value = {
            "chapter": {
                "title": "Test Chapter",
                "content": "Generated chapter content " * 100,  # Large content
                "npcs": [{"id": str(uuid4()), "name": f"NPC {i}"} for i in range(50)],
                "locations": [{"id": str(uuid4()), "name": f"Location {i}"} for i in range(20)],
            }
        }
        
        # Generate multiple chapters
        for campaign in test_campaigns[:5]:
            for i in range(10):
                await factory_service.generate_chapter(
                    campaign_id=campaign.id,
                    chapter_number=i,
                    theme="dark_fantasy",
                    requirements={"encounters": 5, "npcs": 10},
                )
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        logger.info(
            "Memory usage metrics",
            initial_mb=initial_memory,
            final_mb=final_memory,
            increase_mb=memory_increase,
        )
        
        # Verify reasonable memory usage
        assert memory_increase < 500, f"Memory usage increased by {memory_increase} MB"
    
    async def test_database_performance(
        self,
        test_db: AsyncSession,
        test_campaigns: List[Campaign],
    ) -> None:
        """Test database operation performance."""
        campaign = test_campaigns[0]
        
        # Time database operations
        operations = {
            "campaign_fetch": test_db.get(Campaign, campaign.id),
            "campaign_list": test_db.execute(
                select(Campaign)
                .where(Campaign.state == CampaignState.DRAFT)
            ),
            "campaign_update": test_db.execute(
                update(Campaign)
                .where(Campaign.id == campaign.id)
                .values(name="Updated Name")
            ),
        }
        
        for op_name, operation in operations.items():
            duration = await time_operation(op_name, operation)
            assert duration < 0.1, f"Database operation {op_name} took {duration} seconds"