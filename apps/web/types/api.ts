// API CONTRACT — this file mirrors the backend's response shapes.
// Do not edit without checking the backend PR / Member 2's schema first.

export interface Project {
  project_id: string
  project_name: string
  sector: string
  ministry: string
  state: string
  original_cost: number
  approval_date: string
  original_completion_date: string
}

export interface RiskScore {
  risk_id: number
  project_id: string
  report_month: string
  cost_risk: number
  schedule_risk: number
  trajectory_risk: number
  composite_score: number
  tier: 'critical' | 'high' | 'moderate' | 'stable'
  confidence_score: number
  intervention_priority: number
  top_drivers: { feature: string; contribution: number }[]
  risk_delta: number
  predicted_delay_months: number
  predicted_cost_overrun_pct: number
}

export interface DashboardSummary {
  total_projects: number
  critical_count: number
  high_count: number
  moderate_count: number
  stable_count: number
  portfolio_value: number
  capital_at_risk: number
}

export interface Alert {
  alert_id: number
  project_id: string
  alert_type: string
  severity: 'critical' | 'high' | 'moderate'
  title: string
  description: string
  risk_delta: number
  status: string
  triggered_at: string
}

export interface Intervention {
  intervention_id: number
  project_id: string
  alert_id: number
  owner: string
  category: string
  action_description: string
  status: string
  due_date: string
}

export interface CounterfactualResult {
  baseline_probability: number
  counterfactual_probability: number
  delta: number
  interpretation: string
  disclaimer: string
}

export interface AssistantResponse {
  query: string
  formatted_answer: string
  data: Record<string, unknown>[]
  sources: string[]
}
