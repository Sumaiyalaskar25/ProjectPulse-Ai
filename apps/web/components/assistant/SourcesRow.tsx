import { FileText } from 'lucide-react'

const SOURCES = ['Q3 Financial Audit', 'Land Registry v.24', 'Sensor Node 442 Logs']

export function SourcesRow() {
  return (
    <div className="mt-3 flex flex-wrap items-center gap-2">
      <span className="text-xs font-bold uppercase tracking-wider text-text-muted">
        Sources:
      </span>
      {SOURCES.map((source) => (
        <button
          key={source}
          type="button"
          className="inline-flex items-center gap-1.5 rounded-full border border-background-border bg-background-surface px-3 py-1 text-xs font-medium text-text-secondary transition-colors hover:text-text-primary"
        >
          <FileText className="h-3.5 w-3.5 text-text-muted" />
          {source}
        </button>
      ))}
    </div>
  )
}