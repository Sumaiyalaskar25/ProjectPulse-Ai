import { AppShell } from '@/components/layout/AppShell'
import { AiRecommendation } from '@/components/simulator/AiRecommendation'
import { InterventionParameters } from '@/components/simulator/InterventionParameters'
import { SimulatedOutcome } from '@/components/simulator/SimulatedOutcome'
import { SimulatorControls } from '@/components/simulator/SimulatorControls'
import { SimulationFooter } from '@/components/simulator/SimulationFooter'
import { Badge } from '@/components/ui/Badge'
import { pageTitle } from '@/lib/design-tokens'
import { cn } from '@/lib/utils'
import { notFound } from 'next/navigation'
import { getProjectById } from '@/lib/projects'

interface SimulatePageProps {
  params: { id: string }
}

const isLiveBackend = process.env.NEXT_PUBLIC_USE_MOCK_DATA === 'false'

export default function SimulatePage({ params }: SimulatePageProps) {
  const project = getProjectById(params.id)
  if (!project) {
    notFound()
  }

  return (
    <AppShell activeNav="National Assets" breadcrumb={['Dashboard', 'National Assets', project.name, 'Risk Simulator']}>
      <div className="flex flex-col gap-6">
        <p className="font-mono text-xs text-text-muted">
          NATIONAL ASSETS &gt; {project.name.toUpperCase()} &gt; RISK SIMULATOR
        </p>

        <header className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="neutral">STRATEGIC SIMULATION</Badge>
              <span className={cn(
                "inline-flex items-center gap-1.5 text-xs font-semibold",
                isLiveBackend ? "text-status-stable" : "text-status-moderate"
              )}>
                <span className={cn(
                  "h-2 w-2 rounded-full",
                  isLiveBackend ? "bg-status-stable" : "bg-status-moderate"
                )} />
                {isLiveBackend ? 'BACKEND ML MODEL' : 'LOCAL DEMO ENGINE'}
              </span>
            </div>
            <h1 className={cn(pageTitle, 'mt-3')}>
              WHAT-IF COUNTERFACTUAL RISK SIMULATOR
            </h1>
            <p className="mt-2 text-sm leading-relaxed text-text-secondary">
              Analyzing: {project.name} ({project.ministry} · {project.region})
            </p>
          </div>
          <SimulatorControls />
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <InterventionParameters />
          <SimulatedOutcome />
        </div>

        <AiRecommendation />

        <SimulationFooter projectName={project.name} />
      </div>
    </AppShell>
  )
}