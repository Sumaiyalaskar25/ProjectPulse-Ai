# services/api/repositories/alert_repo.py
from abc import ABC, abstractmethod
from typing import Optional, Any, List
from datetime import datetime, timezone
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

    @abstractmethod
    async def acknowledge_alert(self, alert_id: int, assigned_to: Optional[str] = None) -> Optional[dict[str, Any]]:
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
        alerts_list: List[dict[str, Any]] = []
        for r in rows:
            alert_dict: dict[str, Any] = {str(k): v for k, v in r.items()}
            if alert_dict.get("triggered_at"):
                alert_dict["triggered_at"] = str(alert_dict["triggered_at"])
            alerts_list.append(alert_dict)
        return alerts_list

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

    async def acknowledge_alert(self, alert_id: int, assigned_to: Optional[str] = None) -> Optional[dict[str, Any]]:
        stmt = text("""
            UPDATE alerts
            SET status = 'acknowledged',
                acknowledged_at = NOW(),
                assigned_to = COALESCE(:assigned_to, assigned_to)
            WHERE alert_id = :alert_id
            RETURNING alert_id, project_id, alert_type, severity, title, description,
                      risk_previous, risk_current, risk_delta, status, triggered_at, acknowledged_at
        """)
        result = await self.db.execute(stmt, {"alert_id": alert_id, "assigned_to": assigned_to})
        await self.db.commit()
        row = result.mappings().first()
        if not row:
            return None
        res: dict[str, Any] = {str(k): v for k, v in row.items()}
        if res.get("triggered_at"):
            res["triggered_at"] = str(res["triggered_at"])
        if res.get("acknowledged_at"):
            res["acknowledged_at"] = str(res["acknowledged_at"])
        return res
