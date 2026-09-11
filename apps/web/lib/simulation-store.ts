import { create } from 'zustand'
import {
  DEFAULT_SIMULATION_INPUT,
  runSimulation,
  type SimulationInput,
  type SimulationResult,
} from './simulation'

interface SimulationState {
  values: SimulationInput
  result: SimulationResult | null
  running: boolean
  setValue: (key: keyof SimulationInput, value: number) => void
  reset: () => void
  run: () => Promise<void>
}

export const useSimulationStore = create<SimulationState>()((set, get) => ({
  values: DEFAULT_SIMULATION_INPUT,
  result: null,
  running: false,
  setValue: (key, value) =>
    set((state) => ({ values: { ...state.values, [key]: value } })),
  reset: () =>
    set({ values: DEFAULT_SIMULATION_INPUT, result: null, running: false }),
  run: async () => {
    set({ running: true })
    const result = await runSimulation(get().values)
    set({ result, running: false })
  },
}))