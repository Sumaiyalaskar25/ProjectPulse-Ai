# backend/services/ml/scripts/generate_synthetic.py
"""
Generate synthetic PAIMANA-like project snapshots for ProjectPulse AI.

Produces ~300 projects x ~24 months of snapshots, with realistic:
  - S-curve physical progress
  - Cost escalation (overruns)
  - Schedule slippage
  - Delay reasons (NLP corpus)

Output: backend/data/processed/snapshots.parquet
Schema matches db.py: Project + ProjectSnapshot (denormalized).

Run:
    python -m services.ml.scripts.generate_synthetic
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import DATA_PROCESSED_DIR, ensure_directories


# ------------------------------------------------------------------------
# CONSTANTS
# ------------------------------------------------------------------------

SEED = 42
N_PROJECTS = 300

SECTORS = [
    "Roads", "Railways", "Power", "Water", "Urban Development",
    "Ports", "Airports", "Telecom", "Oil & Gas", "Mining",
]

MINISTRIES = [
    "MoRTH", "MoR", "MoP", "MoWR", "MoHUA",
    "MoPSW", "MoCA", "MoC", "MoPNG", "MoM",
]

STATES = [
    "Maharashtra", "Uttar Pradesh", "Karnataka", "Tamil Nadu",
    "Gujarat", "West Bengal", "Rajasthan", "Kerala",
    "Madhya Pradesh", "Bihar", "Odisha", "Punjab",
]

DELAY_REASONS = [
    "Land acquisition pending in district",
    "Environmental clearance delayed by MoEF",
    "Contractor abandoned work midway",
    "Funds not released by state treasury",
    "Monsoon damage and rework required",
    "Utility shifting not completed",
    "Forest clearance pending",
    "Design changes requested by ministry",
    "Law and order issue in project area",
    "Material procurement delay due to supplier",
    "Right of way dispute with locals",
    "Detailed design approval pending",
    "Quality assurance testing extended",
    "Third-party inspection delayed",
    "Arbitration pending with contractor",
]

RISK_PROFILES = {
    # (weight, delay_multiplier, cost_multiplier)
    "good":      (0.25, 1.00, 1.02),
    "average":   (0.40, 1.20, 1.15),
    "bad":       (0.25, 1.60, 1.40),
    "terrible":  (0.10, 2.50, 1.90),
}


# ------------------------------------------------------------------------
# GENERATOR
# ------------------------------------------------------------------------

def _s_curve_progress(t: float, rng: np.random.Generator) -> float:
    """S-curve: slow start, fast middle, slow end. Returns 0-100.

    t is normalized time [0, 1] over the project's planned duration.
    """
    if t < 0:
        t = 0.0
    if t > 1.0:
        t = 1.0
    # Logistic with noise
    base = 100.0 / (1.0 + np.exp(-10.0 * (t - 0.5)))
    noise = rng.normal(0, 2.0)
    return float(np.clip(base + noise, 0.0, 100.0))


def _pick(choices: list, rng: np.random.Generator) -> str:
    return choices[rng.integers(0, len(choices))]


def _generate_project(project_index: int, rng: np.random.Generator) -> pd.DataFrame:
    project_id = f"PRJ{project_index:05d}"

    sector = _pick(SECTORS, rng)
    ministry = _pick(MINISTRIES, rng)
    state = _pick(STATES, rng)

    # Base financials (log-normal so most projects are small, few are huge)
    original_cost = float(np.exp(rng.normal(loc=6.5, scale=1.5)))  # in crores

    # Duration: 24-72 months
    planned_duration_months = int(rng.integers(24, 73))

    # Approval date: somewhere between 2020-01 and 2023-06
    approval_offset_days = int(rng.integers(0, 365 * 3 + 180))
    approval_date = date(2020, 1, 1) + timedelta(days=approval_offset_days)

    original_completion_date = approval_date + timedelta(days=planned_duration_months * 30)

    # Risk profile
    profile_names = list(RISK_PROFILES.keys())
    profile_weights = [RISK_PROFILES[p][0] for p in profile_names]
    profile = rng.choice(profile_names, p=profile_weights)
    _, delay_mult, cost_mult = RISK_PROFILES[profile]

    # Final outcome
    final_duration_months = int(planned_duration_months * delay_mult)
    final_cost = original_cost * cost_mult

    # Generate monthly snapshots up to min(final_duration + 3, 36) so we don't
    # produce 5 years of data for each project
    max_months = min(final_duration_months + 3, 36)

    rows = []
    for m in range(max_months):
        _total_months = approval_date.month - 1 + m
        _year = approval_date.year + _total_months // 12
        _month = _total_months % 12 + 1
        report_month = date(_year, _month, 1)

        # Progress via S-curve
        t_norm = m / max(final_duration_months, 1)
        progress = _s_curve_progress(t_norm, rng)

        # Cumulative expenditure (tracks progress with lag + cost escalation)
        expenditure_ratio = progress / 100.0
        expenditure = final_cost * expenditure_ratio * float(rng.uniform(0.85, 1.15))
        expenditure = max(0.0, expenditure)

        # Revised cost ramps from original to final over the project
        if m == 0:
            revised_cost = original_cost
        else:
            revised_cost = original_cost + (final_cost - original_cost) * min(1.0, m / max(final_duration_months, 1))

        # Revised completion date
        if m < 3:
            revised_completion = original_completion_date
        else:
            delay_days = (final_duration_months - planned_duration_months) * 30
            revised_completion = original_completion_date + timedelta(
                days=int(delay_days * min(1.0, m / max(final_duration_months, 1)))
            )

        # Delay reason (only for slow projects past mid-point)
        if profile in ("bad", "terrible") and progress > 20:
            delay_reason = _pick(DELAY_REASONS, rng)
        else:
            delay_reason = ""

        # Status
        if progress >= 99.0:
            status = "Completed"
        elif progress < 5.0:
            status = "Not Started"
        else:
            status = "In Progress"

        rows.append({
            "project_id": project_id,
            "project_name": f"{sector} Project {project_id}",
            "report_month": report_month,
            "original_cost": round(original_cost, 2),
            "revised_cost": round(revised_cost, 2),
            "cumulative_expenditure": round(expenditure, 2),
            "physical_progress": round(progress, 2),
            "approval_date": approval_date,
            "original_completion_date": original_completion_date,
            "latest_revised_completion_date": revised_completion,
            "sector": sector,
            "ministry": ministry,
            "state": state,
            "delay_reason_text": delay_reason,
            "project_status": status,
        })

    return pd.DataFrame(rows)


def generate_all() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    frames = [_generate_project(i, rng) for i in range(N_PROJECTS)]
    df = pd.concat(frames, ignore_index=True)
    # Ensure types
    for c in ["report_month", "approval_date",
              "original_completion_date", "latest_revised_completion_date"]:
        df[c] = pd.to_datetime(df[c]).dt.normalize()
    return df


# ------------------------------------------------------------------------
# RUN
# ------------------------------------------------------------------------

def main() -> None:
    ensure_directories()
    out_path = DATA_PROCESSED_DIR / "snapshots.parquet"

    print(f"Generating {N_PROJECTS} synthetic projects (seed={SEED})...")
    df = generate_all()

    df.to_parquet(out_path, index=False)

    # Report
    print()
    print("=" * 60)
    print("Synthetic Data Report")
    print("=" * 60)
    print(f"Output file:        {out_path}")
    print(f"Total snapshots:    {len(df):,}")
    print(f"Total projects:     {df['project_id'].nunique()}")
    print(f"Date range:         {df['report_month'].min().date()} to {df['report_month'].max().date()}")
    print(f"Snapshots/project:  {len(df) / df['project_id'].nunique():.1f} (avg)")
    print(f"Sectors:            {df['sector'].nunique()}")
    print(f"Ministries:         {df['ministry'].nunique()}")
    print(f"States:             {df['state'].nunique()}")
    print(f"Rows with delays:   {(df['delay_reason_text'] != '').sum():,} "
          f"({(df['delay_reason_text'] != '').mean() * 100:.1f}%)")
    print()
    print("Sample row:")
    print(df.iloc[0].to_string())


if __name__ == "__main__":
    main()
