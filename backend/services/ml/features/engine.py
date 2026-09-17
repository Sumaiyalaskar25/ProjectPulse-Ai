# backend/services/ml/features/engine.py
"""
Leakage-free feature transformer for ProjectPulse AI.

Design principles:
  1. fit() learns encoders, bucket edges, and benchmarks on TRAINING data.
  2. transform() reuses those fitted values — never re-fits on new data.
  3. Categorical handling uses OneHotEncoder(handle_unknown='ignore') so
     unseen ministries/states at inference time do not crash.
  4. Time buckets use fixed edges learned at fit time — no re-quantiling.
  5. Trajectory features use .shift(+k) — LAGGED, not future.
  6. Velocity requires k months of history; early rows get 0 (safe).
  7. The exact feature column list is stable and exported via .feature_cols.

Feature families (about 30 features):
  Basic:      original_cost_log, months_since_approval, time_elapsed_ratio,
              physical_progress, cumulative_expenditure, expenditure_to_original
  Trajectory: progress_velocity_3m, expenditure_velocity_3m,
              progress_acceleration_3m, expenditure_acceleration_3m
  Financial:  cost_burn_ratio, cost_revision_pct
  Schedule:   schedule_slippage_days, schedule_slippage_months,
              schedule_revision_count
  Benchmark:  sector_baseline_zscore
  Confidence: data_quality_score, history_length
  Categorical: one-hot columns for sector, ministry, state
"""

from __future__ import annotations

from typing import List, Optional, cast

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder

from ..config import (
    BENCHMARK_QUANTILES,
    VELOCITY_WINDOW_MONTHS,
)


# ------------------------------------------------------------------------
# CONSTANTS
# ------------------------------------------------------------------------

CATEGORICAL_COLS = ["sector", "ministry", "state"]

NUMERIC_FEATURE_COLS = [
    # Basic
    "original_cost_log",
    "months_since_approval",
    "time_elapsed_ratio",
    "physical_progress",
    "cumulative_expenditure",
    "expenditure_to_original",
    # Trajectory
    "progress_velocity_3m",
    "expenditure_velocity_3m",
    "progress_acceleration_3m",
    "expenditure_acceleration_3m",
    # Financial
    "cost_burn_ratio",
    "cost_revision_pct",
    # Schedule
    "schedule_slippage_days",
    "schedule_slippage_months",
    "schedule_revision_count",
    # Benchmark
    "sector_baseline_zscore",
    # Confidence
    "data_quality_score",
    "history_length",
]


REQUIRED_COLUMNS = [
    "project_id",
    "report_month",
    "original_cost",
    "revised_cost",
    "cumulative_expenditure",
    "physical_progress",
    "approval_date",
    "original_completion_date",
    "latest_revised_completion_date",
    "sector",
    "ministry",
    "state",
]


# ------------------------------------------------------------------------
# TRANSFORMER
# ------------------------------------------------------------------------

class LeakageFreeFeatureEngine(BaseEstimator, TransformerMixin):
    """sklearn-compatible transformer that produces a leakage-free feature
    matrix from a project_snapshots dataframe.

    Usage:
        engine = LeakageFreeFeatureEngine()
        X_train = engine.fit_transform(train_df)
        X_test  = engine.transform(test_df)
    """

    def __init__(self):
        self.onehot: Optional[OneHotEncoder] = None
        self.sector_encoder: Optional[OneHotEncoder] = None
        self.bucket_edges: Optional[np.ndarray] = None
        self.sector_benchmarks: Optional[pd.DataFrame] = None
        self.feature_cols: List[str] = []
        self._is_fitted: bool = False

    # -------------------------- FIT --------------------------

    def fit(self, X: pd.DataFrame, y=None) -> "LeakageFreeFeatureEngine":
        self._validate_input(X)
        df = self._prepare_types(X)

        # 1. OneHotEncoder for all categoricals
        self.onehot = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        self.onehot.fit(df[CATEGORICAL_COLS].fillna("Unknown"))

        # 1b. Dedicated Sector encoder (BUG-003 fix: never conflate with ministry/state)
        self.sector_encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        self.sector_encoder.fit(df[["sector"]].fillna("Unknown"))

        # 2. Bucket edges for time_elapsed_ratio (fit on training data)
        months_since = pd.to_timedelta(df["report_month"] - df["approval_date"]).dt.days / 30.4375
        planned_dur = pd.to_timedelta(df["original_completion_date"] - df["approval_date"]).dt.days / 30.4375
        time_ratio = months_since / (planned_dur + 1e-5)

        # Guard against all-NaN
        if time_ratio.notna().any():
            _, bucket_edges = pd.qcut(
                time_ratio.dropna(),
                q=BENCHMARK_QUANTILES,
                labels=False,
                retbins=True,
                duplicates="drop",
            )
            self.bucket_edges = np.asarray(bucket_edges, dtype=float)
        else:
            self.bucket_edges = np.linspace(0.0, 2.0, BENCHMARK_QUANTILES + 1)

        # 3. Sector benchmarks using dedicated sector encoder
        temp = df.copy()
        temp["time_bucket"] = pd.cut(
            time_ratio, bins=list(self.bucket_edges), labels=False, include_lowest=True
        )
        sec_matrix = np.asarray(self.sector_encoder.transform(temp[["sector"]].fillna("Unknown")))
        has_sec = sec_matrix.sum(axis=1) > 0
        temp["_sector_id"] = -1
        if has_sec.any():
            temp.loc[has_sec, "_sector_id"] = np.argmax(sec_matrix[has_sec], axis=1)

        self.sector_benchmarks = (
            temp[temp["_sector_id"] >= 0]
            .groupby(["_sector_id", "time_bucket"], observed=False)["physical_progress"]
            .agg(["median", "std"])
            .reset_index()
            .rename(columns={"_sector_id": "sector_id",
                             "median": "sector_median",
                             "std": "sector_std"})
        )
        if self.sector_benchmarks.empty:
            self.sector_benchmarks = pd.DataFrame(columns=["sector_id", "time_bucket", "sector_median", "sector_std"])
        else:
            self.sector_benchmarks["sector_std"] = (
                self.sector_benchmarks["sector_std"].fillna(1.0).replace(0, 1.0)
            )

        # 4. Mark as fitted BEFORE calling transform so it can run
        self._is_fitted = True

        # 5. Compute the feature column list ONCE using this transform
        sample = self.transform(X)
        self.feature_cols = list(sample.columns)

        return self

    # -------------------------- TRANSFORM --------------------------

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if not self._is_fitted:
            raise RuntimeError("Must call fit() before transform().")
        assert self.onehot is not None
        assert self.sector_encoder is not None
        assert self.bucket_edges is not None
        assert self.sector_benchmarks is not None

        self._validate_input(X)
        df = self._prepare_types(X)

        # Sort to make chronological lookups accurate
        df = df.sort_values(["project_id", "report_month"]).reset_index(drop=True)

        # --- 1. Categoricals -> one-hot ---
        cat_matrix = np.asarray(self.onehot.transform(df[CATEGORICAL_COLS].fillna("Unknown")))
        cat_cols = list(self.onehot.get_feature_names_out(CATEGORICAL_COLS))
        cat_df = pd.DataFrame(cat_matrix, columns=cat_cols, index=df.index)
        df = pd.concat([df, cat_df], axis=1)

        # --- 2. Basic features ---
        df["original_cost_log"] = np.log1p(df["original_cost"])
        df["months_since_approval"] = (
            pd.to_timedelta(df["report_month"] - df["approval_date"]).dt.days / 30.4375
        )
        planned_dur = (
            pd.to_timedelta(df["original_completion_date"] - df["approval_date"]).dt.days / 30.4375
        )
        df["time_elapsed_ratio"] = df["months_since_approval"] / (planned_dur + 1e-5)
        df["expenditure_to_original"] = (
            df["cumulative_expenditure"] / (df["original_cost"] + 1e-5)
        )
        df["cost_revision_pct"] = (
            (df["revised_cost"] - df["original_cost"]) / (df["original_cost"] + 1e-5)
        ) * 100.0

        # --- 3. Trajectory (Calendar-aware Lagged — BUG-004 fix) ---
        w = VELOCITY_WINDOW_MONTHS
        
        # Calendar-aware lookup for T - 3 months and T - 6 months
        df_lags = df[["project_id", "report_month", "physical_progress", "cumulative_expenditure"]].copy()
        
        # Target lag dates
        df["_row_idx"] = np.arange(len(df))
        df["_target_lag1"] = df["report_month"] - pd.DateOffset(months=w)
        df["_target_lag2"] = df["report_month"] - pd.DateOffset(months=2 * w)
        
        # Merge as-of with backward direction and 45-day tolerance
        lag1_match = pd.merge_asof(
            df[["_row_idx", "project_id", "_target_lag1", "report_month"]].sort_values("_target_lag1"),
            df_lags.rename(columns={
                "report_month": "_lag1_month",
                "physical_progress": "_p_lag",
                "cumulative_expenditure": "_e_lag"
            }).sort_values("_lag1_month"),
            left_on="_target_lag1",
            right_on="_lag1_month",
            by="project_id",
            tolerance=pd.Timedelta(days=45),
            direction="nearest"
        )
        # Ensure lag month is strictly prior to report_month
        valid_lag1 = lag1_match["_lag1_month"] < lag1_match["report_month"]
        lag1_match.loc[~valid_lag1, ["_p_lag", "_e_lag", "_lag1_month"]] = np.nan
        lag1_sorted = lag1_match.sort_values("_row_idx")

        lag2_match = pd.merge_asof(
            df[["_row_idx", "project_id", "_target_lag2", "report_month"]].sort_values("_target_lag2"),
            df_lags.rename(columns={
                "report_month": "_lag2_month",
                "physical_progress": "_p_lag2",
                "cumulative_expenditure": "_e_lag2"
            }).sort_values("_lag2_month"),
            left_on="_target_lag2",
            right_on="_lag2_month",
            by="project_id",
            tolerance=pd.Timedelta(days=45),
            direction="nearest"
        )
        valid_lag2 = lag2_match["_lag2_month"] < lag2_match["report_month"]
        lag2_match.loc[~valid_lag2, ["_p_lag2", "_e_lag2", "_lag2_month"]] = np.nan
        lag2_sorted = lag2_match.sort_values("_row_idx")

        df["_p_lag"] = lag1_sorted["_p_lag"].values
        df["_e_lag"] = lag1_sorted["_e_lag"].values
        df["_p_lag2"] = lag2_sorted["_p_lag2"].values
        df["_e_lag2"] = lag2_sorted["_e_lag2"].values

        df["progress_velocity_3m"] = ((df["physical_progress"] - df["_p_lag"]) / w).fillna(0.0)
        df["expenditure_velocity_3m"] = ((df["cumulative_expenditure"] - df["_e_lag"]) / w).fillna(0.0)
        df["progress_acceleration_3m"] = (
            ((df["physical_progress"] - df["_p_lag"]) - (df["_p_lag"] - df["_p_lag2"])) / (w * w)
        ).fillna(0.0)
        df["expenditure_acceleration_3m"] = (
            ((df["cumulative_expenditure"] - df["_e_lag"]) - (df["_e_lag"] - df["_e_lag2"])) / (w * w)
        ).fillna(0.0)

        # --- 4. Financial ---
        df["cost_burn_ratio"] = (
            df["expenditure_to_original"] / ((df["physical_progress"] / 100.0) + 1e-5)
        )

        # --- 5. Schedule ---
        df["schedule_slippage_days"] = pd.to_timedelta(
            df["latest_revised_completion_date"] - df["original_completion_date"]
        ).dt.days.fillna(0)
        df["schedule_slippage_months"] = df["schedule_slippage_days"] / 30.4375

        # Revision count = how many times completion date has changed so far
        df["_prev_completion"] = df.groupby("project_id")[
            "latest_revised_completion_date"
        ].shift(1)
        df["_revision_flag"] = (
            df["latest_revised_completion_date"] != df["_prev_completion"]
        ).astype(int)
        df["schedule_revision_count"] = (
            df.groupby("project_id")["_revision_flag"].cumsum().fillna(0).astype(int)
        )
        # First observation = 0 revisions
        first_idx = df.groupby("project_id").head(1).index
        df.loc[first_idx, "schedule_revision_count"] = 0

        # --- 6. Benchmark (using fitted edges + fitted benchmarks + BUG-003 fix) ---
        df["_time_bucket"] = pd.cut(
            df["time_elapsed_ratio"],
            bins=list(self.bucket_edges),
            labels=False,
            include_lowest=True,
        )
        sec_matrix = np.asarray(self.sector_encoder.transform(df[["sector"]].fillna("Unknown")))
        has_sec = sec_matrix.sum(axis=1) > 0
        df["_sector_id"] = -1
        if has_sec.any():
            df.loc[has_sec, "_sector_id"] = np.argmax(sec_matrix[has_sec], axis=1)

        df = df.merge(
            self.sector_benchmarks,
            left_on=["_sector_id", "_time_bucket"],
            right_on=["sector_id", "time_bucket"],
            how="left",
        )
        df["sector_baseline_zscore"] = (
            (df["physical_progress"] - df["sector_median"])
            / (df["sector_std"] + 1e-5)
        ).fillna(0.0)

        # --- 7. Confidence ---
        df["history_length"] = df.groupby("project_id").cumcount() + 1
        df["data_quality_score"] = 1.0  # baseline; extended later

        # --- 8. Select final features ---
        final_cols = NUMERIC_FEATURE_COLS + list(cat_cols)
        X_out = df[final_cols].copy()
        X_out = X_out.replace([np.inf, -np.inf], 0.0).fillna(0.0)

        return X_out

    # -------------------------- HELPERS --------------------------

    @staticmethod
    def _validate_input(df: pd.DataFrame) -> None:
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        if df.empty:
            raise ValueError("Input dataframe is empty")

    @staticmethod
    def _prepare_types(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        for c in ["report_month", "approval_date", "original_completion_date",
                  "latest_revised_completion_date"]:
            out[c] = pd.to_datetime(out[c]).dt.normalize()
        for c in ["original_cost", "revised_cost", "cumulative_expenditure"]:
            out[c] = out[c].astype(float)
        out["physical_progress"] = out["physical_progress"].astype(float).clip(0, 100)
        return out


# ------------------------------------------------------------------------
# SELF-TEST
# ------------------------------------------------------------------------

def _make_snapshots(n_projects: int = 20, n_months: int = 12) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    rows = []
    for i in range(n_projects):
        sector = rng.choice(["Roads", "Railways", "Power"])
        ministry = rng.choice(["MoRTH", "MoR", "MoP"])
        state = rng.choice(["MH", "KA", "TN"])
        original_cost = float(rng.uniform(100, 1000))
        approval = pd.Timestamp("2022-01-01")
        planned_end = approval + pd.DateOffset(months=36)
        for m in range(n_months):
            report_month = approval + pd.DateOffset(months=m)
            progress = min(100.0, max(0.0, (m + 1) * 5 + rng.normal(0, 2)))
            rows.append({
                "project_id": f"PRJ_{i:03d}",
                "report_month": report_month,
                "original_cost": original_cost,
                "revised_cost": original_cost * (1 + 0.02 * m),
                "cumulative_expenditure": original_cost * progress / 100.0,
                "physical_progress": progress,
                "approval_date": approval,
                "original_completion_date": planned_end,
                "latest_revised_completion_date": planned_end + pd.DateOffset(months=m // 4),
                "sector": sector,
                "ministry": ministry,
                "state": state,
                "delay_reason_text": "",
            })
    return pd.DataFrame(rows)


def _run_tests() -> None:
    df = _make_snapshots(20, 12)
    engine = LeakageFreeFeatureEngine()

    X = engine.fit(df).transform(df)

    # 1. Shape check
    assert X.shape[0] == len(df), f"Row count mismatch: {X.shape[0]} vs {len(df)}"
    assert X.shape[1] > 20, f"Expected >20 features, got {X.shape[1]}"
    print(f"[OK] fit_transform produced shape {X.shape}")

    # 2. No NaN/Inf
    assert not X.isna().any().any(), "Features contain NaN"
    assert not np.isinf(X.values).any(), "Features contain Inf"
    print("[OK] No NaN or Inf in features")

    # 3. Column list is stable
    assert engine.feature_cols == list(X.columns), "feature_cols mismatch"
    print(f"[OK] feature_cols stable: {len(engine.feature_cols)} columns")

    # 4. Transform on NEW data (unseen sector) should not crash
    new_df = _make_snapshots(3, 6).copy()
    new_df.loc[new_df.index[0], "sector"] = "Nuclear"  # unseen
    X_new = engine.transform(new_df)
    assert X_new.shape[1] == X.shape[1], "Column count changed on unseen data"
    print("[OK] Unseen category handled gracefully (handle_unknown='ignore')")

    # 5. Bucket edges are the same after transform (no re-fit)
    assert engine.bucket_edges is not None
    edges_before = engine.bucket_edges.copy()
    _ = engine.transform(new_df)
    assert engine.bucket_edges is not None
    assert np.array_equal(edges_before, engine.bucket_edges), "Bucket edges changed"
    print("[OK] Bucket edges stable across transforms")

    # 6. Velocity requires history: first row of each project must be 0
    v = cast(pd.Series, X["progress_velocity_3m"])
    assert v.abs().max() < 1e3, f"Velocity suspiciously large: {v.abs().max()}"

    # First observation per project should have zero velocity
    df_reset = df.sort_values(["project_id", "report_month"]).reset_index(drop=True)
    first_idx = df_reset.groupby("project_id").head(1).index
    first_velocities = v.iloc[first_idx]
    assert (first_velocities == 0.0).all(), \
        f"First-row velocities should be 0, got {first_velocities.unique()}"
    print("[OK] Velocity is zero for first observation of each project (no history leak)")

    print()
    print("All feature engine tests passed.")


if __name__ == "__main__":
    print("=" * 60)
    print("ProjectPulse AI -- Feature Engine Self-Test")
    print("=" * 60)
    _run_tests()
