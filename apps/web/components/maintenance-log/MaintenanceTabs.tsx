import { cn } from '@/lib/utils'
import type { MaintenanceTabKey } from '@/lib/maintenance-records'

interface TabDef {
  key: MaintenanceTabKey
  label: string
}

const TABS: TabDef[] = [
  { key: 'all', label: 'All' },
  { key: 'overdue', label: 'Overdue' },
  { key: 'in-progress', label: 'In Progress' },
  { key: 'scheduled', label: 'Scheduled' },
  { key: 'completed', label: 'Completed' },
]

interface MaintenanceTabsProps {
  activeTab: MaintenanceTabKey
  counts: Record<MaintenanceTabKey, string>
  onChange: (tab: MaintenanceTabKey) => void
}

export function MaintenanceTabs({
  activeTab,
  counts,
  onChange,
}: MaintenanceTabsProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-b border-background-border">
      <div className="flex items-center gap-6">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            type="button"
            onClick={() => onChange(tab.key)}
            className={cn(
              '-mb-px border-b-2 pb-2.5 text-sm font-semibold transition-colors',
              activeTab === tab.key
                ? 'border-status-info text-text-primary'
                : 'border-transparent text-text-secondary hover:text-text-primary',
            )}
          >
            {tab.label} ({counts[tab.key]})
          </button>
        ))}
      </div>
      <span className="flex items-center gap-2 font-mono text-xs text-text-secondary">
        <span className="h-2 w-2 rounded-full bg-status-stable" />
        ⚡ LIVE_DB_FEED: SYNC_OK
      </span>
    </div>
  )
}