import type {
  Alert,
  AssistantResponse,
  CounterfactualResult,
  DashboardSummary,
  Intervention,
  Project,
  RiskScore,
} from '@/types/api'
import type {
  ProjectFilters,
  AlertFilters,
  SimulationPerturbations,
  CreateInterventionInput,
} from './api-client'

/**
 * MOCK DATA MODE
 * -----------------
 * These functions return hard-coded data mirroring what the backend
 * endpoints will eventually return. One function per API client function
 * (see lib/api-client.ts) so they are swappable one-to-one. The React
 * Query hooks select between these and the live API client based on the
 * NEXT_PUBLIC_USE_MOCK_DATA environment variable.
 */

export function mockDashboardSummary(): Promise<DashboardSummary> {
  return Promise.resolve({
    total_projects: 1775,
    critical_count: 142,
    high_count: 318,
    moderate_count: 589,
    stable_count: 726,
    portfolio_value: 14200,
    capital_at_risk: 3800,
  })
}

const MOCK_PROJECTS: Project[] = [
  {
    project_id: 'ASSET-NH44-001',
    project_name: 'NH-44 Expressway Extension (VII)',
    sector: 'Road Transport & Highways',
    ministry: 'Road Transport & Highways',
    state: 'Uttar Pradesh',
    original_cost: 12000000000,
    approval_date: '2023-01-15',
    original_completion_date: '2024-12-01',
  },
  {
    project_id: 'METRO-MUM-P3',
    project_name: 'Mumbai Metro Phase 3 - Line 1',
    sector: 'Urban Development',
    ministry: 'Urban Development',
    state: 'Maharashtra',
    original_cost: 48000000000,
    approval_date: '2023-03-10',
    original_completion_date: '2025-06-01',
  },
  {
    project_id: 'GRID-CHEN-04',
    project_name: 'Chennai Smart Grid Expansion',
    sector: 'Power & Energy',
    ministry: 'Power & Energy',
    state: 'Tamil Nadu',
    original_cost: 8000000000,
    approval_date: '2023-02-20',
    original_completion_date: '2025-03-01',
  },
  {
    project_id: 'PORT-KOL-EXT',
    project_name: 'Kolkata Deep Water Port',
    sector: 'Ports & Shipping',
    ministry: 'Ports & Shipping',
    state: 'West Bengal',
    original_cost: 21000000000,
    approval_date: '2022-11-05',
    original_completion_date: '2024-12-01',
  },
  {
    project_id: 'WATER-GAN-IX',
    project_name: 'Ganges Basin Treatment Node',
    sector: 'Jal Shakti',
    ministry: 'Jal Shakti',
    state: 'Uttar Pradesh',
    original_cost: 5000000000,
    approval_date: '2023-04-12',
    original_completion_date: '2025-09-01',
  },
  {
    project_id: 'SOLAR-PUNE-01',
    project_name: 'Pune Photovoltaic Cluster',
    sector: 'New & Renewable Energy',
    ministry: 'New & Renewable Energy',
    state: 'Maharashtra',
    original_cost: 3000000000,
    approval_date: '2023-01-05',
    original_completion_date: '2024-10-01',
  },
  {
    project_id: 'RAIL-DFCC-EAST',
    project_name: 'Dedicated Freight Corridor',
    sector: 'Railways',
    ministry: 'Railways',
    state: 'Gujarat',
    original_cost: 125000000000,
    approval_date: '2022-12-01',
    original_completion_date: '2026-03-01',
  },
]

export function mockProjects(
  _filters?: ProjectFilters,
): Promise<Project[]> {
  return Promise.resolve(MOCK_PROJECTS)
}

export function mockProject(id: string): Promise<Project> {
  const project = MOCK_PROJECTS.find((p) => p.project_id === id)
  if (!project) return Promise.reject(new Error(`Project ${id} not found`))
  return Promise.resolve(project)
}

const MOCK_RISK_HISTORY: RiskScore[] = [
  {
    risk_id: 1,
    project_id: 'ASSET-NH44-001',
    report_month: '2023-05-01',
    cost_risk: 55,
    schedule_risk: 61,
    trajectory_risk: 68,
    composite_score: 75,
    tier: 'critical',
    confidence_score: 92,
    intervention_priority: 1,
    top_drivers: [
      { feature: 'Land Acquisition', contribution: 92 },
      { feature: 'Env. Clearance', contribution: 68 },
      { feature: 'Utility Shifting', contribution: 41 },
    ],
    risk_delta: 18,
    predicted_delay_months: 18,
    predicted_cost_overrun_pct: 34.2,
  },
  {
    risk_id: 2,
    project_id: 'ASSET-NH44-001',
    report_month: '2023-06-01',
    cost_risk: 58,
    schedule_risk: 64,
    trajectory_risk: 71,
    composite_score: 78,
    tier: 'critical',
    confidence_score: 93,
    intervention_priority: 1,
    top_drivers: [
      { feature: 'Land Acquisition', contribution: 94 },
      { feature: 'Env. Clearance', contribution: 70 },
      { feature: 'Contractor Perf.', contribution: -24 },
    ],
    risk_delta: 19,
    predicted_delay_months: 19,
    predicted_cost_overrun_pct: 35.1,
  },
  {
    risk_id: 3,
    project_id: 'ASSET-NH44-001',
    report_month: '2023-07-01',
    cost_risk: 61,
    schedule_risk: 67,
    trajectory_risk: 74,
    composite_score: 82,
    tier: 'critical',
    confidence_score: 94,
    intervention_priority: 1,
    top_drivers: [
      { feature: 'Land Acquisition', contribution: 95 },
      { feature: 'Env. Clearance', contribution: 72 },
      { feature: 'Material Supply', contribution: -12 },
    ],
    risk_delta: 18,
    predicted_delay_months: 18,
    predicted_cost_overrun_pct: 36.0,
  },
]

export function mockProjectRiskHistory(
  _id: string,
): Promise<RiskScore[]> {
  return Promise.resolve(MOCK_RISK_HISTORY)
}

export function mockProjectDrivers(_id: string): Promise<RiskScore> {
  return Promise.resolve(MOCK_RISK_HISTORY[MOCK_RISK_HISTORY.length - 1])
}

export function mockSimulateProject(
  _id: string,
  _perturbations: SimulationPerturbations,
): Promise<CounterfactualResult> {
  return Promise.resolve({
    baseline_probability: 0.34,
    counterfactual_probability: 0.58,
    delta: 0.24,
    interpretation:
      'Prioritizing Contractor Mobilization yields a 12% higher efficiency return in the Northern Corridor.',
    disclaimer:
      'Simulated estimates are counterfactual projections and should not be treated as guaranteed outcomes.',
  })
}

const MOCK_ALERTS: Alert[] = [
  {
    alert_id: 8821,
    project_id: 'ASSET-NH44-001',
    alert_type: 'CIVIL_STRUCTURAL',
    severity: 'critical',
    title: 'NH-44 Expressway Extension (VII)',
    description:
      'Anomalous vibration detected in Section VII structural pylons. Risk probability has increased significantly due to recent thermal fluctuations.',
    risk_delta: 18,
    status: 'open',
    triggered_at: '2023-10-27T12:20:00Z',
  },
  {
    alert_id: 8819,
    project_id: 'METRO-MUM-P3',
    alert_type: 'BUDGET',
    severity: 'high',
    title: 'Mumbai Metro Phase 3 - Line 1',
    description: 'Budget variance approaching threshold with escalating material costs.',
    risk_delta: 12.4,
    status: 'open',
    triggered_at: '2023-10-27T12:47:00Z',
  },
  {
    alert_id: 8817,
    project_id: 'WATER-GAN-IX',
    alert_type: 'ENVIRONMENTAL',
    severity: 'high',
    title: 'Ganges Basin Treatment Node',
    description: 'Groundwater level variances suggest potential soil instability.',
    risk_delta: 8.2,
    status: 'open',
    triggered_at: '2023-10-27T11:30:00Z',
  },
  {
    alert_id: 8815,
    project_id: 'GRID-CHEN-04',
    alert_type: 'SENSOR',
    severity: 'critical',
    title: 'Chennai Smart Grid Node Expansion',
    description: 'Sensor node 442 reporting anomalous load on expansion grid.',
    risk_delta: 24.1,
    status: 'open',
    triggered_at: '2023-10-27T13:27:00Z',
  },
  {
    alert_id: 8813,
    project_id: 'PORT-KOL-EXT',
    alert_type: 'MAINTENANCE',
    severity: 'moderate',
    title: 'Kolkata Deep Water Port Expansion',
    description: 'Routine maintenance thresholds crossed; no immediate structural risk.',
    risk_delta: -2.5,
    status: 'open',
    triggered_at: '2023-10-27T10:05:00Z',
  },
]

export function mockAlerts(_filters?: AlertFilters): Promise<Alert[]> {
  return Promise.resolve(MOCK_ALERTS)
}

export function mockAcknowledgeAlert(id: number): Promise<Alert> {
  const alert = MOCK_ALERTS.find((a) => a.alert_id === id)
  if (!alert) return Promise.reject(new Error(`Alert ${id} not found`))
  return Promise.resolve({ ...alert, status: 'acknowledged' })
}

const MOCK_INTERVENTIONS: Intervention[] = [
  {
    intervention_id: 2012,
    project_id: 'ASSET-NH44-001',
    alert_id: 8821,
    owner: 'S. Kulkarni',
    category: 'FIELD_REPAIR',
    action_description: 'NH-48 Pothole Repair Cluster 7',
    status: 'in_progress',
    due_date: '2023-11-10',
  },
  {
    intervention_id: 1094,
    project_id: 'ASSET-NH44-001',
    alert_id: 8821,
    owner: 'R. Mehta',
    category: 'STRUCTURAL',
    action_description: 'Krishna Dam Spillway Gate Actuator',
    status: 'in_progress',
    due_date: '2023-11-15',
  },
  {
    intervention_id: 5510,
    project_id: 'METRO-MUM-P3',
    alert_id: 8819,
    owner: 'A. Nair',
    category: 'MAINTENANCE',
    action_description: 'Metro Viaduct Expansion Joints',
    status: 'scheduled',
    due_date: '2023-11-20',
  },
]

export function mockInterventions(): Promise<Intervention[]> {
  return Promise.resolve(MOCK_INTERVENTIONS)
}

export function mockCreateIntervention(
  data: CreateInterventionInput,
): Promise<Intervention> {
  const intervention: Intervention = {
    intervention_id: Math.floor(Math.random() * 10000),
    project_id: data.project_id,
    alert_id: data.alert_id,
    owner: data.owner,
    category: data.category,
    action_description: data.action_description,
    status: data.status,
    due_date: data.due_date,
  }
  return Promise.resolve(intervention)
}

export function mockQueryAssistant(
  query: string,
): Promise<AssistantResponse> {
  return Promise.resolve({
    query,
    formatted_answer:
      'Based on the latest data sync, three critical projects show significant budget variances driven by land acquisition litigation and unexpected soil instability during the monsoon period.',
    data: [
      {
        project: 'NH-44 Expressway Ext.',
        budget: '4.2B Cr',
        overrun: '+34.2%',
        status: 'CRITICAL',
      },
      {
        project: 'Mumbai Metro Line 3',
        budget: '12.8B Cr',
        overrun: '+18.5%',
        status: 'AT RISK',
      },
      {
        project: 'Chennai Smart Grid',
        budget: '1.5B Cr',
        overrun: '+22.1%',
        status: 'AT RISK',
      },
    ],
    sources: ['Q3 Financial Audit', 'Land Registry v.24', 'Sensor Node 442 Logs'],
  })
}
