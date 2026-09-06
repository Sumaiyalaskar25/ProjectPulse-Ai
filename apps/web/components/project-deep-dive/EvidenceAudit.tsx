import { FileText } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'

interface Evidence {
  title: string
  snippet: string
  contributor: string
  dated: string
}

const EVIDENCE: Evidence[] = [
  {
    title: 'Environmental Clearance R...',
    snippet:
      '"Groundwater level variances in Sector IX suggest significant soil instability, potentially delaying pylon foundation by 4-6 months."',
    contributor: 'Dr. Sarah Chen',
    dated: 'Oct 12, 2023',
  },
  {
    title: 'Land Registry Audit',
    snippet:
      '"Outstanding litigation on 4.2 hectares of the Southern Corridor is now designated \'High Complexity\' following the latest court order."',
    contributor: 'A. Malhotra, Legal',
    dated: 'Sep 28, 2023',
  },
  {
    title: 'Quarterly Vendor Perf. Rep...',
    snippet:
      '"Vendor delivery timelines continue to underperform against SLA thresholds by an average of 18 days across the Northern Corridor segments—"',
    contributor: 'V. Iyer, Procurement',
    dated: 'Sep 15, 2023',
  },
]

export function EvidenceAudit() {
  return (
    <Card className="flex flex-col gap-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-text-primary">
            📈 Evidence Audit
          </h2>
          <p className="mt-1 text-sm text-text-secondary">
            Document snippets confirming AI risk assessments.
          </p>
        </div>
        <button
          type="button"
          className="text-sm font-semibold text-status-info transition-colors hover:text-sky-300"
        >
          View All
        </button>
      </div>

      <div className="flex flex-col gap-3">
        {EVIDENCE.map((item) => (
          <div
            key={item.title}
            className="rounded-lg border border-background-border bg-background-surface p-4"
          >
            <div className="flex items-center justify-between gap-3">
              <div className="flex min-w-0 items-center gap-2">
                <FileText className="h-4 w-4 shrink-0 text-status-info" />
                <p className="truncate text-sm font-semibold text-text-primary">
                  {item.title}
                </p>
              </div>
              <Badge variant="neutral" className="shrink-0">
                PDF
              </Badge>
            </div>
            <p className="mt-2 line-clamp-2 text-sm italic text-text-secondary">
              {item.snippet}
            </p>
            <div className="mt-3 flex items-center justify-between gap-2 border-t border-background-border pt-3">
              <span className="font-mono text-xs text-text-muted">
                CONTRIBUTOR: {item.contributor}
              </span>
              <span className="font-mono text-xs text-text-muted">
                DATED: {item.dated}
              </span>
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}