from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from ..dependencies import get_assistant_service
from ..services.assistant_service import AssistantService
from ..middleware.rate_limit import rate_limit
from ..core.auth import get_current_user, AuthenticatedUser

router = APIRouter(prefix="/api/v1/assistant", tags=["assistant"])

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Natural language question about infrastructure projects")

@router.post("/query")
async def ask_assistant(
    request: QueryRequest,
    service: AssistantService = Depends(get_assistant_service),
    _limiter: None = Depends(rate_limit(max_requests=20, window_seconds=60)),
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Grounded natural language query assistant using LLM + allow-listed SQL queries.
    Protected by rate limiter (20 req/min) and auth.
    """
    return await service.process_query(request.query)
