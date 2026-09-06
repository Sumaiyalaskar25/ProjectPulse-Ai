import { ArrowRight, Lightbulb } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { PendingAction } from '@/components/ui/PendingAction'

export function AiRecommendation() {
  return (
    <Card className="flex items-start justify-between gap-6">
      <div className="flex min-w-0 flex-1 items-start gap-4">
        <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg border border-background-border bg-background-surface">
          <Lightbulb className="h-5 w-5 text-status-info" />
        </span>
        <div className="min-w-0">
          <h2 className="text-lg font-semibold text-text-primary">
            AI Strategic Recommendation
          </h2>
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-text-secondary">
            The current simulation suggests that prioritizing{' '}
            <strong className="font-semibold text-text-primary">
              Contractor Mobilization
            </strong>{' '}
            over{' '}
            <strong className="font-semibold text-text-primary">
              Budget Injection
            </strong>{' '}
            yields a 12% higher efficiency return in the Northern Corridor. AI
            suggests accelerating Section VII environmental clearances to
            bypass the forecasted monsoon stagnation period.
          </p>
          <div className="mt-4 flex flex-wrap gap-5">
            <button
              type="button"
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-status-info transition-colors hover:text-sky-300"
            >
              View Detailed Policy Log
              <ArrowRight className="h-4 w-4" />
            </button>
            <PendingAction>
              <button
                type="button"
                className="inline-flex items-center gap-1.5 text-sm font-semibold text-status-info transition-colors hover:text-sky-300"
              >
                Export as Executive Brief
                <ArrowRight className="h-4 w-4" />
              </button>
            </PendingAction>
          </div>
        </div>
      </div>
      <div className="shrink-0 text-right">
        <p className="text-xs font-bold uppercase tracking-wider text-text-muted">
          Estimated Net Savings
        </p>
        <p className="mt-1 font-mono text-4xl font-bold text-status-stable">
          $2.42B USD
        </p>
      </div>
    </Card>
  )
}