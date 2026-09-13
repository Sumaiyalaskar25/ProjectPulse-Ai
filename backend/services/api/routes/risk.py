# services/api/routes/risk.py
"""
ML risk prediction routes.

Calls services.ml.inference.predict.predict_risk() in-process.
No external service; no HTTP hop.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from ...ml.inference.predict import predict_risk
from ...ml.inference.counterfactual import (
    simulate_counterfactual,
    list_actionable_inputs,
)
from ..core.errors import AppException
from ..core.logging import get_logger

logger = get_logger("risk_routes")
router = APIRouter(prefix="/api/v1/risk", tags=["risk"])


# ------------------------------------------------------------------------
# SCHEMAS
# ------------------------------------------------------------------------

class ProjectSnapshotIn(BaseModel):
    project_id: str = Field(..., min_length=1, max_length=64)
    report_month: str
    original_cost: float = Field(..., gt=0)
    revised_cost: Optional[float] = None
    cumulative_expenditure: Optional[float] = None
    physical_progress: Optional[float] = Field(None, ge=0, le=100)
    approval_date: str
    original_completion_date: str
    latest_revised_completion_date: Optional[str] = None
    sector: Optional[str] = "Unknown"
    ministry: Optional[str] = "Unknown"
    state: Optional[str] = "Unknown"
    delay_reason_text: Optional[str] = ""
    history: Optional[List[Dict[str, Any]]] = None


class WhatIfRequest(BaseModel):
    project_id: str
    perturbations: Dict[str, float]
    target: str = "schedule"


# ------------------------------------------------------------------------
# ENDPOINTS
# ------------------------------------------------------------------------

@router.post("/predict")
async def predict_endpoint(req: ProjectSnapshotIn):
    """
    Predict risk score for a single project snapshot.

    Returns a dict matching RiskScoreOutput schema.
    """
    try:
        snapshot = req.dict()
        history = snapshot.pop("history", None)
        result = predict_risk(snapshot, history=history)
        return result
    except Exception as e:
        logger.exception("predict_risk failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/what-if")
async def what_if_endpoint(req: WhatIfRequest):
    """
    Run a counterfactual simulation.

    Returns dict matching apps/web/types/api.ts::CounterfactualResult.
    """
    try:
        result = simulate_counterfactual(
            project_id=req.project_id,
            perturbations=req.perturbations,
            target=req.target,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("simulate_counterfactual failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/actionable-inputs")
async def actionable_inputs():
    """Return the list of fields users can perturb in What-If."""
    return list_actionable_inputs()
