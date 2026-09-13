# backend/services/ml/experiments/cuf_ablation.py
"""
CUF Ablation Experiment — ProjectPulse AI.

Compares CUF-only features vs CUF + augmented features through the same
rolling-origin protocol. Answers the PS question: "What fields should be
added to the CUF to improve early warning?"

Run:
    python -m services.ml.experiments.cuf_ablation
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Dict, List

import numpy as np
import pandas as pd
import lightgbm as lgb
import shap
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ..config import (
    DATA_PROCESSED_DIR,
    LGBM_PARAMS,
    LOOKAHEAD_MONTHS,
    MODELS_ARTIFACTS_DIR,
    ROLLING_FOLDS,
    ROLLING_ORIGIN_MONTHS,
)
from ..features.engine import LeakageFreeFeatureEngine
from ..targets.builder import TargetBuilder


# ------------------------------------------------------------------------
# FEATURE SETS
# ------------------------------------------------------------------------

# Fields currently in the CUF (Creative Utilization Fund / PAIMANA reporting).
# These are the fields a project snapshot already contains.
CUF_ONLY_FEATURES = [
    "original_cost_log",
    "months_since_approval",
    "time_elapsed_ratio",
    "physical_progress",
    "cumulative_expenditure",
    "expenditure_to_original",
    "schedule_slippage_days",
    "schedule_slippage_months",
    "cost_revision_pct",
]

# Augmented features — everything we engineered on top of CUF.
# The delta between CUF_ONLY_FEATURES and these is what we recommend adding.
AUGMENTED_FEATURES = CUF_ONLY_FEATURES + [
    "progress_velocity_3m",
    "expenditure_velocity_3m",
    "progress_acceleration_3m",
    "expenditure_acceleration_3m",
    "cost_burn_ratio",
    "schedule_revision_count",
    "sector_baseline_zscore",
    "history_length",
    "data_quality_score",
]


TARGET = "schedule_binary_6mo"


# ------------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------------

def _load_data():
    snap_path = DATA_PROCESSED_DIR / "snapshots.parquet"
    if not snap_path.exists():
        raise FileNotFoundError(f"Missing {snap_path}")

    df = pd.read_parquet(snap_path)
    labels = TargetBuilder(lookahead_months=LOOKAHEAD_MONTHS).build(df)
    labels = labels[~labels["is_censored"]].copy()
    return df, labels


def _evaluate(model, X_test, y_test) -> Dict[str, float]:
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    k = max(1, int(0.2 * len(y_test)))
    top_k_idx = np.argsort(y_proba)[-k:]
    return {
        "f1": f1_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, y_proba),
        "pr_auc": average_precision_score(y_test, y_proba),
        "topk_precision": float(y_test.iloc[top_k_idx].mean()),
        "n_test": int(len(y_test)),
    }


def _rolling_backtest_for_features(
    df_snapshots: pd.DataFrame,
    labels: pd.DataFrame,
    feature_set: List[str],
    model_builder,
    feature_cols_full: List[str],
) -> Dict:
    """Run rolling-origin backtest restricted to the given feature subset."""
    months = np.array(sorted(df_snapshots["report_month"].unique()))
    fold_size = max(1, (len(months) - ROLLING_ORIGIN_MONTHS - LOOKAHEAD_MONTHS) // ROLLING_FOLDS)

    fold_metrics = []

    for k in range(ROLLING_FOLDS):
        train_end_i = ROLLING_ORIGIN_MONTHS + k * fold_size
        if train_end_i + fold_size > len(months):
            break
        train_end = pd.Timestamp(months[train_end_i - 1])
        test_start = pd.Timestamp(months[train_end_i])
        test_end = pd.Timestamp(months[min(train_end_i + fold_size - 1, len(months) - 1)])

        train_snaps = df_snapshots[df_snapshots["report_month"] <= train_end]
        test_snaps = df_snapshots[
            (df_snapshots["report_month"] >= test_start) &
            (df_snapshots["report_month"] <= test_end)
        ]

        # Fit feature engine on train, transform both
        engine = LeakageFreeFeatureEngine()
        X_tr_full = engine.fit_transform(train_snaps)
        X_te_full = engine.transform(test_snaps)

        # Verify requested features are all present
        missing = [c for c in feature_set if c not in X_tr_full.columns]
        if missing:
            # Features that are one-hot (e.g., sector_Roads) may not
            # appear if a category is unseen. Skip them silently.
            available = [c for c in feature_set if c in X_tr_full.columns]
        else:
            available = feature_set

        # Attach keys
        tr_keys = train_snaps[["project_id", "report_month"]].reset_index(drop=True)
        te_keys = test_snaps[["project_id", "report_month"]].reset_index(drop=True)
        X_tr_full = pd.concat([tr_keys, X_tr_full.reset_index(drop=True)], axis=1)
        X_te_full = pd.concat([te_keys, X_te_full.reset_index(drop=True)], axis=1)

        train_df = X_tr_full.merge(labels, on=["project_id", "report_month"], how="inner")
        test_df = X_te_full.merge(labels, on=["project_id", "report_month"], how="inner")

        if len(train_df) < 100 or len(test_df) < 30:
            continue

        X_tr = train_df[available]
        X_te = test_df[available]
        y_tr = train_df[TARGET].astype(int)
        y_te = test_df[TARGET].astype(int)

        if y_tr.nunique() < 2 or y_te.nunique() < 2:
            continue

        model = model_builder()
        model.fit(X_tr, y_tr)
        fold_metrics.append(_evaluate(model, X_te, y_te))

    if not fold_metrics:
        return {"error": "no folds completed"}

    agg = {}
    for key in ["f1", "roc_auc", "pr_auc", "precision", "recall", "topk_precision"]:
        vals = [m[key] for m in fold_metrics]
        agg[f"{key}_mean"] = float(np.mean(vals))
        agg[f"{key}_std"] = float(np.std(vals))
    agg["n_folds"] = len(fold_metrics)
    return agg


# ------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------

def run_ablation() -> Dict:
    df_snapshots, labels = _load_data()
    print(f"Snapshots: {len(df_snapshots):,}")
    print(f"Trainable labels: {len(labels):,}")
    print(f"Target: {TARGET}")
    print()

    # Determine the full feature list by fitting the engine once
    probe_engine = LeakageFreeFeatureEngine()
    probe_engine.fit(df_snapshots)
    feature_cols_full = probe_engine.feature_cols

    # Augmented list must also include one-hot categoricals
    augmented_full = [c for c in feature_cols_full if c not in (
        "original_cost_log",  # keep only the ones we care about
    )]
    # Actually keep all — filter is done implicitly by feature_set
    def _unique_preserve_order(cols):
        seen = set()
        out = []
        for c in cols:
            if c not in seen:
                out.append(c)
                seen.add(c)
        return out

    augmented_set = _unique_preserve_order(
        [c for c in AUGMENTED_FEATURES if c in feature_cols_full] +
        [c for c in feature_cols_full if c.startswith(("sector_", "ministry_", "state_"))]
    )
    cuf_set = _unique_preserve_order(
        [c for c in CUF_ONLY_FEATURES if c in feature_cols_full] +
        [c for c in feature_cols_full if c.startswith(("sector_", "ministry_", "state_"))]
    )

    print(f"CUF-only feature count:  {len(cuf_set)}")
    print(f"Augmented feature count: {len(augmented_set)}")
    print(f"Additional features:     {len(augmented_set) - len(cuf_set)}")
    print()

    # LightGBM builder
    lgbm_builder = lambda: lgb.LGBMClassifier(**LGBM_PARAMS, class_weight="balanced")

    # ---- Experiment A: CUF only ----
    print("=" * 60)
    print("Experiment A: CUF-only features")
    print("=" * 60)
    res_cuf = _rolling_backtest_for_features(
        df_snapshots, labels, cuf_set, lgbm_builder, feature_cols_full,
    )
    if "error" in res_cuf:
        raise RuntimeError(f"Experiment A failed: {res_cuf['error']}")
    print(f"  F1:      {res_cuf['f1_mean']:.4f} ± {res_cuf['f1_std']:.4f}")
    print(f"  ROC-AUC: {res_cuf['roc_auc_mean']:.4f} ± {res_cuf['roc_auc_std']:.4f}")
    print(f"  PR-AUC:  {res_cuf['pr_auc_mean']:.4f} ± {res_cuf['pr_auc_std']:.4f}")
    print()

    # ---- Experiment B: Augmented ----
    print("=" * 60)
    print("Experiment B: CUF + augmented features")
    print("=" * 60)
    res_aug = _rolling_backtest_for_features(
        df_snapshots, labels, augmented_set, lgbm_builder, feature_cols_full,
    )
    if "error" in res_aug:
        raise RuntimeError(f"Experiment B failed: {res_aug['error']}")
    print(f"  F1:      {res_aug['f1_mean']:.4f} ± {res_aug['f1_std']:.4f}")
    print(f"  ROC-AUC: {res_aug['roc_auc_mean']:.4f} ± {res_aug['roc_auc_std']:.4f}")
    print(f"  PR-AUC:  {res_aug['pr_auc_mean']:.4f} ± {res_aug['pr_auc_std']:.4f}")
    print()

    # ---- Improvement ----
    f1_improvement = (res_aug["f1_mean"] - res_cuf["f1_mean"]) / max(res_cuf["f1_mean"], 1e-6) * 100
    auc_improvement = (res_aug["roc_auc_mean"] - res_cuf["roc_auc_mean"]) / max(res_cuf["roc_auc_mean"], 1e-6) * 100
    prauc_improvement = (res_aug["pr_auc_mean"] - res_cuf["pr_auc_mean"]) / max(res_cuf["pr_auc_mean"], 1e-6) * 100

    print("=" * 60)
    print("IMPROVEMENT (Augmented vs CUF-only)")
    print("=" * 60)
    print(f"  F1:      {f1_improvement:+.2f}%")
    print(f"  ROC-AUC: {auc_improvement:+.2f}%")
    print(f"  PR-AUC:  {prauc_improvement:+.2f}%")
    print()

    # ---- Rank new features by average |SHAP| ----
    print("Computing SHAP importance to rank recommended new fields...")
    # Fit engine + model on full data for ranking
    engine = LeakageFreeFeatureEngine()
    X_full = engine.fit_transform(df_snapshots)
    keys = df_snapshots[["project_id", "report_month"]].reset_index(drop=True)
    X_full = pd.concat([keys, X_full.reset_index(drop=True)], axis=1)
    merged = X_full.merge(labels, on=["project_id", "report_month"], how="inner")
    merged = merged.dropna(subset=[TARGET])

    X_train = merged[augmented_set]
    y_train = merged[TARGET].astype(int)

    model = lgb.LGBMClassifier(**LGBM_PARAMS, class_weight="balanced")
    model.fit(X_train, y_train)

    explainer = shap.TreeExplainer(model)
    shap_raw = explainer.shap_values(X_train.sample(min(1000, len(X_train)), random_state=42))
    if isinstance(shap_raw, list):
        shap_vals = np.asarray(shap_raw[1])
    elif np.asarray(shap_raw).ndim == 3:
        shap_vals = np.asarray(shap_raw)[:, :, 1]
    else:
        shap_vals = np.asarray(shap_raw)

    mean_abs_shap = np.mean(np.abs(shap_vals), axis=0)
    feature_importance = pd.DataFrame({
        "feature": augmented_set,
        "mean_abs_shap": mean_abs_shap,
    }).sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)

    # Only list features NOT in CUF-only, and exclude one-hot categoricals
    # (already present as raw fields in the CUF) and data-collection artifacts.
    cuf_set_no_cat = set(CUF_ONLY_FEATURES)
    EXCLUDED_PREFIXES = ("sector_", "ministry_", "state_")
    EXCLUDED_EXACT = {"history_length", "data_quality_score"}

    def _is_genuine_new_field(name: str) -> bool:
        if name in EXCLUDED_EXACT:
            return False
        if name.startswith(EXCLUDED_PREFIXES):
            return False
        if name in cuf_set_no_cat:
            return False
        return True

    new_features = feature_importance[
        feature_importance["feature"].apply(_is_genuine_new_field)
    ].copy()
    new_features["rank"] = range(1, len(new_features) + 1)

    print()
    print("=" * 60)
    print("RECOMMENDED NEW CUF FIELDS (ranked by mean |SHAP|)")
    print("=" * 60)
    for _, row in new_features.head(10).iterrows():
        print(f"  {int(row['rank']):2d}. {row['feature']:32s}  mean|SHAP| = {row['mean_abs_shap']:.4f}")
    print()

    # ---- Save results ----
    MODELS_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "lookahead_months": LOOKAHEAD_MONTHS,
        "target": TARGET,
        "cuf_only": {
            "n_features": len(cuf_set),
            "features": cuf_set,
            "metrics": res_cuf,
        },
        "augmented": {
            "n_features": len(augmented_set),
            "features": augmented_set,
            "metrics": res_aug,
        },
        "improvement": {
            "f1_pct": round(f1_improvement, 2),
            "roc_auc_pct": round(auc_improvement, 2),
            "pr_auc_pct": round(prauc_improvement, 2),
        },
        "recommended_new_fields": new_features.head(10).to_dict(orient="records"),
    }

    out_path = MODELS_ARTIFACTS_DIR / "cuf_ablation_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("=" * 60)
    print("SUMMARY FOR PITCH")
    print("=" * 60)
    print(f"Adding {len(augmented_set) - len(cuf_set)} new features to the CUF")
    print(f"improves F1 by {f1_improvement:+.2f}%, ROC-AUC by {auc_improvement:+.2f}%,")
    print(f"and PR-AUC by {prauc_improvement:+.2f}%.")
    print()
    print(f"Top 3 recommended CUF additions:")
    for _, row in new_features.head(3).iterrows():
        print(f"  - {row['feature']}")
    print()
    print(f"Saved to {out_path}")
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("ProjectPulse AI -- CUF Ablation Experiment")
    print("=" * 60)
    print()
    run_ablation()
