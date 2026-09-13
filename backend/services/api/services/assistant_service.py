# services/api/services/assistant_service.py
import json
import os
from typing import Dict, Optional, Any, List
import anyio
from groq import Groq
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.logging import get_logger

logger = get_logger("assistant_service")

class AssistantService:
    ALLOWED_METRICS = ['risk', 'cost', 'schedule', 'count']
    ALLOWED_FILTERS = ['sector', 'ministry', 'state', 'tier']
    ALLOWED_ENTITIES = ['projects', 'alerts']
    ALLOWED_SORT = ['risk_asc', 'risk_desc', 'priority_desc']
    MAX_LIMIT = 20
    
    def __init__(self, db: AsyncSession):
        self.db = db
        api_key = os.getenv("GROQ_API_KEY", "")
        self.client = Groq(api_key=api_key) if api_key else None
    
    def _build_system_prompt(self) -> str:
        return f"""
        You are an assistant for a government infrastructure monitoring system.
        Extract structured parameters from user queries.
        
        ALLOWED VALUES:
        - metric: {', '.join(self.ALLOWED_METRICS)}
        - filters: {', '.join(self.ALLOWED_FILTERS)} (each can be a string value)
        - entity: {', '.join(self.ALLOWED_ENTITIES)}
        - limit: integer between 1 and {self.MAX_LIMIT}
        - sort: {', '.join(self.ALLOWED_SORT)}
        
        Output ONLY valid JSON with these keys.
        """
    
    async def process_query(self, user_query: str) -> Dict[str, Any]:
        if not self.client:
            return {
                "query": user_query,
                "formatted_answer": "Assistant API key (GROQ_API_KEY) is not configured in this environment.",
                "data": [],
                "sources": []
            }
            
        try:
            # Step 1: Extract intent offloaded to thread
            def _extract_intent():
                return self.client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {"role": "system", "content": self._build_system_prompt()},
                        {"role": "user", "content": user_query}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )

            response = await anyio.to_thread.run_sync(_extract_intent)
            intent = json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.exception("Failed to extract intent from Groq model")
            return {
                "query": user_query,
                "formatted_answer": "Unable to process natural language query at this moment.",
                "data": [],
                "sources": []
            }

        # Validate parameters
        metric = intent.get('metric', 'risk')
        if metric not in self.ALLOWED_METRICS:
            metric = 'risk'
        
        sanitized_filters = {}
        for filter_key, val in intent.get('filters', {}).items():
            if filter_key in self.ALLOWED_FILTERS and isinstance(val, str):
                sanitized_filters[filter_key] = val
        intent['filters'] = sanitized_filters

        if intent.get('entity') not in self.ALLOWED_ENTITIES:
            intent['entity'] = 'projects'

        # Step 3: Build parameterized SQL
        sql, params = self._build_sql(intent)
        
        # Step 4: Execute query
        try:
            result = await self.db.execute(text(sql), params)
            rows = result.mappings().all()
            data = [dict(row) for row in rows]
        except Exception as e:
            logger.exception("Assistant SQL execution failed")
            data = []

        # Step 5: Format human-readable response and sources
        sources = ["ProjectPulse Infrastructure Registry", "Central Risk Engine"]
        if intent['entity'] == 'alerts':
            sources.append("Operational Alerts Queue")

        count = len(data)
        if count == 0:
            formatted_answer = f"No {intent['entity']} found matching your query criteria."
        else:
            formatted_answer = (
                f"Found {count} {intent['entity']} matching your criteria. "
                f"Top records include: {', '.join([d.get('project_name') or d.get('title') or d.get('project_id', '') for d in data[:3]])}."
            )

        return {
            "query": user_query,
            "intent": intent,
            "formatted_answer": formatted_answer,
            "data": data,
            "sources": sources,
            "count": count
        }
    
    def _build_sql(self, intent: Dict) -> tuple:
        """Returns (sql_string, params_dict)."""
        filters = intent.get('filters', {})
        entity = intent.get('entity', 'projects')
        limit = min(intent.get('limit', 5), self.MAX_LIMIT)
        
        params: dict[str, Any] = {"limit": limit}
        
        if entity == 'projects':
            sql = """
                SELECT p.project_id, p.project_name, p.sector, p.ministry, p.state,
                       rs.composite_score as risk_score, rs.tier, rs.intervention_priority
                FROM projects p
                LEFT JOIN risk_scores rs ON p.project_id = rs.project_id
                WHERE (rs.report_month IS NULL OR rs.report_month = (
                    SELECT MAX(report_month) FROM risk_scores r2 
                    WHERE r2.project_id = p.project_id
                ))
            """
            if filters.get('sector'):
                sql += " AND p.sector ILIKE :sector"
                params['sector'] = f"%{filters['sector']}%"
            if filters.get('ministry'):
                sql += " AND p.ministry ILIKE :ministry"
                params['ministry'] = f"%{filters['ministry']}%"
            if filters.get('state'):
                sql += " AND p.state ILIKE :state"
                params['state'] = f"%{filters['state']}%"
            if filters.get('tier'):
                sql += " AND rs.tier ILIKE :tier"
                params['tier'] = filters['tier']

            sort = intent.get('sort', 'priority_desc')
            if sort == 'risk_desc':
                sql += " ORDER BY rs.composite_score DESC NULLS LAST"
            elif sort == 'risk_asc':
                sql += " ORDER BY rs.composite_score ASC NULLS LAST"
            else:
                sql += " ORDER BY rs.intervention_priority DESC NULLS LAST"
        else:  # alerts
            sql = """
                SELECT a.alert_id, a.project_id, p.project_name, a.severity, a.alert_type, 
                       a.title, a.description, a.risk_delta, a.triggered_at, a.status
                FROM alerts a
                LEFT JOIN projects p ON a.project_id = p.project_id
                LEFT JOIN risk_scores rs ON a.risk_id = rs.risk_id
                WHERE 1=1
            """
            if filters.get('sector'):
                sql += " AND p.sector ILIKE :sector"
                params['sector'] = f"%{filters['sector']}%"
            if filters.get('ministry'):
                sql += " AND p.ministry ILIKE :ministry"
                params['ministry'] = f"%{filters['ministry']}%"
            if filters.get('state'):
                sql += " AND p.state ILIKE :state"
                params['state'] = f"%{filters['state']}%"
            if filters.get('tier'):
                sql += " AND rs.tier ILIKE :tier"
                params['tier'] = filters['tier']

            sql += " ORDER BY a.triggered_at DESC NULLS LAST"
        
        sql += " LIMIT :limit"
        return sql, params
