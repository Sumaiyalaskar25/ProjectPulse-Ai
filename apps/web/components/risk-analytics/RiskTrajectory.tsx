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
  portfolio: number | null
  forecasted: number | null
}

const DATA: TrajectoryPoint[] = [
  { month: 'Oct 22', portfolio: 15, forecasted: null },
  { month: 'Nov 22', portfolio: 22, forecasted: null },
  { month: 'Dec 22', portfolio: 28, forecasted: null },
  { month: 'Jan 23', portfolio: 34, forecasted: null },
  { month: 'Feb 23', portfolio: 42, forecasted: null },
  { month: 'Mar 23', portfolio: 48, forecasted: null },
  { month: 'Apr 23', portfolio: 53, forecasted: null },
  { month: 'May 23', portfolio: 60, forecasted: null },
  { month: 'Jun 23', portfolio: 65, forecasted: 65 },
  { month: 'Jul 23', portfolio: null, forecasted: 70 },
  { month: 'Aug 23', portfolio: null, forecasted: 75 },
  { month: 'Sep 23', portfolio: null, forecasted: 80 },
]

const PORTFOLIO_COLOR = '#64748B'
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
            〰 Risk Trajectory
          </h2>
          <p className="mt-1 text-sm text-text-secondary">
            12-month risk movement with AI-driven predictive forecast
          </p>
        </div>
        <Badge variant="stable">Confidence: 94.8%</Badge>
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
              name="Portfolio Risk Score"
              dataKey="portfolio"
              type="monotone"
              stroke={PORTFOLIO_COLOR}
              strokeWidth={2}
              dot={{ r: 3, fill: PORTFOLIO_COLOR }}
            />
            <Line
              name="Predictive Forecast"
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

      <div className="flex items-start justify-between gap-3 rounded-lg border border-status-info/20 bg-status-info/5 p-4">
        <div className="flex gap-3">
          <Info className="mt-0.5 h-4 w-4 shrink-0 text-status-info" />
          <p className="text-sm leading-relaxed text-text-secondary">
            <span className="font-semibold text-text-primary">
              Trajectory Observation:
            </span>{' '}
            Forecasted 14% deviation in Northern Corridor due to seasonal
            variance.
          </p>
        </div>
        <a
          href="#"
          className="inline-flex shrink-0 items-center gap-1 text-sm font-medium text-status-info transition-colors hover:underline"
        >
          Details →
        </a>
      </div>
    </Card>
  )
}