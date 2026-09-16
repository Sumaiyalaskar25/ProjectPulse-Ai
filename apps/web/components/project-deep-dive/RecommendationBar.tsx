'use client'

import { useState } from 'react'
import { AlertCircle, ShieldCheck } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { useToastStore } from '@/lib/toast-store'

export function RecommendationBar() {
  const showToast = useToastStore((state) => state.show)
  const [status, setStatus] = useState<string | null>(null)

  const handleEscalate = () => {
    setStatus('escalated')
    showToast('Escalation notice dispatched to Ministry Oversight Committee.')
  }

  const handleScheduleMeeting = () => {
    showToast('Deep Dive inspection meeting scheduled for next sprint.')
  }

  const handleIgnore = () => {
    setStatus('ignored')
    showToast('Assessment recommendation dismissed from active queue.')
  }

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
          onClick={handleIgnore}
        >
          Ignore Assessment
        </Button>
        <Button variant="secondary" onClick={handleScheduleMeeting}>
          Schedule Deep Dive Meeting
        </Button>
        <Button
          variant="danger"
          disabled={status === 'escalated'}
          onClick={handleEscalate}
        >
          {status === 'escalated' ? (
            <span className="inline-flex items-center gap-1.5">
              <AlertCircle className="h-4 w-4" /> Escalated to Ministry
            </span>
          ) : (
            'Escalate to Ministry Level'
          )}
        </Button>
      </div>
    </div>
  )
}