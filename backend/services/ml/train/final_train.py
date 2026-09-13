# backend/services/ml/train/final_train.py
"""
Train production models for ProjectPulse AI.

Outputs (all saved to backend/models/artifacts/):
  schedule_classifier_<version>.joblib
  cost_classifier_<version>.joblib
  schedule_regressor_<version>.joblib
  cost_regressor_<version>.joblib
  feature_engine_<version>.joblib
  manifest_<version>.json

The cutoff date is computed from the data — the latest month that still
allows a full 6-month lookahead window.

Run:
    python -m services.ml.train.final_train
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd

from ..config import (
    DATA_PROCESSED_DIR,
    FEATURE_VERSION,
    LGBM_PARAMS,
    LOOKAHEAD_MONTHS,
    MODELS_ARTIFACTS_DIR,
    SCHEMA_VERSION,
    COST_OVERRUN_THRESHOLD_PCT,
    SCHEDULE_OVERRUN_THRESHOLD_MONTHS,
)
from ..features.engine import LeakageFreeFeatureEngine
from ..targets.builder import TargetBuilder


# ------------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------------

def _compute_cutoff(df: pd.DataFrame) -> pd.Timestamp:
    """Latest month that still allows a full lookahead window."""
    latest = pd.to_datetime(df["report_month"]).max()
    return (latest - pd.DateOffset(months=LOOKAHEAD_MONTHS)).normalize()


def _feature_hash(feature_cols: list[str]) -> str:
    return hashlib.md5(",".join(feature_cols).encode()).hexdigest()[:12]


def _version_from_timestamp() -> str:
    return f"lgbm_v1_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"


# ------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------

def train_final() -> dict:
    # 1. Load snapshots
    snap_path = DATA_PROCESSED_DIR / "snapshots.parquet"
    if not snap_path.exists():
        raise FileNotFoundError(f"Missing {snap_path}. Run generate_synthetic first.")
    snapshots = pd.read_parquet(snap_path)

    # 2. Compute cutoff
    cutoff = _compute_cutoff(snapshots)
    print(f"Training cutoff: {cutoff.date()}")
    print(f"Lookahead:      {LOOKAHEAD_MONTHS} months")

    train_snapshots = snapshots[snapshots["report_month"] <= cutoff].copy()
    print(f"Snapshots used: {len(train_snapshots):,} / {len(snapshots):,}")

    # 3. Build targets
    print("Building targets...")
    builder = TargetBuilder(lookahead_months=LOOKAHEAD_MONTHS)
    labels = builder.build(train_snapshots)
    labels_train = labels[~labels["is_censored"]].copy()
    print(f"Trainable labels: {len(labels_train):,}")

    # 4. Fit feature engine on TRAIN snapshots
    print("Fitting feature engine...")
    engine = LeakageFreeFeatureEngine()
    X = engine.fit_transform(train_snapshots)
    feature_cols = engine.feature_cols
    print(f"Feature matrix: {X.shape}")
    print(f"Feature hash:   {_feature_hash(feature_cols)}")

    # 5. Merge features + labels
    keys = train_snapshots[["project_id", "report_month"]].reset_index(drop=True)
    X_with_keys = pd.concat([keys, X.reset_index(drop=True)], axis=1)
    merged = X_with_keys.merge(labels_train, on=["project_id", "report_month"], how="inner")
    print(f"Merged shape:   {merged.shape}")

    if len(merged) < 100:
        raise RuntimeError(f"Too few training rows ({len(merged)}). Check cutoff/data.")

    X_train = merged[feature_cols]
    y_sched_cls = merged["schedule_binary_6mo"].astype(int)
    y_cost_cls = merged["cost_binary_20pct"].astype(int)
    y_sched_reg = merged["schedule_overrun_months"]
    y_cost_reg = merged["cost_overrun_pct"]

    # 6. Train 4 models
    print()
    print("Training 4 models...")

    clf_sched = lgb.LGBMClassifier(**LGBM_PARAMS, class_weight="balanced")
    clf_sched.fit(X_train, y_sched_cls)
    print("  [OK] schedule_classifier")

    clf_cost = lgb.LGBMClassifier(**LGBM_PARAMS, class_weight="balanced")
    clf_cost.fit(X_train, y_cost_cls)
    print("  [OK] cost_classifier")

    reg_sched = lgb.LGBMRegressor(**LGBM_PARAMS)
    reg_sched.fit(X_train, y_sched_reg)
    print("  [OK] schedule_regressor")

    reg_cost = lgb.LGBMRegressor(**LGBM_PARAMS)
    reg_cost.fit(X_train, y_cost_reg)
    print("  [OK] cost_regressor")

    # 7. Compute training-set sanity metrics
    print()
    print("Training set metrics:")
    from sklearn.metrics import f1_score, roc_auc_score, mean_absolute_error
    print(f"  schedule_classifier:  F1={f1_score(y_sched_cls, clf_sched.predict(X_train)):.3f}  "
          f"AUC={roc_auc_score(y_sched_cls, clf_sched.predict_proba(X_train)[:, 1]):.3f}")
    print(f"  cost_classifier:      F1={f1_score(y_cost_cls, clf_cost.predict(X_train)):.3f}  "
          f"AUC={roc_auc_score(y_cost_cls, clf_cost.predict_proba(X_train)[:, 1]):.3f}")
    print(f"  schedule_regressor:   MAE={mean_absolute_error(y_sched_reg, reg_sched.predict(X_train)):.2f}")
    print(f"  cost_regressor:       MAE={mean_absolute_error(y_cost_reg, reg_cost.predict(X_train)):.2f}")
    print("  (Note: these are TRAIN metrics, not test metrics)")

    # 8. Save artifacts
    version = _version_from_timestamp()
    MODELS_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    files = {
        "schedule_classifier": f"schedule_classifier_{version}.joblib",
        "cost_classifier":     f"cost_classifier_{version}.joblib",
        "schedule_regressor":  f"schedule_regressor_{version}.joblib",
        "cost_regressor":      f"cost_regressor_{version}.joblib",
        "feature_engine":      f"feature_engine_{version}.joblib",
    }

    joblib.dump(clf_sched,  MODELS_ARTIFACTS_DIR / files["schedule_classifier"])
    joblib.dump(clf_cost,   MODELS_ARTIFACTS_DIR / files["cost_classifier"])
    joblib.dump(reg_sched,  MODELS_ARTIFACTS_DIR / files["schedule_regressor"])
    joblib.dump(reg_cost,   MODELS_ARTIFACTS_DIR / files["cost_regressor"])
    joblib.dump(engine,     MODELS_ARTIFACTS_DIR / files["feature_engine"])

    print()
    print(f"Saved {len(files)} artifacts to {MODELS_ARTIFACTS_DIR}")

    # 9. Write manifest
    manifest = {
        "version": version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_type": "LightGBM",
        "schema_version": SCHEMA_VERSION,
        "feature_version": FEATURE_VERSION,
        "feature_hash": _feature_hash(feature_cols),
        "feature_columns": feature_cols,
        "training_cutoff": str(cutoff.date()),
        "lookahead_months": LOOKAHEAD_MONTHS,
        "cost_overrun_threshold_pct": COST_OVERRUN_THRESHOLD_PCT,
        "schedule_overrun_threshold_months": SCHEDULE_OVERRUN_THRESHOLD_MONTHS,
        "training_rows": int(len(merged)),
        "training_projects": int(merged["project_id"].nunique()),
        "files": files,
    }

    manifest_path = MODELS_ARTIFACTS_DIR / f"manifest_{version}.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    # 10. Update "latest" symlink (on Windows, use a text pointer instead)
    latest_pointer = MODELS_ARTIFACTS_DIR / "latest.txt"
    latest_pointer.write_text(manifest_path.name)
    print(f"Wrote manifest: {manifest_path.name}")
    print(f"Updated pointer: {latest_pointer.name}")

    # 11. Human-readable summary
    print()
    print("=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"Version:           {version}")
    print(f"Cutoff:            {cutoff.date()}")
    print(f"Training rows:     {manifest['training_rows']:,}")
    print(f"Training projects: {manifest['training_projects']}")
    print(f"Features:          {len(feature_cols)}")
    print(f"Artifacts:         {len(files)} joblib files")
    print(f"Manifest:          {manifest_path.name}")
    print()
    print(f"Next: run predictions via services.ml.inference.predict")

    return manifest


# ------------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("ProjectPulse AI -- Final Model Training")
    print("=" * 60)
    print()
    train_final()
