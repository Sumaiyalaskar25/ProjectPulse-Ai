import { Card } from '@/components/ui/Card'
import type { DashboardSummary } from '@/types/api'
import { cn } from '@/lib/utils'

interface RiskTierStripProps {
  summary?: DashboardSummary
}

const TIER_BASE = [
  {
    key: 'critical',
    label: 'Critical Risk',
    tint: 'text-status-critical',
    border: 'border-l-status-critical',
    description: 'Immediate structural',
  },
  {
    key: 'high',
    label: 'High Risk',
    tint: 'text-status-high',
    border: 'border-l-status-high',
    description: 'Delayed maintenance,',
  },
  {
    key: 'moderate',
    label: 'Moderate Risk',
    tint: 'text-status-moderate',
    border: 'border-l-status-moderate',
    description: 'Standard wear,',
  },
  {
    key: 'stable',
    label: 'Stable Risk',
    tint: 'text-status-stable',
    border: 'border-l-status-stable',
    description: 'Optimal performance, no',
  },
] as const

type TierKey = (typeof TIER_BASE)[number]['key']

const DEFAULT_COUNTS: Record<TierKey, string> = {
  critical: '142',
  high: '318',
  moderate: '589',
  stable: '726',
}

function countFor(
  key: TierKey,
  summary?: DashboardSummary,
): string {
  if (!summary) return DEFAULT_COUNTS[key]
  return summary[`${key}_count`].toLocaleString()
}

export function RiskTierStrip({ summary }: RiskTierStripProps) {
  return (
    <div className="grid grid-cols-4 gap-4">
      {TIER_BASE.map((tier) => (
        <Card key={tier.label} className={cn('border-l-4', tier.border)}>
          <p className="text-xs font-bold uppercase tracking-wider text-text-muted">
            {tier.label}
          </p>
          <p className={cn('mt-2 font-mono text-3xl font-bold', tier.tint)}>
            {countFor(tier.key, summary)}
          </p>
          <p className="mt-1 text-xs text-text-secondary">{tier.description}</p>
        </Card>
      ))}
    </div>
  )
}