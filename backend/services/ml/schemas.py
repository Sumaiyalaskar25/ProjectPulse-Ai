# backend/services/ml/schemas.py
"""
Pydantic v2 schemas for the ProjectPulse AI ML pipeline.

These models mirror backend/services/api/models/db.py so that:
  - Data loaded from the DB is type-checked on ingestion
  - ML outputs are validated before writing to risk_scores
  - Backend can import these for consistency

Everything is Pydantic v2 syntax.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ========================================================================
# CONSTANTS
# ========================================================================

TIER_VALUES = ("Stable", "Moderate", "High", "Critical")
TierLiteral = Literal["Stable", "Moderate", "High", "Critical"]

EVIDENCE_DIRECTION_VALUES = ("positive", "negative")
DirectionLiteral = Literal["positive", "negative"]


# ========================================================================
# INPUT: PROJECT SNAPSHOT
# ========================================================================

class ProjectSnapshot(BaseModel):
    """One row from the project_snapshots table.

    This is the atomic input to the ML pipeline: the state of a single
    project at a single report_month.

    Field names match db.py's ProjectSnapshot class EXACTLY.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    # Identity
    project_id: str = Field(..., min_length=1, max_length=64)
    report_month: date

    # Core metrics from the snapshot
    revised_cost: Optional[float] = Field(None, ge=0.0)
    cumulative_expenditure: Optional[float] = Field(None, ge=0.0)
    physical_progress: Optional[float] = Field(None, ge=0.0, le=100.0)
    latest_revised_completion_date: Optional[date] = None
    project_status: Optional[str] = None
    delay_reason_text: Optional[str] = ""

    # Denormalized from projects table (loader adds these)
    original_cost: Optional[float] = Field(None, gt=0.0)
    approval_date: Optional[date] = None
    original_completion_date: Optional[date] = None
    sector: Optional[str] = None
    ministry: Optional[str] = None
    state: Optional[str] = None

    # Lineage
    snapshot_id: Optional[int] = None
    source_file: Optional[str] = None
    source_page: Optional[int] = None
    source_row: Optional[int] = None

    @field_validator("physical_progress")
    @classmethod
    def _progress_bounds(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < 0.0 or v > 100.0):
            raise ValueError(f"physical_progress must be in [0, 100], got {v}")
        return v

    @model_validator(mode="after")
    def _date_ordering(self) -> "ProjectSnapshot":
        if (
            self.approval_date is not None
            and self.original_completion_date is not None
            and self.original_completion_date <= self.approval_date
        ):
            raise ValueError(
                "original_completion_date must be after approval_date "
                f"({self.original_completion_date} <= {self.approval_date})"
            )
        return self


# ========================================================================
# INTERMEDIATE: FEATURE VECTOR
# ========================================================================

class FeatureVector(BaseModel):
    """A single feature vector for one (project_id, report_month).

    Features are stored as a flat Dict[str, float] to match the JSONB
    column in project_features.features.
    """

    model_config = ConfigDict(extra="forbid")

    project_id: str
    report_month: date
    feature_version: str = "v1"
    features: Dict[str, float]


# ========================================================================
# TRAINING LABELS
# ========================================================================

class PredictionTargets(BaseModel):
    """Leakage-free labels for one (project_id, report_month).

    These are what the model learns to predict.
    """

    model_config = ConfigDict(extra="forbid")

    project_id: str
    report_month: date

    # Continuous targets
    cost_overrun_pct: float = Field(..., description="(future_revised - original) / original * 100")
    schedule_overrun_months: float = Field(..., description="(future_completion - original_completion) in months")

    # Binary targets
    cost_binary_10pct: int = Field(..., ge=0, le=1)
    cost_binary_20pct: int = Field(..., ge=0, le=1)
    schedule_binary_3mo: int = Field(..., ge=0, le=1)
    schedule_binary_6mo: int = Field(..., ge=0, le=1)
    schedule_binary_12mo: int = Field(..., ge=0, le=1)

    # Censoring flag
    is_censored: bool = False


# ========================================================================
# OUTPUT: RISK SCORE (matches db.py RiskScore)
# ========================================================================

class RiskScoreOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    # Identity
    project_id: str
    report_month: date
    model_version: str = Field(..., min_length=1, max_length=32)

    # Component risks (0-100)
    cost_risk: float = Field(..., ge=0.0, le=100.0)
    schedule_risk: float = Field(..., ge=0.0, le=100.0)
    trajectory_risk: float = Field(..., ge=0.0, le=100.0)
    composite_score: float = Field(..., ge=0.0, le=100.0)

    # Tier -- matches db.py comment (capitalized)
    tier: TierLiteral

    # Forecasts
    predicted_cost_overrun_pct: float
    predicted_delay_months: float
    predicted_completion_date: Optional[date] = None

    # Probabilities (0-1)
    prob_cost_overrun_gt_10pct: float = Field(..., ge=0.0, le=1.0)
    prob_cost_overrun_gt_20pct: float = Field(..., ge=0.0, le=1.0)
    prob_delay_gt_3mo: float = Field(..., ge=0.0, le=1.0)
    prob_delay_gt_6mo: float = Field(..., ge=0.0, le=1.0)
    prob_delay_gt_12mo: float = Field(..., ge=0.0, le=1.0)

    # Confidence & priority
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    intervention_priority: float = Field(..., ge=0.0, le=100.0)

    # Drivers (JSONB)
    top_drivers: Optional[List[Dict[str, Any]]] = None
    driver_summary: Optional[str] = None

    # Trajectory
    risk_previous: Optional[float] = None
    risk_delta: Optional[float] = None
    risk_acceleration: Optional[float] = None

    # Timing
    prediction_timestamp: Optional[datetime] = None
    inference_time_ms: Optional[int] = None

    @model_validator(mode="after")
    def _tier_consistency(self) -> "RiskScoreOutput":
        """Verify tier matches composite_score boundaries."""
        score = self.composite_score
        expected_tier: str
        if score >= 75:
            expected_tier = "Critical"
        elif score >= 50:
            expected_tier = "High"
        elif score >= 25:
            expected_tier = "Moderate"
        else:
            expected_tier = "Stable"
        if self.tier != expected_tier:
            raise ValueError(
                f"tier '{self.tier}' inconsistent with composite_score "
                f"{score:.2f} (expected '{expected_tier}')"
            )
        return self


# ========================================================================
# OUTPUT: PREDICTION EVIDENCE (matches db.py PredictionEvidence)
# ========================================================================

class PredictionEvidenceOutput(BaseModel):
    """One row for the prediction_evidence table.

    Explains WHY a risk score was produced by listing the top contributors.
    """

    model_config = ConfigDict(extra="forbid")

    project_id: str
    report_month: date

    feature_name: str = Field(..., max_length=64)
    observed_value: Optional[float] = None
    reference_value: Optional[float] = None
    contribution: float
    direction: DirectionLiteral

    # Lineage
    source_snapshot_id: Optional[int] = None
    source_file: Optional[str] = None
    source_page: Optional[int] = None
    source_row: Optional[int] = None

    evidence_text: Optional[str] = None


# ========================================================================
# MODEL REGISTRY MANIFEST
# ========================================================================

class ModelManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    version: str
    timestamp: datetime
    model_type: str = "LightGBM"
    schema_version: str = "1.0.0"

    # Training config
    training_cutoff: date
    lookahead_months: int = 6
    feature_version: str = "v1"
    feature_columns: List[str]

    # Thresholds used during training
    cost_overrun_threshold_pct: float = 20.0
    schedule_overrun_threshold_months: int = 6

    # Data stats
    training_rows: int = Field(..., ge=0)
    training_projects: int = Field(..., ge=0)

    # Metrics (optional; filled after backtest)
    metrics: Optional[Dict[str, Any]] = None

    # Artifact file names (relative to models/artifacts/)
    files: Dict[str, str]


# ========================================================================
# SELF-TEST
# ========================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ProjectPulse AI -- ML Schemas Self-Test")
    print("=" * 60)

    # Test 1: Valid snapshot
    snap = ProjectSnapshot(
        project_id="PRJ00001",
        report_month=date(2024, 6, 1),
        revised_cost=650.0,
        cumulative_expenditure=400.0,
        physical_progress=55.0,
        approval_date=date(2022, 1, 1),
        original_completion_date=date(2024, 1, 1),
        latest_revised_completion_date=date(2024, 9, 1),
        sector="Roads",
        ministry="MoRTH",
        state="Maharashtra",
    )
    print(f"[OK] ProjectSnapshot created: {snap.project_id} @ {snap.report_month}")

    # Test 2: Invalid progress should fail
    try:
        ProjectSnapshot(
            project_id="PRJ00002",
            report_month=date(2024, 6, 1),
            physical_progress=150.0,
        )
        print("[FAIL] Should have rejected physical_progress=150")
    except Exception as e:
        print(f"[OK] Correctly rejected invalid progress: {type(e).__name__}")

    # Test 3: Date ordering must be enforced
    try:
        ProjectSnapshot(
            project_id="PRJ00003",
            report_month=date(2024, 6, 1),
            approval_date=date(2024, 1, 1),
            original_completion_date=date(2023, 1, 1),
        )
        print("[FAIL] Should have rejected completion <= approval")
    except Exception as e:
        print(f"[OK] Correctly rejected bad date ordering: {type(e).__name__}")

    # Test 4: Valid RiskScoreOutput
    score = RiskScoreOutput(
        project_id="PRJ00001",
        report_month=date(2024, 6, 1),
        model_version="lgbm_v1",
        cost_risk=72.0,
        schedule_risk=81.0,
        trajectory_risk=65.0,
        composite_score=77.5,
        tier="Critical",
        predicted_cost_overrun_pct=25.3,
        predicted_delay_months=8.5,
        prob_cost_overrun_gt_10pct=0.85,
        prob_cost_overrun_gt_20pct=0.72,
        prob_delay_gt_3mo=0.91,
        prob_delay_gt_6mo=0.81,
        prob_delay_gt_12mo=0.45,
        confidence_score=0.78,
        intervention_priority=88.0,
    )
    print(f"[OK] RiskScoreOutput created: composite={score.composite_score}, tier={score.tier}")

    # Test 5: Tier inconsistency must fail
    try:
        RiskScoreOutput(
            project_id="PRJ00001",
            report_month=date(2024, 6, 1),
            model_version="lgbm_v1",
            cost_risk=10.0,
            schedule_risk=10.0,
            trajectory_risk=10.0,
            composite_score=10.0,
            tier="Critical",
            predicted_cost_overrun_pct=0.0,
            predicted_delay_months=0.0,
            prob_cost_overrun_gt_10pct=0.1,
            prob_cost_overrun_gt_20pct=0.05,
            prob_delay_gt_3mo=0.1,
            prob_delay_gt_6mo=0.05,
            prob_delay_gt_12mo=0.02,
            confidence_score=0.5,
            intervention_priority=5.0,
        )
        print("[FAIL] Should have rejected tier/composite mismatch")
    except Exception as e:
        print(f"[OK] Correctly rejected tier mismatch: {type(e).__name__}")

    print()
    print("All schema tests passed.")
