import { useQuery } from '@tanstack/react-query'
import { getDashboardSummary } from '@/lib/api-client'
import { mockDashboardSummary } from '@/lib/mock-data'

const useMockData = process.env.NEXT_PUBLIC_USE_MOCK_DATA !== 'false'

export function useDashboardSummary() {
  return useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: () =>
      useMockData ? mockDashboardSummary() : getDashboardSummary(),
  })
}
