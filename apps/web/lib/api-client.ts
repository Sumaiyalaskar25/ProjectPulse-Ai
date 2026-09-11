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
}

export interface AlertFilters {
  severity?: 'critical' | 'high' | 'moderate'
  status?: string
}

export interface SimulationPerturbations {
  budget?: number
  clearance?: number
  mobilization?: number
}

export interface CreateInterventionInput {
  project_id: string
  alert_id: number
  owner: string
  category: string
  action_description: string
  status: string
  due_date: string
}

export function getDashboardSummary(): Promise<DashboardSummary> {
  return fetchApi<DashboardSummary>('/dashboard/summary')
}

export function getProjects(
  filters?: ProjectFilters,
): Promise<Project[]> {
  const params = new URLSearchParams()
  if (filters?.sector) params.set('sector', filters.sector)
  if (filters?.ministry) params.set('ministry', filters.ministry)
  if (filters?.state) params.set('state', filters.state)
  if (filters?.tier) params.set('tier', filters.tier)

  const query = params.toString()
  return fetchApi<Project[]>(`/projects${query ? `?${query}` : ''}`)
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

export function simulateProject(
  id: string,
  perturbations: SimulationPerturbations,
): Promise<CounterfactualResult> {
  return fetchApi<CounterfactualResult>(`/projects/${id}/simulate`, {
    method: 'POST',
    body: JSON.stringify(perturbations),
  })
}

export function getAlerts(filters?: AlertFilters): Promise<Alert[]> {
  const params = new URLSearchParams()
  if (filters?.severity) params.set('severity', filters.severity)
  if (filters?.status) params.set('status', filters.status)

  const query = params.toString()
  return fetchApi<Alert[]>(`/alerts${query ? `?${query}` : ''}`)
}

export function acknowledgeAlert(id: number): Promise<Alert> {
  return fetchApi<Alert>(`/alerts/${id}/acknowledge`, { method: 'POST' })
}

export function getInterventions(): Promise<Intervention[]> {
  return fetchApi<Intervention[]>('/interventions')
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
