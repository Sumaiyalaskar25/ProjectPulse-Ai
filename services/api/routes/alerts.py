# services/api/routes/alerts.py
from fastapi import APIRouter, Depends, Query
from typing import Optional
from ..dependencies import get_alert_repository, get_alert_engine
from ..repositories.alert_repo import AlertRepository
from ..services.alert_service import AlertEngine

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])

@router.get("")
async def list_alerts(
    status: Optional[str] = Query(None, description="Filter by status (open, acknowledged, resolved)"),
    severity: Optional[str] = Query(None, description="Filter by severity (critical, high, moderate)"),
    limit: int = Query(50, ge=1, le=100),
    repo: AlertRepository = Depends(get_alert_repository)
):
    """List active and historical alerts."""
    alerts = await repo.list_alerts(status=status, severity=severity, limit=limit)
    return {"alerts": alerts}

@router.post("/run-engine")
async def trigger_alert_engine(
    engine: AlertEngine = Depends(get_alert_engine)
):
    """Run alert detection rules across projects and record any new alerts."""
    new_alert_ids = await engine.generate_alerts()
    return {
        "status": "success",
        "new_alerts_count": len(new_alert_ids),
        "alert_ids": new_alert_ids
    }
