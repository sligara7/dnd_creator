"""Metrics endpoints router."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class MetricQuery(BaseModel):
    """Metric query model."""
    query: str
    start: Optional[str] = None
    end: Optional[str] = None
    step: Optional[str] = None
    timeout: Optional[str] = None

class MetricResponse(BaseModel):
    """Metric query response model."""
    status: str
    data: dict

@router.post("/push")
async def push_metrics():
    """Push metrics endpoint."""
    pass

@router.post("/query")
async def query_metrics(query: MetricQuery):
    """Query metrics endpoint."""
    pass

@router.get("/targets")
async def get_targets():
    """Get scrape targets."""
    pass