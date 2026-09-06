import { ArrowUpRight } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { cn } from '@/lib/utils'

const PILLS = [
  {
    text: '🛡 Security Integrity: EN_INFRA_V4.2.1 PASS',
    className:
      'border-status-stable/30 bg-status-stable/10 text-status-stable',
  },
  {
    text: '⚠ Validation Drift: 0.02% Variance (OK)',
    className: 'border-status-high/30 bg-status-high/10 text-status-high',
  },
]

export function AuditFooter() {
  return (
    <Card className="flex flex-col justify-between gap-6 p-6">
      <div className="flex justify-end">
        <div className="max-w-2xl text-right">
          <p className="font-mono text-xs text-text-muted">
            Last Global Audit: 27 Oct 2023 · 14:32:01 UTC
          </p>
          <p className="mt-2 text-xs italic leading-relaxed text-text-secondary">
            Authorized Personnel Only. All data ingestions are logged for
            institutional audit trails. PAIMANA Intelligence models are
            retrained every 24 hours based on these validated feeds.
          </p>
          <a
            href="#"
            className="mt-3 inline-flex items-center gap-1 text-sm font-medium text-status-info transition-colors hover:underline"
          >
            View Detailed Lineage Audit
            <ArrowUpRight className="h-4 w-4" />
          </a>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {PILLS.map((pill) => (
          <span
            key={pill.text}
            className={cn(
              'inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium',
              pill.className,
            )}
          >
            {pill.text}
          </span>
        ))}
      </div>
    </Card>
  )
}