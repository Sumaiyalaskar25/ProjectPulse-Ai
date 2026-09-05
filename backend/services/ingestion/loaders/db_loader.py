# services/ingestion/loaders/db_loader.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import pandas as pd
from typing import Any, Dict, List, cast

class DatabaseLoader:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def batch_upsert_projects(self, df: pd.DataFrame):
        """Bulk upsert using SQLAlchemy core."""
        # Convert DataFrame to list of dicts
        records = cast(List[Dict[str, Any]], df.to_dict('records'))
        if not records:
            return
        
        # Use raw SQL with executemany for speed
        stmt = text("""
            INSERT INTO projects 
            (project_id, project_name, sector, ministry, state, implementing_agency, 
             original_cost, approval_date, original_completion_date)
            VALUES (:project_id, :project_name, :sector, :ministry, :state, :implementing_agency,
                    :original_cost, :approval_date, :original_completion_date)
            ON CONFLICT (project_id) DO UPDATE SET
                project_name = EXCLUDED.project_name,
                sector = EXCLUDED.sector,
                ministry = EXCLUDED.ministry,
                state = EXCLUDED.state,
                implementing_agency = EXCLUDED.implementing_agency,
                original_cost = EXCLUDED.original_cost,
                approval_date = EXCLUDED.approval_date,
                original_completion_date = EXCLUDED.original_completion_date,
                updated_at = NOW()
        """)
        
        await self.session.execute(stmt, records)
        await self.session.commit()
    
    async def batch_upsert_snapshots(self, df: pd.DataFrame, run_id: int):
        """Bulk upsert snapshots."""
        records = cast(List[Dict[str, Any]], df.to_dict('records'))
        if not records:
            return
            
        # Add run_id to each record
        for r in records:
            r['ingestion_run_id'] = run_id
        
        stmt = text("""
            INSERT INTO project_snapshots 
            (project_id, report_month, revised_cost, cumulative_expenditure, 
             physical_progress, latest_revised_completion_date, project_status,
             delay_reason_text, source_file, source_page, source_row, 
             source_hash, parser_version, ingestion_run_id)
            VALUES (:project_id, :report_month, :revised_cost, :cumulative_expenditure,
                    :physical_progress, :latest_revised_completion_date, :project_status,
                    :delay_reason_text, :source_file, :source_page, :source_row,
                    :source_hash, :parser_version, :ingestion_run_id)
            ON CONFLICT (project_id, report_month) DO UPDATE SET
                revised_cost = EXCLUDED.revised_cost,
                cumulative_expenditure = EXCLUDED.cumulative_expenditure,
                physical_progress = EXCLUDED.physical_progress,
                latest_revised_completion_date = EXCLUDED.latest_revised_completion_date,
                project_status = EXCLUDED.project_status,
                delay_reason_text = EXCLUDED.delay_reason_text,
                source_file = EXCLUDED.source_file,
                source_page = EXCLUDED.source_page,
                source_row = EXCLUDED.source_row,
                source_hash = EXCLUDED.source_hash,
                parser_version = EXCLUDED.parser_version
        """)
        
        await self.session.execute(stmt, records)
        await self.session.commit()