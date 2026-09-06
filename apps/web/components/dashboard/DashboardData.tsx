'use client'

import { AlertTriangle } from 'lucide-react'
import { useDashboardSummary } from '@/hooks/use-dashboard'
import { useProjects } from '@/hooks/use-projects'
import { KpiCards } from './KpiCards'
import { RiskTierStrip } from './RiskTierStrip'

export function DashboardData() {
  const summary = useDashboardSummary()
  const projects = useProjects()

  return (
    <div className="flex flex-col gap-6">
      {summary.isLoading || projects.isLoading ? (
        <p className="font-mono text-xs text-text-muted">
          LOADING PORTFOLIO DATA...
        </p>
      ) : summary.isError || projects.isError ? (
        <p className="flex items-center gap-2 font-mono text-xs text-status-critical">
          <AlertTriangle className="h-3.5 w-3.5" />
          FAILED TO LOAD PORTFOLIO DATA
        </p>
      ) : (
        <>
          <KpiCards summary={summary.data} />
          <RiskTierStrip summary={summary.data} />
        </>
      )}
    </div>
  )
}