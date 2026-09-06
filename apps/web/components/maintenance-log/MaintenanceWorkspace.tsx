'use client'

import { useMemo, useState } from 'react'
import { ChevronDown, Filter, Search } from 'lucide-react'
import { MaintenanceTable } from './MaintenanceTable'
import { MaintenanceTabs } from './MaintenanceTabs'
import { MaintenanceHealth } from './MaintenanceHealth'
import { RecentActivity } from './RecentActivity'
import { Card } from '@/components/ui/Card'
import {
  MAINTENANCE_RECORDS,
  MAINTENANCE_TAB_COUNTS,
  type MaintenanceTabKey,
} from '@/lib/maintenance-records'

const DROPDOWNS = ['All Types', 'All Priorities', 'All India']

export function MaintenanceWorkspace() {
  const [activeTab, setActiveTab] = useState<MaintenanceTabKey>('all')
  const [search, setSearch] = useState('')

  const rows = useMemo(() => {
    const q = search.trim().toLowerCase()
    const tabFiltered =
      activeTab === 'all'
        ? MAINTENANCE_RECORDS
        : MAINTENANCE_RECORDS.filter((record) => record.tabKey === activeTab)
    if (!q) return tabFiltered
    return tabFiltered.filter(
      (record) =>
        record.logId.toLowerCase().includes(q) ||
        record.assetId.toLowerCase().includes(q) ||
        record.name.toLowerCase().includes(q) ||
        record.team.toLowerCase().includes(q),
    )
  }, [activeTab, search])

  return (
    <div className="flex items-start gap-6">
      <div className="flex min-w-0 flex-1 flex-col gap-6">
        <Card className="flex flex-wrap items-center gap-2">
          <div className="relative min-w-[220px] flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
            <input
              type="search"
              aria-label="Search maintenance records"
              placeholder="Search maintenance ID, asset, or team..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              className="h-9 w-full rounded-lg border border-background-border bg-background-surface pl-9 pr-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-status-info/50"
            />
          </div>
          {DROPDOWNS.map((label) => (
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
            <Filter className="h-4 w-4" />
            Advanced
          </button>
          <button
            type="button"
            onClick={() => setSearch('')}
            className="text-sm font-medium text-status-critical transition-colors hover:text-status-critical/80"
          >
            Reset
          </button>
        </Card>

        <MaintenanceTabs
          activeTab={activeTab}
          counts={MAINTENANCE_TAB_COUNTS}
          onChange={setActiveTab}
        />

        <MaintenanceTable rows={rows} />
      </div>

      <div className="flex w-full shrink-0 flex-col gap-6 md:w-[360px]">
        <MaintenanceHealth />
        <RecentActivity />
        <Card className="flex flex-col divide-y divide-background-border p-0">
          <a
            href="#"
            className="px-6 py-4 text-sm font-medium text-text-primary transition-colors hover:text-text-secondary"
          >
            📄 Compliance Docs
          </a>
          <a
            href="#"
            className="px-6 py-4 text-sm font-medium text-text-primary transition-colors hover:text-text-secondary"
          >
            👥 Assigned Teams
          </a>
        </Card>
      </div>
    </div>
  )
}