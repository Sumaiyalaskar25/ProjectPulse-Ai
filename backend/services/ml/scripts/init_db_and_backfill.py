# backend/services/ml/scripts/init_db_and_backfill.py
"""
Database bootstrap for ProjectPulse AI.

Creates the schema (if not exists) and populates all tables from the
synthetic snapshots. Runs predictions on every project's latest snapshot
and writes them to risk_scores + prediction_evidence.

Uses a sync SQLAlchemy engine (psycopg2). Async is unnecessary for a
batch script.

Run:
    python -m services.ml.scripts.init_db_and_backfill
"""

from __future__ import annotations

import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from sqlalchemy import create_engine, select, func, text
from sqlalchemy.orm import Session, sessionmaker
from dotenv import load_dotenv

# Import backend models
from ...api.models.db import (
    Base,
    Project,
    ProjectSnapshot,
    RiskScore,
    PredictionEvidence,
)

# Import our ML inference
from ..inference.predict import predict_risk
from ..config import DATA_PROCESSED_DIR


# ------------------------------------------------------------------------
# ENGINE
# ------------------------------------------------------------------------

def _sync_database_url() -> str:
    """Convert async URL to sync URL for psycopg2."""
    load_dotenv()
    url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/projectpulse",
    )
    # Convert asyncpg -> psycopg2
    if "+asyncpg" in url:
        url = url.replace("+asyncpg", "+psycopg2")
    return url


def _build_session() -> Session:
    engine = create_engine(_sync_database_url(), echo=False, future=True)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    return SessionLocal()


# ------------------------------------------------------------------------
# SCHEMA
# ------------------------------------------------------------------------

def create_schema(session: Session) -> None:
    """Create all tables from db.py models. Idempotent."""
    engine = session.get_bind()
    Base.metadata.create_all(engine)
    print("  [OK] Schema created (or already exists)")


# ------------------------------------------------------------------------
# PROJECTS
# ------------------------------------------------------------------------

def _to_date(value) -> date:
    """Coerce to Python date."""
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, pd.Timestamp):
        return value.date()
    if isinstance(value, str):
        return date.fromisoformat(value[:10])
    raise TypeError(f"Cannot coerce {value!r} to date")


def backfill_projects(session: Session, snapshots: pd.DataFrame) -> int:
    """Insert one row per unique project_id."""
    existing = session.execute(select(func.count(Project.project_id))).scalar() or 0
    if existing > 0:
        print(f"  [SKIP] projects table already has {existing} rows")
        return existing

    # Take first snapshot per project as the "project master"
    first_rows = snapshots.sort_values(["project_id", "report_month"]).groupby(
        "project_id", as_index=False
    ).head(1)

    inserted = 0
    for _, row in first_rows.iterrows():
        proj = Project(
            project_id=str(row["project_id"]),
            project_name=str(row.get("project_name", f"Project {row['project_id']}")),
            sector=str(row.get("sector", "Unknown")),
            ministry=str(row.get("ministry", "Unknown")),
            state=str(row.get("state", "Unknown")),
            implementing_agency=None,
            original_cost=float(row["original_cost"]),
            approval_date=_to_date(row["approval_date"]),
            original_completion_date=_to_date(row["original_completion_date"]),
            first_seen_report_month=_to_date(row["report_month"]),
        )
        session.add(proj)
        inserted += 1

    session.commit()
    print(f"  [OK] Inserted {inserted} projects")
    return inserted


# ------------------------------------------------------------------------
# SNAPSHOTS
# ------------------------------------------------------------------------

def backfill_snapshots(session: Session, snapshots: pd.DataFrame) -> int:
    """Insert all snapshots into project_snapshots."""
    existing = session.execute(select(func.count(ProjectSnapshot.snapshot_id))).scalar() or 0
    if existing > 0:
        print(f"  [SKIP] project_snapshots table already has {existing} rows")
        return existing

    # Get all valid project_ids from the projects table
    valid_pids = {
        r[0] for r in session.execute(select(Project.project_id)).all()
    }

    inserted = 0
    BATCH = 1000
    batch = []
    for _, row in snapshots.iterrows():
        pid = str(row["project_id"])
        if pid not in valid_pids:
            continue
        snap = ProjectSnapshot(
            project_id=pid,
            report_month=_to_date(row["report_month"]),
            revised_cost=float(row.get("revised_cost", row["original_cost"])),
            cumulative_expenditure=float(row.get("cumulative_expenditure", 0.0)),
            physical_progress=float(row.get("physical_progress", 0.0)),
            latest_revised_completion_date=_to_date(row["latest_revised_completion_date"]),
            project_status=str(row.get("project_status", "In Progress")),
            delay_reason_text=str(row.get("delay_reason_text", "") or ""),
            source_file="synthetic:generate_synthetic.py",
            parser_version="v1",
        )
        batch.append(snap)
        if len(batch) >= BATCH:
            session.add_all(batch)
            session.commit()
            inserted += len(batch)
            batch = []

    if batch:
        session.add_all(batch)
        session.commit()
        inserted += len(batch)

    print(f"  [OK] Inserted {inserted} snapshots")
    return inserted


# ------------------------------------------------------------------------
# RISK SCORES + EVIDENCE
# ------------------------------------------------------------------------

def backfill_risk_scores(session: Session, snapshots: pd.DataFrame) -> int:
    """Run predictions for latest snapshot per project, insert risk_scores."""
    existing = session.execute(select(func.count(RiskScore.risk_id))).scalar() or 0
    if existing > 0:
        print(f"  [SKIP] risk_scores table already has {existing} rows")
        return existing

    inserted = 0
    evidence_rows = 0
    snapshots_sorted = snapshots.sort_values(["project_id", "report_month"]).reset_index(drop=True)

    for pid, group in snapshots_sorted.groupby("project_id"):
        group = group.sort_values("report_month").reset_index(drop=True)
        latest = group.iloc[-1].to_dict()
        history = group.iloc[:-1].to_dict("records")

        try:
            result = predict_risk(latest, history=history)
        except Exception as e:
            print(f"  [WARN] Prediction failed for {pid}: {e}")
            continue

        rs = RiskScore(
            project_id=result["project_id"],
            report_month=_to_date(result["report_month"]),
            model_version=result["model_version"],
            cost_risk=result["cost_risk"],
            schedule_risk=result["schedule_risk"],
            trajectory_risk=result["trajectory_risk"],
            composite_score=result["composite_score"],
            tier=result["tier"],
            predicted_cost_overrun_pct=result["predicted_cost_overrun_pct"],
            predicted_delay_months=result["predicted_delay_months"],
            prob_cost_overrun_gt_10pct=result["prob_cost_overrun_gt_10pct"],
            prob_cost_overrun_gt_20pct=result["prob_cost_overrun_gt_20pct"],
            prob_delay_gt_3mo=result["prob_delay_gt_3mo"],
            prob_delay_gt_6mo=result["prob_delay_gt_6mo"],
            prob_delay_gt_12mo=result["prob_delay_gt_12mo"],
            confidence_score=result["confidence_score"],
            intervention_priority=result["intervention_priority"],
            top_drivers=result["top_drivers"],
            driver_summary=result["driver_summary"],
            risk_previous=result.get("risk_previous"),
            risk_delta=result.get("risk_delta"),
            risk_acceleration=result.get("risk_acceleration"),
            inference_time_ms=result["inference_time_ms"],
        )
        session.add(rs)
        session.flush()  # get risk_id

        # Evidence rows
        for d in result.get("top_drivers", [])[:3]:
            ev = PredictionEvidence(
                project_id=result["project_id"],
                report_month=_to_date(result["report_month"]),
                risk_id=rs.risk_id,
                feature_name=str(d["feature"])[:64],
                observed_value=float(d.get("value", 0.0)),
                reference_value=None,
                contribution=float(d.get("contribution", 0.0)),
                direction="positive" if d.get("direction") == "increase" else "negative",
                evidence_text=f"{d['feature']} contributed {d['contribution']:.4f}",
            )
            session.add(ev)
            evidence_rows += 1

        inserted += 1

    session.commit()
    print(f"  [OK] Inserted {inserted} risk_scores")
    print(f"  [OK] Inserted {evidence_rows} prediction_evidence rows")
    return inserted


# ------------------------------------------------------------------------
# VERIFY
# ------------------------------------------------------------------------

def print_summary(session: Session) -> None:
    counts = {
        "ministries":          session.execute(select(func.count()).select_from(text("ministries"))).scalar() or 0,
        "sectors":             session.execute(select(func.count()).select_from(text("sectors"))).scalar() or 0,
        "states":              session.execute(select(func.count()).select_from(text("states"))).scalar() or 0,
        "projects":            session.execute(select(func.count(Project.project_id))).scalar() or 0,
        "project_snapshots":   session.execute(select(func.count(ProjectSnapshot.snapshot_id))).scalar() or 0,
        "risk_scores":         session.execute(select(func.count(RiskScore.risk_id))).scalar() or 0,
        "prediction_evidence": session.execute(select(func.count(PredictionEvidence.evidence_id))).scalar() or 0,
    }
    print()
    print("=" * 60)
    print("DATABASE SUMMARY")
    print("=" * 60)
    for k, v in counts.items():
        print(f"  {k:24s}  {v:>10,} rows")
    print()

    # Tier distribution
    tier_rows = session.execute(
        select(RiskScore.tier, func.count(RiskScore.risk_id))
        .group_by(RiskScore.tier)
    ).all()
    if tier_rows:
        print("Tier distribution:")
        for tier, count in sorted(tier_rows, key=lambda x: x[1], reverse=True):
            print(f"  {tier:12s}  {count:>5}")
        print()

    # Sample critical project
    sample = session.execute(
        select(RiskScore, Project)
        .join(Project, Project.project_id == RiskScore.project_id)
        .where(RiskScore.tier == "Critical")
        .limit(1)
    ).first()
    if sample:
        rs, proj = sample
        print("Sample Critical project:")
        print(f"  {proj.project_id} — {proj.project_name}")
        print(f"  composite_score: {rs.composite_score}")
        print(f"  cost_risk:       {rs.cost_risk}")
        print(f"  schedule_risk:   {rs.schedule_risk}")
        print(f"  top_drivers:     {rs.top_drivers}")
    else:
        print("No Critical projects in DB.")


# ------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("ProjectPulse AI -- DB Init + Backfill")
    print("=" * 60)
    print(f"Sync DB URL: {_sync_database_url().split('@')[-1]}")
    print()

    snap_path = DATA_PROCESSED_DIR / "snapshots.parquet"
    if not snap_path.exists():
        raise FileNotFoundError(f"Missing {snap_path}. Run generate_synthetic first.")
    snapshots = pd.read_parquet(snap_path)
    print(f"Loaded {len(snapshots):,} snapshots ({snapshots['project_id'].nunique()} projects)")
    print()

    session = _build_session()
    try:
        print("Step 1: Create schema")
        create_schema(session)
        print()

        print("Step 2: Backfill projects")
        backfill_projects(session, snapshots)
        print()

        print("Step 3: Backfill snapshots")
        backfill_snapshots(session, snapshots)
        print()

        print("Step 4: Backfill risk_scores + prediction_evidence")
        backfill_risk_scores(session, snapshots)
        print()

        print("Step 5: Verify")
        print_summary(session)
    finally:
        session.close()

    print()
    print("=" * 60)
    print("BACKFILL COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
