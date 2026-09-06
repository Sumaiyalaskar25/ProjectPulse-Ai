'use client'

import { useMemo, useState } from 'react'
import {
  AlertCircle,
  CheckCircle2,
  ChevronDown,
  Clock,
  Filter,
  Search,
} from 'lucide-react'
import { AlertInsights } from './AlertInsights'
import { AlertTable, ALERTS } from './AlertTable'
import { AlertTabs, type AlertTabKey } from './AlertTabs'
import { Card } from '@/components/ui/Card'

const DROPDOWNS = ['All Ministries', 'All Severities']

const STATS = [
  {
    label: 'Triage Efficiency',
    value: '94.2%',
    icon: CheckCircle2,
    iconClass: 'text-status-stable',
  },
  {
    label: 'Avg. Response Time',
    value: '14.2m',
    icon: Clock,
    iconClass: 'text-status-info',
  },
  {
    label: 'High Sensitivity Backlog',
    value: '12',
    icon: AlertCircle,
    iconClass: 'text-status-high',
  },
]

export function AlertsWorkspace() {
  const [activeTab, setActiveTab] = useState<AlertTabKey>('all')
  const [search, setSearch] = useState('')

  const searchFiltered = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return ALERTS
    return ALERTS.filter(
      (alert) =>
        alert.name.toLowerCase().includes(q) ||
        alert.assetId.toLowerCase().includes(q) ||
        (alert.officer !== null &&
          alert.officer.name.toLowerCase().includes(q)),
    )
  }, [search])

  const counts = useMemo(
    () => ({
      all: searchFiltered.length,
      unassigned: searchFiltered.filter((alert) => alert.officer === null)
        .length,
      'in-progress': searchFiltered.filter(
        (alert) => alert.status === 'in-progress',
      ).length,
      resolved: searchFiltered.filter((alert) => alert.status === 'resolved')
        .length,
    }),
    [searchFiltered],
  )

  const rows = useMemo(() => {
    if (activeTab === 'unassigned') {
      return searchFiltered.filter((alert) => alert.officer === null)
    }
    if (activeTab === 'in-progress' || activeTab === 'resolved') {
      return searchFiltered.filter((alert) => alert.status === activeTab)
    }
    return searchFiltered
  }, [activeTab, searchFiltered])

  return (
    <div className="flex items-start gap-6">
      <div className="flex min-w-0 flex-1 flex-col gap-6">
        <AlertTabs activeTab={activeTab} counts={counts} onChange={setActiveTab} />

        <Card className="flex flex-wrap items-center gap-2">
          <div className="relative min-w-[220px] flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
            <input
              type="search"
              aria-label="Search alerts"
              placeholder="Search by project, asset ID, or officer..."
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
            Advanced Filters
          </button>
        </Card>

        <AlertTable rows={rows} />

        <div className="grid grid-cols-3 gap-4">
          {STATS.map((stat) => {
            const Icon = stat.icon
            return (
              <Card key={stat.label} className="flex items-center gap-3 p-4">
                <Icon className={`h-5 w-5 shrink-0 ${stat.iconClass}`} />
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-text-muted">
                    {stat.label}
                  </p>
                  <p className="font-mono text-xl font-bold text-text-primary">
                    {stat.value}
                  </p>
                </div>
              </Card>
            )
          })}
        </div>
      </div>

      <AlertInsights />
    </div>
  )
}