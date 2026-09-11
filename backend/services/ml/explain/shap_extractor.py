# backend/services/ml/explain/shap_extractor.py
"""
Batch SHAP extraction for ProjectPulse AI.

For each project's latest snapshot, computes SHAP values using
shap.TreeExplainer on the schedule classifier. Extracts the top-5
drivers and writes them to:

    backend/data/features/project_drivers.parquet

Schema:
    project_id, report_month, rank, feature, contribution, value, direction

Run:
    python -m services.ml.explain.shap_extractor
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap

from ..config import (
    DATA_FEATURES_DIR,
    DATA_PROCESSED_DIR,
    MODELS_ARTIFACTS_DIR,
)


# ------------------------------------------------------------------------
# LOADING
# ------------------------------------------------------------------------

def _load_manifest() -> dict:
    pointer = MODELS_ARTIFACTS_DIR / "latest.txt"
    if not pointer.exists():
        raise FileNotFoundError(f"Missing {pointer}. Run final_train first.")
    manifest_path = MODELS_ARTIFACTS_DIR / pointer.read_text().strip()
    with open(manifest_path, "r") as f:
        return json.load(f)


def _load_models(manifest: dict) -> dict:
    files = manifest["files"]
    return {
        "schedule_classifier": joblib.load(MODELS_ARTIFACTS_DIR / files["schedule_classifier"]),
        "feature_engine": joblib.load(MODELS_ARTIFACTS_DIR / files["feature_engine"]),
    }


# ------------------------------------------------------------------------
# SHAP EXTRACTION
# ------------------------------------------------------------------------

def _latest_snapshot_per_project(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["project_id", "report_month"])
    return df.groupby("project_id", as_index=False).tail(1).reset_index(drop=True)


def _extract_shap(
    classifier,
    X: pd.DataFrame,
    top_n: int = 5,
) -> np.ndarray:
    """Compute SHAP values for the classifier on X.

    For LightGBM classifiers, shap.TreeExplainer returns either:
      - a 2D array (n_rows, n_features) for binary classification
      - a list of 2 arrays (one per class) in older shap versions
    We normalize to a 2D array of shape (n_rows, n_features) for class 1.
    """
    explainer = shap.TreeExplainer(classifier)
    raw = explainer.shap_values(X)

    if isinstance(raw, list):
        # List of [neg_class_array, pos_class_array]
        return np.asarray(raw[1])
    arr = np.asarray(raw)
    if arr.ndim == 3:
        # (n_rows, n_features, n_classes) -> pick class 1
        return arr[:, :, 1]
    return arr  # already (n_rows, n_features)


def extract_all_drivers() -> pd.DataFrame:
    # 1. Load manifest + models
    manifest = _load_manifest()
    print(f"Model version: {manifest['version']}")
    models = _load_models(manifest)
    classifier = models["schedule_classifier"]
    engine = models["feature_engine"]

    # 2. Load snapshots
    snap_path = DATA_PROCESSED_DIR / "snapshots.parquet"
    if not snap_path.exists():
        raise FileNotFoundError(f"Missing {snap_path}")
    df = pd.read_parquet(snap_path)
    print(f"Loaded {len(df):,} snapshots")

    # 3. Take latest snapshot per project
    latest = _latest_snapshot_per_project(df)
    print(f"Latest snapshots: {len(latest)} (one per project)")

    # 4. Compute features on the FULL history for accurate velocity
    #    (we need history for velocity, but we only keep the last row per project)
    print("Computing features (using full history)...")
    # Group by project, keep full history for feature calculation
    df_sorted = df.sort_values(["project_id", "report_month"]).reset_index(drop=True)
    X_all = engine.transform(df_sorted)
    X_all["project_id"] = df_sorted["project_id"].values
    X_all["report_month"] = df_sorted["report_month"].values

    # Keep only the latest row per project
    X_latest = X_all.groupby("project_id", as_index=False).tail(1).reset_index(drop=True)
    feature_cols = [c for c in X_all.columns if c not in ("project_id", "report_month")]
    X_features = X_latest[feature_cols]
    print(f"Feature matrix (latest per project): {X_features.shape}")

    # 5. Compute SHAP values
    print("Computing SHAP values...")
    shap_values = _extract_shap(classifier, X_features)
    print(f"SHAP shape: {shap_values.shape}")

    # 6. Extract top-N drivers per project
    print(f"Extracting top-{5} drivers per project...")
    rows = []
    for i, project_id in enumerate(X_latest["project_id"].values):
        contribs = shap_values[i]
        values = X_features.iloc[i].values
        order = np.argsort(np.abs(contribs))[::-1][:5]
        for rank, idx in enumerate(order, start=1):
            contrib = float(contribs[idx])
            rows.append({
                "project_id": project_id,
                "report_month": X_latest.iloc[i]["report_month"],
                "rank": rank,
                "feature": feature_cols[idx],
                "contribution": round(contrib, 6),
                "value": round(float(values[idx]), 6),
                "direction": "increase" if contrib > 0 else "decrease",
            })

    drivers = pd.DataFrame(rows)
    print(f"Total driver rows: {len(drivers):,}")
    return drivers


# ------------------------------------------------------------------------
# RUN
# ------------------------------------------------------------------------

def main() -> None:
    DATA_FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_FEATURES_DIR / "project_drivers.parquet"

    print("=" * 60)
    print("ProjectPulse AI -- SHAP Driver Extraction")
    print("=" * 60)
    print()

    drivers = extract_all_drivers()
    drivers.to_parquet(out_path, index=False)

    print()
    print(f"Saved drivers to {out_path}")
    print(f"File size: {out_path.stat().st_size / 1024:.1f} KB")
    print()
    print("Sample (first 10 driver rows):")
    print(drivers.head(10).to_string(index=False))
    print()
    print("Feature frequency (top 10):")
    freq = drivers["feature"].value_counts().head(10)
    for feature, count in freq.items():
        print(f"  {feature:32s}  {count}")
    print()
    print("=" * 60)
    print("SHAP EXTRACTION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
