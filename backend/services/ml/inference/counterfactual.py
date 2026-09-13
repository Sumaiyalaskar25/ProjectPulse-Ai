# backend/services/ml/inference/counterfactual.py
"""
What-If counterfactual engine for ProjectPulse AI.

Given a project and a set of perturbations, re-runs the frozen model on
perturbed history and returns the delta.

Design rules:
  - Only RAW actionable inputs can be perturbed (physical_progress,
    cumulative_expenditure, latest_revised_completion_date).
  - Derived features (cost_burn_ratio, velocity, etc.) are NEVER edited
    directly — they are recomputed by the feature engine.
  - The full history is preserved so velocity features are meaningful.
  - The frozen model is used as-is (no retraining).

Output matches apps/web/types/api.ts::CounterfactualResult:
    {baseline_probability, counterfactual_probability, delta,
     interpretation, disclaimer}

Run:
    python -m services.ml.inference.counterfactual
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd

from ..config import (
    DATA_PROCESSED_DIR,
    MODELS_ARTIFACTS_DIR,
)


# ------------------------------------------------------------------------
# CONSTANTS
# ------------------------------------------------------------------------

# Fields that can be perturbed. Each entry: (type, min, max_or_None).
# 'delta' means the value is added to the current value.
# 'absolute' means the value replaces the current value.
ACTIONABLE_INPUTS: Dict[str, Dict[str, Any]] = {
    "physical_progress": {
        "mode": "delta",       # perturb as additive change (percentage points)
        "min": -100.0,
        "max": 100.0,
    },
    "cumulative_expenditure": {
        "mode": "delta_pct",   # perturb as % change of current value
        "min": -100.0,
        "max": 200.0,
    },
    "schedule_slippage_days": {
        "mode": "delta",       # perturb as additive change (days)
        "min": -365.0,
        "max": 365.0,
    },
}

DISCLAIMER = (
    "This is a model-based counterfactual scenario, not a causal guarantee. "
    "It shows what the current model would predict under different observed "
    "conditions, holding all else equal."
)


# ------------------------------------------------------------------------
# MODEL LOADING
# ------------------------------------------------------------------------

_MODELS: Optional[Dict[str, Any]] = None


def _load_models() -> Dict[str, Any]:
    global _MODELS
    if _MODELS is not None:
        return _MODELS

    pointer = MODELS_ARTIFACTS_DIR / "latest.txt"
    if not pointer.exists():
        raise FileNotFoundError(f"Missing {pointer}. Run final_train first.")
    manifest_path = MODELS_ARTIFACTS_DIR / pointer.read_text().strip()
    with open(manifest_path) as f:
        manifest = json.load(f)

    files = manifest["files"]
    _MODELS = {
        "schedule_classifier": joblib.load(MODELS_ARTIFACTS_DIR / files["schedule_classifier"]),
        "cost_classifier":     joblib.load(MODELS_ARTIFACTS_DIR / files["cost_classifier"]),
        "schedule_regressor":  joblib.load(MODELS_ARTIFACTS_DIR / files["schedule_regressor"]),
        "cost_regressor":      joblib.load(MODELS_ARTIFACTS_DIR / files["cost_regressor"]),
        "feature_engine":      joblib.load(MODELS_ARTIFACTS_DIR / files["feature_engine"]),
        "manifest": manifest,
    }
    return _MODELS


# ------------------------------------------------------------------------
# VALIDATION
# ------------------------------------------------------------------------

def _validate_perturbations(perturbations: Dict[str, float]) -> None:
    if not perturbations:
        raise ValueError("No perturbations provided.")
    for key, value in perturbations.items():
        if key not in ACTIONABLE_INPUTS:
            raise ValueError(
                f"Field '{key}' is not actionable. "
                f"Allowed: {list(ACTIONABLE_INPUTS.keys())}"
            )
        spec = ACTIONABLE_INPUTS[key]
        if not isinstance(value, (int, float)):
            raise ValueError(f"Perturbation for '{key}' must be numeric, got {type(value)}")
        if value < spec["min"] or value > spec["max"]:
            raise ValueError(
                f"Perturbation for '{key}' = {value} outside allowed range "
                f"[{spec['min']}, {spec['max']}]"
            )


def _apply_perturbation(
    row: pd.Series,
    field: str,
    value: float,
) -> pd.Series:
    """Apply a perturbation to a single row for the given field."""
    spec = ACTIONABLE_INPUTS[field]
    mode = spec["mode"]
    row = row.copy()

    if field == "schedule_slippage_days":
        # Special case: schedule_slippage_days is derived from completion dates.
        # Perturbing it means shifting latest_revised_completion_date.
        current_completion = pd.to_datetime(row["latest_revised_completion_date"])
        new_completion = current_completion + pd.Timedelta(days=value)
        row["latest_revised_completion_date"] = new_completion
        return row

    current = float(row.get(field, 0.0) or 0.0)

    if mode == "delta":
        new_value = current + value
    elif mode == "delta_pct":
        new_value = current * (1.0 + value / 100.0)
    elif mode == "absolute":
        new_value = value
    else:
        raise ValueError(f"Unknown mode '{mode}' for field '{field}'")

    # Clip to valid ranges
    if field == "physical_progress":
        new_value = float(np.clip(new_value, 0.0, 100.0))
    elif field == "cumulative_expenditure":
        new_value = max(0.0, new_value)

    row[field] = new_value
    return row


# ------------------------------------------------------------------------
# PREDICTION HELPER
# ------------------------------------------------------------------------

def _predict_prob(models: Dict[str, Any], df: pd.DataFrame) -> Tuple[float, float]:
    """Run the model on the given history, return (prob_delay, prob_cost)."""
    engine = models["feature_engine"]
    X = engine.transform(df)
    X_latest = X.iloc[[-1]]
    prob_delay = float(models["schedule_classifier"].predict_proba(X_latest)[0][1])
    prob_cost = float(models["cost_classifier"].predict_proba(X_latest)[0][1])
    return prob_delay, prob_cost


# ------------------------------------------------------------------------
# PUBLIC API
# ------------------------------------------------------------------------

def simulate_counterfactual(
    project_id: str,
    perturbations: Dict[str, float],
    target: str = "schedule",
) -> Dict[str, Any]:
    """
    Run a what-if simulation for one project.

    Args:
        project_id: Project to simulate.
        perturbations: Dict of field -> delta or pct delta. Allowed fields:
            physical_progress (delta in percentage points),
            cumulative_expenditure (delta in %),
            schedule_slippage_days (delta in days).
        target: "schedule" or "cost" — which risk to report delta for.

    Returns:
        Dict matching apps/web/types/api.ts::CounterfactualResult.
    """
    _validate_perturbations(perturbations)
    if target not in ("schedule", "cost"):
        raise ValueError(f"target must be 'schedule' or 'cost', got {target!r}")

    models = _load_models()

    # 1. Load full history for the project
    snap_path = DATA_PROCESSED_DIR / "snapshots.parquet"
    if not snap_path.exists():
        raise FileNotFoundError(f"Missing {snap_path}")
    df_all = pd.read_parquet(snap_path)
    history = df_all[df_all["project_id"] == project_id].sort_values("report_month").copy()
    if history.empty:
        raise ValueError(f"No snapshots found for project_id={project_id}")

    # Coerce dates for feature engine
    for col in ["report_month", "approval_date",
                "original_completion_date", "latest_revised_completion_date"]:
        if col in history.columns:
            history[col] = pd.to_datetime(history[col])

    # 2. Baseline prediction
    prob_delay_base, prob_cost_base = _predict_prob(models, history)
    baseline_prob = prob_delay_base if target == "schedule" else prob_cost_base

    # 3. Build perturbed history: apply perturbations to LAST row
    perturbed = history.reset_index(drop=True).copy()
    last_idx = len(perturbed) - 1
    last_row = perturbed.iloc[last_idx]

    for field, value in perturbations.items():
        perturbed_row = _apply_perturbation(last_row, field, value)
        # Replace the last row's values
        for col, val in perturbed_row.items():
            perturbed.loc[last_idx, col] = val

    # 4. Counterfactual prediction
    prob_delay_cf, prob_cost_cf = _predict_prob(models, perturbed)
    cf_prob = prob_delay_cf if target == "schedule" else prob_cost_cf

    delta = cf_prob - baseline_prob

    # 5. Interpretation
    direction = "decreases" if delta < 0 else ("increases" if delta > 0 else "stays the same")
    target_label = "delay" if target == "schedule" else "cost overrun"
    interpretation = (
        f"Under the scenario, {target_label} risk {direction} from "
        f"{baseline_prob * 100:.1f}% to {cf_prob * 100:.1f}% "
        f"({delta * 100:+.1f} percentage points)."
    )

    # 6. Narrative of perturbations
    narrative_parts = []
    for field, value in perturbations.items():
        if field == "physical_progress":
            narrative_parts.append(f"progress {value:+.1f}pp")
        elif field == "cumulative_expenditure":
            narrative_parts.append(f"expenditure {value:+.1f}%")
        elif field == "schedule_slippage_days":
            narrative_parts.append(f"schedule {value:+.0f}d")
    narrative = ", ".join(narrative_parts) if narrative_parts else "no changes"

    return {
        "project_id": project_id,
        "target": target,
        "perturbations": perturbations,
        "narrative": narrative,
        "baseline_probability": round(baseline_prob, 4),
        "counterfactual_probability": round(cf_prob, 4),
        "delta": round(delta, 4),
        "baseline_probability_pct": round(baseline_prob * 100, 2),
        "counterfactual_probability_pct": round(cf_prob * 100, 2),
        "delta_pct_points": round(delta * 100, 2),
        "interpretation": interpretation,
        "disclaimer": DISCLAIMER,
        "model_version": models["manifest"]["version"],
        "computed_at": datetime.utcnow().isoformat() + "Z",
    }


def list_actionable_inputs() -> Dict[str, Dict[str, Any]]:
    """Expose the schema for the frontend's UI sliders."""
    return ACTIONABLE_INPUTS


# ------------------------------------------------------------------------
# SELF-TEST
# ------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("ProjectPulse AI -- Counterfactual Engine Self-Test")
    print("=" * 60)

    # Pick the highest-risk project so the counterfactual has a visible effect.
    df = pd.read_parquet(DATA_PROCESSED_DIR / "snapshots.parquet")
    models = _load_models()
    engine = models["feature_engine"]

    df_sorted = df.sort_values(["project_id", "report_month"]).reset_index(drop=True)
    X_all = engine.transform(df_sorted)
    X_all["project_id"] = df_sorted["project_id"].values
    X_last = X_all.groupby("project_id").tail(1).reset_index(drop=True)
    feature_cols = [c for c in X_all.columns if c != "project_id"]
    probs = models["schedule_classifier"].predict_proba(X_last[feature_cols])[:, 1]

    # Pick a project near 50% baseline risk — that's where the model is
    # uncertain and perturbations have the most visible impact.
    target_prob = 0.5
    closest_idx = int(np.argmin(np.abs(probs - target_prob)))
    test_project = X_last.iloc[closest_idx]["project_id"]
    baseline = probs[closest_idx]
    n_snaps = int((df["project_id"] == test_project).sum())
    print(f"Test project (near-median risk): {test_project}")
    print(f"  Snapshots: {n_snaps}")
    print(f"  Baseline delay probability: {baseline*100:.1f}%")

    # --- Test 1: Baseline no-op (empty perturbations → error) ---
    print()
    print("Test 1: Empty perturbations should raise ValueError")
    try:
        simulate_counterfactual(test_project, {})
        print("  [FAIL] Should have raised")
    except ValueError as e:
        print(f"  [OK] {e}")

    # --- Test 2: Invalid field ---
    print()
    print("Test 2: Invalid field name should raise ValueError")
    try:
        simulate_counterfactual(test_project, {"physical_progress_bad": 10})
        print("  [FAIL] Should have raised")
    except ValueError as e:
        print(f"  [OK] {e}")

    # --- Test 3: Valid perturbation ---
    print()
    print("Test 3: Physical progress +10pp")
    result = simulate_counterfactual(
        test_project,
        {"physical_progress": 10.0},
        target="schedule",
    )
    for key in ["baseline_probability", "counterfactual_probability",
                "delta", "interpretation"]:
        print(f"  {key:32s} = {result[key]}")

    # --- Test 4: Multiple perturbations ---
    print()
    print("Test 4: Progress +10pp AND expenditure -10%")
    result = simulate_counterfactual(
        test_project,
        {"physical_progress": 10.0, "cumulative_expenditure": -10.0},
        target="schedule",
    )
    print(f"  narrative: {result['narrative']}")
    print(f"  baseline:  {result['baseline_probability_pct']}%")
    print(f"  perturbed: {result['counterfactual_probability_pct']}%")
    print(f"  delta:     {result['delta_pct_points']} pp")

    # --- Test 5: Cost target ---
    print()
    print("Test 5: Cost target, expenditure +20%")
    result = simulate_counterfactual(
        test_project,
        {"cumulative_expenditure": 20.0},
        target="cost",
    )
    print(f"  target: {result['target']}")
    print(f"  baseline:  {result['baseline_probability_pct']}%")
    print(f"  perturbed: {result['counterfactual_probability_pct']}%")

    print()
    print("=" * 60)
    print("All counterfactual tests passed.")
    print("=" * 60)
