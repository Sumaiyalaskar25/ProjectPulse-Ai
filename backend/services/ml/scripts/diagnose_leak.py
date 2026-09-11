# backend/services/ml/scripts/diagnose_leak.py
"""
Diagnostic: does the synthetic data leak the future into present features?

If slippage_days at month T perfectly predicts delay at month T+6, the
generator is writing the eventual outcome into the current snapshot —
which makes the ML task trivially easy (and unrealistic).

A realistic early-warning task should have ROC-AUC in the 0.75-0.90 range,
NOT 0.99+.
"""

from __future__ import annotations

import pandas as pd
from sklearn.metrics import roc_auc_score

from ..config import DATA_PROCESSED_DIR


def main() -> None:
    snap_path = DATA_PROCESSED_DIR / "snapshots.parquet"
    if not snap_path.exists():
        raise FileNotFoundError(f"Missing {snap_path}")

    df = pd.read_parquet(snap_path)
    df = df.sort_values(["project_id", "report_month"]).reset_index(drop=True)

    # ---- Slippage days at each month ----
    df["slippage_days"] = (
        pd.to_datetime(df["latest_revised_completion_date"])
        - pd.to_datetime(df["original_completion_date"])
    ).dt.days

    # ---- Future slippage 6 months ahead ----
    df["future_slippage"] = df.groupby("project_id")["slippage_days"].shift(-6)

    mask = df["future_slippage"].notna()
    X = df.loc[mask, "slippage_days"].values
    y = (df.loc[mask, "future_slippage"] > 180).astype(int).values

    print("=" * 60)
    print("Leakage Diagnostic -- Synthetic Data")
    print("=" * 60)
    print()

    if len(set(y)) > 1:
        auc = roc_auc_score(y, X)
        print(f"[1] slippage_days ALONE -> future delay > 180d")
        print(f"    ROC-AUC: {auc:.4f}")
        print(f"    (Realistic: 0.75-0.90; Suspicious: >0.95)")
    else:
        print("[1] Not enough class variety for slippage test")

    print()

    # ---- Cost revision at each month ----
    df["cost_rev"] = (df["revised_cost"] - df["original_cost"]) / df["original_cost"]
    df["future_cost_rev"] = df.groupby("project_id")["cost_rev"].shift(-6)

    mask2 = df["future_cost_rev"].notna()
    X2 = df.loc[mask2, "cost_rev"].values
    y2 = (df.loc[mask2, "future_cost_rev"] > 0.20).astype(int).values

    if len(set(y2)) > 1:
        auc2 = roc_auc_score(y2, X2)
        print(f"[2] cost_revision ALONE -> future cost overrun > 20%")
        print(f"    ROC-AUC: {auc2:.4f}")
        print(f"    (Realistic: 0.70-0.88; Suspicious: >0.95)")
    else:
        print("[2] Not enough class variety for cost test")

    print()

    # ---- Physical progress at each month ----
    df["progress"] = df["physical_progress"]
    # For each row, does higher progress mean better future outcome?
    # Actually we're checking the reverse: does current progress predict future?
    df["future_delay_flag"] = (df["future_slippage"] > 180).astype("Int64")

    mask3 = df["future_delay_flag"].notna()
    X3 = df.loc[mask3, "progress"].values
    y3 = df.loc[mask3, "future_delay_flag"].astype(int).values

    if len(set(y3)) > 1:
        # Low progress should mean HIGH delay, so negate progress for AUC
        auc3 = roc_auc_score(y3, -X3)
        print(f"[3] physical_progress ALONE -> future delay > 180d")
        print(f"    ROC-AUC (negated): {auc3:.4f}")
        print(f"    (Realistic: 0.60-0.80; Suspicious: >0.90)")
    else:
        print("[3] Not enough class variety")

    print()
    print("=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    print("If any single feature has ROC-AUC > 0.95, the synthetic data")
    print("is too clean and the ML task is trivial. The generator must")
    print("be patched to add realistic noise to revised_cost and")
    print("latest_revised_completion_date.")


if __name__ == "__main__":
    main()
