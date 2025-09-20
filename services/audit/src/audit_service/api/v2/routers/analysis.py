"""
Analysis router for the Audit Service.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from audit_service.core.exceptions import AnalysisError
from audit_service.services.analysis_service import AnalysisService

router = APIRouter(
    prefix="/api/v2/analysis",
    tags=["analysis"]
)

async def get_analysis_service() -> AnalysisService:
    """Dependency for getting analysis service instance."""
    service = AnalysisService()
    try:
        await service.setup()
        yield service
    finally:
        await service.cleanup()

@router.post(
    "/patterns",
    response_model=List[Dict[str, Any]],
    summary="Detect event patterns",
    description="Analyze events to detect patterns and correlations"
)
async def analyze_patterns(
    start_date: datetime = Query(..., description="Start of analysis period"),
    end_date: datetime = Query(..., description="End of analysis period"),
    event_types: Optional[List[str]] = Query(None, description="Types of events to analyze"),
    min_support: float = Query(0.1, description="Minimum pattern support threshold"),
    analysis: AnalysisService = Depends(get_analysis_service)
) -> List[Dict[str, Any]]:
    """Analyze patterns in audit events."""
    try:
        return await analysis.analyze_patterns(
            start_date=start_date,
            end_date=end_date,
            event_types=event_types,
            min_support=min_support
        )
    except AnalysisError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post(
    "/anomalies",
    response_model=List[Dict[str, Any]],
    summary="Detect anomalies",
    description="Analyze events to detect anomalies and outliers"
)
async def detect_anomalies(
    start_date: datetime = Query(..., description="Start of analysis period"),
    end_date: datetime = Query(..., description="End of analysis period"),
    event_types: Optional[List[str]] = Query(None, description="Types of events to analyze"),
    sensitivity: float = Query(0.8, description="Anomaly detection sensitivity"),
    analysis: AnalysisService = Depends(get_analysis_service)
) -> List[Dict[str, Any]]:
    """Detect anomalies in audit events."""
    try:
        return await analysis.detect_anomalies(
            start_date=start_date,
            end_date=end_date,
            event_types=event_types,
            sensitivity=sensitivity
        )
    except AnalysisError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/trends",
    response_model=List[Dict[str, Any]],
    summary="Analyze trends",
    description="Analyze event trends and patterns over time"
)
async def analyze_trends(
    start_date: datetime = Query(..., description="Start of analysis period"),
    end_date: datetime = Query(..., description="End of analysis period"),
    event_types: Optional[List[str]] = Query(None, description="Types of events to analyze"),
    interval: str = Query("1h", description="Time interval for trend buckets"),
    analysis: AnalysisService = Depends(get_analysis_service)
) -> List[Dict[str, Any]]:
    """Analyze trends in audit events."""
    try:
        return await analysis.analyze_trends(
            start_date=start_date,
            end_date=end_date,
            event_types=event_types,
            interval=interval
        )
    except AnalysisError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )