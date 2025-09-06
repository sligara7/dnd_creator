"""API endpoints for chapter organization."""
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from ..core.exceptions import ChapterError, IntegrationError
from ..models.chapter import (
    Chapter,
    ChapterOrganization,
    ChapterSection,
    StoryBeat,
    CreateChapterRequest,
    CreateSectionRequest,
    CreateStoryBeatRequest,
    UpdateChapterRequest,
    UpdateSectionRequest,
    UpdateStoryBeatRequest,
)
from ..models.theme import ThemeContext
from ..services.campaign_integration import CampaignService
from ..services.chapter_service import ChapterService
from ..services.generation import GenerationPipeline


router = APIRouter(prefix="/api/v2/chapters", tags=["chapters"])


async def get_campaign_service() -> CampaignService:
    """Get Campaign service instance."""
    from ..core.dependencies import get_settings
    settings = get_settings()
    return CampaignService(settings)


async def get_generation_pipeline() -> GenerationPipeline:
    """Get generation pipeline instance."""
    from ..core.dependencies import get_settings, get_rate_limiter
    settings = get_settings()
    rate_limiter = get_rate_limiter()
    return GenerationPipeline(settings, rate_limiter)


@router.post(
    "/",
    response_model=Chapter,
    description="Create a new chapter"
)
async def create_chapter(
    request: CreateChapterRequest,
    campaign_service: CampaignService = Depends(get_campaign_service),
    generation_pipeline: GenerationPipeline = Depends(get_generation_pipeline),
    background_tasks: BackgroundTasks = None
) -> Chapter:
    """Create a new chapter in a campaign."""
    try:
        chapter_service = ChapterService(
            campaign_service,
            generation_pipeline,
            background_tasks
        )

        # Get campaign organization
        organization = await campaign_service.get_chapter_organization(
            request.campaign_id
        )

        # Create chapter
        chapter = await chapter_service.create_chapter(request, organization)

        # Generate content if needed
        if not request.description:
            background_tasks.add_task(
                chapter_service.generate_chapter_content,
                chapter,
                organization
            )

        return chapter

    except (ChapterError, IntegrationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{chapter_id}",
    response_model=Chapter,
    description="Update an existing chapter"
)
async def update_chapter(
    chapter_id: UUID,
    request: UpdateChapterRequest,
    campaign_service: CampaignService = Depends(get_campaign_service),
    generation_pipeline: GenerationPipeline = Depends(get_generation_pipeline),
    background_tasks: BackgroundTasks = None
) -> Chapter:
    """Update an existing chapter."""
    try:
        chapter_service = ChapterService(
            campaign_service,
            generation_pipeline,
            background_tasks
        )

        # Get campaign organization
        campaign_id = await campaign_service.get_campaign_id(chapter_id)
        organization = await campaign_service.get_chapter_organization(campaign_id)

        return await chapter_service.update_chapter(
            chapter_id,
            request,
            organization
        )

    except (ChapterError, IntegrationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{chapter_id}",
    description="Delete a chapter"
)
async def delete_chapter(
    chapter_id: UUID,
    campaign_service: CampaignService = Depends(get_campaign_service),
    generation_pipeline: GenerationPipeline = Depends(get_generation_pipeline),
    background_tasks: BackgroundTasks = None
) -> Dict[str, str]:
    """Delete a chapter."""
    try:
        chapter_service = ChapterService(
            campaign_service,
            generation_pipeline,
            background_tasks
        )

        # Get campaign organization
        campaign_id = await campaign_service.get_campaign_id(chapter_id)
        organization = await campaign_service.get_chapter_organization(campaign_id)

        await chapter_service.delete_chapter(chapter_id, organization)
        return {"status": "Chapter deleted"}

    except (ChapterError, IntegrationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{chapter_id}/sections",
    response_model=ChapterSection,
    description="Add a section to a chapter"
)
async def add_section(
    chapter_id: UUID,
    request: CreateSectionRequest,
    campaign_service: CampaignService = Depends(get_campaign_service),
    generation_pipeline: GenerationPipeline = Depends(get_generation_pipeline),
    background_tasks: BackgroundTasks = None
) -> ChapterSection:
    """Add a section to a chapter."""
    try:
        chapter_service = ChapterService(
            campaign_service,
            generation_pipeline,
            background_tasks
        )

        # Get campaign organization
        campaign_id = await campaign_service.get_campaign_id(chapter_id)
        organization = await campaign_service.get_chapter_organization(campaign_id)

        return await chapter_service.add_section(
            chapter_id,
            request,
            organization
        )

    except (ChapterError, IntegrationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{chapter_id}/sections/{section_id}",
    response_model=ChapterSection,
    description="Update a chapter section"
)
async def update_section(
    chapter_id: UUID,
    section_id: UUID,
    request: UpdateSectionRequest,
    campaign_service: CampaignService = Depends(get_campaign_service),
    generation_pipeline: GenerationPipeline = Depends(get_generation_pipeline),
    background_tasks: BackgroundTasks = None
) -> ChapterSection:
    """Update a chapter section."""
    try:
        chapter_service = ChapterService(
            campaign_service,
            generation_pipeline,
            background_tasks
        )

        # Get campaign organization
        campaign_id = await campaign_service.get_campaign_id(chapter_id)
        organization = await campaign_service.get_chapter_organization(campaign_id)

        return await chapter_service.update_section(
            chapter_id,
            section_id,
            request,
            organization
        )

    except (ChapterError, IntegrationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{chapter_id}/sections/{section_id}",
    description="Delete a chapter section"
)
async def delete_section(
    chapter_id: UUID,
    section_id: UUID,
    campaign_service: CampaignService = Depends(get_campaign_service),
    generation_pipeline: GenerationPipeline = Depends(get_generation_pipeline),
    background_tasks: BackgroundTasks = None
) -> Dict[str, str]:
    """Delete a chapter section."""
    try:
        chapter_service = ChapterService(
            campaign_service,
            generation_pipeline,
            background_tasks
        )

        # Get campaign organization
        campaign_id = await campaign_service.get_campaign_id(chapter_id)
        organization = await campaign_service.get_chapter_organization(campaign_id)

        await chapter_service.delete_section(chapter_id, section_id, organization)
        return {"status": "Section deleted"}

    except (ChapterError, IntegrationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{chapter_id}/sections/{section_id}/beats",
    response_model=StoryBeat,
    description="Add a story beat to a section"
)
async def add_story_beat(
    chapter_id: UUID,
    section_id: UUID,
    request: CreateStoryBeatRequest,
    campaign_service: CampaignService = Depends(get_campaign_service),
    generation_pipeline: GenerationPipeline = Depends(get_generation_pipeline),
    background_tasks: BackgroundTasks = None
) -> StoryBeat:
    """Add a story beat to a section."""
    try:
        chapter_service = ChapterService(
            campaign_service,
            generation_pipeline,
            background_tasks
        )

        # Get campaign organization
        campaign_id = await campaign_service.get_campaign_id(chapter_id)
        organization = await campaign_service.get_chapter_organization(campaign_id)

        return await chapter_service.add_story_beat(
            chapter_id,
            section_id,
            request,
            organization
        )

    except (ChapterError, IntegrationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{chapter_id}/sections/{section_id}/beats/{beat_id}",
    response_model=StoryBeat,
    description="Update a story beat"
)
async def update_story_beat(
    chapter_id: UUID,
    section_id: UUID,
    beat_id: UUID,
    request: UpdateStoryBeatRequest,
    campaign_service: CampaignService = Depends(get_campaign_service),
    generation_pipeline: GenerationPipeline = Depends(get_generation_pipeline),
    background_tasks: BackgroundTasks = None
) -> StoryBeat:
    """Update a story beat."""
    try:
        chapter_service = ChapterService(
            campaign_service,
            generation_pipeline,
            background_tasks
        )

        # Get campaign organization
        campaign_id = await campaign_service.get_campaign_id(chapter_id)
        organization = await campaign_service.get_chapter_organization(campaign_id)

        return await chapter_service.update_story_beat(
            chapter_id,
            section_id,
            beat_id,
            request,
            organization
        )

    except (ChapterError, IntegrationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{chapter_id}/sections/{section_id}/beats/{beat_id}",
    description="Delete a story beat"
)
async def delete_story_beat(
    chapter_id: UUID,
    section_id: UUID,
    beat_id: UUID,
    campaign_service: CampaignService = Depends(get_campaign_service),
    generation_pipeline: GenerationPipeline = Depends(get_generation_pipeline),
    background_tasks: BackgroundTasks = None
) -> Dict[str, str]:
    """Delete a story beat."""
    try:
        chapter_service = ChapterService(
            campaign_service,
            generation_pipeline,
            background_tasks
        )

        # Get campaign organization
        campaign_id = await campaign_service.get_campaign_id(chapter_id)
        organization = await campaign_service.get_chapter_organization(campaign_id)

        await chapter_service.delete_story_beat(
            chapter_id,
            section_id,
            beat_id,
            organization
        )
        return {"status": "Story beat deleted"}

    except (ChapterError, IntegrationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{chapter_id}/generate",
    description="Generate content for a chapter"
)
async def generate_chapter_content(
    chapter_id: UUID,
    campaign_service: CampaignService = Depends(get_campaign_service),
    generation_pipeline: GenerationPipeline = Depends(get_generation_pipeline),
    background_tasks: BackgroundTasks = None
) -> Dict[str, str]:
    """Generate content for a chapter."""
    try:
        chapter_service = ChapterService(
            campaign_service,
            generation_pipeline,
            background_tasks
        )

        # Get campaign organization
        campaign_id = await campaign_service.get_campaign_id(chapter_id)
        organization = await campaign_service.get_chapter_organization(campaign_id)

        # Find chapter
        chapter = next(
            (c for c in organization.chapters if c.chapter_id == chapter_id),
            None
        )
        if not chapter:
            raise ChapterError(f"Chapter {chapter_id} not found")

        background_tasks.add_task(
            chapter_service.generate_chapter_content,
            chapter,
            organization
        )

        return {"status": "Content generation started"}

    except (ChapterError, IntegrationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/reorder",
    description="Reorder chapters in a campaign"
)
async def reorder_chapters(
    campaign_id: UUID,
    chapter_orders: Dict[UUID, int],
    campaign_service: CampaignService = Depends(get_campaign_service),
    generation_pipeline: GenerationPipeline = Depends(get_generation_pipeline),
    background_tasks: BackgroundTasks = None
) -> Dict[str, str]:
    """Reorder chapters in a campaign."""
    try:
        chapter_service = ChapterService(
            campaign_service,
            generation_pipeline,
            background_tasks
        )

        # Get campaign organization
        organization = await campaign_service.get_chapter_organization(campaign_id)

        await chapter_service.reorder_chapters(chapter_orders, organization)
        return {"status": "Chapters reordered"}

    except (ChapterError, IntegrationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{chapter_id}/sections/reorder",
    description="Reorder sections in a chapter"
)
async def reorder_sections(
    chapter_id: UUID,
    section_orders: Dict[UUID, int],
    campaign_service: CampaignService = Depends(get_campaign_service),
    generation_pipeline: GenerationPipeline = Depends(get_generation_pipeline),
    background_tasks: BackgroundTasks = None
) -> Dict[str, str]:
    """Reorder sections in a chapter."""
    try:
        chapter_service = ChapterService(
            campaign_service,
            generation_pipeline,
            background_tasks
        )

        # Get campaign organization
        campaign_id = await campaign_service.get_campaign_id(chapter_id)
        organization = await campaign_service.get_chapter_organization(campaign_id)

        await chapter_service.reorder_sections(
            chapter_id,
            section_orders,
            organization
        )
        return {"status": "Sections reordered"}

    except (ChapterError, IntegrationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{chapter_id}/sections/{section_id}/beats/reorder",
    description="Reorder story beats in a section"
)
async def reorder_story_beats(
    chapter_id: UUID,
    section_id: UUID,
    beat_orders: Dict[UUID, int],
    campaign_service: CampaignService = Depends(get_campaign_service),
    generation_pipeline: GenerationPipeline = Depends(get_generation_pipeline),
    background_tasks: BackgroundTasks = None
) -> Dict[str, str]:
    """Reorder story beats in a section."""
    try:
        chapter_service = ChapterService(
            campaign_service,
            generation_pipeline,
            background_tasks
        )

        # Get campaign organization
        campaign_id = await campaign_service.get_campaign_id(chapter_id)
        organization = await campaign_service.get_chapter_organization(campaign_id)

        await chapter_service.reorder_story_beats(
            chapter_id,
            section_id,
            beat_orders,
            organization
        )
        return {"status": "Story beats reordered"}

    except (ChapterError, IntegrationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
