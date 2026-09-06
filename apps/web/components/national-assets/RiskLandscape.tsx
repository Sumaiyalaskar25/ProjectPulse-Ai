'use client'

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
import { RISK_PERCENT, type Project, type RiskLevel } from '@/lib/projects'

const STATUS_COLORS: Record<string, string> = {
  critical: '#EF4444',
  high: '#F59E0B',
  moderate: '#F97316',
  stable: '#22C55E',
}

const AXIS_TICK = { fill: '#64748B', fontSize: 11 }
const AXIS_LINE = { stroke: '#1F2637' }
const TOOLTIP_STYLE = {
  background: '#141925',
  border: '1px solid #1F2637',
  borderRadius: 12,
  color: '#F8FAFC',
  fontSize: 12,
}

function exposureToNumber(exposure: string, risk: RiskLevel): number {
  const match = exposure.match(/([\d.]+)\s*B\s*Cr/i)
  if (match) return Math.round(parseFloat(match[1]) * 1000)
  return RISK_PERCENT[risk]
}

function toPoint(project: Project) {
  return {
    x: RISK_PERCENT[project.risk],
    y: exposureToNumber(project.exposure, project.risk),
    status: project.risk.toLowerCase(),
  }
}

interface RiskLandscapeProps {
  projects: Project[]
}

export function RiskLandscape({ projects }: RiskLandscapeProps) {
  const points = projects.map(toPoint)
  const maxExposure = Math.max(800, ...points.map((point) => point.y))
  const yDomain = [0, Math.ceil((maxExposure * 1.1) / 500) * 500]

  return (
    <Card className="flex flex-col">
      <div>
        <h2 className="text-lg font-semibold text-text-primary">
          🗺 Risk Landscape
        </h2>
        <p className="mt-1 text-sm text-text-secondary">
          Cross-referencing Risk Scores with Financial Exposure for priority
          projects.
        </p>
      </div>

      <div className="mt-4 flex flex-1 items-center">
        <ResponsiveContainer width="100%" height={320}>
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
              domain={yDomain}
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
              contentStyle={TOOLTIP_STYLE}
              labelStyle={{ color: '#94A3B8', fontSize: 11 }}
            />
            <Scatter name="Projects" data={points}>
              {points.map((point) => (
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
        {Object.entries(STATUS_COLORS).map(([key, color]) => (
          <span
            key={key}
            className="flex items-center gap-1.5 text-xs capitalize text-text-secondary"
          >
            <span
              className="h-2 w-2 rounded-full"
              style={{ backgroundColor: color }}
            />
            {key}
          </span>
        ))}
      </div>
    </Card>
  )
}