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
import { Card } from '@/components/ui/Card'

const DATA = [
  { name: 'Land Acquisition', value: 92 },
  { name: 'Env. Clearance', value: 68 },
  { name: 'Utility Shifting', value: 41 },
  { name: 'Material Supply', value: 26 },
  { name: 'Funding Delays', value: 12 },
]

const RISK_COLOR = '#EF4444'

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
      <div>
        <h2 className="text-lg font-semibold text-text-primary">
          ⚠ Top Risk Drivers
        </h2>
        <p className="mt-1 text-sm text-text-secondary">
          Primary contributors to portfolio-level sensitivity
        </p>
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
              domain={[0, 100]}
              tick={AXIS_TICK}
              tickLine={AXIS_LINE}
              axisLine={AXIS_LINE}
              tickFormatter={(value) => `${value}%`}
            />
            <YAxis
              type="category"
              dataKey="name"
              width={130}
              tick={AXIS_TICK}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              cursor={{ fill: 'rgba(148, 163, 184, 0.06)' }}
              contentStyle={TOOLTIP_STYLE}
              labelStyle={{ color: '#94A3B8', fontSize: 11 }}
              formatter={(value) => `${value}%`}
            />
            <Bar dataKey="value" radius={4} barSize={16}>
              {DATA.map((driver) => (
                <Cell key={driver.name} fill={RISK_COLOR} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="flex items-center justify-between border-t border-background-border pt-4">
        <span className="flex items-center gap-1.5 text-xs text-text-secondary">
          <span
            className="h-2 w-2 rounded-full"
            style={{ backgroundColor: RISK_COLOR }}
          />
          Risk Slippage Impact
        </span>
        <span className="text-xs font-semibold text-status-critical">
          Impact Sensitivity: High
        </span>
      </div>
    </Card>
  )
}