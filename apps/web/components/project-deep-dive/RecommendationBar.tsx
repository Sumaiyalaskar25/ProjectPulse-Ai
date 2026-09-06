import { ShieldCheck } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { PendingAction } from '@/components/ui/PendingAction'

export function RecommendationBar() {
  return (
    <div className="flex flex-wrap items-center gap-4 rounded-xl border border-background-border bg-background-surface px-5 py-4">
      <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg border border-background-border bg-background-card">
        <ShieldCheck className="h-5 w-5 text-status-info" />
      </span>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-bold tracking-wide text-text-primary">
          STRATEGIC RECOMMENDATION
        </p>
        <p className="mt-0.5 text-sm text-text-secondary">
          Initiate &apos;Accelerated Resource Deployment&apos; to recover 12% of
          schedule delta.
        </p>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <Button
          variant="secondary"
          className="border-transparent hover:border-transparent"
        >
          Ignore Assessment
        </Button>
        <Button variant="secondary">Schedule Deep Dive Meeting</Button>
        <PendingAction>
          <Button variant="danger">Escalate to Ministry Level</Button>
        </PendingAction>
      </div>
    </div>
  )
}