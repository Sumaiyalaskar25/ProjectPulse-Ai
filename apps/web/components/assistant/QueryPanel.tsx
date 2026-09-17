'use client'

import { Download, MessageSquare, Plus } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { useAssistantStore } from '@/lib/assistant-store'
import { useToastStore } from '@/lib/toast-store'

const QUICK_ACTIONS = [
  {
    icon: '📊',
    label: 'Analyze Overruns',
    description: 'Compare budget vs actuals for highway corridors.',
    query: 'Analyze the highest budget overruns across highway and transport projects.',
  },
  {
    icon: '✨',
    label: 'Risk Forecast',
    description: 'Project delays and trajectory across critical assets.',
    query: 'Which projects have the highest predicted delay in the next 12 months?',
  },
  {
    icon: '🗄',
    label: 'Data Audit',
    description: 'Validate data freshness and anomalies across ministries.',
    query: 'Show a breakdown of projects by ministry and risk tier.',
  },
]

const SESSIONS = [
  {
    title: 'NH-44 Bridge Risk Analysis',
    date: 'Oct 24, 2023',
    query: 'Provide a detailed status on NH-44 Expressway Extension and its key risk drivers.',
  },
  {
    title: 'Monsoon Impact Projection',
    date: 'Oct 22, 2023',
    query: 'How does seasonal monsoon rainfall impact construction schedules in the Eastern region?',
  },
  {
    title: 'Mumbai Metro Phase 3 Budget',
    date: 'Oct 18, 2023',
    query: 'What is the current cost overrun and completion trajectory for Mumbai Metro Phase 3?',
  },
  {
    title: 'Solar Park Grid Integration',
    date: 'Oct 15, 2023',
    query: 'List power and energy projects with critical transmission bottlenecks.',
  },
]

export function QueryPanel() {
  const { sendMessage, clearChat, exportChat, currentSessionId } = useAssistantStore()
  const showToast = useToastStore((state) => state.show)

  return (
    <div className="flex w-[320px] shrink-0 flex-col gap-4">
      <Button
        variant="primary"
        className="w-full"
        onClick={clearChat}
      >
        <Plus className="h-4 w-4" />
        New Intelligence Query
      </Button>

      {QUICK_ACTIONS.map((action) => (
        <button
          key={action.label}
          type="button"
          onClick={() => {
            void sendMessage(action.query)
          }}
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
          onClick={() => showToast('Displaying 4 recorded executive sessions.')}
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
            onClick={() => {
              void sendMessage(session.query)
            }}
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
            ID: {currentSessionId}
          </p>
        </div>
        <button
          type="button"
          aria-label="Download session logs"
          onClick={exportChat}
          className="text-text-secondary transition-colors hover:text-text-primary"
        >
          <Download className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}