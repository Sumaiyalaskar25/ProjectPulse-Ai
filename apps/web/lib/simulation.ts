export interface SimulationInput {
  budget: number
  clearance: number
  mobilization: number
}

export interface SimulationChartPoint {
  month: string
  baseline: number
  green: number | null
  red: number | null
}

export interface SimulationResult {
  riskScore: number
  delayMonths: number
  confidence: number
  chart: SimulationChartPoint[]
}

export const DEFAULT_SIMULATION_INPUT: SimulationInput = {
  budget: 15,
  clearance: 4,
  mobilization: 50,
}

const BASELINE_RISK = 88
const BASELINE_DELAY = 18

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value))
}

export async function runSimulation(
  input: SimulationInput,
): Promise<SimulationResult> {
  await new Promise((resolve) => setTimeout(resolve, 900))

  const budgetEff = clamp(input.budget, 0, 50) / 50
  const clearanceEff = clamp(input.clearance, 0, 12) / 12
  const mobilizationEff = clamp(input.mobilization, 0, 100) / 100
  const eff = 0.5 * budgetEff + 0.35 * clearanceEff + 0.65 * mobilizationEff

  const riskScore = Math.round(
    Math.max(15, BASELINE_RISK - BASELINE_RISK * 0.65 * eff),
  )
  const delayMonths = Math.max(
    3,
    Math.round(BASELINE_DELAY - BASELINE_DELAY * 0.99 * eff),
  )

  const successBase = clamp(100 - riskScore, 30, 85)
  const chart: SimulationChartPoint[] = [
    { month: 'M1', baseline: 38, green: successBase - 8, red: null },
    { month: 'M2', baseline: 42, green: successBase - 4, red: null },
    { month: 'M3', baseline: 37, green: successBase + 1, red: null },
    { month: 'M4', baseline: 45, green: successBase + 5, red: null },
    { month: 'M5', baseline: 41, green: successBase + 9, red: null },
    { month: 'M6', baseline: 36, green: successBase + 12, red: successBase + 12 },
    { month: 'M7', baseline: 44, green: null, red: successBase + 7 },
    { month: 'M8', baseline: 40, green: null, red: successBase + 9 },
    { month: 'M9', baseline: 35, green: null, red: successBase + 2 },
    { month: 'M10', baseline: 42, green: null, red: successBase - 4 },
  ]

  return {
    riskScore,
    delayMonths,
    confidence: 94.2,
    chart,
  }
}