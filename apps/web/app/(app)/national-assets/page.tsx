'use client'

import { useState } from 'react'
import { Download, Plus } from 'lucide-react'
import { AppShell } from '@/components/layout/AppShell'
import { NationalAssetsWorkspace } from '@/components/national-assets/NationalAssetsWorkspace'
import { Button } from '@/components/ui/Button'
import { StatCard } from '@/components/ui/StatCard'
import { pageTitle } from '@/lib/design-tokens'
import { cn } from '@/lib/utils'
import { PROJECTS } from '@/lib/projects'
import { useToastStore } from '@/lib/toast-store'

export default function NationalAssetsPage() {
  const showToast = useToastStore((state) => state.show)
  const [showAddModal, setShowAddModal] = useState(false)

  const handleExport = () => {
    const csvHeader = 'Project ID,Name,Ministry,Region,Risk,Change,Exposure,Confidence,Status\n'
    const csvRows = PROJECTS.map(
      (p) =>
        `"${p.id}","${p.name}","${p.ministry}","${p.region}","${p.risk}","${p.change}","${p.exposure}",${p.confidence}%,"${p.status}"`,
    ).join('\n')

    const blob = new Blob([csvHeader + csvRows], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `national_assets_portfolio_${Date.now()}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    showToast('National assets portfolio exported as CSV.')
  }

  const handleAddProject = () => {
    showToast('Asset Registration Portal opened. Submitting project telemetry to registry.')
  }

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
            <Button variant="secondary" onClick={handleExport}>
              <Download className="h-4 w-4" />
              Export Portfolio
            </Button>
            <Button variant="primary" onClick={handleAddProject}>
              <Plus className="h-4 w-4" />
              Add / Register Project
            </Button>
          </div>
        </header>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
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