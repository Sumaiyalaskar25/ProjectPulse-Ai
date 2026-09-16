'use client'

import { Download, Plus } from 'lucide-react'
import { AppShell } from '@/components/layout/AppShell'
import { MaintenanceWorkspace } from '@/components/maintenance-log/MaintenanceWorkspace'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { StatCard } from '@/components/ui/StatCard'
import { pageTitle } from '@/lib/design-tokens'
import { cn } from '@/lib/utils'
import { MAINTENANCE_RECORDS } from '@/lib/maintenance-records'
import { useToastStore } from '@/lib/toast-store'

export default function MaintenanceLogPage() {
  const showToast = useToastStore((state) => state.show)

  const handleExport = () => {
    const csvHeader = 'Log ID,Asset ID,Project Name,Task Type,Priority,Team,Status,Last Check,Due\n'
    const csvRows = MAINTENANCE_RECORDS.map(
      (r) =>
        `"${r.logId}","${r.assetId}","${r.name}","${r.taskType}","${r.priority}","${r.team}","${r.status}","${r.lastCheck}","${r.due}"`,
    ).join('\n')

    const blob = new Blob([csvHeader + csvRows], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `maintenance_log_${Date.now()}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    showToast('Maintenance and intervention records exported as CSV.')
  }

  const handleSchedule = () => {
    showToast('Scheduled new preventative maintenance service window.')
  }

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
            <Button variant="secondary" onClick={handleExport}>
              <Download className="h-4 w-4" />
              Export Log
            </Button>
            <Button variant="primary" onClick={handleSchedule}>
              <Plus className="h-4 w-4" />
              Schedule Maintenance
            </Button>
          </div>
        </header>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
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