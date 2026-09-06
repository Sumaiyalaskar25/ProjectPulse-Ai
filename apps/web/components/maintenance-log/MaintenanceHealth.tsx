import { Card } from '@/components/ui/Card'
import { cn } from '@/lib/utils'

const METRICS = [
  { label: 'Overdue', value: '128', dot: 'bg-status-critical' },
  { label: 'Due 7 Days', value: '46', dot: 'bg-status-high' },
  { label: 'Due 30 Days', value: '214', dot: 'bg-status-moderate' },
  { label: 'Up to Date', value: '2,098', dot: 'bg-status-stable' },
]

export function MaintenanceHealth() {
  return (
    <Card className="flex flex-col gap-4">
      <h2 className="text-base font-semibold text-text-primary">
        ⚡ Maintenance Health
      </h2>
      <ul className="flex flex-col">
        {METRICS.map((metric) => (
          <li
            key={metric.label}
            className="flex items-center justify-between gap-3 border-b border-background-border py-2.5 last:border-0"
          >
            <span className="inline-flex items-center gap-2.5 text-sm text-text-secondary">
              <span className={cn('h-2 w-2 rounded-full', metric.dot)} />
              {metric.label}
            </span>
            <span className="font-mono text-sm font-bold text-text-primary">
              {metric.value}
            </span>
          </li>
        ))}
      </ul>

      <div className="rounded-lg border border-background-border bg-background-surface p-4">
        <p className="text-xs font-bold uppercase tracking-wider text-text-muted">
          Avg Response Time
        </p>
        <p className="mt-1 font-mono text-2xl font-bold text-text-primary">
          14.2h
        </p>
        <p className="mt-1 text-xs font-medium text-status-stable">
          -2.4% from baseline. Efficiency trend is positive.
        </p>
      </div>
    </Card>
  )
}