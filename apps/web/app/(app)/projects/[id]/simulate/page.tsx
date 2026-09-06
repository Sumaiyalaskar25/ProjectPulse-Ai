import { AlertTriangle } from 'lucide-react'
import { AppShell } from '@/components/layout/AppShell'
import { AiRecommendation } from '@/components/simulator/AiRecommendation'
import { InterventionParameters } from '@/components/simulator/InterventionParameters'
import { SimulatedOutcome } from '@/components/simulator/SimulatedOutcome'
import { SimulatorControls } from '@/components/simulator/SimulatorControls'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { PendingAction } from '@/components/ui/PendingAction'
import { pageTitle } from '@/lib/design-tokens'
import { cn } from '@/lib/utils'

interface SimulatePageProps {
  params: { id: string }
}

export default function SimulatePage({ params }: SimulatePageProps) {
  return (
    <AppShell activeNav="National Assets">
      <div className="flex flex-col gap-6">
        <p className="font-mono text-xs text-text-muted">
          NATIONAL ASSETS &gt; NH-44 EXPRESSWAY &gt; RISK SIMULATOR
        </p>

        <header className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="neutral">STRATEGIC SIMULATION</Badge>
              <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-status-stable">
                <span className="h-2 w-2 rounded-full bg-status-stable" />
                MODEL LIVE
              </span>
            </div>
            <h1 className={cn(pageTitle, 'mt-3')}>
              WHAT-IF COUNTERFACTUAL RISK SIMULATOR
            </h1>
            <p className="mt-2 text-sm leading-relaxed text-text-secondary">
              Analyzing: National Northern Corridor Expansion (Segment VII)
            </p>
          </div>
          <SimulatorControls />
        </header>

        <div className="grid grid-cols-2 gap-6">
          <InterventionParameters />
          <SimulatedOutcome />
        </div>

        <AiRecommendation />

        <div className="flex flex-wrap items-center gap-4 rounded-xl border border-background-border bg-background-surface px-5 py-4">
          <div className="flex min-w-0 flex-1 items-start gap-3">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-status-high" />
            <div>
              <p className="text-sm font-bold tracking-wide text-text-primary">
                SIMULATION INTEGRITY CHECK
              </p>
              <p className="mt-0.5 text-sm text-text-secondary">
                Current model incorporates historical variances from Oct 2022
                - Sept 2023.
              </p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button variant="secondary">Compare with Alt Scenario</Button>
            <PendingAction>
              <Button className="bg-status-stable text-background hover:bg-status-stable/90">
                Commit Scenario to Strategic Plan
              </Button>
            </PendingAction>
          </div>
        </div>
      </div>
    </AppShell>
  )
}