import { Download, Plus } from 'lucide-react'
import { AppShell } from '@/components/layout/AppShell'
import { NationalAssetsWorkspace } from '@/components/national-assets/NationalAssetsWorkspace'
import { Button } from '@/components/ui/Button'
import { PendingAction } from '@/components/ui/PendingAction'
import { StatCard } from '@/components/ui/StatCard'
import { pageTitle } from '@/lib/design-tokens'
import { cn } from '@/lib/utils'

export default function NationalAssetsPage() {
  return (
    <AppShell
      activeNav="National Assets"
      breadcrumb={['Dashboard', 'National Assets']}
    >
      <div className="flex flex-col gap-6">
        <header className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="font-mono text-xs text-text-muted">
              DASHBOARD &gt; NATIONAL ASSETS
            </p>
            <h1 className={cn(pageTitle, 'mt-2')}>NATIONAL ASSETS</h1>
            <p className="mt-2 max-w-2xl text-sm leading-relaxed text-text-secondary">
              National infrastructure project portfolio monitoring.
              High-precision command view for risk assessment and capital
              allocation tracking across all ministries.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <PendingAction>
              <Button variant="secondary">
                <Download className="h-4 w-4" />
                Export Portfolio
              </Button>
            </PendingAction>
            <Button variant="primary">
              <Plus className="h-4 w-4" />
              Add / Register Project
            </Button>
          </div>
        </header>

        <div className="grid grid-cols-4 gap-4">
          <StatCard
            label="Total Projects"
            value="1,775"
            delta={12}
            deltaSuffix="% from Q2 baseline"
            deltaDirection="good"
          />
          <StatCard
            label="Critical Projects"
            value="142"
            subLabel="Requires immediate attention"
          />
          <StatCard
            label="Capital at Risk"
            value="3.8K Cr"
            delta={12.1}
            deltaSuffix="% variance this month"
            deltaDirection="bad"
          />
          <StatCard
            label="Under Monitoring"
            value="318"
            subLabel="High-risk projects assigned"
          />
        </div>

        <NationalAssetsWorkspace />
      </div>
    </AppShell>
  )
}