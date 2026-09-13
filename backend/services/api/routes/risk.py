# services/api/routes/risk.py
"""
ML risk prediction routes.

Calls services.ml.inference.predict.predict_risk() offloaded to worker thread.
Returns 503 if model artifacts are not loaded/ready.
"""

from typing import Any, Dict, List, Optional
import anyio
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ...ml.inference.predict import (
    predict_risk,
    check_model_readiness,
    ModelUnavailableException,
)
from ...ml.inference.counterfactual import (
    simulate_counterfactual,
    list_actionable_inputs,
)
from ..core.errors import ModelUnavailableError, ValidationError
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

@router.get("/readiness")
async def model_readiness():
    """Check whether ML prediction models and artifacts are ready to serve traffic."""
    readiness = check_model_readiness()
    return {
        "status": "ready" if readiness.get("ready") else "unavailable",
        **readiness
    }


@router.post("/predict")
async def predict_endpoint(req: ProjectSnapshotIn):
    """
    Predict risk score for a single project snapshot.
    Offloaded to a worker thread to prevent event loop blocking.
    """
    try:
        snapshot = req.model_dump() if hasattr(req, "model_dump") else req.dict()
        history = snapshot.pop("history", None)
        result = await anyio.to_thread.run_sync(predict_risk, snapshot, history)
        return result
    except ModelUnavailableException as e:
        logger.warning(f"Prediction requested but model is unavailable: {e}")
        raise ModelUnavailableError(str(e))
    except ValueError as e:
        raise ValidationError(str(e))
    except Exception as e:
        logger.exception("predict_risk failed unexpectedly")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Risk prediction processing encountered an internal error."
        )


@router.post("/what-if")
async def what_if_endpoint(req: WhatIfRequest):
    """
    Run a counterfactual simulation.
    Offloaded to worker thread.
    """
    try:
        def _run_cf():
            return simulate_counterfactual(
                project_id=req.project_id,
                perturbations=req.perturbations,
                target=req.target,
            )
        result = await anyio.to_thread.run_sync(_run_cf)
        return result
    except ModelUnavailableException as e:
        logger.warning(f"What-if requested but model is unavailable: {e}")
        raise ModelUnavailableError(str(e))
    except ValueError as e:
        raise ValidationError(str(e))
    except Exception as e:
        logger.exception("simulate_counterfactual failed unexpectedly")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Counterfactual simulation encountered an internal error."
        )


@router.get("/actionable-inputs")
async def actionable_inputs():
    """Return the list of fields users can perturb in What-If."""
    return list_actionable_inputs()
