# services/api/services/assistant_service.py
import json
import os
from typing import Dict, Optional
from groq import Groq
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

class AssistantService:
    # ALLOW-LIST: The assistant can only query these
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
    
    async def process_query(self, user_query: str) -> Dict:
        if not self.client:
            return {"error": "GROQ_API_KEY environment variable is not configured."}
            
        # Step 1: Extract intent with allow-list enforcement
        response = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": self._build_system_prompt()},
                {"role": "user", "content": user_query}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        intent = json.loads(response.choices[0].message.content)
        
        # Step 2: Validate against allow-list
        if intent.get('metric') not in self.ALLOWED_METRICS:
            return {"error": f"Unsupported metric. Allowed: {self.ALLOWED_METRICS}"}
        
        for filter_key in intent.get('filters', {}).keys():
            if filter_key not in self.ALLOWED_FILTERS:
                return {"error": f"Unsupported filter: {filter_key}"}
        
        if intent.get('entity') not in self.ALLOWED_ENTITIES:
            return {"error": f"Unsupported entity. Allowed: {self.ALLOWED_ENTITIES}"}
        
        # Step 3: Build parameterized SQL (NOT string interpolation)
        sql, params = self._build_sql(intent)
        
        # Step 4: Execute with bound parameters
        result = await self.db.execute(text(sql), params)
        rows = result.mappings().all()
        
        # Step 5: Format response
        return {
            "query": user_query,
            "intent": intent,
            "data": [dict(row) for row in rows],
            "count": len(rows)
        }
    
    def _build_sql(self, intent: Dict) -> tuple:
        """Returns (sql_string, params_dict)."""
        filters = intent.get('filters', {})
        entity = intent.get('entity', 'projects')
        limit = min(intent.get('limit', 5), self.MAX_LIMIT)
        
        # Base query templates (pre-approved)
        if entity == 'projects':
            sql = """
                SELECT p.project_id, p.project_name, p.sector, p.ministry, 
                       rs.composite_score as risk_score, rs.tier
                FROM projects p
                JOIN risk_scores rs ON p.project_id = rs.project_id
                WHERE rs.report_month = (
                    SELECT MAX(report_month) FROM risk_scores r2 
                    WHERE r2.project_id = p.project_id
                )
            """
        else:  # alerts
            sql = """
                SELECT a.alert_id, a.project_id, a.severity, a.alert_type, 
                       a.triggered_at, a.status
                FROM alerts a
                WHERE 1=1
            """
        
        params = {}
        
        # Apply filters with bound parameters
        if filters.get('sector'):
            sql += " AND p.sector = :sector"
            params['sector'] = filters['sector']
        
        if filters.get('ministry'):
            sql += " AND p.ministry = :ministry"
            params['ministry'] = filters['ministry']
        
        if filters.get('state'):
            sql += " AND p.state = :state"
            params['state'] = filters['state']
        
        if filters.get('tier'):
            sql += " AND rs.tier = :tier"
            params['tier'] = filters['tier']
        
        # Sorting
        sort = intent.get('sort', 'priority_desc')
        if sort == 'risk_desc':
            sql += " ORDER BY rs.composite_score DESC"
        elif sort == 'risk_asc':
            sql += " ORDER BY rs.composite_score ASC"
        else:  # priority_desc
            if entity == 'projects':
                sql += " ORDER BY rs.intervention_priority DESC"
            else:
                sql += " ORDER BY a.triggered_at DESC"
        
        sql += " LIMIT :limit"
        params['limit'] = limit
        
        return sql, params
