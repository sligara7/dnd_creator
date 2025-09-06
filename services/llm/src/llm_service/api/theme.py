"""Theme analysis API endpoints."""
from fastapi import APIRouter, Depends

from llm_service.core.exceptions import ThemeAnalysisError
from llm_service.schemas.theme import ThemeAnalysisRequest, ThemeAnalysisResponse
from llm_service.services.theme import ThemeAnalysisService

router = APIRouter(prefix="/theme", tags=["theme"])


@router.post("/analyze", response_model=ThemeAnalysisResponse)
async def analyze_theme(
    request: ThemeAnalysisRequest,
    theme_service: ThemeAnalysisService = Depends(),
) -> ThemeAnalysisResponse:
    """Analyze content themes and compatibility.

    Args:
        request: Theme analysis request
        theme_service: Theme analysis service

    Returns:
        Theme analysis response with detailed analysis and suggestions

    Raises:
        ThemeAnalysisError: If theme analysis fails
    """
    try:
        return await theme_service.analyze_theme(request)
    except Exception as e:
        raise ThemeAnalysisError(
            message=f"Theme analysis failed: {str(e)}",
            details={"content_length": len(request.content)},
        ) from e
