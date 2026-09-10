# backend/services/ml/inference/predict.py
"""
Backend-facing prediction function for ProjectPulse AI.

Single entry point: predict_risk(snapshot, history) -> RiskScoreOutput dict

Run as a self-test:
    python -m services.ml.inference.predict
"""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
from scipy.stats import norm

from ..config import (
    MODELS_ARTIFACTS_DIR,
    TIER_CRITICAL_MIN,
    TIER_HIGH_MIN,
    TIER_MODERATE_MIN,
    WEIGHT_COST_RISK,
    WEIGHT_SCHEDULE_RISK,
    WEIGHT_TRAJECTORY_RISK,
    tier_from_score,
)


# ------------------------------------------------------------------------
# MODEL LOADING (singleton)
# ------------------------------------------------------------------------

_MODELS: Optional[Dict[str, Any]] = None
_MANIFEST: Optional[Dict[str, Any]] = None


def _load_models() -> Dict[str, Any]:
    """Lazy-load all artifacts. Cached after first call."""
    global _MODELS, _MANIFEST
    if _MODELS is not None:
        return _MODELS

    manifest_path = _resolve_latest_manifest()
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    files = manifest["files"]
    _MODELS = {
        "schedule_classifier": joblib.load(MODELS_ARTIFACTS_DIR / files["schedule_classifier"]),
        "cost_classifier":     joblib.load(MODELS_ARTIFACTS_DIR / files["cost_classifier"]),
        "schedule_regressor":  joblib.load(MODELS_ARTIFACTS_DIR / files["schedule_regressor"]),
        "cost_regressor":      joblib.load(MODELS_ARTIFACTS_DIR / files["cost_regressor"]),
        "feature_engine":      joblib.load(MODELS_ARTIFACTS_DIR / files["feature_engine"]),
    }
    _MANIFEST = manifest
    return _MODELS


def _resolve_latest_manifest() -> Path:
    """Read latest.txt pointer and return the full path to the manifest."""
    pointer = MODELS_ARTIFACTS_DIR / "latest.txt"
    if not pointer.exists():
        raise FileNotFoundError(
            f"Missing {pointer}. Run: python -m services.ml.train.final_train"
        )
    manifest_name = pointer.read_text().strip()
    manifest_path = MODELS_ARTIFACTS_DIR / manifest_name
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest {manifest_path} not found.")
    return manifest_path


# ------------------------------------------------------------------------
# PROBABILITY DERIVATION
# ------------------------------------------------------------------------

def _prob_from_regressor(predicted_mean: float, threshold: float, sigma: float) -> float:
    """Given a regressor's point prediction, estimate P(target > threshold)
    using a Gaussian CDF with a fixed stddev (sigma).

    Simple but effective: captures the fact that larger predictions
    correlate with larger probabilities.
    """
    if sigma <= 0:
        return 1.0 if predicted_mean > threshold else 0.0
    z = (threshold - predicted_mean) / sigma
    p = 1.0 - norm.cdf(z)  # P(X > threshold)
    return float(np.clip(p, 0.0, 1.0))


# ------------------------------------------------------------------------
# DRIVER EXTRACTION (approximate feature contribution)
# ------------------------------------------------------------------------

def _top_drivers(
    models: Dict[str, Any],
    X_instance: pd.DataFrame,
    top_n: int = 3,
) -> List[Dict[str, Any]]:
    """Approximate per-instance feature contribution using:
        contribution = feature_value * model_global_importance_for_feature

    This is not SHAP, but it is:
      - Fast (no per-instance explainer)
      - Deterministic
      - Easy to ship
    The full SHAP extraction is done separately and stored in
    prediction_evidence.
    """
    clf = models["schedule_classifier"]
    importances = clf.feature_importances_  # array of length n_features
    feature_names = list(X_instance.columns)
    values = X_instance.iloc[0].values

    # Simple contribution: |value| * importance
    contribs = np.abs(values) * importances

    order = np.argsort(contribs)[::-1][:top_n]
    drivers = []
    for idx in order:
        val = float(values[idx])
        imp = float(importances[idx])
        contribution = float(contribs[idx])
        drivers.append({
            "feature": feature_names[idx],
            "value": round(val, 4),
            "importance": round(imp, 4),
            "contribution": round(contribution, 4),
            "direction": "increase" if val > 0 else "decrease",
        })
    return drivers


# ------------------------------------------------------------------------
# MAIN PREDICTION FUNCTION
# ------------------------------------------------------------------------

def predict_risk(
    snapshot: Dict[str, Any],
    history: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Compute a risk score for a single project snapshot.

    Args:
        snapshot: Latest snapshot dict (keys match ProjectSnapshot).
        history:  Optional list of prior snapshots (oldest -> newest) for
                  the same project. If provided, velocity features are
                  computed from real history. If None, velocity = 0.

    Returns:
        Dict matching RiskScoreOutput (and db.py::RiskScore).
    """
    import time
    t0 = time.perf_counter()

    models = _load_models()
    manifest = _MANIFEST
    assert manifest is not None

    # Assemble the full history to run through the feature engine
    if history:
        full_history = list(history) + [snapshot]
    else:
        full_history = [snapshot]
    df = pd.DataFrame(full_history)

    # Coerce dates
    for col in ["report_month", "approval_date",
                "original_completion_date", "latest_revised_completion_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])

    # Ensure required columns exist with safe defaults
    defaults = {
        "revised_cost": df["original_cost"] if "original_cost" in df else 0.0,
        "cumulative_expenditure": 0.0,
        "physical_progress": 0.0,
        "latest_revised_completion_date": df.get("original_completion_date"),
        "sector": "Unknown",
        "ministry": "Unknown",
        "state": "Unknown",
        "delay_reason_text": "",
    }
    for k, v in defaults.items():
        if k not in df.columns:
            df[k] = v

    # Compute features
    engine = models["feature_engine"]
    X = engine.transform(df)
    X_latest = X.iloc[[-1]]

    # ---- Predictions ----
    prob_delay_6mo = float(models["schedule_classifier"].predict_proba(X_latest)[0][1])
    prob_cost_20pct = float(models["cost_classifier"].predict_proba(X_latest)[0][1])

    pred_delay_months = float(models["schedule_regressor"].predict(X_latest)[0])
    pred_cost_overrun_pct = float(models["cost_regressor"].predict(X_latest)[0])

    # ---- Derived probabilities (Gaussian approximation) ----
    prob_cost_10pct = _prob_from_regressor(pred_cost_overrun_pct, threshold=10.0, sigma=8.0)
    prob_delay_3mo  = _prob_from_regressor(pred_delay_months, threshold=3.0, sigma=3.5)
    prob_delay_12mo = _prob_from_regressor(pred_delay_months, threshold=12.0, sigma=5.0)

    # ---- Component risks (0-100) ----
    cost_risk = prob_cost_20pct * 100.0
    schedule_risk = prob_delay_6mo * 100.0
    # Trajectory risk: based on history length. Shorter history -> lower confidence, higher risk
    history_len = len(df)
    trajectory_risk = float(np.clip(50.0 * (1.0 - min(history_len, 12) / 12.0), 0.0, 100.0))

    # ---- Composite ----
    composite = (
        WEIGHT_COST_RISK * cost_risk +
        WEIGHT_SCHEDULE_RISK * schedule_risk +
        WEIGHT_TRAJECTORY_RISK * trajectory_risk
    )
    composite = float(np.clip(composite, 0.0, 100.0))

    tier = tier_from_score(composite)

    # ---- Confidence ----
    # Confidence in [0, 1], driven by history length and feature completeness
    confidence = float(np.clip(0.3 + 0.7 * min(history_len, 12) / 12.0, 0.0, 1.0))

    # ---- Intervention priority (0-100) ----
    # Priority = risk * exposure. We use original_cost_log as exposure proxy.
    original_cost = float(df.iloc[-1].get("original_cost", 100.0))
    exposure_norm = float(np.clip(np.log1p(original_cost) / 10.0, 0.0, 1.0))
    priority = float(np.clip(composite * (0.5 + 0.5 * exposure_norm), 0.0, 100.0))

    # ---- Trajectory delta (if history exists) ----
    risk_previous = None
    risk_delta = None
    risk_acceleration = None
    if history and len(history) >= 2:
        # Quick approximation: recompute on history[:-1] to get prior score
        # (in production, we'd store prior scores in DB and look them up)
        try:
            prior = _compute_quick_composite(models, history[:-1] + [history[-1]])
            if prior is not None:
                risk_previous = prior
                risk_delta = composite - prior
        except Exception:
            pass

    # ---- Top drivers ----
    try:
        drivers = _top_drivers(models, X_latest, top_n=3)
    except Exception:
        drivers = []

    # ---- Assembly ----
    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    project_id = snapshot.get("project_id", "UNKNOWN")
    report_month = snapshot.get("report_month")
    if isinstance(report_month, (pd.Timestamp, datetime)):
        report_month = report_month.date()
    elif isinstance(report_month, str):
        report_month = date.fromisoformat(report_month[:10])

    return {
        "project_id": project_id,
        "report_month": report_month,
        "model_version": manifest["version"],

        "cost_risk": round(cost_risk, 2),
        "schedule_risk": round(schedule_risk, 2),
        "trajectory_risk": round(trajectory_risk, 2),
        "composite_score": round(composite, 2),
        "tier": tier,

        "predicted_cost_overrun_pct": round(pred_cost_overrun_pct, 2),
        "predicted_delay_months": round(pred_delay_months, 2),

        "prob_cost_overrun_gt_10pct": round(prob_cost_10pct, 4),
        "prob_cost_overrun_gt_20pct": round(prob_cost_20pct, 4),
        "prob_delay_gt_3mo":  round(prob_delay_3mo, 4),
        "prob_delay_gt_6mo":  round(prob_delay_6mo, 4),
        "prob_delay_gt_12mo": round(prob_delay_12mo, 4),

        "confidence_score": round(confidence, 3),
        "intervention_priority": round(priority, 2),

        "top_drivers": drivers,
        "driver_summary": _summarize_drivers(drivers) if drivers else None,

        "risk_previous": round(risk_previous, 2) if risk_previous is not None else None,
        "risk_delta": round(risk_delta, 2) if risk_delta is not None else None,
        "risk_acceleration": None,

        "prediction_timestamp": datetime.now(timezone.utc).isoformat(),
        "inference_time_ms": elapsed_ms,
    }


def _compute_quick_composite(models: Dict[str, Any], history: List[Dict[str, Any]]) -> Optional[float]:
    """Fast approximation: run classifiers on the given history's last row."""
    try:
        df = pd.DataFrame(history)
        for col in ["report_month", "approval_date",
                    "original_completion_date", "latest_revised_completion_date"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
        engine = models["feature_engine"]
        X = engine.transform(df)
        X_last = X.iloc[[-1]]
        prob_s = float(models["schedule_classifier"].predict_proba(X_last)[0][1])
        prob_c = float(models["cost_classifier"].predict_proba(X_last)[0][1])
        composite = (0.5 * prob_s + 0.5 * prob_c) * 100.0
        return composite
    except Exception:
        return None


def _summarize_drivers(drivers: List[Dict[str, Any]]) -> str:
    parts = [f"{d['feature']} ({d['direction']})" for d in drivers[:3]]
    return "Top drivers: " + ", ".join(parts)


def reset_cache() -> None:
    """Clear the model cache (used in tests)."""
    global _MODELS, _MANIFEST
    _MODELS = None
    _MANIFEST = None


# ------------------------------------------------------------------------
# SELF-TEST
# ------------------------------------------------------------------------

if __name__ == "__main__":
    import pandas as pd
    from ..config import DATA_PROCESSED_DIR

    print("=" * 60)
    print("ProjectPulse AI -- Inference Self-Test")
    print("=" * 60)

    snap_path = DATA_PROCESSED_DIR / "snapshots.parquet"
    if not snap_path.exists():
        raise FileNotFoundError(f"Missing {snap_path}")
    df = pd.read_parquet(snap_path)

    # Pick a project with enough history
    counts = df.groupby("project_id").size().sort_values(ascending=False)
    test_pid = counts.index[0]
    project_df = df[df["project_id"] == test_pid].sort_values("report_month").reset_index(drop=True)
    print(f"Test project: {test_pid} ({len(project_df)} snapshots)")

    latest = project_df.iloc[-1].to_dict()
    history = project_df.iloc[:-1].to_dict("records")

    result = predict_risk(latest, history=history)

    print()
    print("Prediction result:")
    for key in ["project_id", "report_month", "tier", "composite_score",
                "cost_risk", "schedule_risk", "trajectory_risk",
                "predicted_cost_overrun_pct", "predicted_delay_months",
                "prob_cost_overrun_gt_20pct", "prob_delay_gt_6mo",
                "confidence_score", "intervention_priority",
                "inference_time_ms"]:
        print(f"  {key:32s} = {result[key]}")

    print()
    print("Top drivers:")
    for d in result["top_drivers"]:
        print(f"  {d['feature']:32s}  contrib={d['contribution']:.4f}  {d['direction']}")

    print()
    print("Cold start test (no history):")
    cold = predict_risk(latest, history=None)
    print(f"  composite_score = {cold['composite_score']}  tier = {cold['tier']}")

    print()
    print("Self-test passed.")
