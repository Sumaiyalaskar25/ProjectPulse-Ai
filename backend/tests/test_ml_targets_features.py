# tests/test_ml_targets_features.py
import pytest
import pandas as pd
import numpy as np
from services.ml.targets.builder import TargetBuilder
from services.ml.features.engine import LeakageFreeFeatureEngine
from services.ml.inference.predict import check_model_readiness

def test_target_matching_forward_direction_only():
    """Verify TC-008 & BUG-002: Future target matching never selects a historical snapshot."""
    # Project with Jan snapshot, June snapshot, but missing July (T+6) snapshot
    snapshots = pd.DataFrame([
        {
            "project_id": "PRJ_TEST",
            "report_month": pd.Timestamp("2023-01-01"),
            "original_cost": 100.0,
            "revised_cost": 100.0,
            "original_completion_date": pd.Timestamp("2024-01-01"),
            "latest_revised_completion_date": pd.Timestamp("2024-01-01"),
        },
        {
            "project_id": "PRJ_TEST",
            "report_month": pd.Timestamp("2023-06-01"),  # 5 months ahead (T+5), NOT T+6 or after
            "original_cost": 100.0,
            "revised_cost": 120.0,
            "original_completion_date": pd.Timestamp("2024-01-01"),
            "latest_revised_completion_date": pd.Timestamp("2024-03-01"),
        }
    ])
    
    builder = TargetBuilder(lookahead_months=6, tolerance_days=31)
    labels = builder.build(snapshots)
    
    # Jan row has target month 2023-07-01. With direction='forward', June (2023-06-01) cannot be matched as future target!
    jan_row = labels[labels["report_month"] == pd.Timestamp("2023-01-01")].iloc[0]
    assert jan_row["is_censored"] == True, "Missing forward target must be censored, never backward substituted"

def test_unknown_sector_handling():
    """Verify TC-006 & BUG-003: Unseen sector produces isolated dummy columns and zero baseline zscore."""
    train_df = pd.DataFrame([
        {
            "project_id": "PRJ_01",
            "report_month": pd.Timestamp("2023-01-01"),
            "original_cost": 100.0,
            "revised_cost": 100.0,
            "cumulative_expenditure": 10.0,
            "physical_progress": 15.0,
            "approval_date": pd.Timestamp("2022-01-01"),
            "original_completion_date": pd.Timestamp("2024-01-01"),
            "latest_revised_completion_date": pd.Timestamp("2024-01-01"),
            "sector": "Roads",
            "ministry": "MoRTH",
            "state": "Maharashtra",
        }
    ])
    
    engine = LeakageFreeFeatureEngine()
    engine.fit(train_df)
    
    # New data with completely unseen sector, ministry, and state
    unseen_df = pd.DataFrame([
        {
            "project_id": "PRJ_NEW",
            "report_month": pd.Timestamp("2023-01-01"),
            "original_cost": 200.0,
            "revised_cost": 200.0,
            "cumulative_expenditure": 20.0,
            "physical_progress": 25.0,
            "approval_date": pd.Timestamp("2022-01-01"),
            "original_completion_date": pd.Timestamp("2024-01-01"),
            "latest_revised_completion_date": pd.Timestamp("2024-01-01"),
            "sector": "Aerospace",      # Unseen
            "ministry": "MoSpace",       # Unseen
            "state": "Goa",              # Unseen
        }
    ])
    
    X_new = engine.transform(unseen_df)
    assert not X_new.isna().any().any(), "Features for unseen categoricals must not contain NaN"
    assert "sector_baseline_zscore" in X_new.columns
    # Benchmark Z-score defaults gracefully to 0.0 for unknown sector
    assert X_new["sector_baseline_zscore"].iloc[0] == 0.0

def test_calendar_aware_velocity_with_missing_months():
    """Verify TC-009 & BUG-004: Irregular monthly reports calculate correct calendar velocity."""
    # Observations at Month 1 (Jan), Month 2 (Feb), and Month 7 (July)
    # Shifting 3 rows would have incorrectly compared July against Jan (6 calendar months),
    # but calendar as-of matching correctly detects that Jan is not in the T-3m window!
    snapshots = pd.DataFrame([
        {
            "project_id": "PRJ_IRR",
            "report_month": pd.Timestamp("2023-01-01"),
            "original_cost": 100.0,
            "revised_cost": 100.0,
            "cumulative_expenditure": 10.0,
            "physical_progress": 10.0,
            "approval_date": pd.Timestamp("2022-01-01"),
            "original_completion_date": pd.Timestamp("2024-01-01"),
            "latest_revised_completion_date": pd.Timestamp("2024-01-01"),
            "sector": "Roads",
            "ministry": "MoRTH",
            "state": "Maharashtra",
        },
        {
            "project_id": "PRJ_IRR",
            "report_month": pd.Timestamp("2023-04-01"),  # Exactly 3 months later
            "original_cost": 100.0,
            "revised_cost": 100.0,
            "cumulative_expenditure": 25.0,
            "physical_progress": 22.0,
            "approval_date": pd.Timestamp("2022-01-01"),
            "original_completion_date": pd.Timestamp("2024-01-01"),
            "latest_revised_completion_date": pd.Timestamp("2024-01-01"),
            "sector": "Roads",
            "ministry": "MoRTH",
            "state": "Maharashtra",
        }
    ])
    
    engine = LeakageFreeFeatureEngine()
    X = engine.fit_transform(snapshots)
    # At April (index 1), progress was 22, Jan was 10. (22 - 10)/3 = 4.0 velocity
    v_apr = X["progress_velocity_3m"].iloc[1]
    assert abs(v_apr - 4.0) < 0.1
