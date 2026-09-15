# services/api/repositories/project_repo.py
from abc import ABC, abstractmethod
from typing import Optional, Any, List
from sqlalchemy import select, func, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.db import Project, ProjectSnapshot, RiskScore

class ProjectRepository(ABC):
    """Abstract Port for Project data access."""
    
    @abstractmethod
    async def get_by_id(self, project_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def list_with_filters(
        self,
        filters: dict[str, Any],
        page: int = 1,
        limit: int = 50,
        cursor: Optional[str] = None
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def get_risk_history(self, project_id: str, limit: int = 12) -> List[dict]:
        pass

    @abstractmethod
    async def get_risk_drivers(self, project_id: str) -> Optional[dict]:
        pass

class SQLAlchemyProjectRepository(ProjectRepository):
    """Concrete SQLAlchemy adapter for Project repository."""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, project_id: str) -> Optional[dict]:
        stmt = select(Project).where(Project.project_id == project_id)
        result = await self.db.execute(stmt)
        project = result.scalar_one_or_none()
        if not project:
            return None
        return {
            "project_id": project.project_id,
            "project_name": project.project_name,
            "sector": project.sector,
            "ministry": project.ministry,
            "state": project.state,
            "original_cost": project.original_cost,
            "approval_date": str(project.approval_date) if project.approval_date else None,
            "original_completion_date": str(project.original_completion_date) if project.original_completion_date else None,
        }

    async def list_with_filters(
        self,
        filters: dict[str, Any],
        page: int = 1,
        limit: int = 50,
        cursor: Optional[str] = None
    ) -> dict[str, Any]:
        # Subquery for latest snapshot per project
        latest_snapshot_subq = (
            select(
                ProjectSnapshot.project_id,
                func.max(ProjectSnapshot.report_month).label('latest_month')
            )
            .group_by(ProjectSnapshot.project_id)
            .subquery('latest_snap')
        )
        
        # Subquery for latest risk score per project
        latest_risk_subq = (
            select(
                RiskScore.project_id,
                func.max(RiskScore.prediction_timestamp).label('latest_risk_time')
            )
            .group_by(RiskScore.project_id)
            .subquery('latest_risk')
        )
        
        # Main query with explicit joins
        query = (
            select(
                Project.project_id,
                Project.project_name,
                Project.sector,
                Project.ministry,
                Project.state,
                Project.original_cost,
                ProjectSnapshot.physical_progress,
                RiskScore.composite_score,
                RiskScore.tier,
                RiskScore.intervention_priority
            )
            .select_from(Project)
            .outerjoin(
                ProjectSnapshot,
                and_(
                    ProjectSnapshot.project_id == Project.project_id,
                    ProjectSnapshot.report_month == latest_snapshot_subq.c.latest_month
                )
            )
            .outerjoin(
                latest_snapshot_subq,
                latest_snapshot_subq.c.project_id == Project.project_id
            )
            .outerjoin(
                latest_risk_subq,
                latest_risk_subq.c.project_id == Project.project_id
            )
            .outerjoin(
                RiskScore,
                and_(
                    RiskScore.project_id == Project.project_id,
                    RiskScore.prediction_timestamp == latest_risk_subq.c.latest_risk_time
                )
            )
        )
        
        # Apply filters
        if filters.get('ministry'):
            query = query.where(Project.ministry == filters['ministry'])
        if filters.get('sector'):
            query = query.where(Project.sector == filters['sector'])
        if filters.get('state'):
            query = query.where(Project.state == filters['state'])
        if filters.get('tier'):
            # Case-insensitive tier matching
            query = query.where(RiskScore.tier.ilike(filters['tier']))
        if filters.get('search'):
            search_term = f"%{filters['search']}%"
            query = query.where(
                (Project.project_id.ilike(search_term)) |
                (Project.project_name.ilike(search_term)) |
                (Project.implementing_agency.ilike(search_term))
            )
        
        if cursor:
            query = query.where(Project.project_id > cursor)

        # Count total records for pagination
        total_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(total_query)
        
        # Cursor vs offset pagination
        if cursor:
            query = query.order_by(Project.project_id).limit(limit)
        else:
            query = query.order_by(Project.project_id).offset((page - 1) * limit).limit(limit)
            
        result = await self.db.execute(query)
        rows = result.all()
        
        data = [
            {
                "project_id": row[0],
                "project_name": row[1],
                "sector": row[2],
                "ministry": row[3],
                "state": row[4],
                "original_cost": row[5],
                "physical_progress": row[6],
                "risk_score": row[7],
                "risk_tier": row[8],
                "intervention_priority": row[9]
            }
            for row in rows
        ]
        
        next_cursor = data[-1]["project_id"] if (len(data) == limit and data) else None
        
        return {
            "data": data,
            "page": page,
            "limit": limit,
            "total": total or 0,
            "total_pages": ((total - 1) // limit + 1) if (total and total > 0) else 0,
            "next_cursor": next_cursor
        }

    async def get_risk_history(self, project_id: str, limit: int = 12) -> List[dict]:
        """Fetch historical risk scores for a project."""
        stmt = (
            select(RiskScore)
            .where(RiskScore.project_id == project_id)
            .order_by(RiskScore.report_month.desc(), RiskScore.prediction_timestamp.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        scores = result.scalars().all()
        return [
            {
                "risk_id": s.risk_id,
                "project_id": s.project_id,
                "report_month": str(s.report_month),
                "cost_risk": s.cost_risk,
                "schedule_risk": s.schedule_risk,
                "trajectory_risk": s.trajectory_risk,
                "composite_score": s.composite_score,
                "tier": (s.tier or "").lower(),
                "confidence_score": s.confidence_score or 0.0,
                "intervention_priority": s.intervention_priority or 0.0,
                "top_drivers": s.top_drivers or [],
                "risk_delta": s.risk_delta or 0.0,
                "predicted_delay_months": s.predicted_delay_months or 0.0,
                "predicted_cost_overrun_pct": s.predicted_cost_overrun_pct or 0.0,
            }
            for s in scores
        ]

    async def get_risk_drivers(self, project_id: str) -> Optional[dict]:
        """Fetch latest risk drivers for a project."""
        stmt = (
            select(RiskScore)
            .where(RiskScore.project_id == project_id)
            .order_by(RiskScore.report_month.desc(), RiskScore.prediction_timestamp.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        s = result.scalar_one_or_none()
        if not s:
            return None
        return {
            "risk_id": s.risk_id,
            "project_id": s.project_id,
            "report_month": str(s.report_month),
            "cost_risk": s.cost_risk,
            "schedule_risk": s.schedule_risk,
            "trajectory_risk": s.trajectory_risk,
            "composite_score": s.composite_score,
            "tier": (s.tier or "").lower(),
            "confidence_score": s.confidence_score or 0.0,
            "intervention_priority": s.intervention_priority or 0.0,
            "top_drivers": s.top_drivers or [],
            "risk_delta": s.risk_delta or 0.0,
            "predicted_delay_months": s.predicted_delay_months or 0.0,
            "predicted_cost_overrun_pct": s.predicted_cost_overrun_pct or 0.0,
        }
