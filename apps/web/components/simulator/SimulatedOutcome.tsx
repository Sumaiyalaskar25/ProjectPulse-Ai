'use client'

import { useState } from 'react'
import { Loader2 } from 'lucide-react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { useSimulationStore } from '@/lib/simulation-store'
import type { SimulationChartPoint } from '@/lib/simulation'
import { cn } from '@/lib/utils'

const BASELINE_COLOR = '#94A3B8'
const SIMULATED_COLOR = '#22C55E'
const EROSION_COLOR = '#EF4444'

const BASELINE_RISK = 88
const BASELINE_DELAY = 18

const DEFAULT_DATA: SimulationChartPoint[] = [
  { month: 'M1', baseline: 38, green: 52, red: null },
  { month: 'M2', baseline: 42, green: 58, red: null },
  { month: 'M3', baseline: 37, green: 63, red: null },
  { month: 'M4', baseline: 45, green: 69, red: null },
  { month: 'M5', baseline: 41, green: 74, red: null },
  { month: 'M6', baseline: 36, green: 78, red: 78 },
  { month: 'M7', baseline: 44, green: null, red: 72 },
  { month: 'M8', baseline: 40, green: null, red: 76 },
  { month: 'M9', baseline: 35, green: null, red: 63 },
  { month: 'M10', baseline: 42, green: null, red: 58 },
]

const AXIS_TICK = { fill: '#94A3B8', fontSize: 11 }
const AXIS_LINE = { stroke: '#1F2637' }
const TOOLTIP_STYLE = {
  background: '#141925',
  border: '1px solid #1F2637',
  borderRadius: 12,
  color: '#F8FAFC',
  fontSize: 12,
}

export function SimulatedOutcome() {
  const [deltaMode, setDeltaMode] = useState(false)
  const result = useSimulationStore((state) => state.result)
  const running = useSimulationStore((state) => state.running)

  const riskScore = result?.riskScore ?? BASELINE_RISK
  const delayMonths = result?.delayMonths ?? BASELINE_DELAY
  const riskDelta = BASELINE_RISK - riskScore
  const delayDelta = BASELINE_DELAY - delayMonths
  const data = result?.chart ?? DEFAULT_DATA

  return (
    <Card className="flex flex-col gap-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-text-primary">
            ⚠ Simulated Outcome Analysis
          </h2>
          <p className="mt-1 text-sm text-text-secondary">
            Projected risk reduction and schedule recovery metrics.
          </p>
        </div>
        <div className="flex shrink-0 flex-col items-end gap-2">
          {running && (
            <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-status-info">
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
              COMPUTING COUNTERFACTUAL...
            </span>
          )}
          <button
            type="button"
            onClick={() => setDeltaMode((mode) => !mode)}
            className="inline-flex items-center gap-2 text-xs font-medium text-text-secondary transition-colors hover:text-text-primary"
          >
            Delta vs Baseline
            <span
              className={cn(
                'relative h-5 w-9 rounded-full transition-colors',
                deltaMode ? 'bg-status-stable' : 'bg-background-border',
              )}
            >
              <span
                className={cn(
                  'absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-all',
                  deltaMode ? 'left-[18px]' : 'left-0.5',
                )}
              />
            </span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-lg border border-background-border bg-background-surface p-4">
          <p className="text-xs font-bold uppercase tracking-wider text-text-muted">
            Aggregate Risk Score
          </p>
          <p className="mt-2 font-mono text-xl font-semibold text-text-muted line-through">
            88% (CRITICAL)
          </p>
          <div className="mt-1 flex items-center gap-2">
            <span
              className={cn(
                'font-mono text-4xl font-bold text-text-primary',
                running && 'animate-pulse',
              )}
            >
              {riskScore}%
            </span>
            {result && (
              <Badge variant={riskDelta > 0 ? 'stable' : 'neutral'}>
                {riskDelta > 0 ? `-${riskDelta}%` : `${riskDelta}%`}
              </Badge>
            )}
          </div>
        </div>
        <div className="rounded-lg border border-background-border bg-background-surface p-4">
          <p className="text-xs font-bold uppercase tracking-wider text-text-muted">
            Predicted Project Delay
          </p>
          <p className="mt-2 font-mono text-xl font-semibold text-text-muted line-through">
            18 Months
          </p>
          <div className="mt-1 flex items-center gap-2">
            <span
              className={cn(
                'font-mono text-4xl font-bold text-text-primary',
                running && 'animate-pulse',
              )}
            >
              {delayMonths} Months
            </span>
            {result && (
              <Badge variant={delayDelta > 0 ? 'stable' : 'neutral'}>
                {delayDelta > 0 ? `-${delayDelta} Mo.` : `${delayDelta} Mo.`}
              </Badge>
            )}
          </div>
        </div>
      </div>

      <div className="border-t border-background-border pt-4">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary">
              Probability Transition Graph
            </h3>
            <p className="mt-0.5 text-xs text-text-secondary">
              Likelihood of project success (%)
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5 text-xs text-text-secondary">
              <span
                className="h-2 w-2"
                style={{ backgroundColor: BASELINE_COLOR }}
              />
              Baseline
            </span>
            <span className="flex items-center gap-1.5 text-xs text-text-secondary">
              <span
                className="h-2 w-2"
                style={{ backgroundColor: SIMULATED_COLOR }}
              />
              Simulated
            </span>
          </div>
        </div>

        <div
          className={cn(
            'relative mt-3 h-64',
            running && 'opacity-60',
          )}
        >
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={data}
              margin={{ top: 10, right: 16, bottom: 4, left: -12 }}
            >
              <CartesianGrid stroke="#1F2637" strokeDasharray="3 3" />
              <XAxis
                dataKey="month"
                tick={AXIS_TICK}
                tickLine={AXIS_LINE}
                axisLine={AXIS_LINE}
              />
              <YAxis
                domain={[0, 100]}
                tickFormatter={(value) => `${value}%`}
                tick={AXIS_TICK}
                tickLine={AXIS_LINE}
                axisLine={AXIS_LINE}
              />
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                labelStyle={{ color: '#94A3B8', fontSize: 11 }}
                formatter={(value) => `${value}%`}
              />
              <Line
                name="Baseline"
                dataKey="baseline"
                type="linear"
                stroke={BASELINE_COLOR}
                strokeWidth={2}
                dot={{ r: 3, fill: BASELINE_COLOR }}
              />
              <Line
                name="Simulated"
                dataKey="green"
                type="linear"
                stroke={SIMULATED_COLOR}
                strokeWidth={2}
                connectNulls
                dot={{ r: 3, fill: SIMULATED_COLOR }}
              />
              <Line
                name="Simulated Erosion"
                dataKey="red"
                type="linear"
                stroke={EROSION_COLOR}
                strokeWidth={2}
                connectNulls
                dot={{ r: 3, fill: EROSION_COLOR }}
              />
            </LineChart>
          </ResponsiveContainer>

          <div className="pointer-events-none absolute left-2 top-2 rounded-md border border-status-critical/40 bg-black/60 px-2 py-1 font-mono text-[10px] font-semibold tracking-wide text-status-critical">
            CURRENT MODE: HIGH FAILURE DENSITY
          </div>
          <div className="pointer-events-none absolute bottom-2 right-2 rounded-md border border-status-stable/40 bg-black/60 px-2 py-1 font-mono text-[10px] font-semibold tracking-wide text-status-stable">
            OPTIMAL TARGET: RESILIENCE THRESHOLD META
          </div>
        </div>
      </div>
    </Card>
  )
}