import { Info } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'

export function AuditBanner() {
  return (
    <Card className="flex flex-wrap items-center gap-6">
      <div className="flex min-w-0 flex-1 items-start gap-4">
        <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg border border-background-border bg-background-surface">
          <Info className="h-5 w-5 text-status-info" />
        </span>
        <div className="min-w-0">
          <h2 className="text-base font-bold text-text-primary">
            PORTFOLIO INTEGRITY AUDIT IN-PROGRESS
          </h2>
          <p className="mt-2 text-sm leading-relaxed text-text-secondary">
            The current portfolio view includes 1,775 projects. AI risk models
            suggest a{' '}
            <button
              type="button"
              className="font-semibold text-status-info transition-colors hover:text-sky-300"
            >
              14.2% sensitivity gap
            </button>{' '}
            in the Northern Corridor following recent environmental data
            updates. Stakeholders are advised to re-run the{' '}
            <button
              type="button"
              className="font-semibold text-status-info transition-colors hover:text-sky-300"
            >
              What-If Counterfactual Simulator
            </button>{' '}
            for NH-44 segment projects.
          </p>
        </div>
      </div>
      <Button variant="secondary" className="shrink-0">
        Open Analysis Center
      </Button>
    </Card>
  )
}