import {
  ArrowUpRight,
  ClipboardList,
  FileText,
  Landmark,
  LayoutDashboard,
  Leaf,
  MapPin,
  type LucideIcon,
} from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import type { DataSource } from '@/lib/data-sources'
import { cn } from '@/lib/utils'

const ICONS: Record<string, LucideIcon> = {
  'DS-001': FileText,
  'DS-002': LayoutDashboard,
  'DS-003': ClipboardList,
  'DS-004': Landmark,
  'DS-005': MapPin,
  'DS-006': Leaf,
}

const ACCENTS: Record<string, string> = {
  'DS-001': 'bg-status-info/10 text-status-info',
  'DS-002': 'bg-status-stable/10 text-status-stable',
  'DS-003': 'bg-status-high/10 text-status-high',
  'DS-004': 'bg-status-moderate/10 text-status-moderate',
  'DS-005': 'bg-status-info/10 text-status-info',
  'DS-006': 'bg-status-stable/10 text-status-stable',
}

interface SourceCardProps {
  source: DataSource
}

export function SourceCard({ source }: SourceCardProps) {
  const Icon = ICONS[source.ref] ?? FileText
  const accent =
    ACCENTS[source.ref] ?? 'bg-status-info/10 text-status-info'
  const badgeVariant = source.status === 'healthy' ? 'stable' : 'high'

  return (
    <Card className="flex flex-col gap-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <span
            className={cn(
              'flex h-10 w-10 shrink-0 items-center justify-center rounded-lg',
              accent,
            )}
          >
            <Icon className="h-5 w-5" />
          </span>
          <h3 className="text-base font-semibold text-text-primary">
            {source.title}
          </h3>
        </div>
        <Badge variant={badgeVariant}>
          {source.status === 'healthy' ? 'HEALTHY' : 'WARNING'}
        </Badge>
      </div>

      <p className="text-sm leading-relaxed text-text-secondary">
        {source.description}
      </p>

      <div className="grid grid-cols-3 gap-4 rounded-lg border border-background-border bg-background-surface p-4">
        <Meta label="Data Type" value={source.dataType} />
        <Meta label="Records" value={source.records} />
        <Meta label="Last Update" value={source.lastUpdate} />
      </div>

      <div className="flex items-center justify-between">
        <span className="font-mono text-xs text-text-muted">
          Ref: {source.ref}
        </span>
        <a
          href="#"
          className="inline-flex items-center gap-1 text-sm font-medium text-status-info transition-colors hover:underline"
        >
          View Source
          <ArrowUpRight className="h-4 w-4" />
        </a>
      </div>
    </Card>
  )
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex min-w-0 flex-col gap-1">
      <span className="text-[10px] font-bold uppercase tracking-wider text-text-muted">
        {label}
      </span>
      <span className="truncate font-mono text-sm font-semibold text-text-primary">
        {value}
      </span>
    </div>
  )
}