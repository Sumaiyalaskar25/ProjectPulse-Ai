import { cn } from '@/lib/utils'

export type AlertTabKey = 'all' | 'unassigned' | 'in-progress' | 'resolved'

interface TabDef {
  key: AlertTabKey
  label: string
}

const TABS: TabDef[] = [
  { key: 'all', label: 'All Alerts' },
  { key: 'unassigned', label: 'Unassigned' },
  { key: 'in-progress', label: 'In Progress' },
  { key: 'resolved', label: 'Resolved' },
]

interface AlertTabsProps {
  activeTab: AlertTabKey
  counts: Record<AlertTabKey, number>
  onChange: (tab: AlertTabKey) => void
}

export function AlertTabs({
  activeTab,
  counts,
  onChange,
}: AlertTabsProps) {
  return (
    <div className="flex items-center gap-6 border-b border-background-border">
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
  )
}