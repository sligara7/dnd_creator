"""Style and theme management endpoints."""

from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from image_service.api.schemas.style import (
    ModifyRequest,
    StyleRequest,
    StyleResponse,
    Theme,
    ThemeList,
)
from image_service.core.deps import CommonDeps, get_db, get_redis
from image_service.core.logging import get_logger
from image_service.core.metrics import metrics, track_api_metrics
from image_service.services.style import StyleService

logger = get_logger(__name__)
router = APIRouter(tags=["Styles"])


@router.get("/api/v2/images/styles")
@track_api_metrics(method="GET", endpoint="/api/v2/images/styles")
async def list_available_styles(
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> ThemeList:
    """List available themes and styles."""
    try:
        service = StyleService(session, redis)
        themes = await service.list_themes()
        presets = await service.list_style_presets()

        # Collect all theme compatibility
        compatibility = {}
        for preset in presets:
            for theme in preset.compatibility:
                if theme not in compatibility:
                    compatibility[theme] = []
                compatibility[theme].append(preset.name)

        return ThemeList(
            visual_themes=[t.name for t in themes],
            style_elements=service.get_available_themes()["style_elements"],
            compatibility=compatibility,
        )

    except Exception as e:
        logger.error("Failed to list styles", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list available styles",
        )


@router.get("/api/v2/images/themes/{theme_name}")
@track_api_metrics(method="GET", endpoint="/api/v2/images/themes/{theme_name}")
async def get_theme(
    theme_name: str,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> Theme:
    """Get theme details."""
    try:
        service = StyleService(session, redis)
        theme = await service.get_theme(theme_name)
        if not theme:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Theme '{theme_name}' not found",
            )
        return theme

    except HTTPException:
        raise

    except Exception as e:
        logger.error("Failed to get theme", theme=theme_name, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get theme details",
        )


@router.post("/api/v2/images/modify")
@track_api_metrics(method="POST", endpoint="/api/v2/images/modify")
async def modify_image(
    request: ModifyRequest,
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> StyleResponse:
    """Modify an existing image with a new style."""
    try:
        # First validate style
        service = StyleService(session, redis)
        issues = await service.validate_style(request.style)
        if issues:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Invalid style configuration",
                    "issues": issues,
                },
            )

        # Get original image style
        # TODO: Implement image lookup and original style retrieval

        # Apply style
        style_params = await service.apply_style(
            request.style,
            # original_style=original.style,  # TODO: Pass original style
        )

        # Queue modification task
        params = {
            "image_id": str(request.image_id),
            "style": style_params,
            "size": request.size.dict() if request.size else None,
            "preserve_content": request.preserve_content,
        }
        # TODO: Add to queue and process

        # Return immediate response
        return StyleResponse(
            image_id=request.image_id,
            original_id=request.image_id,  # Same for modification
            style=request.style,
            url="",  # Will be updated when processing completes
            metadata={"status": "processing"},
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            "Failed to modify image",
            image_id=request.image_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to modify image",
        )


@router.post("/api/v2/images/validate-style")
@track_api_metrics(method="POST", endpoint="/api/v2/images/validate-style")
async def validate_style(
    style: StyleRequest,
    context: Dict[str, bool] = {},
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> Dict[str, List[str]]:
    """Validate a style configuration."""
    try:
        service = StyleService(session, redis)
        issues = await service.validate_style(style, context)
        return {"issues": issues}

    except Exception as e:
        logger.error(
            "Failed to validate style",
            style=style.dict(),
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate style",
        )
