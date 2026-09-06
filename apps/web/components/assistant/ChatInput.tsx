'use client'

import { useState } from 'react'
import {
  Database,
  History,
  Mic,
  Paperclip,
  Search,
  Send,
} from 'lucide-react'
import { Button } from '@/components/ui/Button'

export function ChatInput() {
  const [value, setValue] = useState('')

  return (
    <div className="shrink-0 border-t border-background-border p-4">
      <div className="mb-2 flex items-center gap-2">
        <span className="rounded-md border border-status-info/30 bg-status-info/10 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-status-info">
          Internal Data Context
        </span>
        <span className="text-xs text-text-secondary">
          National Portfolio Active
        </span>
      </div>
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
          <input
            type="text"
            value={value}
            onChange={(event) => setValue(event.target.value)}
            placeholder="Query system for national asset anomalies, risk..."
            className="h-11 w-full rounded-xl border border-background-border bg-background-surface pl-9 pr-11 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-status-info/50"
          />
          <button
            type="button"
            aria-label="Voice input"
            className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted transition-colors hover:text-text-primary"
          >
            <Mic className="h-4 w-4" />
          </button>
        </div>
        <Button type="submit" variant="primary" className="h-11 px-4">
          <Send className="h-4 w-4" />
          Transmit
        </Button>
      </div>
      <div className="mt-2.5 flex flex-wrap items-center gap-4">
        <button
          type="button"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-text-secondary transition-colors hover:text-text-primary"
        >
          <History className="h-3.5 w-3.5" />
          Recall Context
        </button>
        <button
          type="button"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-text-secondary transition-colors hover:text-text-primary"
        >
          <Database className="h-3.5 w-3.5" />
          Query Data Warehouse
        </button>
        <button
          type="button"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-text-secondary transition-colors hover:text-text-primary"
        >
          <Paperclip className="h-3.5 w-3.5" />
          Attach Document
        </button>
      </div>
    </div>
  )
}