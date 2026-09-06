'use client'

import { MoreHorizontal } from 'lucide-react'
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
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { backendPendingMessage, useToastStore } from '@/lib/toast-store'

const STATUS_COLORS: Record<string, string> = {
  critical: '#EF4444',
  high: '#F59E0B',
  moderate: '#F97316',
  stable: '#22C55E',
}

const DATA = [
  { x: 82, y: 640, status: 'critical' },
  { x: 68, y: 380, status: 'high' },
  { x: 58, y: 720, status: 'high' },
  { x: 76, y: 210, status: 'critical' },
  { x: 44, y: 180, status: 'moderate' },
  { x: 30, y: 90, status: 'stable' },
]

const LEGEND = [
  { label: 'Critical', color: STATUS_COLORS.critical },
  { label: 'High', color: STATUS_COLORS.high },
  { label: 'Moderate', color: STATUS_COLORS.moderate },
  { label: 'Stable', color: STATUS_COLORS.stable },
]

const AXIS_TICK = { fill: '#64748B', fontSize: 11 }
const AXIS_LINE = { stroke: '#1F2637' }

export function RiskMatrix() {
  const show = useToastStore((state) => state.show)
  return (
    <Card className="col-span-2 flex flex-col">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-text-primary">
            🛡 Portfolio Risk Matrix
          </h2>
          <p className="mt-1 text-sm text-text-secondary">
            Cross-referencing Risk Scores with Financial Exposure for all
            active sectors.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => show(backendPendingMessage)}
          >
            Export CSV
          </Button>
          <Button
            variant="secondary"
            size="sm"
            aria-label="More options"
            className="px-2"
          >
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="mt-4 flex flex-1 items-center">
        <ResponsiveContainer width="100%" height={300}>
          <ScatterChart margin={{ top: 10, right: 20, bottom: 30, left: 20 }}>
            <CartesianGrid stroke="#1F2637" strokeDasharray="3 3" />
            <XAxis
              type="number"
              dataKey="x"
              name="Risk Score"
              domain={[0, 100]}
              tick={{ ...AXIS_TICK }}
              tickLine={{ ...AXIS_LINE }}
              axisLine={{ ...AXIS_LINE }}
              label={{
                value: 'Risk Score (pts)',
                position: 'insideBottom',
                offset: -10,
                fill: '#94A3B8',
                fontSize: 11,
              }}
            />
            <YAxis
              type="number"
              dataKey="y"
              name="Financial Exposure"
              domain={[0, 1000]}
              tick={{ ...AXIS_TICK }}
              tickLine={{ ...AXIS_LINE }}
              axisLine={{ ...AXIS_LINE }}
              tickFormatter={(value) => `${value}Cr`}
              label={{
                value: 'Financial Exposure',
                angle: -90,
                position: 'insideLeft',
                offset: 10,
                fill: '#94A3B8',
                fontSize: 11,
              }}
            />
            <Tooltip
              cursor={{ strokeDasharray: '3 3', stroke: '#1F2637' }}
              contentStyle={{
                background: '#141925',
                border: '1px solid #1F2637',
                borderRadius: 12,
                color: '#F8FAFC',
                fontSize: 12,
              }}
              labelStyle={{ color: '#94A3B8', fontSize: 11 }}
            />
            <Scatter name="Sectors" data={DATA}>
              {DATA.map((point) => (
                <Cell
                  key={`${point.x}-${point.y}`}
                  fill={STATUS_COLORS[point.status]}
                />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 flex items-center justify-center gap-5 border-t border-background-border pt-4">
        {LEGEND.map((item) => (
          <span
            key={item.label}
            className="flex items-center gap-1.5 text-xs text-text-secondary"
          >
            <span
              className="h-2 w-2 rounded-full"
              style={{ backgroundColor: item.color }}
            />
            {item.label}
          </span>
        ))}
      </div>
    </Card>
  )
}