import {
  ChevronLeft,
  ChevronRight,
  Eye,
  LayoutGrid,
  RefreshCw,
} from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { PendingAction } from '@/components/ui/PendingAction'
import type {
  MaintenancePriority,
  MaintenanceRecord,
  MaintenanceStatus,
} from '@/lib/maintenance-records'
import { cn } from '@/lib/utils'

const PRIORITY_DOT: Record<MaintenancePriority, string> = {
  CRITICAL: 'bg-status-critical',
  HIGH: 'bg-status-high',
  MEDIUM: 'bg-status-moderate',
  LOW: 'bg-text-muted',
}

const STATUS_VARIANT: Record<MaintenanceStatus, 'critical' | 'high' | 'neutral' | 'stable'> = {
  OVERDUE: 'critical',
  'IN PROGRESS': 'high',
  SCHEDULED: 'neutral',
  COMPLETED: 'stable',
}

interface MaintenanceTableProps {
  rows: MaintenanceRecord[]
}

export function MaintenanceTable({ rows }: MaintenanceTableProps) {
  return (
    <Card className="flex flex-col gap-0 p-0">
      <div className="flex flex-wrap items-center justify-between gap-3 px-6 pt-5 pb-4">
        <div>
          <h2 className="text-lg font-semibold text-text-primary">
            Intervention History &amp; Queue
          </h2>
          <p className="mt-1 text-sm text-text-secondary">
            Showing prioritized maintenance records
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" className="px-2.5">
            <LayoutGrid className="h-4 w-4" />
          </Button>
          <Button variant="secondary" size="sm" className="px-2.5">
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[1080px] text-left">
          <thead>
            <tr className="border-y border-background-border text-xs font-bold uppercase tracking-wider text-text-muted">
              <th scope="col" className="py-3 pl-6 pr-4">Log ID</th>
              <th scope="col" className="px-4 py-3">Project / Asset</th>
              <th scope="col" className="px-4 py-3">Task Type</th>
              <th scope="col" className="px-4 py-3">Last Check / Due</th>
              <th scope="col" className="px-4 py-3">Priority</th>
              <th scope="col" className="px-4 py-3">Team</th>
              <th scope="col" className="px-4 py-3">Status</th>
              <th scope="col" className="py-3 pl-4 pr-6 text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((record) => (
              <tr
                key={record.logId}
                className="border-b border-background-border last:border-0"
              >
                <td className="py-4 pl-6 pr-4">
                  <p className="font-mono text-sm font-semibold text-text-primary">
                    {record.logId}
                  </p>
                  <p className="mt-0.5 font-mono text-xs text-text-muted">
                    {record.assetId}
                  </p>
                </td>
                <td className="px-4 py-4">
                  <p className="text-sm font-semibold text-text-primary">
                    {record.name}
                  </p>
                  <p className="mt-0.5 text-xs text-text-secondary">
                    {record.segment}
                  </p>
                </td>
                <td className="px-4 py-4 text-sm text-text-primary">
                  {record.taskType}
                </td>
                <td className="px-4 py-4">
                  <p className="font-mono text-xs text-text-secondary">
                    Last: {record.lastCheck}
                  </p>
                  <p className="mt-0.5 font-mono text-xs font-semibold text-text-primary">
                    Due: {record.due}
                  </p>
                </td>
                <td className="px-4 py-4">
                  <span className="inline-flex items-center gap-2 text-sm text-text-primary">
                    <span
                      className={cn(
                        'h-2 w-2 rounded-full',
                        PRIORITY_DOT[record.priority],
                      )}
                    />
                    {record.priority}
                  </span>
                </td>
                <td className="px-4 py-4 text-sm text-text-primary">
                  {record.team}
                </td>
                <td className="px-4 py-4">
                  <Badge variant={STATUS_VARIANT[record.status]}>
                    {record.status}
                  </Badge>
                </td>
                <td className="py-4 pl-4 pr-6 text-right">
                  <PendingAction>
                    <Button variant="secondary" size="sm" className="px-2.5">
                      <Eye className="h-4 w-4" />
                    </Button>
                  </PendingAction>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-background-border px-6 py-4">
        <div className="flex items-center gap-4">
          <span className="text-sm text-text-secondary">
            Showing 1–10 of 2,486 records
          </span>
          <span className="flex items-center gap-1">
            <Button variant="secondary" size="sm" className="px-2.5">
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="inline-flex h-8 min-w-8 items-center justify-center rounded-lg border border-background-border bg-background-surface px-2 font-mono text-sm font-semibold text-text-primary">
              1
            </span>
            <Button variant="secondary" size="sm" className="px-2.5">
              <ChevronRight className="h-4 w-4" />
            </Button>
          </span>
        </div>
        <div className="flex flex-wrap items-center gap-4">
          <span className="font-mono text-xs text-text-secondary">
            Data Freshness: 99.8%
          </span>
          <span className="font-mono text-xs text-text-muted">
            Last Sync: 2023-10-27 16:57:01 UTC
          </span>
          <PendingAction>
            <Button variant="secondary" size="sm">
              <RefreshCw className="h-4 w-4" />
              Force Resync
            </Button>
          </PendingAction>
        </div>
      </div>
    </Card>
  )
}