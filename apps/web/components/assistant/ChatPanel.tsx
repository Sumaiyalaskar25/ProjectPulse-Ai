import { Download, MoreHorizontal, Share2, Sparkles } from 'lucide-react'
import { ChatInput } from './ChatInput'
import { ChatMessage } from './ChatMessage'
import { ResultsTable } from './ResultsTable'
import { SourcesRow } from './SourcesRow'
import { Button } from '@/components/ui/Button'
import { PendingAction } from '@/components/ui/PendingAction'

const EXECUTIVE_AVATAR = 'https://i.pravatar.cc/80?img=5'

export function ChatPanel() {
  return (
    <div className="flex h-full min-h-0 flex-1 flex-col overflow-hidden rounded-xl border border-background-border bg-background-surface">
      <header className="flex shrink-0 items-center justify-between gap-4 border-b border-background-border px-6 py-4">
        <div className="flex items-center gap-3">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-background-card">
            <Sparkles className="h-5 w-5 text-status-info" />
          </span>
          <div>
            <p className="text-sm font-bold text-text-primary">
              Paimana Intelligence
            </p>
            <p className="mt-0.5 flex items-center gap-1.5 font-mono text-xs text-text-muted">
              <span className="h-1.5 w-1.5 rounded-full bg-status-stable" />
              MODEL: ENTERPRISE_INFRA_V4
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <PendingAction>
            <Button variant="secondary" size="sm">
              <Share2 className="h-4 w-4" />
              Share Session
            </Button>
          </PendingAction>
          <PendingAction>
            <Button variant="secondary" size="sm">
              <Download className="h-4 w-4" />
              Export Insights
            </Button>
          </PendingAction>
          <Button
            variant="secondary"
            size="sm"
            aria-label="More options"
            className="px-2"
          >
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </div>
      </header>

      <div className="flex min-h-0 flex-1 flex-col gap-6 overflow-y-auto px-6 py-5">
        <ChatMessage
          role="user"
          author="EXECUTIVE DIRECTOR"
          timestamp="14:32:05"
          avatar={EXECUTIVE_AVATAR}
        >
          Identify the top 3 infrastructure projects currently exceeding
          budget by more than 15% and summarize their primary risk drivers.
        </ChatMessage>

        <ChatMessage
          role="ai"
          author="INTELLIGENCE AGENT"
          timestamp="14:32:06"
        >
          <p>
            Based on the latest data sync (Oct 27, 14:32 UTC), I have
            identified three critical projects with significant budget
            variances. The primary drivers include land acquisition litigation
            and unexpected soil instability during the monsoon period.
          </p>
          <ResultsTable />
          <SourcesRow />
        </ChatMessage>
      </div>

      <ChatInput />
    </div>
  )
}