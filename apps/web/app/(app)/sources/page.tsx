import { Plus, RefreshCw, Search } from 'lucide-react'
import { AppShell } from '@/components/layout/AppShell'
import { AuditFooter } from '@/components/data-sources/AuditFooter'
import { SourceCard } from '@/components/data-sources/SourceCard'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { StatCard } from '@/components/ui/StatCard'
import { SOURCES } from '@/lib/data-sources'
import { pageTitle } from '@/lib/design-tokens'
import { cn } from '@/lib/utils'

const STATUS_READOUTS = [
  { text: '⚡ Gateway Feed: Active', className: 'text-status-stable' },
  { text: '🛡 Audit Protocol: TLS 1.3', className: 'text-text-secondary' },
]

export default function SourcesPage() {
  return (
    <AppShell
      activeNav="Data Sources"
      breadcrumb={['Dashboard', 'Data Sources']}
    >
      <div className="flex flex-col gap-6">
        <header className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className={cn(pageTitle)}>DATA SOURCES</h1>
            <p className="mt-2 max-w-2xl text-sm leading-relaxed text-text-secondary">
              Trusted data powering PAIMANA&apos;s Infrastructure
              Intelligence. Unified gateway for government registries,
              institutional reports, and regional sensor telemetry.
            </p>
          </div>
          <div className="flex flex-col items-end gap-3">
            <p className="font-mono text-xs text-text-muted">
              ID: PAIMANA_SOURCE_V4
            </p>
            <div className="flex items-center gap-2">
              <Button variant="secondary">
                <RefreshCw className="h-4 w-4" />
                Refresh Data
              </Button>
              <Button variant="primary">
                <Plus className="h-4 w-4" />
                Connect New Feed
              </Button>
            </div>
          </div>
        </header>

        <div className="grid grid-cols-3 gap-4">
          <StatCard
            label="Active Data Sources"
            value="08"
            subLabel="7 Healthy · 1 Warning"
          />
          <StatCard
            label="Data Freshness"
            value="98.5%"
            subLabel="Last Synchronized: 27 Oct 2023 · 14:32 UTC"
          />
          <StatCard
            label="Data Records"
            value="1.24M"
            subLabel="Records Currently Available"
          />
        </div>

        <Card className="flex flex-wrap items-center justify-between gap-3 p-4">
          <div className="relative min-w-[280px] flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
            <input
              type="search"
              aria-label="Filter data sources"
              placeholder="Filter data sources, departments, or formats..."
              className="h-9 w-full rounded-lg border border-background-border bg-background-surface pl-9 pr-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-status-info/50"
            />
          </div>
          <div className="flex items-center gap-4">
            {STATUS_READOUTS.map((readout) => (
              <p
                key={readout.text}
                className={cn(
                  'text-xs font-medium',
                  readout.className,
                )}
              >
                {readout.text}
              </p>
            ))}
          </div>
        </Card>

        <section className="flex flex-col gap-4">
          <div>
            <h2 className="text-lg font-semibold text-text-primary">
              🗄 Connected Data Sources
            </h2>
            <p className="mt-1 text-sm text-text-secondary">
              Government and institutional sources currently feeding the
              platform.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {SOURCES.map((source) => (
              <SourceCard key={source.ref} source={source} />
            ))}
          </div>
        </section>

        <AuditFooter />
      </div>
    </AppShell>
  )
}