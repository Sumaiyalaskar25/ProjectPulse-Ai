import { cn } from '@/lib/utils'

export type AssetsView = 'table' | 'landscape'

const VIEWS: { key: AssetsView; label: string }[] = [
  { key: 'table', label: 'Table View' },
  { key: 'landscape', label: 'Risk Landscape' },
]

const PILLS = [
  { label: 'Critical', count: '142', dot: 'bg-status-critical' },
  { label: 'High', count: '318', dot: 'bg-status-high' },
  { label: 'Moderate', count: '589', dot: 'bg-status-moderate' },
  { label: 'Stable', count: '726', dot: 'bg-status-stable' },
]

interface RiskSummaryProps {
  view: AssetsView
  onChange: (view: AssetsView) => void
}

export function RiskSummary({ view, onChange }: RiskSummaryProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div className="flex items-center gap-1 rounded-lg border border-background-border bg-background-surface p-1">
        {VIEWS.map((item) => (
          <button
            key={item.key}
            type="button"
            onClick={() => onChange(item.key)}
            className={cn(
              'rounded-md px-3 py-1.5 text-xs font-medium transition-colors',
              view === item.key
                ? 'bg-background-card text-text-primary'
                : 'text-text-secondary hover:text-text-primary',
            )}
          >
            {item.label}
          </button>
        ))}
      </div>
      <div className="flex flex-wrap items-center gap-2">
        {PILLS.map((pill) => (
          <span
            key={pill.label}
            className="inline-flex items-center gap-1.5 rounded-full border border-background-border bg-background-surface px-3 py-1 text-xs font-semibold text-text-secondary"
          >
            <span className={cn('h-2 w-2 rounded-full', pill.dot)} />
            {pill.label}
            <span className="font-mono font-bold text-text-primary">
              {pill.count}
            </span>
          </span>
        ))}
      </div>
    </div>
  )
}