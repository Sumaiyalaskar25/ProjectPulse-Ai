# services/api/routes/dashboard.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.session import get_db
from ..dependencies import get_cache_service
from ..core.cache import CachePort

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

@router.get("/summary")
async def get_summary(
    db: AsyncSession = Depends(get_db),
    cache: CachePort = Depends(get_cache_service)
):
    """Portfolio summary with tier counts and capital at risk (cached with 60s TTL)."""
    cache_key = "dashboard:summary"
    cached = await cache.get(cache_key)
    if cached:
        return cached

    stmt = text("""
        WITH latest_risk AS (
            SELECT project_id, composite_score, tier,
                   ROW_NUMBER() OVER (PARTITION BY project_id ORDER BY report_month DESC) as rn
            FROM risk_scores
        ),
        current_risk AS (
            SELECT project_id, composite_score, tier
            FROM latest_risk WHERE rn = 1
        )
        SELECT 
            COUNT(*) as total_projects,
            SUM(p.original_cost) as total_cost,
            COUNT(CASE WHEN cr.tier = 'Critical' THEN 1 END) as critical_count,
            COUNT(CASE WHEN cr.tier = 'High' THEN 1 END) as high_count,
            COUNT(CASE WHEN cr.tier = 'Moderate' THEN 1 END) as moderate_count,
            COUNT(CASE WHEN cr.tier = 'Stable' THEN 1 END) as stable_count,
            SUM(CASE WHEN cr.tier IN ('Critical', 'High') THEN p.original_cost ELSE 0 END) as capital_at_risk
        FROM projects p
        LEFT JOIN current_risk cr ON p.project_id = cr.project_id
    """)
    result = await db.execute(stmt)
    row = result.first()
    
    if not row:
        data = {
            "total_projects": 0,
            "total_cost_cr": 0,
            "critical_count": 0,
            "high_count": 0,
            "moderate_count": 0,
            "stable_count": 0,
            "capital_at_risk_cr": 0
        }
    else:
        data = {
            "total_projects": row[0] or 0,
            "total_cost_cr": row[1] or 0,
            "critical_count": row[2] or 0,
            "high_count": row[3] or 0,
            "moderate_count": row[4] or 0,
            "stable_count": row[5] or 0,
            "capital_at_risk_cr": row[6] or 0
        }
        
    await cache.setex(cache_key, 60, data)
    return data

@router.get("/changes")
async def get_changes(
    db: AsyncSession = Depends(get_db),
    cache: CachePort = Depends(get_cache_service)
):
    """What changed this month (cached with 60s TTL)."""
    cache_key = "dashboard:changes"
    cached = await cache.get(cache_key)
    if cached:
        return cached

    stmt = text("""
        WITH ranked_risk AS (
            SELECT project_id, composite_score, tier,
                   ROW_NUMBER() OVER (PARTITION BY project_id ORDER BY report_month DESC) as rn
            FROM risk_scores
        ),
        curr AS (SELECT * FROM ranked_risk WHERE rn = 1),
        prev AS (SELECT * FROM ranked_risk WHERE rn = 2)
        SELECT 
            COUNT(CASE WHEN curr.tier = 'Critical' AND prev.tier != 'Critical' THEN 1 END) as new_critical,
            COUNT(CASE WHEN curr.tier = 'High' AND prev.tier != 'High' AND prev.tier != 'Critical' THEN 1 END) as new_high,
            COUNT(CASE WHEN curr.composite_score < prev.composite_score - 5 THEN 1 END) as improved,
            COUNT(CASE WHEN curr.composite_score > prev.composite_score + 5 THEN 1 END) as deteriorated,
            SUM(CASE WHEN curr.composite_score > prev.composite_score + 5 THEN curr.composite_score - prev.composite_score ELSE 0 END) as deterioration_magnitude
        FROM curr
        JOIN prev ON curr.project_id = prev.project_id
    """)
    result = await db.execute(stmt)
    row = result.first()
    
    if not row:
        data = {
            "new_critical": 0,
            "new_high": 0,
            "improved": 0,
            "deteriorated": 0,
            "deterioration_magnitude": 0
        }
    else:
        data = {
            "new_critical": row[0] or 0,
            "new_high": row[1] or 0,
            "improved": row[2] or 0,
            "deteriorated": row[3] or 0,
            "deterioration_magnitude": row[4] or 0
        }
        
    await cache.setex(cache_key, 60, data)
    return data

@router.get("/priorities")
async def get_priorities(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Top intervention priorities."""
    stmt = text("""
        WITH latest_risk AS (
            SELECT project_id, composite_score, tier, intervention_priority,
                   risk_previous, risk_delta,
                   ROW_NUMBER() OVER (PARTITION BY project_id ORDER BY report_month DESC) as rn
            FROM risk_scores
        ),
        current_risk AS (
            SELECT * FROM latest_risk WHERE rn = 1
        )
        SELECT 
            p.project_id,
            p.project_name,
            p.sector,
            p.ministry,
            cr.composite_score as risk,
            cr.tier,
            cr.intervention_priority as priority,
            cr.risk_delta as delta,
            p.original_cost as exposure
        FROM projects p
        JOIN current_risk cr ON p.project_id = cr.project_id
        ORDER BY cr.intervention_priority DESC
        LIMIT :limit
    """)
    result = await db.execute(stmt, {"limit": limit})
    rows = result.all()
    
    return {
        "priorities": [
            {
                "project_id": r[0],
                "project_name": r[1],
                "sector": r[2],
                "ministry": r[3],
                "risk": r[4],
                "tier": r[5],
                "priority": r[6],
                "delta": r[7],
                "exposure": r[8]
            }
            for r in rows
        ]
    }
