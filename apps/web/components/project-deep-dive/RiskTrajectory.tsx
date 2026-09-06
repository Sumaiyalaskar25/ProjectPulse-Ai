'use client'

import { Info } from 'lucide-react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'

interface TrajectoryPoint {
  month: string
  historical: number | null
  forecasted: number | null
}

const DATA: TrajectoryPoint[] = [
  { month: 'Oct 22', historical: 15, forecasted: null },
  { month: 'Nov 22', historical: 22, forecasted: null },
  { month: 'Dec 22', historical: 30, forecasted: null },
  { month: 'Jan 23', historical: 41, forecasted: null },
  { month: 'Feb 23', historical: 48, forecasted: null },
  { month: 'Mar 23', historical: 55, forecasted: null },
  { month: 'Apr 23', historical: 61, forecasted: null },
  { month: 'May 23', historical: 68, forecasted: null },
  { month: 'Jun 23', historical: 75, forecasted: 75 },
  { month: 'Jul 23', historical: null, forecasted: 81 },
  { month: 'Aug 23', historical: null, forecasted: 86 },
  { month: 'Sep 23', historical: null, forecasted: 90 },
]

const HISTORICAL_COLOR = '#64748B'
const FORECAST_COLOR = '#EF4444'

const AXIS_TICK = { fill: '#94A3B8', fontSize: 11 }
const AXIS_LINE = { stroke: '#1F2637' }
const TOOLTIP_STYLE = {
  background: '#141925',
  border: '1px solid #1F2637',
  borderRadius: 12,
  color: '#F8FAFC',
  fontSize: 12,
}

export function RiskTrajectory() {
  return (
    <Card className="flex flex-col gap-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-text-primary">
            📅 12-Month Risk Trajectory
          </h2>
          <p className="mt-1 text-sm text-text-secondary">
            Comparative view of historical risk progression vs. current AI
            prediction models.
          </p>
        </div>
        <Badge variant="stable">✓ Model Accuracy: 94.8%</Badge>
      </div>

      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={DATA}
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
            <Legend
              wrapperStyle={{ fontSize: 12, color: '#94A3B8' }}
              iconType="plainline"
            />
            <Line
              name="Historical Risk"
              dataKey="historical"
              type="monotone"
              stroke={HISTORICAL_COLOR}
              strokeWidth={2}
              dot={{ r: 3, fill: HISTORICAL_COLOR }}
            />
            <Line
              name="AI Forecasted Trajectory"
              dataKey="forecasted"
              type="monotone"
              stroke={FORECAST_COLOR}
              strokeWidth={2}
              strokeDasharray="6 4"
              dot={{ r: 3, fill: FORECAST_COLOR }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="flex gap-3 rounded-lg border border-status-info/20 bg-status-info/5 p-4 text-sm leading-relaxed text-text-secondary">
        <Info className="mt-0.5 h-4 w-4 shrink-0 text-status-info" />
        <p>
          <span className="font-semibold text-text-primary">Observation:</span>{' '}
          The divergence between Jan 23 and Feb 23 was triggered by the
          &apos;Northern Monsoon Anomaly&apos;. Current forecasts incorporate a 15%
          safety buffer for upcoming seasonal variances.
        </p>
      </div>
    </Card>
  )
}