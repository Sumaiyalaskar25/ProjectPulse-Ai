# services/api/routes/interventions.py
from typing import Optional, List, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..core.errors import NotFoundError, ValidationError, ConflictError
from ..core.auth import get_current_user, require_role, AuthenticatedUser
from datetime import datetime

router = APIRouter(prefix="/api/v1/interventions", tags=["interventions"])


class CreateInterventionRequest(BaseModel):
    project_id: str = Field(..., min_length=1, max_length=64)
    alert_id: Optional[int] = None
    owner: str = Field(..., min_length=1, max_length=64)
    category: str = Field("schedule_review", max_length=32)
    action_description: str = Field(..., min_length=1)
    status: str = Field("pending", max_length=32)
    due_date: Optional[str] = None


@router.get("")
async def list_interventions(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user)
):
    """List project interventions and mitigation actions."""
    query = """
        SELECT intervention_id, project_id, alert_id, owner, owner_role,
               category, action_description, created_at, due_date, status
        FROM interventions
        WHERE 1=1
    """
    params: dict[str, Any] = {"limit": limit}
    if project_id:
        query += " AND project_id = :project_id"
        params["project_id"] = project_id
    if status:
        query += " AND status = :status"
        params["status"] = status

    query += " ORDER BY created_at DESC LIMIT :limit"
    result = await db.execute(text(query), params)
    rows = result.mappings().all()
    return [
        {
            "intervention_id": r["intervention_id"],
            "project_id": r["project_id"],
            "alert_id": r["alert_id"],
            "owner": r["owner"],
            "category": r["category"],
            "action_description": r["action_description"],
            "status": r["status"],
            "due_date": str(r["due_date"]) if r.get("due_date") else None,
            "created_at": str(r["created_at"]) if r.get("created_at") else None,
        }
        for r in rows
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_intervention(
    body: CreateInterventionRequest,
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(require_role(["operator", "manager", "admin"]))
):
    """Record a new intervention for a project with role enforcement and precise validation."""
    # 1. Validate due_date format if provided
    if body.due_date:
        try:
            datetime.strptime(body.due_date, "%Y-%m-%d")
        except ValueError:
            raise ValidationError(
                message=f"Invalid due_date format: '{body.due_date}'. Expected YYYY-MM-DD",
                details={"field": "due_date", "value": body.due_date}
            )

    # 2. Check project existence
    proj_check = await db.execute(
        text("SELECT project_id FROM projects WHERE project_id = :project_id LIMIT 1"),
        {"project_id": body.project_id}
    )
    if not proj_check.first():
        raise NotFoundError(message=f"Project with ID '{body.project_id}' not found")

    # 3. Check alert existence if alert_id is provided
    if body.alert_id is not None:
        alert_check = await db.execute(
            text("SELECT alert_id FROM alerts WHERE alert_id = :alert_id LIMIT 1"),
            {"alert_id": body.alert_id}
        )
        if not alert_check.first():
            raise NotFoundError(message=f"Alert with ID {body.alert_id} not found")

    stmt = text("""
        INSERT INTO interventions 
        (project_id, alert_id, owner, category, action_description, status, due_date, created_at)
        VALUES 
        (:project_id, :alert_id, :owner, :category, :action_description, :status, 
         CASE WHEN :due_date IS NOT NULL THEN CAST(:due_date AS DATE) ELSE NULL END, NOW())
        RETURNING intervention_id, project_id, alert_id, owner, category, action_description, status, due_date, created_at
    """)
    try:
        result = await db.execute(stmt, {
            "project_id": body.project_id,
            "alert_id": body.alert_id,
            "owner": body.owner,
            "category": body.category,
            "action_description": body.action_description,
            "status": body.status,
            "due_date": body.due_date,
        })
        await db.commit()
        row = result.mappings().first()
        if not row:
            raise HTTPException(status_code=500, detail="Failed to create intervention")
        return {
            "intervention_id": row["intervention_id"],
            "project_id": row["project_id"],
            "alert_id": row["alert_id"],
            "owner": row["owner"],
            "category": row["category"],
            "action_description": row["action_description"],
            "status": row["status"],
            "due_date": str(row["due_date"]) if row.get("due_date") else None,
            "created_at": str(row["created_at"]) if row.get("created_at") else None,
        }
    except (NotFoundError, ValidationError):
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error during intervention creation: {str(e)}")
