import {
  ArrowDownRight,
  ArrowUpRight,
  ChevronRight,
} from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import type { QuickView } from './FilterBar'
import { cn } from '@/lib/utils'

type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM'

const QUEUE: {
  id: string
  severity: Severity
  title: string
  location: string
  delta: number
  status: 'in-progress' | 'scheduled'
}[] = [
  {
    id: 'OP-2012-C',
    severity: 'CRITICAL',
    title: 'NH-48 Pothole Repair Cluster 7',
    location: 'Sector 12 · NH-48 Corridor',
    delta: -12,
    status: 'in-progress',
  },
  {
    id: 'OP-1094-K',
    severity: 'HIGH',
    title: 'Krishna Dam Spillway Gate Actuator',
    location: 'Unit 3 · Krishna River Basin',
    delta: 8,
    status: 'in-progress',
  },
  {
    id: 'OP-5510-M',
    severity: 'HIGH',
    title: 'Metro Viaduct Expansion Joints',
    location: 'Line 2 · Sector 9',
    delta: 5,
    status: 'in-progress',
  },
  {
    id: 'OP-0319-P',
    severity: 'MEDIUM',
    title: 'Port Logistics Crane Motor 4',
    location: 'Berth 4 · Port Complex',
    delta: 3,
    status: 'scheduled',
  },
  {
    id: 'OP-7734-T',
    severity: 'MEDIUM',
    title: 'Telecom Tower Monopole 88',
    location: 'Zone 5 · Ring Road',
    delta: -2,
    status: 'scheduled',
  },
  {
    id: 'OP-8441-B',
    severity: 'CRITICAL',
    title: 'Bridge Bearing Replacement V2',
    location: 'Span 14 · NH-44 Ramp',
    delta: -9,
    status: 'in-progress',
  },
]

const BADGE_VARIANT: Record<Severity, 'critical' | 'high' | 'moderate'> = {
  CRITICAL: 'critical',
  HIGH: 'high',
  MEDIUM: 'moderate',
}

function filterQueue(quickView: QuickView): typeof QUEUE {
  if (quickView === 'high-risk') {
    return QUEUE.filter(
      (item) => item.severity === 'CRITICAL' || item.severity === 'HIGH',
    )
  }
  if (quickView === 'under-repair') {
    return QUEUE.filter((item) => item.status === 'in-progress')
  }
  return QUEUE
}

interface InterventionQueueProps {
  quickView?: QuickView
}

export function InterventionQueue({
  quickView = 'portfolio',
}: InterventionQueueProps) {
  const items = filterQueue(quickView)
  return (
    <Card className="flex flex-col">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-text-primary">
            🕐 Intervention Queue
          </h2>
          <p className="mt-1 text-sm text-text-secondary">
            Prioritized active field maintenance tasks.
          </p>
        </div>
        <Badge variant="stable">LIVE UPDATE</Badge>
      </div>

      <ul className="mt-4 flex-1 divide-y divide-background-border">
        {items.map((item) => {
          const isUp = item.delta > 0
          const DeltaIcon = isUp ? ArrowUpRight : ArrowDownRight
          return (
            <li key={item.id} className="flex items-center justify-between gap-3 py-3">
              <div className="flex min-w-0 items-center gap-3">
                <Badge variant={BADGE_VARIANT[item.severity]}>
                  {item.severity}
                </Badge>
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold text-text-primary">
                    {item.title}
                  </p>
                  <p className="truncate font-mono text-xs text-text-muted">
                    {item.id} · {item.location}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-[10px] font-bold uppercase tracking-wider text-text-muted">
                    Risk Delta
                  </p>
                  <p
                    className={cn(
                      'font-mono text-xs font-bold',
                      isUp ? 'text-status-critical' : 'text-status-stable',
                    )}
                  >
                    <DeltaIcon className="mr-0.5 inline h-3 w-3" />
                    {isUp ? '+' : ''}
                    {item.delta}%
                  </p>
                </div>
                <ChevronRight className="h-4 w-4 shrink-0 text-text-muted" />
              </div>
            </li>
          )
        })}
      </ul>

      <Button variant="primary" className="mt-6 w-full">
        ↗ OPEN COMMAND BOARD
      </Button>
    </Card>
  )
}