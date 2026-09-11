# backend/services/ml/train/backtest.py
"""
Rolling-origin backtest for ProjectPulse AI.

Splits data chronologically into 4 folds:
  Fold 1: train on months[0:origin], test on months[origin:origin+fold_size]
  Fold 2: train on months[0:origin+fold], test on next fold_size
  ... and so on.

For each fold:
  - Fit the feature engine on TRAIN ONLY
  - Fit both models on TRAIN
  - Evaluate on TEST

Reports F1, ROC-AUC, PR-AUC for both baseline (LogReg) and champion (LGBM).

Run:
    python -m services.ml.train.backtest
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import lightgbm as lgb

from ..config import (
    DATA_PROCESSED_DIR,
    LGBM_PARAMS,
    LOOKAHEAD_MONTHS,
    ROLLING_FOLDS,
    ROLLING_ORIGIN_MONTHS,
)
from ..features.engine import LeakageFreeFeatureEngine
from ..targets.builder import TargetBuilder


# ------------------------------------------------------------------------
# CONSTANTS
# ------------------------------------------------------------------------

TARGET_BINARY_SCHEDULE = "schedule_binary_6mo"
TARGET_BINARY_COST = "cost_binary_20pct"


# ------------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------------

def _load_and_prepare() -> pd.DataFrame:
    """Load snapshots, compute features, attach labels, drop censored."""
    snap_path = DATA_PROCESSED_DIR / "snapshots.parquet"
    if not snap_path.exists():
        raise FileNotFoundError(f"Missing {snap_path}. Run generate_synthetic first.")

    df = pd.read_parquet(snap_path)

    # Labels
    builder = TargetBuilder(lookahead_months=LOOKAHEAD_MONTHS)
    labels = builder.build(df)
    labels = labels[~labels["is_censored"]].copy()

    # We'll compute features inside each fold (to fit on train only).
    # Here we just return snapshots + labels merged by keys.
    return df, labels


def _fold_boundaries(months: np.ndarray) -> List[tuple]:
    """Return list of (train_end_idx, test_start_idx, test_end_idx) tuples."""
    n = len(months)
    fold_size = max(1, (n - ROLLING_ORIGIN_MONTHS - LOOKAHEAD_MONTHS) // ROLLING_FOLDS)
    folds = []
    for k in range(ROLLING_FOLDS):
        train_end = ROLLING_ORIGIN_MONTHS + k * fold_size
        if train_end + fold_size > n:
            break
        test_start = train_end
        test_end = min(train_end + fold_size, n)
        folds.append((train_end, test_start, test_end))
    return folds


def _evaluate(model, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
    """Compute all classification metrics."""
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # Top-K precision: what fraction of the top 20% riskiest projects truly overrun?
    k = max(1, int(0.2 * len(y_test)))
    top_k_idx = np.argsort(y_proba)[-k:]
    top_k_precision = float(y_test.iloc[top_k_idx].mean())

    return {
        "f1": f1_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, y_proba),
        "pr_auc": average_precision_score(y_test, y_proba),
        "topk_precision": top_k_precision,
        "n_test": len(y_test),
        "n_pos": int(y_test.sum()),
    }


# ------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------

def run_backtest() -> Dict:
    df_snapshots, labels = _load_and_prepare()
    months = np.array(sorted(df_snapshots["report_month"].unique()))
    folds = _fold_boundaries(months)

    print(f"Total months in data: {len(months)}")
    print(f"Folds: {len(folds)}")
    print()

    results: List[Dict] = []

    for fold_idx, (train_end_i, test_start_i, test_end_i) in enumerate(folds, start=1):
        train_end = pd.Timestamp(months[train_end_i - 1])
        test_start = pd.Timestamp(months[test_start_i])
        test_end = pd.Timestamp(months[test_end_i - 1])
        print(f"=== Fold {fold_idx} ===")
        print(f"  Train <= {train_end.date()}")
        print(f"  Test  {test_start.date()}  to  {test_end.date()}")

        # Split snapshots
        train_snaps = df_snapshots[df_snapshots["report_month"] <= train_end].copy()
        test_snaps = df_snapshots[
            (df_snapshots["report_month"] >= test_start) &
            (df_snapshots["report_month"] <= test_end)
        ].copy()

        # Fit feature engine on TRAIN only, transform both
        engine = LeakageFreeFeatureEngine()
        X_train_feat = engine.fit_transform(train_snaps)
        X_test_feat = engine.transform(test_snaps)

        # Attach keys so we can merge with labels
        train_keys = train_snaps[["project_id", "report_month"]].reset_index(drop=True)
        test_keys = test_snaps[["project_id", "report_month"]].reset_index(drop=True)
        X_train_feat = pd.concat([train_keys, X_train_feat.reset_index(drop=True)], axis=1)
        X_test_feat = pd.concat([test_keys, X_test_feat.reset_index(drop=True)], axis=1)

        # Merge with labels
        train_df = X_train_feat.merge(labels, on=["project_id", "report_month"], how="inner")
        test_df = X_test_feat.merge(labels, on=["project_id", "report_month"], how="inner")

        if len(train_df) < 100 or len(test_df) < 30:
            print(f"  SKIP: insufficient data (train={len(train_df)}, test={len(test_df)})")
            print()
            continue

        feature_cols = engine.feature_cols
        X_tr = train_df[feature_cols]
        X_te = test_df[feature_cols]

        # ---- Schedule target: 6-month delay classifier ----
        y_tr_s = train_df[TARGET_BINARY_SCHEDULE].astype(int)
        y_te_s = test_df[TARGET_BINARY_SCHEDULE].astype(int)

        # Baseline: Logistic Regression on scaled features
        baseline = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")),
        ])
        baseline.fit(X_tr, y_tr_s)
        m_baseline = _evaluate(baseline, X_te, y_te_s)

        # Champion: LightGBM
        champion = lgb.LGBMClassifier(**LGBM_PARAMS, class_weight="balanced")
        champion.fit(X_tr, y_tr_s)
        m_lgbm = _evaluate(champion, X_te, y_te_s)

        print(f"  Baseline (LogReg): F1={m_baseline['f1']:.3f}  AUC={m_baseline['roc_auc']:.3f}  "
              f"PR-AUC={m_baseline['pr_auc']:.3f}  TopK-P={m_baseline['topk_precision']:.3f}")
        print(f"  Champion (LGBM):   F1={m_lgbm['f1']:.3f}  AUC={m_lgbm['roc_auc']:.3f}  "
              f"PR-AUC={m_lgbm['pr_auc']:.3f}  TopK-P={m_lgbm['topk_precision']:.3f}")
        print()

        results.append({
            "fold": fold_idx,
            "n_train": len(train_df),
            "n_test": len(test_df),
            "baseline": m_baseline,
            "lgbm": m_lgbm,
        })

    # ---- Aggregate ----
    print("=" * 60)
    print("AGGREGATE RESULTS (schedule_binary_6mo)")
    print("=" * 60)
    if not results:
        print("No folds completed successfully.")
        return {}

    for name in ["baseline", "lgbm"]:
        f1s = [r[name]["f1"] for r in results]
        aucs = [r[name]["roc_auc"] for r in results]
        print(f"  {name:10s}  F1 = {np.mean(f1s):.3f} +/- {np.std(f1s):.3f}  "
              f"ROC-AUC = {np.mean(aucs):.3f} +/- {np.std(aucs):.3f}")

    baseline_f1 = np.mean([r["baseline"]["f1"] for r in results])
    lgbm_f1 = np.mean([r["lgbm"]["f1"] for r in results])
    improvement = ((lgbm_f1 - baseline_f1) / max(baseline_f1, 1e-6)) * 100
    print()
    print(f"  LGBM vs Baseline F1 improvement: {improvement:+.1f}%")

    return {"folds": results}


# ------------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("ProjectPulse AI -- Rolling-Origin Backtest")
    print("=" * 60)
    print()
    run_backtest()
