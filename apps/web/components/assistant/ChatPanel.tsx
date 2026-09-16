'use client'

import { Download, Loader2, MoreHorizontal, Share2, Sparkles } from 'lucide-react'
import { ChatInput } from './ChatInput'
import { ChatMessage } from './ChatMessage'
import { ResultsTable } from './ResultsTable'
import { SourcesRow } from './SourcesRow'
import { Button } from '@/components/ui/Button'
import { useAssistantStore } from '@/lib/assistant-store'
import { useToastStore } from '@/lib/toast-store'

const EXECUTIVE_AVATAR = 'https://i.pravatar.cc/80?img=5'

export function ChatPanel() {
  const { messages, isLoading, exportChat, currentSessionId } = useAssistantStore()
  const showToast = useToastStore((state) => state.show)

  const handleShare = () => {
    if (navigator.clipboard) {
      void navigator.clipboard.writeText(window.location.href)
      showToast('Session link copied to clipboard.')
    } else {
      showToast('Session ID: ' + currentSessionId)
    }
  }

  return (
    <div className="flex h-full min-h-0 flex-1 flex-col overflow-hidden rounded-xl border border-background-border bg-background-surface">
      <header className="flex shrink-0 items-center justify-between gap-4 border-b border-background-border px-6 py-4">
        <div className="flex items-center gap-3">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-background-card">
            <Sparkles className="h-5 w-5 text-status-info" />
          </span>
          <div>
            <p className="text-sm font-bold text-text-primary">
              ProjectPulse Intelligence
            </p>
            <p className="mt-0.5 flex items-center gap-1.5 font-mono text-xs text-text-muted">
              <span className="h-1.5 w-1.5 rounded-full bg-status-stable" />
              SESSION: {currentSessionId}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" onClick={handleShare}>
            <Share2 className="h-4 w-4" />
            Share Session
          </Button>
          <Button variant="secondary" size="sm" onClick={exportChat}>
            <Download className="h-4 w-4" />
            Export Insights
          </Button>
          <Button
            variant="secondary"
            size="sm"
            aria-label="More options"
            className="px-2"
            onClick={() => showToast('Model engine: LightGBM v4 + Mistral-7B Instruct')}
          >
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </div>
      </header>

      <div className="flex min-h-0 flex-1 flex-col gap-6 overflow-y-auto px-6 py-5">
        {messages.length === 0 ? (
          <div className="flex flex-1 flex-col items-center justify-center text-center text-text-muted">
            <Sparkles className="mb-2 h-8 w-8 text-status-info/50" />
            <p className="text-sm font-semibold text-text-primary">
              Ask anything about national projects
            </p>
            <p className="mt-1 text-xs text-text-secondary">
              Query budgets, delays, terrain risk, or ML predictions in natural language.
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <ChatMessage
              key={msg.id}
              role={msg.role}
              author={msg.author}
              timestamp={msg.timestamp}
              avatar={msg.role === 'user' ? EXECUTIVE_AVATAR : undefined}
            >
              <div className="whitespace-pre-wrap">{msg.text}</div>
              {msg.data && msg.data.length > 0 && (
                <ResultsTable data={msg.data} />
              )}
              {msg.sources && msg.sources.length > 0 && (
                <SourcesRow sources={msg.sources} />
              )}
            </ChatMessage>
          ))
        )}

        {isLoading && (
          <ChatMessage
            role="ai"
            author="INTELLIGENCE AGENT"
            timestamp={new Date().toTimeString().split(' ')[0]}
          >
            <div className="flex items-center gap-2 text-text-secondary">
              <Loader2 className="h-4 w-4 animate-spin text-status-info" />
              <span>Analyzing portfolio database and synthesizing response...</span>
            </div>
          </ChatMessage>
        )}
      </div>

      <ChatInput />
    </div>
  )
}