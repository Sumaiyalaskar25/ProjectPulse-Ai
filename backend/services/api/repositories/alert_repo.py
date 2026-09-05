# services/api/repositories/alert_repo.py
from abc import ABC, abstractmethod
from typing import Optional, Any, List
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

class AlertRepository(ABC):
    """Abstract Port for Alert data access."""
    
    @abstractmethod
    async def list_alerts(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 50
    ) -> List[dict[str, Any]]:
        pass

    @abstractmethod
    async def insert_alerts(self, alerts: List[dict[str, Any]]) -> List[int]:
        pass

class SQLAlchemyAlertRepository(AlertRepository):
    """Concrete SQLAlchemy implementation of Alert repository."""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_alerts(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 50
    ) -> List[dict[str, Any]]:
        query = """
            SELECT a.alert_id, a.project_id, p.project_name, a.risk_id, a.alert_type,
                   a.severity, a.title, a.description, a.risk_previous, a.risk_current,
                   a.risk_delta, a.trigger_condition, a.triggered_at, a.status
            FROM alerts a
            LEFT JOIN projects p ON a.project_id = p.project_id
            WHERE 1=1
        """
        params: dict[str, Any] = {"limit": limit}
        if status:
            query += " AND a.status = :status"
            params["status"] = status
        if severity:
            query += " AND a.severity = :severity"
            params["severity"] = severity
            
        query += " ORDER BY a.triggered_at DESC LIMIT :limit"
        result = await self.db.execute(text(query), params)
        rows = result.mappings().all()
        return [dict(r) for r in rows]

    async def insert_alerts(self, alerts: List[dict[str, Any]]) -> List[int]:
        inserted = []
        for alert in alerts:
            # Check for duplicate within 7 days
            check_stmt = text("""
                SELECT alert_id FROM alerts 
                WHERE project_id = :project_id 
                AND alert_type = :alert_type 
                AND triggered_at > NOW() - INTERVAL '7 days'
                LIMIT 1
            """)
            existing = await self.db.execute(check_stmt, {
                'project_id': alert['project_id'],
                'alert_type': alert['alert_type']
            })
            if existing.first():
                continue
                
            stmt = text("""
                INSERT INTO alerts 
                (project_id, risk_id, alert_type, severity, title, description, 
                 risk_previous, risk_current, risk_delta, trigger_condition, triggered_at)
                VALUES 
                (:project_id, :risk_id, :alert_type, :severity, :title, :description,
                 :risk_previous, :risk_current, :risk_delta, :trigger_condition, NOW())
                RETURNING alert_id
            """)
            result = await self.db.execute(stmt, alert)
            inserted.append(result.scalar())
            
        await self.db.commit()
        return inserted
