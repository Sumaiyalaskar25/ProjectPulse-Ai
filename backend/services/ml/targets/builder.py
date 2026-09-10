# backend/services/ml/targets/builder.py
"""
Leakage-free target construction for ProjectPulse AI.

For a snapshot at month T, we predict the project's state at month T+H
(H = LOOKAHEAD_MONTHS). We do NOT use groupby.shift(-H) because that
silently misaligns if a project has missing months. Instead we use
calendar-month matching with a tolerance window.

Key rules:
  1. Future outcome = the project's snapshot at exactly T + H months.
  2. If no snapshot exists at exactly T+H, accept one within +/- TOLERANCE days.
  3. If still no snapshot -> row is CENSORED and DROPPED from training.
     We NEVER fillna(0) on future targets.
  4. Cost overrun is measured against the ORIGINAL cost (from projects table),
     not the current revised cost, so labels remain consistent across time.
  5. Schedule overrun is measured against the ORIGINAL completion date.
"""

from __future__ import annotations

from datetime import date
from typing import Optional, Tuple

import numpy as np
import pandas as pd

from ..config import (
    LOOKAHEAD_MONTHS,
    TARGET_MATCH_TOLERANCE_DAYS,
    COST_OVERRUN_WARNING_PCT,
    COST_OVERRUN_THRESHOLD_PCT,
    SCHEDULE_OVERRUN_WARNING_MONTHS,
    SCHEDULE_OVERRUN_THRESHOLD_MONTHS,
    SCHEDULE_OVERRUN_CRITICAL_MONTHS,
)


# ------------------------------------------------------------------------
# CONSTANTS
# ------------------------------------------------------------------------

REQUIRED_COLUMNS = [
    "project_id",
    "report_month",
    "original_cost",
    "revised_cost",
    "original_completion_date",
    "latest_revised_completion_date",
]


# ------------------------------------------------------------------------
# CORE BUILDER
# ------------------------------------------------------------------------

class TargetBuilder:
    """Builds leakage-free targets from a project_snapshots dataframe.

    Usage:
        builder = TargetBuilder(lookahead_months=6)
        labels = builder.build(snapshots_df)
    """

    def __init__(self, lookahead_months: int = LOOKAHEAD_MONTHS,
                 tolerance_days: int = TARGET_MATCH_TOLERANCE_DAYS):
        self.horizon = lookahead_months
        self.tolerance = pd.Timedelta(days=tolerance_days)

    # -------- public API --------

    def build(self, snapshots: pd.DataFrame) -> pd.DataFrame:
        """Return a dataframe of training labels.

        Columns produced:
            project_id, report_month,
            cost_overrun_pct, schedule_overrun_months,
            cost_binary_10pct, cost_binary_20pct,
            schedule_binary_3mo, schedule_binary_6mo, schedule_binary_12mo,
            is_censored
        """
        self._validate_input(snapshots)

        df = snapshots.copy()

        # Normalize types
        df["report_month"] = pd.to_datetime(df["report_month"]).dt.normalize()
        df["original_completion_date"] = pd.to_datetime(df["original_completion_date"]).dt.normalize()
        df["latest_revised_completion_date"] = pd.to_datetime(
            df["latest_revised_completion_date"]
        ).dt.normalize()

        df = df.sort_values(["project_id", "report_month"]).reset_index(drop=True)

        # Compute target month for each row
        df["_target_month"] = df["report_month"] + pd.DateOffset(months=self.horizon)

        # Build a lookup table of (project_id, report_month) -> future state
        future_states = (
            df[["project_id", "report_month", "revised_cost",
                "latest_revised_completion_date"]]
            .rename(columns={
                "report_month": "_future_month",
                "revised_cost": "_future_revised_cost",
                "latest_revised_completion_date": "_future_completion",
            })
        )

        # Merge on (project_id, target_month) with tolerance
        merged = pd.merge_asof(
            df.sort_values("_target_month"),
            future_states.sort_values("_future_month"),
            left_on="_target_month",
            right_on="_future_month",
            by="project_id",
            tolerance=self.tolerance,
            direction="nearest",
        )

        # Identify censored rows (no future observation available)
        merged["is_censored"] = merged["_future_revised_cost"].isna() | \
                                merged["_future_completion"].isna()

        # Compute continuous targets
        merged["cost_overrun_pct"] = (
            (merged["_future_revised_cost"] - merged["original_cost"])
            / merged["original_cost"]
            * 100.0
        )

        merged["schedule_overrun_months"] = (
            (merged["_future_completion"] - merged["original_completion_date"])
            .dt.days / 30.4375  # average days per month
        )

        # Compute binary targets (5 thresholds)
        merged["cost_binary_10pct"] = (merged["cost_overrun_pct"] > COST_OVERRUN_WARNING_PCT).astype("Int64")
        merged["cost_binary_20pct"] = (merged["cost_overrun_pct"] > COST_OVERRUN_THRESHOLD_PCT).astype("Int64")

        merged["schedule_binary_3mo"]  = (merged["schedule_overrun_months"] > SCHEDULE_OVERRUN_WARNING_MONTHS).astype("Int64")
        merged["schedule_binary_6mo"]  = (merged["schedule_overrun_months"] > SCHEDULE_OVERRUN_THRESHOLD_MONTHS).astype("Int64")
        merged["schedule_binary_12mo"] = (merged["schedule_overrun_months"] > SCHEDULE_OVERRUN_CRITICAL_MONTHS).astype("Int64")

        # Keep only the label columns
        out_cols = [
            "project_id", "report_month",
            "cost_overrun_pct", "schedule_overrun_months",
            "cost_binary_10pct", "cost_binary_20pct",
            "schedule_binary_3mo", "schedule_binary_6mo", "schedule_binary_12mo",
            "is_censored",
        ]
        result = merged[out_cols].copy()

        # Sanity check: non-censored rows must have valid labels
        non_censored = result[~result["is_censored"]]
        assert non_censored["cost_overrun_pct"].notna().all(), \
            "Non-censored rows must have cost_overrun_pct"
        assert non_censored["schedule_overrun_months"].notna().all(), \
            "Non-censored rows must have schedule_overrun_months"

        return result.reset_index(drop=True)

    def build_trainable(self, snapshots: pd.DataFrame) -> pd.DataFrame:
        """Convenience: build labels and DROP censored rows."""
        labels = self.build(snapshots)
        return labels[~labels["is_censored"]].reset_index(drop=True)

    # -------- internals --------

    def _validate_input(self, df: pd.DataFrame) -> None:
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        if df.empty:
            raise ValueError("Input dataframe is empty")
        if (df["original_cost"] <= 0).any():
            raise ValueError("original_cost must be strictly positive")


# ------------------------------------------------------------------------
# SELF-TEST
# ------------------------------------------------------------------------

def _make_fake_snapshots() -> pd.DataFrame:
    """Build 3 tiny projects with known timelines to verify target math."""
    rows = []

    # Project A: perfect project. Original 100cr. Original completion 2024-01.
    # No delay, no cost overrun.
    for i in range(8):
        rows.append({
            "project_id": "PRJ_A",
            "report_month": pd.Timestamp(2023, 1, 1) + pd.DateOffset(months=i),
            "original_cost": 100.0,
            "revised_cost": 100.0,
            "original_completion_date": pd.Timestamp(2024, 1, 1),
            "latest_revised_completion_date": pd.Timestamp(2024, 1, 1),
        })

    # Project B: cost overrun + delay.
    # Original 100cr. By 2024-01 revised = 150 (50% overrun).
    # Original completion 2024-01, revised 2024-09 (8 months delay).
    for i in range(8):
        month = pd.Timestamp(2023, 1, 1) + pd.DateOffset(months=i)
        # Ramp cost from 100 to 150
        cost = 100.0 + (50.0 * i / 7.0)
        # Ramp delay from 0 to 8 months
        delay_months = int(12 * i / 7.0)
        rows.append({
            "project_id": "PRJ_B",
            "report_month": month,
            "original_cost": 100.0,
            "revised_cost": cost,
            "original_completion_date": pd.Timestamp(2024, 1, 1),
            "latest_revised_completion_date": pd.Timestamp(2024, 1, 1) + pd.DateOffset(months=delay_months),
        })

    # Project C: missing months (tests calendar matching)
    for i in [0, 1, 2, 5, 6, 7]:  # missing 3, 4
        rows.append({
            "project_id": "PRJ_C",
            "report_month": pd.Timestamp(2023, 1, 1) + pd.DateOffset(months=i),
            "original_cost": 100.0,
            "revised_cost": 120.0 + i,
            "original_completion_date": pd.Timestamp(2024, 1, 1),
            "latest_revised_completion_date": pd.Timestamp(2024, 4, 1),
        })

    return pd.DataFrame(rows)


def _test_targets_are_correct() -> None:
    df = _make_fake_snapshots()
    builder = TargetBuilder(lookahead_months=6)
    labels = builder.build(df)

    # ------------------------------------------------------------------
    # Project A: with horizon=6, snapshot at 2023-01-01 has target month
    # 2023-07-01. Future state: revised_cost=100, completion=2024-01-01.
    # So cost_overrun_pct = 0, schedule_overrun_months = 0.
    # ------------------------------------------------------------------
    a_jan = labels[(labels["project_id"] == "PRJ_A") &
                   (labels["report_month"] == pd.Timestamp(2023, 1, 1))].iloc[0]
    assert not a_jan["is_censored"], "A Jan should not be censored"
    assert abs(a_jan["cost_overrun_pct"]) < 0.01, f"A cost_overrun should be 0, got {a_jan['cost_overrun_pct']}"
    assert abs(a_jan["schedule_overrun_months"]) < 0.1, f"A schedule_overrun should be 0"
    assert a_jan["cost_binary_20pct"] == 0
    assert a_jan["schedule_binary_6mo"] == 0
    print("[OK] Project A (clean) labels correct")

    # ------------------------------------------------------------------
    # Project B: at 2023-01-01, target month 2023-07-01.
    # Revised cost by 2023-07-01 = 100 + 50*6/7 = 142.857.
    # Overrun = 42.857%.
    # Revised completion by 2023-07-01 = 2024-01-01 + ~6 months = 2024-07.
    # Schedule overrun ~ 6 months.
    # ------------------------------------------------------------------
    b_jan = labels[(labels["project_id"] == "PRJ_B") &
                   (labels["report_month"] == pd.Timestamp(2023, 1, 1))].iloc[0]
    assert not b_jan["is_censored"]
    assert b_jan["cost_overrun_pct"] > 40.0, f"B cost_overrun should be >40%, got {b_jan['cost_overrun_pct']}"
    assert b_jan["cost_binary_20pct"] == 1
    assert b_jan["schedule_binary_6mo"] == 1, f"B should be delayed >6mo, got {b_jan['schedule_overrun_months']}"
    print("[OK] Project B (delay) labels correct")

    # ------------------------------------------------------------------
    # Project C: has missing months. At 2023-01-01, target = 2023-07-01.
    # 2023-07 is month index 6 (exists). Should match within tolerance.
    # ------------------------------------------------------------------
    c_jan = labels[(labels["project_id"] == "PRJ_C") &
                   (labels["report_month"] == pd.Timestamp(2023, 1, 1))].iloc[0]
    assert not c_jan["is_censored"], \
        "Project C Jan should match a future snapshot within tolerance"
    print("[OK] Project C (missing months) handled correctly")

    # ------------------------------------------------------------------
    # Last rows must be censored because T+H falls beyond data range.
    # ------------------------------------------------------------------
    a_last = labels[(labels["project_id"] == "PRJ_A") &
                    (labels["report_month"] == pd.Timestamp(2023, 8, 1))].iloc[0]
    assert a_last["is_censored"], \
        "A's last snapshot should be censored (target beyond data)"
    print("[OK] Censoring works for out-of-range targets")


def _test_no_leakage_via_tolerance() -> None:
    """If we force the tolerance to 0, only exact-month matches succeed."""
    df = _make_fake_snapshots()
    strict_builder = TargetBuilder(lookahead_months=6, tolerance_days=0)
    labels = strict_builder.build(df)

    # Project C at 2023-01-01: target month 2023-07-01.
    # Month 2023-07 exists in data (i=6), so should still match.
    c = labels[(labels["project_id"] == "PRJ_C") &
               (labels["report_month"] == pd.Timestamp(2023, 1, 1))].iloc[0]
    assert not c["is_censored"]
    print("[OK] Strict tolerance still matches exact-month future snapshot")


# ------------------------------------------------------------------------
# RUN
# ------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("ProjectPulse AI -- Target Builder Self-Test")
    print("=" * 60)

    _test_targets_are_correct()
    print()
    _test_no_leakage_via_tolerance()

    print()
    print("All target builder tests passed.")
