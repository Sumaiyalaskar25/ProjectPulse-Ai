import { ChevronDown, Filter } from 'lucide-react'
import { cn } from '@/lib/utils'

export type QuickView = 'portfolio' | 'high-risk' | 'under-repair'

const FILTERS = ['Region: National', 'Asset Type: All', 'Phase: Operational']
const QUICK_VIEWS: { key: QuickView; label: string }[] = [
  { key: 'portfolio', label: 'Portfolio' },
  { key: 'high-risk', label: 'High Risk' },
  { key: 'under-repair', label: 'Under Repair' },
]

const pillClasses =
  'inline-flex items-center gap-2 rounded-full border border-background-border bg-background-surface px-4 py-2 text-sm text-text-secondary transition-colors hover:text-text-primary'

interface FilterBarProps {
  value: QuickView
  onChange: (view: QuickView) => void
}

export function FilterBar({ value, onChange }: FilterBarProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div className="flex flex-wrap items-center gap-2">
        {FILTERS.map((filter) => (
          <button key={filter} type="button" className={pillClasses}>
            <Filter className="h-4 w-4 text-text-muted" />
            {filter}
            <ChevronDown className="h-4 w-4 text-text-muted" />
          </button>
        ))}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm text-text-secondary">Quick Views:</span>
        {QUICK_VIEWS.map((view) => (
          <button
            key={view.key}
            type="button"
            onClick={() => onChange(view.key)}
            className={cn(
              'rounded-full px-4 py-2 text-sm font-medium transition-colors',
              value === view.key
                ? 'border border-background-border bg-background-card text-text-primary'
                : 'text-text-secondary hover:text-text-primary',
            )}
          >
            {view.label}
          </button>
        ))}
      </div>
    </div>
  )
}