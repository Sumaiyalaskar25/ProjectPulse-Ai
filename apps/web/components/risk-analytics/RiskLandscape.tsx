'use client'

import { Maximize2 } from 'lucide-react'
import {
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Card } from '@/components/ui/Card'

const TIER_COLORS: Record<string, string> = {
  Critical: '#EF4444',
  High: '#F59E0B',
  Moderate: '#F97316',
  Stable: '#22C55E',
}

const POINTS = [
  { x: 88, y: 42, tier: 'Critical' },
  { x: 76, y: 12, tier: 'Critical' },
  { x: 68, y: 15, tier: 'High' },
  { x: 64, y: 90, tier: 'High' },
  { x: 52, y: 34, tier: 'Moderate' },
  { x: 32, y: 25, tier: 'Stable' },
]

const AXIS_TICK = { fill: '#64748B', fontSize: 11 }
const AXIS_LINE = { stroke: '#1F2637' }
const TOOLTIP_STYLE = {
  background: '#141925',
  border: '1px solid #1F2637',
  borderRadius: 12,
  color: '#F8FAFC',
  fontSize: 12,
}

export function RiskLandscape() {
  return (
    <Card className="flex flex-col">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-text-primary">
            📊 Risk Landscape
          </h2>
          <p className="mt-1 text-sm text-text-secondary">
            Financial Exposure vs Risk Score mapping
          </p>
        </div>
        <button
          type="button"
          className="flex h-8 w-8 items-center justify-center rounded-lg border border-background-border bg-background-surface text-text-muted transition-colors hover:text-text-primary"
        >
          <Maximize2 className="h-4 w-4" />
        </button>
      </div>

      <div className="mt-4 flex flex-1 items-center">
        <ResponsiveContainer width="100%" height={300}>
          <ScatterChart margin={{ top: 10, right: 20, bottom: 30, left: 16 }}>
            <CartesianGrid stroke="#1F2637" strokeDasharray="3 3" />
            <XAxis
              type="number"
              dataKey="x"
              name="Risk Score"
              domain={[0, 100]}
              tick={{ ...AXIS_TICK }}
              tickLine={{ ...AXIS_LINE }}
              axisLine={{ ...AXIS_LINE }}
              tickFormatter={(value) => `${value}%`}
              label={{
                value: 'Risk Score',
                position: 'insideBottom',
                offset: -10,
                fill: '#94A3B8',
                fontSize: 11,
              }}
            />
            <YAxis
              type="number"
              dataKey="y"
              name="Exposure"
              domain={[0, 100]}
              tick={{ ...AXIS_TICK }}
              tickLine={{ ...AXIS_LINE }}
              axisLine={{ ...AXIS_LINE }}
              tickFormatter={(value) => `${value}Cr`}
              label={{
                value: 'Exposure (Cr)',
                angle: -90,
                position: 'insideLeft',
                offset: 10,
                fill: '#94A3B8',
                fontSize: 11,
              }}
            />
            <Tooltip
              cursor={{ strokeDasharray: '3 3', stroke: '#1F2637' }}
              contentStyle={TOOLTIP_STYLE}
              labelStyle={{ color: '#94A3B8', fontSize: 11 }}
              formatter={(value, name) =>
                name === 'x' ? `${value}%` : `${value}Cr`
              }
            />
            <Scatter name="Projects" data={POINTS}>
              {POINTS.map((point) => (
                <Cell
                  key={`${point.x}-${point.y}`}
                  fill={TIER_COLORS[point.tier]}
                />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 flex items-center justify-center gap-5 border-t border-background-border pt-4">
        {Object.entries(TIER_COLORS).map(([tier, color]) => (
          <span
            key={tier}
            className="flex items-center gap-1.5 text-xs text-text-secondary"
          >
            <span
              className="h-2 w-2 rounded-full"
              style={{ backgroundColor: color }}
            />
            {tier}
          </span>
        ))}
      </div>
    </Card>
  )
}