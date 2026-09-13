import type {
  Alert,
  AssistantResponse,
  CounterfactualResult,
  DashboardSummary,
  Intervention,
  Project,
  RiskScore,
} from '@/types/api'

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api/v1'

export class ApiError extends Error {
  status: number
  statusText: string

  constructor(message: string, status: number, statusText: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.statusText = statusText
  }
}

export async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers ?? {}),
    },
    ...options,
  })

  if (!res.ok) {
    let message = res.statusText
    try {
      const body = await res.json()
      if (body?.detail) message = body.detail
      else if (body?.error?.message) message = body.error.message
    } catch {
      // ignore non-JSON error bodies
    }
    throw new ApiError(message, res.status, res.statusText)
  }

  return (await res.json()) as T
}

export interface ProjectFilters {
  sector?: string
  ministry?: string
  state?: string
  tier?: 'critical' | 'high' | 'moderate' | 'stable'
  search?: string
  page?: number
  limit?: number
}

export interface AlertFilters {
  severity?: 'critical' | 'high' | 'moderate'
  status?: string
}

export interface SimulationPerturbations {
  budget?: number
  clearance?: number
  mobilization?: number
  [key: string]: number | undefined
}

export interface CreateInterventionInput {
  project_id: string
  alert_id?: number
  owner: string
  category: string
  action_description: string
  status: string
  due_date?: string
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const res = await fetchApi<Record<string, any>>('/dashboard/summary')
  return {
    total_projects: res.total_projects ?? 0,
    critical_count: res.critical_count ?? 0,
    high_count: res.high_count ?? 0,
    moderate_count: res.moderate_count ?? 0,
    stable_count: res.stable_count ?? 0,
    portfolio_value: res.portfolio_value ?? res.total_cost_cr ?? 0,
    capital_at_risk: res.capital_at_risk ?? res.capital_at_risk_cr ?? 0,
  }
}

export async function getProjects(
  filters?: ProjectFilters,
): Promise<Project[]> {
  const params = new URLSearchParams()
  if (filters?.sector) params.set('sector', filters.sector)
  if (filters?.ministry) params.set('ministry', filters.ministry)
  if (filters?.state) params.set('state', filters.state)
  if (filters?.tier) params.set('tier', filters.tier)
  if (filters?.search) params.set('search', filters.search)
  if (filters?.page) params.set('page', String(filters.page))
  if (filters?.limit) params.set('limit', String(filters.limit))

  const query = params.toString()
  const res = await fetchApi<any>(`/projects${query ? `?${query}` : ''}`)
  if (Array.isArray(res)) return res
  if (res && Array.isArray(res.data)) return res.data
  return []
}

export function getProject(id: string): Promise<Project> {
  return fetchApi<Project>(`/projects/${id}`)
}

export function getProjectRiskHistory(
  id: string,
): Promise<RiskScore[]> {
  return fetchApi<RiskScore[]>(`/projects/${id}/risk-history`)
}

export function getProjectDrivers(id: string): Promise<RiskScore> {
  return fetchApi<RiskScore>(`/projects/${id}/drivers`)
}

export async function simulateProject(
  id: string,
  perturbations: SimulationPerturbations,
  target: string = 'schedule',
): Promise<CounterfactualResult> {
  const cleanPerturbations: Record<string, number> = {}
  for (const [k, v] of Object.entries(perturbations)) {
    if (typeof v === 'number') {
      cleanPerturbations[k] = v
    }
  }

  return fetchApi<CounterfactualResult>('/risk/what-if', {
    method: 'POST',
    body: JSON.stringify({
      project_id: id,
      perturbations: cleanPerturbations,
      target,
    }),
  })
}

export async function getAlerts(filters?: AlertFilters): Promise<Alert[]> {
  const params = new URLSearchParams()
  if (filters?.severity) params.set('severity', filters.severity)
  if (filters?.status) params.set('status', filters.status)

  const query = params.toString()
  const res = await fetchApi<any>(`/alerts${query ? `?${query}` : ''}`)
  if (Array.isArray(res)) return res
  if (res && Array.isArray(res.alerts)) return res.alerts
  return []
}

export function acknowledgeAlert(id: number): Promise<Alert> {
  return fetchApi<Alert>(`/alerts/${id}/acknowledge`, { method: 'POST' })
}

export function getInterventions(projectId?: string): Promise<Intervention[]> {
  const params = new URLSearchParams()
  if (projectId) params.set('project_id', projectId)
  const query = params.toString()
  return fetchApi<Intervention[]>(`/interventions${query ? `?${query}` : ''}`)
}

export function createIntervention(
  data: CreateInterventionInput,
): Promise<Intervention> {
  return fetchApi<Intervention>('/interventions', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function queryAssistant(
  query: string,
): Promise<AssistantResponse> {
  return fetchApi<AssistantResponse>('/assistant/query', {
    method: 'POST',
    body: JSON.stringify({ query }),
  })
}
