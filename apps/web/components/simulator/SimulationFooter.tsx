'use client'

import { useState } from 'react'
import { AlertTriangle, Check, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { useToastStore } from '@/lib/toast-store'

interface SimulationFooterProps {
  projectName: string
}

export function SimulationFooter({ projectName }: SimulationFooterProps) {
  const showToast = useToastStore((state) => state.show)
  const [committed, setCommitted] = useState(false)
  const [isCommitting, setIsCommitting] = useState(false)

  const handleCommit = () => {
    setIsCommitting(true)
    setTimeout(() => {
      setIsCommitting(false)
      setCommitted(true)
      showToast(`Scenario parameters committed to strategic plan for ${projectName}.`)
    }, 600)
  }

  const handleCompare = () => {
    showToast('Comparing with baseline target trajectory.')
  }

  return (
    <div className="flex flex-wrap items-center gap-4 rounded-xl border border-background-border bg-background-surface px-5 py-4">
      <div className="flex min-w-0 flex-1 items-start gap-3">
        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-status-high" />
        <div>
          <p className="text-sm font-bold tracking-wide text-text-primary">
            SIMULATION INTEGRITY CHECK
          </p>
          <p className="mt-0.5 text-sm text-text-secondary">
            Current model incorporates historical variances from Oct 2022 - Sept 2023.
          </p>
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <Button variant="secondary" onClick={handleCompare}>
          Compare with Alt Scenario
        </Button>
        <Button
          className="bg-status-stable text-background hover:bg-status-stable/90"
          disabled={isCommitting || committed}
          onClick={handleCommit}
        >
          {isCommitting ? (
            <span className="inline-flex items-center gap-1.5">
              <Loader2 className="h-4 w-4 animate-spin" /> Committing...
            </span>
          ) : committed ? (
            <span className="inline-flex items-center gap-1.5">
              <Check className="h-4 w-4" /> Committed
            </span>
          ) : (
            'Commit Scenario to Strategic Plan'
          )}
        </Button>
      </div>
    </div>
  )
}
