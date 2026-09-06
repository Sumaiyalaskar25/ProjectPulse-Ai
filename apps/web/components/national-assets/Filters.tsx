import { ChevronDown, Filter, Search } from 'lucide-react'
import { Card } from '@/components/ui/Card'

const DROPDOWNS = ['All Ministries', 'All Sectors', 'All India', 'All Tiers']

interface FiltersProps {
  search: string
  onSearchChange: (value: string) => void
}

export function Filters({ search, onSearchChange }: FiltersProps) {
  return (
    <Card className="flex flex-col gap-4">
      <div className="relative">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
        <input
          type="search"
          aria-label="Search projects"
          placeholder="Search project ID, name, or keywords..."
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          className="h-10 w-full rounded-lg border border-background-border bg-background-surface pl-9 pr-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-status-info/50"
        />
      </div>
      <div className="flex flex-wrap items-center gap-2">
        {DROPDOWNS.map((label) => (
          <button
            key={label}
            type="button"
            className="inline-flex items-center gap-2 rounded-full border border-background-border bg-background-surface px-4 py-2 text-sm text-text-secondary transition-colors hover:text-text-primary"
          >
            {label}
            <ChevronDown className="h-4 w-4 text-text-muted" />
          </button>
        ))}
      </div>
      <div className="flex items-center gap-4">
        <button
          type="button"
          className="inline-flex items-center gap-2 text-sm font-medium text-text-secondary transition-colors hover:text-text-primary"
        >
          <Filter className="h-4 w-4" />
          Advanced
        </button>
        <button
          type="button"
          className="text-sm font-medium text-text-secondary transition-colors hover:text-text-primary"
        >
          Reset
        </button>
      </div>
    </Card>
  )
}