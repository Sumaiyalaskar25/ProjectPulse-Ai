'use client'

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { Card } from '@/components/ui/Card'

const TIERS = [
  { name: 'Critical', count: 142, percent: 8, color: '#EF4444' },
  { name: 'High', count: 318, percent: 18, color: '#F59E0B' },
  { name: 'Moderate', count: 589, percent: 33, color: '#F97316' },
  { name: 'Stable', count: 726, percent: 41, color: '#22C55E' },
]

const TOOLTIP_STYLE = {
  background: '#141925',
  border: '1px solid #1F2637',
  borderRadius: 12,
  color: '#F8FAFC',
  fontSize: 12,
}

export function RiskDonut() {
  return (
    <Card className="flex flex-col">
      <div>
        <h2 className="text-lg font-semibold text-text-primary">
          📄 Risk Tier Distribution
        </h2>
        <p className="mt-1 text-sm text-text-secondary">
          Portfolio segmentation by risk severity
        </p>
      </div>

      <div className="mt-4 flex flex-col items-center gap-6 sm:flex-row">
        <div className="h-56 w-full max-w-[240px] shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={TIERS}
                dataKey="count"
                nameKey="name"
                innerRadius={58}
                outerRadius={88}
                paddingAngle={2}
                stroke="#0B0F19"
              >
                {TIERS.map((tier) => (
                  <Cell key={tier.name} fill={tier.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                labelStyle={{ color: '#94A3B8', fontSize: 11 }}
                formatter={(value, name) => [`${value} projects`, name]}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <ul className="flex w-full min-w-0 flex-1 flex-col gap-3">
          {TIERS.map((tier) => (
            <li
              key={tier.name}
              className="flex items-center justify-between gap-3 text-sm"
            >
              <span className="flex items-center gap-2.5 text-text-secondary">
                <span
                  className="h-3 w-3 rounded"
                  style={{ backgroundColor: tier.color }}
                />
                {tier.name}
              </span>
              <span className="flex items-center gap-3 font-mono">
                <span className="font-bold text-text-primary">
                  {tier.count}
                </span>
                <span className="w-12 text-right text-xs text-text-muted">
                  {tier.percent}%
                </span>
              </span>
            </li>
          ))}
        </ul>
      </div>
    </Card>
  )
}