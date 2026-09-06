import { useQuery } from '@tanstack/react-query'
import {
  getProject,
  getProjectDrivers,
  getProjectRiskHistory,
  getProjects,
  simulateProject,
  type ProjectFilters,
  type SimulationPerturbations,
} from '@/lib/api-client'
import {
  mockProject,
  mockProjectDrivers,
  mockProjectRiskHistory,
  mockProjects,
  mockSimulateProject,
} from '@/lib/mock-data'

const useMockData = process.env.NEXT_PUBLIC_USE_MOCK_DATA !== 'false'

export function useProjects(filters?: ProjectFilters) {
  return useQuery({
    queryKey: ['projects', filters],
    queryFn: () =>
      useMockData ? mockProjects(filters) : getProjects(filters),
  })
}

export function useProject(id: string) {
  return useQuery({
    queryKey: ['project', id],
    enabled: Boolean(id),
    queryFn: () => (useMockData ? mockProject(id) : getProject(id)),
  })
}

export function useProjectRiskHistory(id: string) {
  return useQuery({
    queryKey: ['project-risk-history', id],
    enabled: Boolean(id),
    queryFn: () =>
      useMockData
        ? mockProjectRiskHistory(id)
        : getProjectRiskHistory(id),
  })
}

export function useProjectDrivers(id: string) {
  return useQuery({
    queryKey: ['project-drivers', id],
    enabled: Boolean(id),
    queryFn: () =>
      useMockData ? mockProjectDrivers(id) : getProjectDrivers(id),
  })
}

export function useSimulateProject(
  id: string,
  perturbations: SimulationPerturbations,
  enabled = false,
) {
  return useQuery({
    queryKey: ['project-simulate', id, perturbations],
    enabled,
    queryFn: () =>
      useMockData
        ? mockSimulateProject(id, perturbations)
        : simulateProject(id, perturbations),
  })
}
