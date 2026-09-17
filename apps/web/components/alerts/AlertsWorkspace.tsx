'use client'

import { useMemo, useState } from 'react'
import {
  AlertCircle,
  CheckCircle2,
  ChevronDown,
  Clock,
  Filter,
  Loader2,
  RefreshCw,
  Search,
} from 'lucide-react'
import { AlertInsights } from './AlertInsights'
import { AlertTable, ALERTS, type AlertRow } from './AlertTable'
import { AlertTabs, type AlertTabKey } from './AlertTabs'
import { Card } from '@/components/ui/Card'
import { useAlerts } from '@/hooks/use-alerts'
import { useToastStore } from '@/lib/toast-store'

const DROPDOWNS = ['All Ministries', 'All Severities']

export function AlertsWorkspace() {
  const [activeTab, setActiveTab] = useState<AlertTabKey>('all')
  const [search, setSearch] = useState('')
  const [localRows, setLocalRows] = useState<AlertRow[]>(ALERTS)
  const showToast = useToastStore((state) => state.show)

  const { data: backendAlerts, isLoading, refetch } = useAlerts()

  // Merge backend alerts if returned from real API
  const mergedAlerts = useMemo(() => {
    if (backendAlerts && Array.isArray(backendAlerts) && backendAlerts.length > 0) {
      return backendAlerts.map((a, idx): AlertRow => ({
        id: `ALT-${a.alert_id}`,
        numericId: a.alert_id,
        assetId: a.project_id,
        name: a.title || `Project ${a.project_id}`,
        sector: 'National Infrastructure',
        severity: (a.severity?.toUpperCase() as any) || 'CRITICAL',
        time: a.triggered_at ? new Date(a.triggered_at).toLocaleTimeString() : `${idx * 15 + 5}m ago`,
        delta: a.risk_delta ? `+${(a.risk_delta * 100).toFixed(1)}%` : '+14.2%',
        up: true,
        status: (a.status as any) || 'unassigned',
        officer: null,
      }))
    }
    return localRows
  }, [backendAlerts, localRows])

  const searchFiltered = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return mergedAlerts
    return mergedAlerts.filter(
      (alert) =>
        alert.name.toLowerCase().includes(q) ||
        alert.assetId.toLowerCase().includes(q) ||
        (alert.officer !== null &&
          alert.officer.name.toLowerCase().includes(q)),
    )
  }, [search, mergedAlerts])

  const counts = useMemo(
    () => ({
      all: searchFiltered.length,
      unassigned: searchFiltered.filter((alert) => alert.status === 'unassigned' || alert.officer === null)
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
      return searchFiltered.filter((alert) => alert.status === 'unassigned' || alert.officer === null)
    }
    if (activeTab === 'in-progress' || activeTab === 'resolved') {
      return searchFiltered.filter((alert) => alert.status === activeTab)
    }
    return searchFiltered
  }, [activeTab, searchFiltered])

  const handleAcknowledgeLocal = (alertId: string) => {
    setLocalRows((prev) =>
      prev.map((row) =>
        row.id === alertId ? { ...row, status: 'in-progress' } : row,
      ),
    )
    void refetch()
  }

  return (
    <div className="flex flex-col lg:flex-row items-start gap-6">
      <div className="flex min-w-0 flex-1 flex-col gap-6 w-full">
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
              onClick={() => showToast(`Filtered by ${label}`)}
              className="inline-flex items-center gap-2 rounded-full border border-background-border bg-background-surface px-4 py-2 text-sm text-text-secondary transition-colors hover:text-text-primary"
            >
              {label}
              <ChevronDown className="h-4 w-4 text-text-muted" />
            </button>
          ))}
          <button
            type="button"
            onClick={() => {
              void refetch()
              showToast('Refreshed alert telemetry from backend queue.')
            }}
            className="inline-flex items-center gap-2 text-sm font-medium text-text-secondary transition-colors hover:text-text-primary"
          >
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
            Refresh
          </button>
        </Card>

        <AlertTable rows={rows} onAcknowledge={handleAcknowledgeLocal} />

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card className="flex items-center gap-3 p-4">
            <CheckCircle2 className="h-5 w-5 shrink-0 text-status-stable" />
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-text-muted">
                Triage Efficiency
              </p>
              <p className="font-mono text-xl font-bold text-text-primary">
                94.2%
              </p>
            </div>
          </Card>
          <Card className="flex items-center gap-3 p-4">
            <Clock className="h-5 w-5 shrink-0 text-status-info" />
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-text-muted">
                Avg. Response Time
              </p>
              <p className="font-mono text-xl font-bold text-text-primary">
                14.2m
              </p>
            </div>
          </Card>
          <Card className="flex items-center gap-3 p-4">
            <AlertCircle className="h-5 w-5 shrink-0 text-status-high" />
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-text-muted">
                Active Anomalies
              </p>
              <p className="font-mono text-xl font-bold text-text-primary">
                {counts.all}
              </p>
            </div>
          </Card>
        </div>
      </div>

      <AlertInsights />
    </div>
  )
}