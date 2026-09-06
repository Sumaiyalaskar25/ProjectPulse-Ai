'use client'

import { RefreshCw, Zap } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { useSimulationStore } from '@/lib/simulation-store'

export function SimulatorControls() {
  const running = useSimulationStore((state) => state.running)
  const run = useSimulationStore((state) => state.run)
  const reset = useSimulationStore((state) => state.reset)

  return (
    <div className="flex items-center gap-2">
      <Button variant="secondary" onClick={reset} disabled={running}>
        <RefreshCw className="h-4 w-4" />
        Reset Baseline
      </Button>
      <Button variant="primary" onClick={run} disabled={running}>
        <Zap className="h-4 w-4" />
        Run Simulation
      </Button>
    </div>
  )
}