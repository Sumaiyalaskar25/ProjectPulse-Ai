import { Download, MessageSquare, Plus } from 'lucide-react'
import { Button } from '@/components/ui/Button'

const QUICK_ACTIONS = [
  {
    icon: '📊',
    label: 'Analyze Overruns',
    description: 'Compare budget vs actuals for NH corridors.',
  },
  {
    icon: '✨',
    label: 'Risk Forecast',
    description: 'Project delays for Segment VII based on weather.',
  },
  {
    icon: '🗄',
    label: 'Data Audit',
    description: 'Validate sensor logs from Section IX pylons.',
  },
]

const SESSIONS = [
  { title: 'NH-44 Bridge Risk Analysis', date: 'Oct 24, 2023' },
  { title: 'Monsoon Impact Projection', date: 'Oct 22, 2023' },
  { title: 'Mumbai Metro Phase 3 Budget', date: 'Oct 18, 2023' },
  { title: 'Solar Park Grid Integration', date: 'Oct 15, 2023' },
]

export function QueryPanel() {
  return (
    <div className="flex w-[320px] shrink-0 flex-col gap-4">
      <Button variant="primary" className="w-full">
        <Plus className="h-4 w-4" />
        New Intelligence Query
      </Button>

      {QUICK_ACTIONS.map((action) => (
        <button
          key={action.label}
          type="button"
          className="flex items-start gap-3 rounded-xl border border-background-border bg-background-surface p-4 text-left transition-colors hover:border-text-muted/40 hover:bg-background-card"
        >
          <span className="text-lg leading-none">{action.icon}</span>
          <span className="min-w-0">
            <span className="block text-sm font-bold text-text-primary">
              {action.label}
            </span>
            <span className="mt-0.5 block text-xs text-text-secondary">
              {action.description}
            </span>
          </span>
        </button>
      ))}

      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary">
          Recent Sessions
        </h3>
        <button
          type="button"
          className="text-xs font-semibold text-status-info transition-colors hover:text-sky-300"
        >
          View All
        </button>
      </div>

      <div className="flex flex-col divide-y divide-background-border rounded-xl border border-background-border bg-background-surface">
        {SESSIONS.map((session) => (
          <button
            key={session.title}
            type="button"
            className="flex items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-background-card"
          >
            <MessageSquare className="h-4 w-4 shrink-0 text-text-muted" />
            <span className="min-w-0 flex-1">
              <span className="block truncate text-sm font-medium text-text-primary">
                {session.title}
              </span>
              <span className="text-xs text-text-muted">{session.date}</span>
            </span>
          </button>
        ))}
      </div>

      <div className="mt-auto flex items-center justify-between rounded-xl border border-background-border bg-background-surface px-4 py-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-text-muted">
            Session Logs
          </p>
          <p className="mt-0.5 font-mono text-xs text-text-secondary">
            ID: PULSE-2710-X
          </p>
        </div>
        <button
          type="button"
          aria-label="Download session logs"
          className="text-text-secondary transition-colors hover:text-text-primary"
        >
          <Download className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}