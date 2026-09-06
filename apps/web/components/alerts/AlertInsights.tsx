import { ArrowRight, Maximize2, MessageSquare } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { PendingAction } from '@/components/ui/PendingAction'
import { cn } from '@/lib/utils'

const RECOMMENDATIONS = [
  {
    badge: '92% Match',
    badgeVariant: 'stable',
    title: 'Immediate Site Inspection & Thermal Map Sync',
    link: 'View Model Logic',
  },
  {
    badge: '74% Match',
    badgeVariant: 'moderate',
    title: 'Structural Sensor Calibration (Remote)',
    link: 'Details',
  },
] as const

const TIMELINE = [
  {
    time: '12m ago',
    actor: 'system',
    text: 'Critical alert generated based on real-time sensor node 442.',
  },
  {
    time: '10m ago',
    actor: 'e. vance',
    text: 'Alert acknowledged and moved to Triage Queue.',
  },
  {
    time: '8m ago',
    actor: 'system',
    text: 'AI generated 2 strategic intervention recommendations.',
  },
  {
    time: 'Just now',
    actor: 'system',
    text: 'Assigned officer S. Kulkarni updated sector health status.',
  },
]

export function AlertInsights() {
  return (
    <Card className="flex w-full shrink-0 flex-col gap-5 md:w-[360px]">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-text-primary">
          📄 Alert Insights
        </h2>
        <button
          type="button"
          aria-label="Expand insights"
          className="text-text-secondary transition-colors hover:text-text-primary"
        >
          <Maximize2 className="h-4 w-4" />
        </button>
      </div>

      <div className="rounded-lg border border-background-border bg-background-surface p-4">
        <div className="flex items-center justify-between gap-2">
          <span className="font-mono text-xs text-text-muted">ALT-8821</span>
          <Badge variant="critical">CRITICAL</Badge>
        </div>
        <p className="mt-2 text-sm font-semibold text-text-primary">
          NH-44 Expressway Extension (VII)
        </p>
        <p className="mt-1.5 text-sm leading-relaxed text-text-secondary">
          Anomalous vibration detected in Section VII structural pylons. Risk
          probability has increased significantly due to recent thermal
          fluctuations.
        </p>
      </div>

      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary">
          💡 AI Intervention Recommendations
        </h3>
        <div className="mt-3 flex flex-col gap-3">
          {RECOMMENDATIONS.map((rec) => (
            <div
              key={rec.title}
              className="rounded-lg border border-background-border bg-background-surface p-4"
            >
              <div className="flex justify-end">
                <Badge variant={rec.badgeVariant}>{rec.badge}</Badge>
              </div>
              <p className="mt-2 text-sm font-semibold text-text-primary">
                {rec.title}
              </p>
              <button
                type="button"
                className="mt-2 inline-flex items-center gap-1 text-xs font-semibold text-status-info transition-colors hover:text-sky-300"
              >
                {rec.link}
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary">
          🕐 Audit Timeline
        </h3>
        <ol className="mt-4">
          {TIMELINE.map((entry, i) => (
            <li
              key={`${entry.time}-${entry.actor}`}
              className="relative pl-5 pb-5 last:pb-0"
            >
              {i < TIMELINE.length - 1 && (
                <span className="absolute left-[5px] top-3.5 h-full w-px bg-background-border" />
              )}
              <span
                className={cn(
                  'absolute left-0 top-1.5 h-2.5 w-2.5 rounded-full border-2 border-status-info',
                  i === TIMELINE.length - 1 ? 'bg-status-info' : 'bg-background-surface',
                )}
              />
              <p className="text-sm font-semibold text-text-primary">
                {entry.time}
                <span className="ml-1.5 font-mono text-xs font-medium text-text-muted">
                  {entry.actor}
                </span>
              </p>
              <p className="mt-0.5 text-sm text-text-secondary">
                {entry.text}
              </p>
            </li>
          ))}
        </ol>
      </div>

      <div className="flex gap-2 border-t border-background-border pt-4">
        <PendingAction>
          <Button variant="secondary" className="flex-1">
            <MessageSquare className="h-4 w-4" />
            Discuss
          </Button>
        </PendingAction>
        <PendingAction>
          <Button variant="primary" className="flex-1">
            Execute
          </Button>
        </PendingAction>
      </div>
    </Card>
  )
}