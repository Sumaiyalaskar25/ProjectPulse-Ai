import { ArrowRight } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'

const ACTIVITY = [
  {
    title: 'NH-44 Pylon Inspection',
    actor: 'Elena Vance',
    badge: 'Approved',
    badgeVariant: 'stable' as const,
    time: '24m ago',
  },
  {
    title: 'Metro Ventilation Sync',
    actor: 'System Bot',
    badge: 'Auto-Scheduled',
    badgeVariant: 'neutral' as const,
    time: '54m ago',
  },
  {
    title: 'Grid Relay #42 Failover',
    actor: 'S. Kulkarni',
    badge: 'Intervention',
    badgeVariant: 'high' as const,
    time: '1h3m ago',
  },
]

export function RecentActivity() {
  return (
    <Card className="flex flex-col gap-4">
      <h2 className="text-base font-semibold text-text-primary">
        🕐 Recent Activity
      </h2>
      <ul className="flex flex-col">
        {ACTIVITY.map((item) => (
          <li
            key={item.title}
            className="flex flex-col gap-1.5 border-b border-background-border py-3 last:border-0"
          >
            <div className="flex items-center justify-between gap-2">
              <p className="text-sm font-semibold text-text-primary">
                {item.title}
              </p>
              <Badge variant={item.badgeVariant}>{item.badge}</Badge>
            </div>
            <div className="flex items-center justify-between gap-2">
              <p className="text-xs text-text-secondary">{item.actor}</p>
              <p className="font-mono text-xs text-text-muted">
                {item.time}
              </p>
            </div>
          </li>
        ))}
      </ul>
      <a
        href="#"
        className="inline-flex items-center gap-1 text-sm font-medium text-status-info transition-colors hover:underline"
      >
        View Complete Audit Trail
        <ArrowRight className="h-3.5 w-3.5" />
      </a>
    </Card>
  )
}