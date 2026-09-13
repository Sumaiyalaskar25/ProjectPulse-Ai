# backend/services/ml/scripts/pipeline_smoke_test.py
"""
End-to-end pipeline smoke test.

Verifies: snapshots -> targets -> features -> merged training set

Runs in ~30 seconds. Prints a diagnostic report so we know the model
will have reasonable data before we spend time training.

Run:
    python -m services.ml.scripts.pipeline_smoke_test
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ..config import DATA_PROCESSED_DIR, LOOKAHEAD_MONTHS
from ..features.engine import LeakageFreeFeatureEngine
from ..targets.builder import TargetBuilder


def _print_section(title: str) -> None:
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def main() -> None:
    snapshot_path = DATA_PROCESSED_DIR / "snapshots.parquet"
    if not snapshot_path.exists():
        raise FileNotFoundError(
            f"Missing {snapshot_path}. Run:\n"
            f"  python -m services.ml.scripts.generate_synthetic"
        )

    # ---------------------------------------------------------------
    # STEP 1: Load snapshots
    # ---------------------------------------------------------------
    _print_section("STEP 1: Load snapshots")
    df = pd.read_parquet(snapshot_path)
    print(f"Loaded {len(df):,} snapshots from {snapshot_path.name}")
    print(f"Projects: {df['project_id'].nunique()}")
    print(f"Date range: {df['report_month'].min().date()} to {df['report_month'].max().date()}")

    # ---------------------------------------------------------------
    # STEP 2: Build targets
    # ---------------------------------------------------------------
    _print_section("STEP 2: Build targets (leakage-free)")
    builder = TargetBuilder(lookahead_months=LOOKAHEAD_MONTHS)
    labels = builder.build(df)

    n_total = len(labels)
    n_trainable = (~labels["is_censored"]).sum()
    n_censored = labels["is_censored"].sum()
    print(f"Total label rows:     {n_total:,}")
    print(f"Trainable (uncensored): {n_trainable:,} ({n_trainable / n_total * 100:.1f}%)")
    print(f"Censored (dropped):     {n_censored:,} ({n_censored / n_total * 100:.1f}%)")

    trainable = labels[~labels["is_censored"]].copy()

    if len(trainable) == 0:
        raise RuntimeError("No trainable labels produced. Check lookahead horizon vs data range.")

    # Target distributions
    print()
    print("Continuous target stats (trainable rows):")
    print(f"  cost_overrun_pct:          mean={trainable['cost_overrun_pct'].mean():.2f}  "
          f"std={trainable['cost_overrun_pct'].std():.2f}  "
          f"min={trainable['cost_overrun_pct'].min():.2f}  "
          f"max={trainable['cost_overrun_pct'].max():.2f}")
    print(f"  schedule_overrun_months:   mean={trainable['schedule_overrun_months'].mean():.2f}  "
          f"std={trainable['schedule_overrun_months'].std():.2f}  "
          f"min={trainable['schedule_overrun_months'].min():.2f}  "
          f"max={trainable['schedule_overrun_months'].max():.2f}")

    print()
    print("Binary target class balance (trainable rows):")
    for col in ["cost_binary_10pct", "cost_binary_20pct",
                "schedule_binary_3mo", "schedule_binary_6mo",
                "schedule_binary_12mo"]:
        pos = int(trainable[col].sum())
        neg = int(len(trainable) - pos)
        pct = pos / len(trainable) * 100
        print(f"  {col:24s}: {pos:5d} positive / {neg:5d} negative ({pct:5.1f}%)")

    # ---------------------------------------------------------------
    # STEP 3: Compute features
    # ---------------------------------------------------------------
    _print_section("STEP 3: Compute features")
    engine = LeakageFreeFeatureEngine()
    X = engine.fit_transform(df)
    print(f"Feature matrix shape: {X.shape}")
    print(f"Feature columns: {len(engine.feature_cols)}")
    print(f"Any NaN: {X.isna().any().any()}")
    print(f"Any Inf: {np.isinf(X.values).any()}")

    # ---------------------------------------------------------------
    # STEP 4: Merge features + labels
    # ---------------------------------------------------------------
    _print_section("STEP 4: Merge features + labels")
    # Attach the row index from engine.transform (which sorts by project/month)
    features_df = df[["project_id", "report_month"]].copy()
    features_df = features_df.sort_values(["project_id", "report_month"]).reset_index(drop=True)
    features_df = pd.concat([features_df, X.reset_index(drop=True)], axis=1)

    merged = features_df.merge(
        trainable,
        on=["project_id", "report_month"],
        how="inner",
    )
    print(f"Merged shape: {merged.shape}")
    print(f"Rows: {len(merged):,}")
    print(f"Features: {len(engine.feature_cols)}")
    print(f"Label columns added: {[c for c in trainable.columns if c not in ('project_id', 'report_month')]}")

    # Sanity checks
    assert len(merged) == n_trainable, \
        f"Merged row count {len(merged)} != trainable label rows {n_trainable}"
    assert not merged[engine.feature_cols].isna().any().any(), "Merged features contain NaN"

    # ---------------------------------------------------------------
    # STEP 5: Sanity check for class balance (not 99/1)
    # ---------------------------------------------------------------
    _print_section("STEP 5: Trainability check")
    for col in ["cost_binary_20pct", "schedule_binary_6mo"]:
        pos_rate = merged[col].mean()
        if pos_rate < 0.02:
            print(f"WARNING: {col} has only {pos_rate * 100:.1f}% positives — model may struggle")
        elif pos_rate > 0.98:
            print(f"WARNING: {col} has {pos_rate * 100:.1f}% positives — near-constant")
        else:
            print(f"OK: {col} positive rate = {pos_rate * 100:.1f}%")

    # ---------------------------------------------------------------
    # STEP 6: Sample row
    # ---------------------------------------------------------------
    _print_section("STEP 6: Sample training row")
    sample = merged.iloc[0]
    print("Project / Month:", sample["project_id"], sample["report_month"].date())
    print()
    print("Key features:")
    for c in ["original_cost_log", "months_since_approval", "time_elapsed_ratio",
              "physical_progress", "cost_burn_ratio", "schedule_slippage_months"]:
        print(f"  {c:28s} = {sample[c]:.4f}")
    print()
    print("Targets:")
    for c in ["cost_overrun_pct", "schedule_overrun_months",
              "cost_binary_20pct", "schedule_binary_6mo"]:
        print(f"  {c:28s} = {sample[c]}")

    # ---------------------------------------------------------------
    # FINAL
    # ---------------------------------------------------------------
    _print_section("SMOKE TEST PASSED")
    print(f"Final training set: {merged.shape[0]:,} rows x {len(engine.feature_cols)} features")
    print("Ready to train models.")


if __name__ == "__main__":
    main()
