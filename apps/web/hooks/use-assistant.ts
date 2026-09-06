import { useQuery } from '@tanstack/react-query'
import { queryAssistant } from '@/lib/api-client'
import { mockQueryAssistant } from '@/lib/mock-data'

const useMockData = process.env.NEXT_PUBLIC_USE_MOCK_DATA !== 'false'

export function useAssistantQuery(query: string, enabled = false) {
  return useQuery({
    queryKey: ['assistant-query', query],
    enabled: Boolean(query) && enabled,
    queryFn: () =>
      useMockData ? mockQueryAssistant(query) : queryAssistant(query),
  })
}