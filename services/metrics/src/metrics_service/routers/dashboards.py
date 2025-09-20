"""Dashboard management router."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from metrics_service.dependencies import get_message_client
from metrics_service.core.message_client import MessageClient

router = APIRouter()

class DashboardPanel(BaseModel):
    """Dashboard panel model."""
    title: str
    type: str
    targets: List[dict]

class Dashboard(BaseModel):
    """Dashboard model."""
    title: str
    refresh: Optional[str] = "1m"
    panels: List[DashboardPanel]

class DashboardResponse(BaseModel):
    """Dashboard response model."""
    id: str
    title: str

@router.get("/")
async def list_dashboards(client: MessageClient = Depends(get_message_client)):
    """List all dashboards via Storage Service through Message Hub."""
    resp = await client.send_message(
        message_type=None,  # Placeholder for scan/list op
        payload={"collection": "dashboards", "operation": "scan", "filters": {"is_deleted": False}}
    )
    return resp.model_dump()

@router.post("/")
async def create_dashboard(dashboard: Dashboard, client: MessageClient = Depends(get_message_client)):
    """Create new dashboard."""
    resp = await client.create_dashboard(dashboard.model_dump())
    return resp.model_dump()

@router.get("/{dashboard_id}")
async def get_dashboard(dashboard_id: str, client: MessageClient = Depends(get_message_client)):
    """Get dashboard by ID."""
    resp = await client.get_dashboard(dashboard_id)
    return resp.model_dump()

@router.put("/{dashboard_id}")
async def update_dashboard(dashboard_id: str, dashboard: Dashboard, client: MessageClient = Depends(get_message_client)):
    """Update dashboard."""
    resp = await client.update_dashboard(dashboard_id, dashboard.model_dump())
    return resp.model_dump()

@router.delete("/{dashboard_id}")
async def delete_dashboard(dashboard_id: str, client: MessageClient = Depends(get_message_client)):
    """Delete dashboard."""
    resp = await client.delete_dashboard(dashboard_id)
    return resp.model_dump()
