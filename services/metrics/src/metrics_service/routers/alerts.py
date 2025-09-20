"""Alert management router."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from metrics_service.dependencies import get_message_client
from metrics_service.core.message_client import MessageClient

router = APIRouter()

class AlertRule(BaseModel):
    """Alert rule model."""
    name: str
    expression: str
    duration: str
    severity: str
    labels: Optional[dict] = None
    annotations: Optional[dict] = None

class AlertResponse(BaseModel):
    """Alert response model."""
    id: str
    name: str
    status: str

@router.get("/")
async def list_alerts(client: MessageClient = Depends(get_message_client)):
    """List all alerts via Storage Service through Message Hub."""
    # Query pattern: collection scan with filters (delegated to storage)
    resp = await client.send_message(
        message_type=None,  # Storage service may define a 'scan' op; placeholder until ICD
        payload={"collection": "alert_rules", "operation": "scan", "filters": {"is_deleted": False}}
    )
    return resp.model_dump()

@router.post("/")
async def create_alert(alert: AlertRule, client: MessageClient = Depends(get_message_client)):
    """Create new alert rule (persisted via Storage Service)."""
    resp = await client.create_alert_rule(alert.model_dump())
    return resp.model_dump()

@router.get("/{alert_id}")
async def get_alert(alert_id: str, client: MessageClient = Depends(get_message_client)):
    """Get alert by ID."""
    resp = await client.get_alert_rule(alert_id)
    return resp.model_dump()

@router.put("/{alert_id}")
async def update_alert(alert_id: str, alert: AlertRule, client: MessageClient = Depends(get_message_client)):
    """Update alert."""
    resp = await client.update_alert_rule(alert_id, alert.model_dump())
    return resp.model_dump()

@router.delete("/{alert_id}")
async def delete_alert(alert_id: str, client: MessageClient = Depends(get_message_client)):
    """Delete alert."""
    resp = await client.delete_alert_rule(alert_id)
    return resp.model_dump()
