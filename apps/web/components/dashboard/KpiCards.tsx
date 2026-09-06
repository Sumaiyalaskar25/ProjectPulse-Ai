import { StatCard } from '@/components/ui/StatCard'
import type { DashboardSummary } from '@/types/api'

interface KpiCardsProps {
  summary?: DashboardSummary
}

const DEFAULT_KPIS = [
  {
    label: 'TOTAL PROJECTS',
    value: '1,775',
    delta: 12,
    deltaSuffix: '% from Q2',
    deltaDirection: 'good' as const,
  },
  {
    label: 'PORTFOLIO VALUE',
    value: '14.2K Cr',
    delta: 4.8,
    deltaSuffix: '% YoY',
    deltaDirection: 'good' as const,
  },
  {
    label: 'CAPITAL AT RISK',
    value: '3.8K Cr',
    delta: 1.2,
    deltaSuffix: '% this mo',
    deltaDirection: 'bad' as const,
  },
  {
    label: 'CRITICAL PROJECTS',
    value: '142',
    delta: -5,
    deltaSuffix: ' cases',
    deltaDirection: 'bad' as const,
  },
]

export function KpiCards({ summary }: KpiCardsProps) {
  const kpis = summary
    ? [
        {
          label: 'TOTAL PROJECTS',
          value: summary.total_projects.toLocaleString(),
          delta: 12,
          deltaSuffix: '% from Q2',
          deltaDirection: 'good' as const,
        },
        {
          label: 'PORTFOLIO VALUE',
          value: `${(summary.portfolio_value / 1000).toFixed(1)}K Cr`,
          delta: 4.8,
          deltaSuffix: '% YoY',
          deltaDirection: 'good' as const,
        },
        {
          label: 'CAPITAL AT RISK',
          value: `${(summary.capital_at_risk / 1000).toFixed(1)}K Cr`,
          delta: 1.2,
          deltaSuffix: '% this mo',
          deltaDirection: 'bad' as const,
        },
        {
          label: 'CRITICAL PROJECTS',
          value: summary.critical_count.toLocaleString(),
          delta: -5,
          deltaSuffix: ' cases',
          deltaDirection: 'bad' as const,
        },
      ]
    : DEFAULT_KPIS

  return (
    <div className="grid grid-cols-4 gap-4">
      {kpis.map((kpi) => (
        <StatCard
          key={kpi.label}
          label={kpi.label}
          value={kpi.value}
          delta={kpi.delta}
          deltaSuffix={kpi.deltaSuffix}
          deltaDirection={kpi.deltaDirection}
        />
      ))}
    </div>
  )
}