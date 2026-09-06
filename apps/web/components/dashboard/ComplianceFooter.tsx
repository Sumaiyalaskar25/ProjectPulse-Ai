import { AlertTriangle, Shield, ShieldCheck } from 'lucide-react'
import { Card } from '@/components/ui/Card'

const METRICS = [
  {
    label: 'Policy Compliance',
    value: '98.2%',
    icon: ShieldCheck,
    iconClass: 'text-status-stable',
  },
  {
    label: 'Unmapped Anomalies',
    value: '14',
    icon: Shield,
    iconClass: 'text-status-high',
  },
  {
    label: 'Regulatory Warnings',
    value: '03',
    icon: AlertTriangle,
    iconClass: 'text-status-critical',
  },
]

export function ComplianceFooter() {
  return (
    <Card className="grid grid-cols-3 divide-x divide-background-border p-0">
      {METRICS.map((metric) => {
        const Icon = metric.icon
        return (
          <div key={metric.label} className="flex items-center gap-4 py-5 pl-6 pr-6">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg border border-background-border bg-background-surface">
              <Icon className={`h-5 w-5 ${metric.iconClass}`} />
            </span>
            <div className="flex flex-col">
              <span className="text-xs font-bold uppercase tracking-wider text-text-muted">
                {metric.label}
              </span>
              <span className="font-mono text-2xl font-bold text-text-primary">
                {metric.value}
              </span>
            </div>
          </div>
        )
      })}
    </Card>
  )
}