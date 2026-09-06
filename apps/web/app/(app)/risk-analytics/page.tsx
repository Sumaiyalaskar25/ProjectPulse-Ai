import { ChevronDown, Download, Search } from 'lucide-react'
import { AppShell } from '@/components/layout/AppShell'
import { DeterioratingProjectsTable } from '@/components/risk-analytics/DeterioratingProjectsTable'
import { RiskDonut } from '@/components/risk-analytics/RiskDonut'
import { RiskDrivers } from '@/components/risk-analytics/RiskDrivers'
import { RiskLandscape } from '@/components/risk-analytics/RiskLandscape'
import { RiskTrajectory } from '@/components/risk-analytics/RiskTrajectory'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { PendingAction } from '@/components/ui/PendingAction'
import { StatCard } from '@/components/ui/StatCard'
import { pageTitle } from '@/lib/design-tokens'
import { cn } from '@/lib/utils'

const FILTER_DROPDOWNS = [
  'All Ministries',
  'All Sectors',
  'National',
  'All Tiers',
  'Q3 2023',
]

export default function RiskAnalyticsPage() {
  return (
    <AppShell
      activeNav="Risk Analytics"
      breadcrumb={['Dashboard', 'Risk Analytics']}
    >
      <div className="flex flex-col gap-6">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className={cn(pageTitle)}>RISK ANALYTICS</h1>
              <Badge variant="stable">● Active Pulse</Badge>
            </div>
            <p className="mt-2 max-w-2xl text-sm leading-relaxed text-text-secondary">
              Portfolio-level risk intelligence, structural drivers, and
              asset deterioration analysis across national infrastructure
              units.
            </p>
          </div>
          <div className="flex flex-col items-end gap-3">
            <p className="font-mono text-xs text-text-muted">
              Last Model Run: Oct 27, 2023 14:32:01 UTC
            </p>
            <div className="flex items-center gap-2">
              <PendingAction>
                <Button variant="secondary">Compare Period</Button>
              </PendingAction>
              <PendingAction>
                <Button variant="primary">
                  <Download className="h-4 w-4" />
                  Export Analysis
                </Button>
              </PendingAction>
            </div>
          </div>
        </header>

        <Card className="flex flex-wrap items-center gap-2 p-4">
          <div className="relative min-w-[220px] flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
            <input
              type="search"
              aria-label="Search projects"
              placeholder="Search projects..."
              className="h-9 w-full rounded-lg border border-background-border bg-background-surface pl-9 pr-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-status-info/50"
            />
          </div>
          {FILTER_DROPDOWNS.map((label) => (
            <button
              key={label}
              type="button"
              className="inline-flex items-center gap-2 rounded-full border border-background-border bg-background-surface px-4 py-2 text-sm text-text-secondary transition-colors hover:text-text-primary"
            >
              {label}
              <ChevronDown className="h-4 w-4 text-text-muted" />
            </button>
          ))}
          <button
            type="button"
            className="inline-flex items-center gap-2 text-sm font-medium text-text-secondary transition-colors hover:text-text-primary"
          >
            Advanced Filters
          </button>
        </Card>

        <div className="grid grid-cols-4 gap-4">
          <StatCard
            label="Portfolio Risk Score"
            value="64.8%"
            delta={1.2}
            deltaSuffix="%"
            deltaDirection="bad"
            subLabel="Aggregate sensitivity across sectors"
          />
          <StatCard
            label="Capital at Risk"
            value="3.8K Cr"
            subLabel="142 critical projects identified"
          />
          <StatCard
            label="Projects Deteriorating"
            value="184"
            delta={23}
            deltaSuffix=" this reporting period"
            deltaDirection="bad"
          />
          <StatCard
            label="High-Sensitivity Projects"
            value="318"
            subLabel="Requires executive monitoring"
          />
        </div>

        <div className="grid grid-cols-2 gap-6">
          <RiskLandscape />
          <RiskDonut />
        </div>

        <div className="grid grid-cols-2 gap-6">
          <RiskTrajectory />
          <RiskDrivers />
        </div>

        <DeterioratingProjectsTable />

        <Card className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3">
            <span className="flex items-center gap-2 font-mono text-sm text-status-stable">
              <span className="text-xs">🟢</span> Data Integrity: 99.8%
            </span>
            <Badge variant="neutral">ER_INFRA_V4.2.1</Badge>
          </div>
          <p className="max-w-xl text-sm leading-relaxed text-text-secondary">
            Executive Summary: Portfolio sensitivity is within baseline
            (+/- 5%) for 82% of assets.
          </p>
          <PendingAction>
            <Button variant="secondary">Re-Run Model</Button>
          </PendingAction>
        </Card>
      </div>
    </AppShell>
  )
}