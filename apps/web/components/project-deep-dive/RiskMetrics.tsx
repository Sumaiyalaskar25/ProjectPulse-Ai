import { StatCard } from '@/components/ui/StatCard'

export function RiskMetrics() {
  return (
    <div className="grid grid-cols-3 gap-4">
      <StatCard
        label="Predicted Cost Overrun"
        value="+34.2%"
        subLabel="+$4.2B Estimated"
        subLabelClassName="text-status-critical"
      />
      <StatCard
        label="Predicted Schedule Delay"
        value="+18 Months"
        subLabel="Revised: June 2026"
      />
      <StatCard
        label="AI Confidence Score"
        value="92%"
        subLabel="Based on 4.2M datapoints"
        subLabelClassName="text-status-stable"
      />
    </div>
  )
}