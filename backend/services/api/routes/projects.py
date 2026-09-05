# services/api/routes/projects.py
from fastapi import APIRouter, Depends, Query
from typing import Optional
from ..dependencies import get_project_service
from ..services.project_service import ProjectService
from ..core.errors import NotFoundError

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])

@router.get("")
async def list_projects(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(50, ge=1, le=100, description="Page size limit"),
    cursor: Optional[str] = Query(None, description="Cursor for keyset pagination"),
    ministry: Optional[str] = Query(None, description="Filter by ministry name"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    state: Optional[str] = Query(None, description="Filter by state"),
    tier: Optional[str] = Query(None, description="Filter by risk tier (Critical, High, Moderate, Stable)"),
    search: Optional[str] = Query(None, description="Search query across project name/id"),
    service: ProjectService = Depends(get_project_service)
):
    """
    List infrastructure projects with filtering, full pagination, and latest risk/snapshot linkage.
    """
    filters = {
        "ministry": ministry,
        "sector": sector,
        "state": state,
        "tier": tier,
        "search": search
    }
    # Filter out None values
    active_filters = {k: v for k, v in filters.items() if v is not None}
    
    return await service.list_projects(
        filters=active_filters,
        page=page,
        limit=limit,
        cursor=cursor
    )

@router.get("/{project_id}")
async def get_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """
    Retrieve project details by unique project ID.
    """
    project = await service.get_project(project_id)
    if not project:
        raise NotFoundError(message=f"Project '{project_id}' not found")
    return project
