import { useQuery } from '@tanstack/react-query'
import { runSimulation, type SimulationInput, type SimulationResult } from '@/lib/simulation'
import { simulateProject } from '@/lib/api-client'

const useMockData = process.env.NEXT_PUBLIC_USE_MOCK_DATA !== 'false'

export function useSimulation(
  input: SimulationInput & { projectId?: string },
  enabled = false
) {
  return useQuery<SimulationResult>({
    queryKey: ['simulation', input],
    enabled,
    queryFn: async () => {
      if (useMockData) {
        return runSimulation(input)
      }

      try {
        const projectId = input.projectId ?? 'PRJ_A'
        const cf = await simulateProject(
          projectId,
          {
            budget: input.budget,
            clearance: input.clearance,
            mobilization: input.mobilization,
          },
          'schedule'
        )

        // Convert backend CounterfactualResult to UI SimulationResult shape
        const riskScore = Math.round(cf.counterfactual_probability * 100)
        const baselineRisk = Math.round(cf.baseline_probability * 100)
        const delayMonths = Math.max(2, Math.round((riskScore / 100) * 18))
        const successBase = Math.min(85, Math.max(30, 100 - riskScore))

        return {
          riskScore,
          delayMonths,
          confidence: 95.0,
          chart: [
            { month: 'M1', baseline: baselineRisk - 10, green: successBase - 8, red: null },
            { month: 'M2', baseline: baselineRisk - 5, green: successBase - 4, red: null },
            { month: 'M3', baseline: baselineRisk, green: successBase + 1, red: null },
            { month: 'M4', baseline: baselineRisk + 5, green: successBase + 5, red: null },
            { month: 'M5', baseline: baselineRisk + 8, green: successBase + 9, red: null },
            { month: 'M6', baseline: baselineRisk + 12, green: successBase + 12, red: successBase + 12 },
            { month: 'M7', baseline: baselineRisk + 15, green: null, red: successBase + 7 },
            { month: 'M8', baseline: baselineRisk + 18, green: null, red: successBase + 9 },
            { month: 'M9', baseline: baselineRisk + 20, green: null, red: successBase + 2 },
            { month: 'M10', baseline: baselineRisk + 22, green: null, red: successBase - 4 },
          ],
        }
      } catch (err) {
        console.warn('Backend simulation call failed, using local simulation engine fallback:', err)
        return runSimulation(input)
      }
    },
  })
}