import Link from 'next/link'
import { AlertTriangle } from 'lucide-react'
import { AppShell } from '@/components/layout/AppShell'
import { AlertsWorkspace } from '@/components/alerts/AlertsWorkspace'
import { Button } from '@/components/ui/Button'
import { PendingAction } from '@/components/ui/PendingAction'
import { pageTitle } from '@/lib/design-tokens'
import { cn } from '@/lib/utils'

export default function AlertsPage() {
  return (
    <AppShell
      activeNav="Alerts"
      breadcrumb={['Portfolio', 'National Infrastructure']}
    >
      <div className="flex flex-col gap-6">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg border border-background-border bg-background-surface">
              <AlertTriangle className="h-5 w-5 text-status-critical" />
            </span>
            <div>
              <h1 className={cn(pageTitle)}>
                INTERVENTION &amp; ALERT TRIAGE QUEUE
              </h1>
              <p className="mt-1 text-sm text-text-secondary">
                Prioritizing 142 active anomalies across national infrastructure
                assets.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <PendingAction>
              <Button variant="secondary">View History</Button>
            </PendingAction>
            <Button asChild variant="secondary">
              <Link href="/dashboard">Command Dashboard</Link>
            </Button>
          </div>
        </header>

        <AlertsWorkspace />
      </div>
    </AppShell>
  )
}