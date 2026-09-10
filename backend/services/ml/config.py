# backend/services/ml/config.py
"""
Centralized configuration for ProjectPulse AI ML module.

Every parameter, path, and threshold used across the ML pipeline lives here.
Nothing else in the codebase should hardcode these values.

Environment-aware: reads paths relative to the backend/ directory.
"""

from pathlib import Path
from datetime import date
from functools import lru_cache

# ========================================================================
# PATHS
# ========================================================================

# The ML module lives at backend/services/ml/config.py
# So backend/ = two levels up from this file
BACKEND_ROOT: Path = Path(__file__).resolve().parent.parent.parent

# Data directories (gitignored)
DATA_DIR: Path = BACKEND_ROOT / "data"
DATA_RAW_DIR: Path = DATA_DIR / "raw"
DATA_STAGING_DIR: Path = DATA_DIR / "staging"
DATA_PROCESSED_DIR: Path = DATA_DIR / "processed"
DATA_FEATURES_DIR: Path = DATA_DIR / "features"

# Model artifacts (gitignored except .gitkeep)
MODELS_DIR: Path = BACKEND_ROOT / "models"
MODELS_ARTIFACTS_DIR: Path = MODELS_DIR / "artifacts"

# Reports (checked in selectively)
REPORTS_DIR: Path = BACKEND_ROOT.parent / "reports"
REPORTS_FIGURES_DIR: Path = REPORTS_DIR / "figures"


# ========================================================================
# TEMPORAL PARAMETERS
# ========================================================================

# How far into the future we predict. A snapshot at month T produces a
# label describing the project's state at month T + LOOKAHEAD_MONTHS.
LOOKAHEAD_MONTHS: int = 6

# Minimum history required to compute velocity features.
# With 3 months of snapshots, we can compute a 3-month velocity.
MIN_HISTORY_MONTHS: int = 3

# Window used for velocity calculations (months).
VELOCITY_WINDOW_MONTHS: int = 3

# Rolling-origin backtest configuration.
ROLLING_FOLDS: int = 4
ROLLING_ORIGIN_MONTHS: int = 12  # Initial training window

# Tolerance in days when matching a target month to an actual snapshot.
# Allows +/- 1 month drift due to missing reports.
TARGET_MATCH_TOLERANCE_DAYS: int = 31


# ========================================================================
# BUSINESS THRESHOLDS
# ========================================================================

# A project is "in cost overrun" if its revised cost exceeds original
# cost by this percentage.
COST_OVERRUN_THRESHOLD_PCT: float = 20.0
COST_OVERRUN_WARNING_PCT: float = 10.0

# A project is "delayed" if its latest revised completion date exceeds
# the original completion date by this many months.
SCHEDULE_OVERRUN_THRESHOLD_MONTHS: int = 6
SCHEDULE_OVERRUN_WARNING_MONTHS: int = 3
SCHEDULE_OVERRUN_CRITICAL_MONTHS: int = 12


# ========================================================================
# RISK TIER BOUNDARIES (composite_score, 0-100)
# ========================================================================

# Tier is determined by the composite score:
#   Stable:    0 to TIER_MODERATE_MIN - 1
#   Moderate:  TIER_MODERATE_MIN to TIER_HIGH_MIN - 1
#   High:      TIER_HIGH_MIN to TIER_CRITICAL_MIN - 1
#   Critical:  TIER_CRITICAL_MIN to 100
TIER_MODERATE_MIN: int = 25
TIER_HIGH_MIN: int = 50
TIER_CRITICAL_MIN: int = 75

# Human-readable tier labels -- MUST match backend's db.py comments.
# db.py says: "Critical/High/Moderate/Stable" (capitalized).
TIER_STABLE = "Stable"
TIER_MODERATE = "Moderate"
TIER_HIGH = "High"
TIER_CRITICAL = "Critical"


# ========================================================================
# COMPOSITE RISK WEIGHTS
# ========================================================================

# Composite score is a weighted combination of component risks.
# Must sum to 1.0.
WEIGHT_COST_RISK: float = 0.35
WEIGHT_SCHEDULE_RISK: float = 0.45
WEIGHT_TRAJECTORY_RISK: float = 0.20

# Sanity check
assert abs(WEIGHT_COST_RISK + WEIGHT_SCHEDULE_RISK + WEIGHT_TRAJECTORY_RISK - 1.0) < 1e-9, \
    "Composite risk weights must sum to 1.0"


# ========================================================================
# FEATURE ENGINEERING
# ========================================================================

# Number of quantile buckets for sector benchmarks (time_elapsed_ratio).
BENCHMARK_QUANTILES: int = 10

# Anomaly detection thresholds.
ANOMALY_COST_DROP_THRESHOLD_PCT: float = 5.0   # Cost dropped > 5% month-over-month
ANOMALY_PROGRESS_DROP_PP: float = 5.0          # Progress dropped > 5 percentage points
ANOMALY_STAGNATION_MONTHS: int = 3             # No progress change for N months


# ========================================================================
# MODEL HYPERPARAMETERS
# ========================================================================

# LightGBM defaults for classifiers and regressors.
LGBM_PARAMS: dict = {
    "n_estimators": 500,
    "learning_rate": 0.05,
    "num_leaves": 31,
    "min_child_samples": 20,
    "random_state": 42,
    "verbose": -1,
    "n_jobs": -1,
}

# Model versioning -- updated automatically by training script.
DEFAULT_MODEL_VERSION: str = "lgbm_v1"
FEATURE_VERSION: str = "v1"
SCHEMA_VERSION: str = "1.0.0"


# ========================================================================
# HELPER FUNCTIONS
# ========================================================================

def ensure_directories() -> None:
    """Create all expected directories if they don't exist.

    Safe to call multiple times. Called once at pipeline startup.
    """
    dirs_to_create = [
        DATA_RAW_DIR,
        DATA_STAGING_DIR,
        DATA_PROCESSED_DIR,
        DATA_FEATURES_DIR,
        MODELS_ARTIFACTS_DIR,
        REPORTS_FIGURES_DIR,
    ]
    for d in dirs_to_create:
        d.mkdir(parents=True, exist_ok=True)


def tier_from_score(score: float) -> str:
    """Map a composite score (0-100) to a tier label.

    Args:
        score: Composite risk score in [0, 100].

    Returns:
        One of "Stable", "Moderate", "High", "Critical".
    """
    if score >= TIER_CRITICAL_MIN:
        return TIER_CRITICAL
    elif score >= TIER_HIGH_MIN:
        return TIER_HIGH
    elif score >= TIER_MODERATE_MIN:
        return TIER_MODERATE
    else:
        return TIER_STABLE


@lru_cache(maxsize=1)
def get_snapshot_file() -> Path:
    """Return the canonical path for the processed snapshots parquet file.

    Cached so the path is computed once. Update this if you move the file.
    """
    return DATA_PROCESSED_DIR / "snapshots.parquet"


@lru_cache(maxsize=1)
def get_feature_file() -> Path:
    """Return the canonical path for the cached feature matrix."""
    return DATA_FEATURES_DIR / "features.parquet"


if __name__ == "__main__":
    # Self-test: print all configured paths and verify they resolve.
    print("=" * 60)
    print("ProjectPulse AI -- ML Configuration")
    print("=" * 60)
    print(f"BACKEND_ROOT:          {BACKEND_ROOT}")
    print(f"DATA_PROCESSED_DIR:    {DATA_PROCESSED_DIR}")
    print(f"DATA_FEATURES_DIR:     {DATA_FEATURES_DIR}")
    print(f"MODELS_ARTIFACTS_DIR:  {MODELS_ARTIFACTS_DIR}")
    print(f"REPORTS_FIGURES_DIR:   {REPORTS_FIGURES_DIR}")
    print()
    print(f"LOOKAHEAD_MONTHS:      {LOOKAHEAD_MONTHS}")
    print(f"MIN_HISTORY_MONTHS:    {MIN_HISTORY_MONTHS}")
    print(f"VELOCITY_WINDOW_MONTHS:{VELOCITY_WINDOW_MONTHS}")
    print()
    print(f"COST threshold:        {COST_OVERRUN_THRESHOLD_PCT}%")
    print(f"Schedule threshold:    {SCHEDULE_OVERRUN_THRESHOLD_MONTHS} months")
    print()
    print(f"Tier boundaries:       Moderate>={TIER_MODERATE_MIN}, High>={TIER_HIGH_MIN}, Critical>={TIER_CRITICAL_MIN}")
    print()

    print("Ensuring directories exist...")
    ensure_directories()
    print("OK - All directories ready.")

    print()
    print("Self-test of tier_from_score():")
    for score in [0, 24, 25, 49, 50, 74, 75, 100]:
        print(f"  score={score:3d} -> {tier_from_score(score)}")

    print()
    print("OK - config.py loaded successfully.")
