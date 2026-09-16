import { FileText } from 'lucide-react'

interface SourcesRowProps {
  sources?: string[]
}

const DEFAULT_SOURCES = ['Q3 Financial Audit', 'Land Registry v.24', 'Sensor Node 442 Logs']

export function SourcesRow({ sources = DEFAULT_SOURCES }: SourcesRowProps) {
  const items = sources && sources.length > 0 ? sources : DEFAULT_SOURCES

  return (
    <div className="mt-3 flex flex-wrap items-center gap-2">
      <span className="text-xs font-bold uppercase tracking-wider text-text-muted">
        Sources:
      </span>
      {items.map((source) => (
        <span
          key={source}
          className="inline-flex items-center gap-1.5 rounded-full border border-background-border bg-background-surface px-3 py-1 text-xs font-medium text-text-secondary"
        >
          <FileText className="h-3.5 w-3.5 text-text-muted" />
          {source}
        </span>
      ))}
    </div>
  )
}