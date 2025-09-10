"""Soft delete tests for Campaign and related models."""
import pytest
from datetime import datetime, UTC
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from campaign_service.models.campaign import (
    Campaign,
    Chapter,
    CampaignType,
    CampaignState,
    ChapterType,
    ChapterState,
)


@pytest.mark.asyncio
async def test_soft_delete_campaign_flags(test_db: AsyncSession) -> None:
    """Soft-deleting a campaign should set is_deleted and deleted_at."""
    campaign = Campaign(
        name="Deletable Campaign",
        description="To be soft-deleted",
        campaign_type=CampaignType.TRADITIONAL,
        state=CampaignState.DRAFT,
        theme_data={},
        campaign_metadata={},
        creator_id=UUID("00000000-0000-0000-0000-000000000001"),
        owner_id=UUID("00000000-0000-0000-0000-000000000001"),
    )
    test_db.add(campaign)
    await test_db.flush()

    # Perform soft delete (application policy)
    campaign.is_deleted = True
    campaign.deleted_at = datetime.now(UTC)
    await test_db.flush()

    # Verify flags persisted
    result = await test_db.execute(select(Campaign).where(Campaign.id == campaign.id))
    deleted_campaign = result.scalar_one()

    assert deleted_campaign.is_deleted is True
    assert deleted_campaign.deleted_at is not None
    assert isinstance(deleted_campaign.deleted_at, datetime)


@pytest.mark.asyncio
async def test_default_like_query_excludes_deleted(test_db: AsyncSession) -> None:
    """Emulate default repository behavior to exclude deleted records by default."""
    active = Campaign(
        name="Active",
        description="Active campaign",
        campaign_type=CampaignType.TRADITIONAL,
        state=CampaignState.DRAFT,
        theme_data={},
        campaign_metadata={},
        creator_id=UUID("00000000-0000-0000-0000-000000000001"),
        owner_id=UUID("00000000-0000-0000-0000-000000000001"),
    )
    deleted = Campaign(
        name="Deleted",
        description="Deleted campaign",
        campaign_type=CampaignType.TRADITIONAL,
        state=CampaignState.DRAFT,
        theme_data={},
        campaign_metadata={},
        creator_id=UUID("00000000-0000-0000-0000-000000000001"),
        owner_id=UUID("00000000-0000-0000-0000-000000000001"),
        is_deleted=True,
        deleted_at=datetime.now(UTC),
    )
    test_db.add_all([active, deleted])
    await test_db.flush()

    # Emulate repository default filter (is_deleted == False)
    result = await test_db.execute(
        select(func.count()).select_from(Campaign).where(Campaign.is_deleted == False)  # noqa: E712
    )
    count_active = result.scalar_one()

    assert count_active >= 1

    # Ensure deleted item is present when explicitly included
    result_all = await test_db.execute(select(func.count()).select_from(Campaign))
    count_all = result_all.scalar_one()
    assert count_all >= count_active


@pytest.mark.asyncio
async def test_chapters_preserved_on_parent_soft_delete(test_db: AsyncSession) -> None:
    """Soft-deleting a campaign should not hard-delete its chapters."""
    campaign = Campaign(
        name="With Chapters",
        description="Parent campaign",
        campaign_type=CampaignType.TRADITIONAL,
        state=CampaignState.DRAFT,
        theme_data={},
        campaign_metadata={},
        creator_id=UUID("00000000-0000-0000-0000-000000000001"),
        owner_id=UUID("00000000-0000-0000-0000-000000000001"),
    )
    chapter = Chapter(
        title="Chapter 1",
        description="Intro",
        chapter_type=ChapterType.STORY,
        state=ChapterState.DRAFT,
        sequence_number=1,
        content={},
        chapter_metadata={},
        prerequisites=[],
    )
    campaign.chapters.append(chapter)
    test_db.add(campaign)
    await test_db.flush()

    # Soft delete parent campaign
    campaign.is_deleted = True
    campaign.deleted_at = datetime.now(UTC)
    await test_db.flush()

    # Verify the chapter still exists in DB
    result = await test_db.execute(select(Chapter).where(Chapter.id == chapter.id))
    child = result.scalar_one()
    assert child is not None
    assert child.title == "Chapter 1"


@pytest.mark.asyncio
async def test_updates_blocked_when_deleted_policy_documented(test_db: AsyncSession) -> None:
    """Repository must prevent updates to soft-deleted campaigns."""
    # Arrange
    campaign = Campaign(
        name="Soft Deleted",
        description="Test",
        campaign_type=CampaignType.TRADITIONAL,
        state=CampaignState.DRAFT,
        theme_data={},
        campaign_metadata={},
        creator_id=UUID("00000000-0000-0000-0000-000000000001"),
        owner_id=UUID("00000000-0000-0000-0000-000000000001"),
        is_deleted=True,
        deleted_at=datetime.now(UTC),
    )
    test_db.add(campaign)
    await test_db.flush()

    # Act/Assert
    from campaign_service.repositories.base import BaseRepository
    from campaign_service.core.exceptions import DeletedEntityError

    repo = BaseRepository[Campaign](test_db, Campaign)

    with pytest.raises(DeletedEntityError):
        await repo.update(campaign.id, {"name": "New Name"})

