import { useQuery } from '@tanstack/react-query'
import { runSimulation, type SimulationInput } from '@/lib/simulation'

const useMockData = process.env.NEXT_PUBLIC_USE_MOCK_DATA !== 'false'

// The local simulation engine (lib/simulation.ts) is the current data source
// for the simulator in both modes. When the simulator page migrates to the
// live backend, swap the live branch for simulateProject() from
// lib/api-client.ts (which returns the CounterfactualResult shape).
export function useSimulation(input: SimulationInput, enabled = false) {
  return useQuery({
    queryKey: ['simulation', input],
    enabled,
    queryFn: () =>
      useMockData
        ? runSimulation(input)
        : runSimulation(input),
  })
}