# services/api/routes/assistant.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from ..dependencies import get_assistant_service
from ..services.assistant_service import AssistantService

router = APIRouter(prefix="/api/v1/assistant", tags=["assistant"])

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Natural language question about infrastructure projects")

@router.post("/query")
async def ask_assistant(
    request: QueryRequest,
    service: AssistantService = Depends(get_assistant_service)
):
    """
    Grounded natural language query assistant using LLM + allow-listed SQL queries.
    """
    return await service.process_query(request.query)
