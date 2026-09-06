import { Badge } from '@/components/ui/Badge'
import { PendingAction } from '@/components/ui/PendingAction'

const ROWS = [
  {
    project: 'NH-44 Expressway Ext.',
    budget: '4.2B Cr',
    overrun: '+34.2%',
    status: 'CRITICAL',
    variant: 'critical' as const,
  },
  {
    project: 'Mumbai Metro Line 3',
    budget: '12.8B Cr',
    overrun: '+18.5%',
    status: 'AT RISK',
    variant: 'high' as const,
  },
  {
    project: 'Chennai Smart Grid',
    budget: '1.5B Cr',
    overrun: '+22.1%',
    status: 'AT RISK',
    variant: 'high' as const,
  },
]

export function ResultsTable() {
  return (
    <div className="mt-3 overflow-hidden rounded-lg border border-background-border">
      <div className="flex items-center justify-between gap-3 bg-background-surface px-4 py-3">
        <p className="text-sm font-bold text-text-primary">
          ▦ Project Budget Variance Audit
        </p>
        <PendingAction>
          <button
            type="button"
            className="text-xs font-semibold text-status-info transition-colors hover:text-sky-300"
          >
            Export Data
          </button>
        </PendingAction>
      </div>
      <table className="w-full text-left">
        <thead>
          <tr className="border-y border-background-border bg-background-card text-xs font-bold uppercase tracking-wider text-text-muted">
            <th scope="col" className="py-2 pl-4 pr-3">Project</th>
            <th scope="col" className="px-3 py-2">Budget (Cr)</th>
            <th scope="col" className="px-3 py-2">Overrun</th>
            <th scope="col" className="py-2 pl-3 pr-4 text-right">Status</th>
          </tr>
        </thead>
        <tbody>
          {ROWS.map((row) => (
            <tr
              key={row.project}
              className="border-b border-background-border last:border-0"
            >
              <td className="py-2.5 pl-4 pr-3 text-sm font-semibold text-text-primary">
                {row.project}
              </td>
              <td className="px-3 py-2.5 font-mono text-sm text-text-secondary">
                {row.budget}
              </td>
              <td className="px-3 py-2.5 font-mono text-sm font-bold text-status-critical">
                {row.overrun}
              </td>
              <td className="py-2.5 pl-3 pr-4 text-right">
                <Badge variant={row.variant}>{row.status}</Badge>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}