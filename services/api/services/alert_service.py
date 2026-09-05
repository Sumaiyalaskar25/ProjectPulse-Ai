# services/api/services/alert_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from datetime import datetime, timedelta
from ..models.db import Alert, RiskScore

class AlertEngine:
    ALERT_TYPES = {
        'risk_escalation': {'severity': 'critical', 'threshold': 75},
        'risk_jump': {'severity': 'high', 'threshold': 15},  # delta > 15
        'rapid_deterioration': {'severity': 'critical', 'threshold': 20},  # delta > 20
        'progress_stagnation': {'severity': 'moderate', 'threshold': 3},  # months
        'schedule_revision': {'severity': 'moderate', 'threshold': 2}  # revisions
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_alerts(self):
        """Run all alert rules and insert new alerts."""
        alerts_generated = []
        
        # Rule 1: High risk
        alerts_generated.extend(await self._check_risk_escalation())
        
        # Rule 2: Risk jump (delta > 15)
        alerts_generated.extend(await self._check_risk_jump())
        
        # Rule 3: Progress stagnation
        alerts_generated.extend(await self._check_progress_stagnation())
        
        # Deduplicate and insert
        inserted = await self._insert_alerts(alerts_generated)
        return inserted
    
    async def _check_risk_escalation(self):
        """High risk > 75."""
        stmt = text("""
            SELECT 
                rs.project_id, rs.risk_id, rs.composite_score,
                p.project_name
            FROM risk_scores rs
            JOIN projects p ON rs.project_id = p.project_id
            WHERE rs.composite_score > 75
            AND rs.report_month = (
                SELECT MAX(report_month) FROM risk_scores r2 
                WHERE r2.project_id = rs.project_id
            )
        """)
        result = await self.db.execute(stmt)
        rows = result.all()
        
        alerts = []
        for row in rows:
            alerts.append({
                'project_id': row[0],
                'risk_id': row[1],
                'alert_type': 'risk_escalation',
                'severity': 'critical',
                'title': f"Critical Risk Alert: {row[3]}",
                'description': f"Project risk score is {row[2]:.0f} (Critical threshold > 75)",
                'risk_current': row[2],
                'risk_previous': None,
                'risk_delta': None,
                'trigger_condition': {'threshold': 75, 'metric': 'composite_score'}
            })
        return alerts
    
    async def _check_risk_jump(self):
        """Risk increased by > 15 points in the last month."""
        stmt = text("""
            WITH latest_risk AS (
                SELECT project_id, composite_score, report_month,
                       ROW_NUMBER() OVER (PARTITION BY project_id ORDER BY report_month DESC) as rn
                FROM risk_scores
            ),
            current AS (
                SELECT project_id, composite_score FROM latest_risk WHERE rn = 1
            ),
            previous AS (
                SELECT project_id, composite_score FROM latest_risk WHERE rn = 2
            )
            SELECT 
                c.project_id, 
                c.composite_score as current_risk,
                p.composite_score as previous_risk,
                (c.composite_score - p.composite_score) as delta,
                pr.project_name
            FROM current c
            JOIN previous p ON c.project_id = p.project_id
            JOIN projects pr ON c.project_id = pr.project_id
            WHERE (c.composite_score - p.composite_score) > 15
        """)
        result = await self.db.execute(stmt)
        rows = result.all()
        
        alerts = []
        for row in rows:
            alerts.append({
                'project_id': row[0],
                'risk_id': None,
                'alert_type': 'risk_jump',
                'severity': 'high' if row[3] < 25 else 'critical',
                'title': f"Rapid Risk Escalation: {row[4]}",
                'description': f"Risk increased by {row[3]:.0f} points (from {row[2]:.0f} to {row[1]:.0f})",
                'risk_previous': row[2],
                'risk_current': row[1],
                'risk_delta': row[3],
                'trigger_condition': {'threshold': 15, 'metric': 'risk_delta'}
            })
        return alerts
    
    async def _check_progress_stagnation(self):
        """No progress change in 3 months."""
        stmt = text("""
            WITH progress_history AS (
                SELECT project_id, report_month, physical_progress,
                       LAG(physical_progress, 3) OVER (PARTITION BY project_id ORDER BY report_month) as progress_3m_ago
                FROM project_snapshots
            ),
            latest AS (
                SELECT project_id, report_month, physical_progress, progress_3m_ago
                FROM progress_history
                WHERE report_month = (
                    SELECT MAX(report_month) FROM project_snapshots s2 
                    WHERE s2.project_id = progress_history.project_id
                )
            )
            SELECT 
                l.project_id,
                l.physical_progress,
                l.progress_3m_ago,
                p.project_name
            FROM latest l
            JOIN projects p ON l.project_id = p.project_id
            WHERE l.physical_progress = l.progress_3m_ago
            AND l.physical_progress < 95  -- Exclude completed
        """)
        result = await self.db.execute(stmt)
        rows = result.all()
        
        alerts = []
        for row in rows:
            alerts.append({
                'project_id': row[0],
                'risk_id': None,
                'alert_type': 'progress_stagnation',
                'severity': 'moderate',
                'title': f"Progress Stagnation: {row[3]}",
                'description': f"Physical progress unchanged at {row[1]:.0f}% for 3 months",
                'risk_current': row[1],
                'risk_previous': row[2],
                'risk_delta': None,
                'trigger_condition': {'threshold': 3, 'metric': 'months_stagnant'}
            })
        return alerts
    
    async def _insert_alerts(self, alerts):
        """Insert alerts with deduplication."""
        inserted = []
        for alert in alerts:
            # Check for duplicate (same project, same type, last 7 days)
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
                continue  # Skip duplicate
            
            # Insert
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
