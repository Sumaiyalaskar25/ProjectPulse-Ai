import { Download } from 'lucide-react'
import { AppShell } from '@/components/layout/AppShell'
import { MaintenanceWorkspace } from '@/components/maintenance-log/MaintenanceWorkspace'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { PendingAction } from '@/components/ui/PendingAction'
import { StatCard } from '@/components/ui/StatCard'
import { pageTitle } from '@/lib/design-tokens'
import { cn } from '@/lib/utils'

export default function MaintenanceLogPage() {
  return (
    <AppShell
      activeNav="Maintenance Log"
      breadcrumb={['Dashboard', 'Maintenance Log']}
    >
      <div className="flex flex-col gap-6">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className={cn(pageTitle)}>MAINTENANCE LOG</h1>
              <Badge variant="stable">AUDIT_MODE: ENABLED</Badge>
            </div>
            <p className="mt-2 max-w-2xl text-sm leading-relaxed text-text-secondary">
              Comprehensive tracking of maintenance activities, structural
              inspections, and service histories across national
              infrastructure units. Live monitoring for predictive failure
              mitigation.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <PendingAction>
              <Button variant="secondary">
                <Download className="h-4 w-4" />
                Export Log
              </Button>
            </PendingAction>
            <PendingAction>
              <Button variant="primary">Schedule Maintenance</Button>
            </PendingAction>
          </div>
        </header>

        <div className="grid grid-cols-4 gap-4">
          <StatCard
            label="Total Records"
            value="2,486"
            subLabel="Lifetime intervention logs"
          />
          <StatCard
            label="Overdue Interventions"
            value="128"
            subLabel="Requires immediate action"
            subLabelClassName="text-status-critical"
          />
          <StatCard
            label="Due This Month"
            value="214"
            subLabel="Scheduled service windows"
          />
          <StatCard
            label="Completed YTD"
            value="2,144"
            subLabel="86.2% completion rate"
            subLabelClassName="text-status-stable"
          />
        </div>

        <MaintenanceWorkspace />
      </div>
    </AppShell>
  )
}