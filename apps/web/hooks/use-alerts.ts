import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  acknowledgeAlert,
  createIntervention,
  getAlerts,
  getInterventions,
  type AlertFilters,
  type CreateInterventionInput,
} from '@/lib/api-client'
import {
  mockAcknowledgeAlert,
  mockAlerts,
  mockCreateIntervention,
  mockInterventions,
} from '@/lib/mock-data'

const useMockData = process.env.NEXT_PUBLIC_USE_MOCK_DATA !== 'false'

export function useAlerts(filters?: AlertFilters) {
  return useQuery({
    queryKey: ['alerts', filters],
    queryFn: () => (useMockData ? mockAlerts(filters) : getAlerts(filters)),
  })
}

export function useAcknowledgeAlert() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) =>
      useMockData ? mockAcknowledgeAlert(id) : acknowledgeAlert(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })
}

export function useInterventions() {
  return useQuery({
    queryKey: ['interventions'],
    queryFn: () =>
      useMockData ? mockInterventions() : getInterventions(),
  })
}

export function useCreateIntervention() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: CreateInterventionInput) =>
      useMockData
        ? mockCreateIntervention(data)
        : createIntervention(data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['interventions'] })
    },
  })
}