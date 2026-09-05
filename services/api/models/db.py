from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Text,
    Float,
    Date,
    DateTime,
    Boolean,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# ==================== MASTER TABLES ====================

class Ministry(Base):
    __tablename__ = 'ministries'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    code = Column(String(16))

class Sector(Base):
    __tablename__ = 'sectors'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)

class State(Base):
    __tablename__ = 'states'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    code = Column(String(4))

# ==================== PROJECTS ====================

class Project(Base):
    __tablename__ = 'projects'
    project_id = Column(String(64), primary_key=True)
    project_name = Column(Text, nullable=False)
    sector = Column(String(64))  # Denormalized for speed
    ministry = Column(String(128))
    state = Column(String(64))
    implementing_agency = Column(String(128))
    original_cost = Column(Float)
    approval_date = Column(Date)
    original_completion_date = Column(Date)
    first_seen_report_month = Column(Date)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_projects_sector', 'sector'),
        Index('idx_projects_ministry', 'ministry'),
        Index('idx_projects_state', 'state'),
    )

# ==================== SNAPSHOTS (TimescaleDB Hypertable) ====================

class ProjectSnapshot(Base):
    __tablename__ = 'project_snapshots'
    snapshot_id = Column(BigInteger, primary_key=True)
    project_id = Column(String(64), ForeignKey('projects.project_id'))
    report_month = Column(Date, nullable=False)
    
    # Core fields
    revised_cost = Column(Float)
    cumulative_expenditure = Column(Float)
    physical_progress = Column(Float)  # 0-100
    latest_revised_completion_date = Column(Date)
    project_status = Column(String(32))
    delay_reason_text = Column(Text)
    
    # Lineage
    source_file = Column(String(256))
    source_page = Column(Integer)
    source_row = Column(Integer)
    source_hash = Column(String(64))
    parser_version = Column(String(16))
    ingestion_run_id = Column(BigInteger, ForeignKey('ingestion_runs.run_id'))
    
    ingested_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        UniqueConstraint('project_id', 'report_month', name='uq_project_month'),
        Index('idx_snapshots_project_month', 'project_id', 'report_month'),
        Index('idx_snapshots_report_month', 'report_month'),
    )

# TimescaleDB hypertable creation (run separately)
# SELECT create_hypertable('project_snapshots', 'report_month');

# ==================== FEATURES ====================

class ProjectFeature(Base):
    __tablename__ = 'project_features'
    feature_id = Column(BigInteger, primary_key=True)
    project_id = Column(String(64), ForeignKey('projects.project_id'))
    report_month = Column(Date, nullable=False)
    feature_version = Column(String(32))
    
    # All features as JSONB (flexible, Member 1 defines schema)
    features = Column(JSONB)  # e.g., {"cost_burn_ratio": 1.2, "progress_velocity_3m": 5.4}
    
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        UniqueConstraint('project_id', 'report_month', 'feature_version', name='uq_project_month_feature'),
        Index('idx_features_project_month', 'project_id', 'report_month'),
    )

# ==================== RISK SCORES ====================

class RiskScore(Base):
    __tablename__ = 'risk_scores'
    risk_id = Column(BigInteger, primary_key=True)
    project_id = Column(String(64), ForeignKey('projects.project_id'))
    report_month = Column(Date, nullable=False)
    model_version = Column(String(32), nullable=False)
    
    # Component risks (0-100)
    cost_risk = Column(Float)
    schedule_risk = Column(Float)
    trajectory_risk = Column(Float)
    composite_score = Column(Float)  # P-Score
    
    tier = Column(String(16))  # Critical/High/Moderate/Stable
    
    # Forecasts
    predicted_cost_overrun_pct = Column(Float)
    predicted_delay_months = Column(Float)
    predicted_completion_date = Column(Date)
    
    # Probabilities
    prob_cost_overrun_gt_10pct = Column(Float)
    prob_cost_overrun_gt_20pct = Column(Float)
    prob_delay_gt_3mo = Column(Float)
    prob_delay_gt_6mo = Column(Float)
    prob_delay_gt_12mo = Column(Float)
    
    # Confidence & Priority
    confidence_score = Column(Float)  # 0-1
    intervention_priority = Column(Float)  # 0-100
    
    # Drivers (SHAP top-N)
    top_drivers = Column(JSONB)  # [{feature, contribution, direction}]
    driver_summary = Column(Text)
    
    # Risk trajectory (for change detection)
    risk_previous = Column(Float)
    risk_delta = Column(Float)
    risk_acceleration = Column(Float)
    
    # Metadata
    prediction_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    inference_time_ms = Column(Integer)
    
    __table_args__ = (
        UniqueConstraint('project_id', 'report_month', 'model_version', name='uq_project_month_model'),
        Index('idx_risk_project', 'project_id', 'report_month'),
        Index('idx_risk_tier', 'tier'),
        Index('idx_risk_priority', 'intervention_priority'),
        Index('idx_risk_composite', 'composite_score'),
    )

# ==================== PREDICTION EVIDENCE ====================

class PredictionEvidence(Base):
    __tablename__ = 'prediction_evidence'
    evidence_id = Column(BigInteger, primary_key=True)
    project_id = Column(String(64), ForeignKey('projects.project_id'))
    report_month = Column(Date, nullable=False)
    risk_id = Column(BigInteger, ForeignKey('risk_scores.risk_id'))
    
    feature_name = Column(String(64))
    observed_value = Column(Float)
    reference_value = Column(Float)
    contribution = Column(Float)
    direction = Column(String(8))  # positive/negative
    
    source_snapshot_id = Column(BigInteger)
    source_file = Column(String(256))
    source_page = Column(Integer)
    source_row = Column(Integer)
    
    evidence_text = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_evidence_risk', 'risk_id'),
        Index('idx_evidence_project', 'project_id'),
    )

# ==================== ALERTS ====================

class Alert(Base):
    __tablename__ = 'alerts'
    alert_id = Column(BigInteger, primary_key=True)
    project_id = Column(String(64), ForeignKey('projects.project_id'))
    risk_id = Column(BigInteger, ForeignKey('risk_scores.risk_id'))
    
    alert_type = Column(String(32))  # risk_escalation / rapid_deterioration / etc.
    severity = Column(String(16))  # critical/high/moderate
    title = Column(String(255))
    description = Column(Text)
    
    # Risk before/after
    risk_previous = Column(Float)
    risk_current = Column(Float)
    risk_delta = Column(Float)
    
    trigger_condition = Column(JSONB)  # What triggered this alert
    
    triggered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    acknowledged_at = Column(DateTime)
    assigned_to = Column(String(64))
    status = Column(String(32), default='open')  # open/acknowledged/in_review/resolved/closed
    
    change_summary = Column(JSONB)  # {metric: {before, after}}
    primary_driver = Column(Text)
    evidence_ids = Column(JSONB)  # Array of evidence IDs
    
    intervention_id = Column(BigInteger, ForeignKey('interventions.intervention_id'))
    
    __table_args__ = (
        Index('idx_alerts_project', 'project_id'),
        Index('idx_alerts_status', 'status'),
        Index('idx_alerts_triggered', 'triggered_at'),
        Index('idx_alerts_severity', 'severity'),
        UniqueConstraint('project_id', 'alert_type', 'triggered_at', name='uq_alert_dedup'),
    )

# ==================== INTERVENTIONS ====================

class Intervention(Base):
    __tablename__ = 'interventions'
    intervention_id = Column(BigInteger, primary_key=True)
    project_id = Column(String(64), ForeignKey('projects.project_id'))
    alert_id = Column(BigInteger, ForeignKey('alerts.alert_id'))
    
    owner = Column(String(64))
    owner_role = Column(String(32))
    created_by = Column(String(64))
    
    category = Column(String(32))  # schedule_review / cost_optimization / etc.
    action_description = Column(Text)
    action_plan = Column(JSONB)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    assigned_at = Column(DateTime)
    acknowledged_at = Column(DateTime)
    started_at = Column(DateTime)
    due_date = Column(Date)
    resolved_at = Column(DateTime)
    closed_at = Column(DateTime)
    
    status = Column(String(32), default='pending')  # pending/acknowledged/in_progress/resolved/closed/overdue
    resolution = Column(Text)
    resolution_evidence = Column(JSONB)
    
    # For learning loop
    predicted_impact_pct = Column(Float)
    outcome_rating = Column(String(16))  # successful/partial/unsuccessful
    
    __table_args__ = (
        Index('idx_interventions_project', 'project_id'),
        Index('idx_interventions_status', 'status'),
        Index('idx_interventions_due', 'due_date'),
        Index('idx_interventions_owner', 'owner'),
    )

# ==================== INTERVENTION OUTCOMES ====================

class InterventionOutcome(Base):
    __tablename__ = 'intervention_outcomes'
    outcome_id = Column(BigInteger, primary_key=True)
    intervention_id = Column(BigInteger, ForeignKey('interventions.intervention_id'))
    project_id = Column(String(64), ForeignKey('projects.project_id'))
    
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    outcome_rating = Column(String(16))
    outcome_description = Column(Text)
    
    risk_before = Column(Float)
    risk_after = Column(Float)
    risk_improvement = Column(Float)
    
    cost_impact = Column(JSONB)  # {"predicted": X, "actual": Y}
    schedule_impact = Column(JSONB)
    
    evidence = Column(JSONB)
    lessons_learned = Column(Text)
    
    __table_args__ = (
        Index('idx_outcomes_intervention', 'intervention_id'),
        Index('idx_outcomes_project', 'project_id'),
    )

# ==================== MODEL REGISTRY ====================

class ModelRegistry(Base):
    __tablename__ = 'model_registry'
    model_id = Column(Integer, primary_key=True)
    model_version = Column(String(32), unique=True, nullable=False)
    model_type = Column(String(32))  # baseline/lgb/xgb/ensemble
    
    dataset_version = Column(String(32))
    feature_version = Column(String(32))
    training_cutoff = Column(Date)
    prediction_horizon = Column(Integer)  # months
    validation_start = Column(Date)
    validation_end = Column(Date)
    test_start = Column(Date)
    test_end = Column(Date)
    
    metrics = Column(JSONB)  # {cost: {mae, rmse, r2}, schedule: {f1, auc}}
    artifact_path = Column(Text)
    
    status = Column(String(16), default='staging')  # staging/production/archived
    is_active = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    deployed_at = Column(DateTime)
    
    __table_args__ = (
        Index('idx_model_version', 'model_version'),
        Index('idx_model_active', 'is_active'),
    )

# ==================== MODEL RUNS ====================

class ModelRun(Base):
    __tablename__ = 'model_runs'
    run_id = Column(BigInteger, primary_key=True)
    model_version = Column(String(32), ForeignKey('model_registry.model_version'))
    run_type = Column(String(16))  # training/backtest/inference
    
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    status = Column(String(16))  # running/completed/failed
    
    metrics = Column(JSONB)
    error_message = Column(Text)
    
    rows_processed = Column(Integer)
    inference_time_ms = Column(Integer)
    
    __table_args__ = (
        Index('idx_runs_model', 'model_version'),
        Index('idx_runs_status', 'status'),
    )

# ==================== INGESTION RUNS ====================

class IngestionRun(Base):
    __tablename__ = 'ingestion_runs'
    run_id = Column(BigInteger, primary_key=True)
    
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime)
    status = Column(String(16), default='running')  # running/completed/failed
    
    source_type = Column(String(16))  # dashboard/flash_report
    report_month = Column(Date)
    
    rows_downloaded = Column(Integer)
    rows_parsed = Column(Integer)
    rows_loaded = Column(Integer)
    rows_rejected = Column(Integer)
    
    errors = Column(JSONB)
    run_metadata = Column('metadata', JSONB)
    
    triggered_by = Column(String(64))
    
    __table_args__ = (
        Index('idx_ingestion_status', 'status'),
        Index('idx_ingestion_month', 'report_month'),
    )

# ==================== INGESTION FILES (for manifest) ====================

class IngestionFile(Base):
    __tablename__ = 'ingestion_files'
    file_id = Column(BigInteger, primary_key=True)
    run_id = Column(BigInteger, ForeignKey('ingestion_runs.run_id'))
    
    source_url = Column(Text)
    local_path = Column(Text)
    file_hash = Column(String(64))
    file_size = Column(Integer)
    
    file_type = Column(String(16))  # json/xlsx/pdf
    report_month = Column(Date)
    file_metadata = Column('metadata', JSONB)
    
    downloaded_at = Column(DateTime)
    
    __table_args__ = (
        UniqueConstraint('source_url', name='uq_file_url'),
        Index('idx_files_hash', 'file_hash'),
    )

# ==================== AUDIT LOGS ====================

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    log_id = Column(BigInteger, primary_key=True)
    user_id = Column(String(64))
    user_role = Column(String(32))
    
    action = Column(String(64))  # alert_acknowledged / intervention_created / etc.
    resource = Column(String(64))  # projects/alerts/interventions
    resource_id = Column(String(64))
    
    details = Column(JSONB)
    before_state = Column(JSONB)
    after_state = Column(JSONB)
    
    ip_address = Column(String(45))
    user_agent = Column(Text)
    request_id = Column(String(64))
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_audit_user', 'user_id'),
        Index('idx_audit_action', 'action'),
        Index('idx_audit_created', 'created_at'),
        Index('idx_audit_resource', 'resource', 'resource_id'),
    )
