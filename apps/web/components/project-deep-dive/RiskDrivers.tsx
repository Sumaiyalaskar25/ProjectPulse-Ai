'use client'

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'

interface Driver {
  name: string
  value: number
  type: 'risk' | 'efficiency'
}

const DATA: Driver[] = [
  { name: 'Land Acquisition', value: 92, type: 'risk' },
  { name: 'Env. Clearance', value: 68, type: 'risk' },
  { name: 'Utility Shifting', value: 41, type: 'risk' },
  { name: 'Contractor Perf.', value: -24, type: 'efficiency' },
  { name: 'Material Supply', value: -12, type: 'efficiency' },
]

const RISK_COLOR = '#EF4444'
const EFFICIENCY_COLOR = '#22C55E'

const AXIS_TICK = { fill: '#94A3B8', fontSize: 11 }
const AXIS_LINE = { stroke: '#1F2637' }
const TOOLTIP_STYLE = {
  background: '#141925',
  border: '1px solid #1F2637',
  borderRadius: 12,
  color: '#F8FAFC',
  fontSize: 12,
}

export function RiskDrivers() {
  return (
    <Card className="flex flex-col">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-text-primary">
            🛡 Top Risk Drivers
          </h2>
          <p className="mt-1 text-sm text-text-secondary">
            Primary contributors to project slippage and budget variance.
          </p>
        </div>
        <Badge variant="high">Sensitivity: High</Badge>
      </div>

      <div className="mt-4 flex flex-1 items-center">
        <ResponsiveContainer width="100%" height={240}>
          <BarChart
            data={DATA}
            layout="vertical"
            margin={{ top: 0, right: 8, bottom: 0, left: 0 }}
          >
            <CartesianGrid
              stroke="#1F2637"
              strokeDasharray="3 3"
              horizontal={false}
            />
            <XAxis
              type="number"
              domain={[-30, 100]}
              tick={AXIS_TICK}
              tickLine={AXIS_LINE}
              axisLine={AXIS_LINE}
              tickFormatter={(value) => `${Math.abs(value)}%`}
            />
            <YAxis
              type="category"
              dataKey="name"
              width={118}
              tick={AXIS_TICK}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              cursor={{ fill: 'rgba(148, 163, 184, 0.06)' }}
              contentStyle={TOOLTIP_STYLE}
              labelStyle={{ color: '#94A3B8', fontSize: 11 }}
              formatter={(value) => `${Math.abs(Number(value))}%`}
            />
            <Bar dataKey="value" radius={4} barSize={16}>
              {DATA.map((driver) => (
                <Cell
                  key={driver.name}
                  fill={driver.type === 'risk' ? RISK_COLOR : EFFICIENCY_COLOR}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="flex items-center justify-center gap-5 border-t border-background-border pt-4">
        <span className="flex items-center gap-1.5 text-xs text-text-secondary">
          <span
            className="h-2 w-2 rounded-full"
            style={{ backgroundColor: RISK_COLOR }}
          />
          Positive Slippage (Risk)
        </span>
        <span className="flex items-center gap-1.5 text-xs text-text-secondary">
          <span
            className="h-2 w-2 rounded-full"
            style={{ backgroundColor: EFFICIENCY_COLOR }}
          />
          Negative Slippage (Efficiency)
        </span>
      </div>
    </Card>
  )
}