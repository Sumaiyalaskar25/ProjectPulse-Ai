'use client'

import { Info } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { useSimulationStore } from '@/lib/simulation-store'
import type { SimulationInput } from '@/lib/simulation'

interface SliderConfig {
  id: keyof SimulationInput
  icon: string
  label: string
  sublabel: string
  min: number
  max: number
  unit: string
  minLabel: string
  maxLabel: string
}

const SLIDERS: SliderConfig[] = [
  {
    id: 'budget',
    icon: '$',
    label: 'ADDITIONAL BUDGET ALLOCATION',
    sublabel: 'Immediate Capital Injection',
    min: 0,
    max: 50,
    unit: '%',
    minLabel: '0%',
    maxLabel: '50%',
  },
  {
    id: 'clearance',
    icon: '🕐',
    label: 'REGULATORY CLEARANCE SPEEDUP',
    sublabel: 'Administrative Velocity',
    min: 0,
    max: 12,
    unit: ' Mo.',
    minLabel: '0 Mo.',
    maxLabel: '12 Mo.',
  },
  {
    id: 'mobilization',
    icon: '⚡',
    label: 'CONTRACTOR MOBILIZATION',
    sublabel: 'Labor Force Density',
    min: 0,
    max: 100,
    unit: '%',
    minLabel: '0%',
    maxLabel: '100%',
  },
]

export function InterventionParameters() {
  const values = useSimulationStore((state) => state.values)
  const setValue = useSimulationStore((state) => state.setValue)
  const result = useSimulationStore((state) => state.result)

  return (
    <Card className="flex flex-col gap-4">
      <div>
        <h2 className="text-lg font-semibold text-text-primary">
          〰 Intervention Parameters
        </h2>
        <p className="mt-1 text-sm text-text-secondary">
          Adjust variables to simulate counterfactual outcomes for the
          Northern Corridor.
        </p>
      </div>

      {SLIDERS.map((slider) => (
        <div
          key={slider.id}
          className="rounded-lg border border-background-border bg-background-surface p-4"
        >
          <div className="flex items-center justify-between gap-2">
            <div className="flex min-w-0 items-center gap-2">
              <span className="text-base">{slider.icon}</span>
              <div className="min-w-0">
                <p className="text-sm font-bold text-text-primary">
                  {slider.label}
                </p>
                <p className="truncate text-xs text-text-secondary">
                  {slider.sublabel}
                </p>
              </div>
            </div>
            <Badge variant="neutral" className="shrink-0">
              +{values[slider.id]}
              {slider.unit}
            </Badge>
          </div>
          <input
            type="range"
            min={slider.min}
            max={slider.max}
            value={values[slider.id]}
            onChange={(event) =>
              setValue(slider.id, Number(event.target.value))
            }
            className="mt-4 w-full accent-status-info"
          />
          <div className="mt-1 flex items-center justify-between text-xs text-text-muted">
            <span>{slider.minLabel}</span>
            <span className="font-medium text-text-secondary">
              Base Target
            </span>
            <span>{slider.maxLabel}</span>
          </div>
        </div>
      ))}

      <div className="flex gap-3 rounded-lg border border-status-info/20 bg-status-info/5 p-4 text-sm leading-relaxed text-text-secondary">
        <Info className="mt-0.5 h-4 w-4 shrink-0 text-status-info" />
        <p>
          Adjusting Budget Allocation primarily offsets material supply chain
          volatility, while Regulatory Speedup reduces bureaucratic stagnation
          in Section IX.
        </p>
      </div>

      <div className="flex items-center justify-between gap-3 border-t border-background-border pt-4">
        <span className="font-mono text-xs text-text-muted">
          🕐 LAST DATA SYNC: TODAY, 08:42 AM
        </span>
        <span className="font-mono text-xs font-semibold text-status-stable">
          CONFIDENCE: {result ? result.confidence.toFixed(1) : '94.2'}%
        </span>
      </div>
    </Card>
  )
}