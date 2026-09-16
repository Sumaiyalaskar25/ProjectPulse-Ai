# services/api/routes/alerts.py
from fastapi import APIRouter, Depends, Query, Body
from typing import Optional
from pydantic import BaseModel
from ..dependencies import get_alert_repository, get_alert_engine
from ..repositories.alert_repo import AlertRepository
from ..services.alert_service import AlertEngine
from ..core.errors import NotFoundError, ConflictError
from ..core.auth import get_current_user, require_role, AuthenticatedUser

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])

class AcknowledgeRequest(BaseModel):
    assigned_to: Optional[str] = None

@router.get("")
async def list_alerts(
    status: Optional[str] = Query(None, description="Filter by status (open, acknowledged, resolved)"),
    severity: Optional[str] = Query(None, description="Filter by severity (critical, high, moderate)"),
    limit: int = Query(50, ge=1, le=100),
    repo: AlertRepository = Depends(get_alert_repository),
    user: AuthenticatedUser = Depends(get_current_user)
):
    """List active and historical alerts."""
    alerts = await repo.list_alerts(status=status, severity=severity, limit=limit)
    return {"alerts": alerts}

@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    body: Optional[AcknowledgeRequest] = None,
    repo: AlertRepository = Depends(get_alert_repository),
    user: AuthenticatedUser = Depends(require_role(["operator", "manager", "admin"]))
):
    """Acknowledge an open alert with role enforcement."""
    assigned_to = body.assigned_to if body else (user.email or user.user_id)
    result = await repo.acknowledge_alert(alert_id=alert_id, assigned_to=assigned_to)
    if result is None:
        raise NotFoundError(message=f"Alert with ID {alert_id} not found or is already resolved/acknowledged")
    return result

@router.post("/run-engine")
async def trigger_alert_engine(
    engine: AlertEngine = Depends(get_alert_engine),
    user: AuthenticatedUser = Depends(require_role(["operator", "manager", "admin"]))
):
    """Run alert detection rules across projects and record any new alerts."""
    new_alert_ids = await engine.generate_alerts()
    return {
        "status": "success",
        "new_alerts_count": len(new_alert_ids),
        "alert_ids": new_alert_ids
    }
