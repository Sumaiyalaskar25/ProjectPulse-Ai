import { ArrowUpRight } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { PendingAction } from '@/components/ui/PendingAction'
import { cn } from '@/lib/utils'

interface DeterioratingProject {
  name: string
  id: string
  riskScore: number
  riskChange: number
  primaryDriver: string
  exposure: string
  confidence: number
}

const ROWS: DeterioratingProject[] = [
  {
    name: 'NH-44 Extension Section VII',
    id: 'ASSET-NH44-001',
    riskScore: 88,
    riskChange: 12.4,
    primaryDriver: 'Land Acquisition',
    exposure: '4.2K Cr',
    confidence: 92,
  },
  {
    name: 'Mumbai Metro Phase 3 - Line 1',
    id: 'METRO-MUM-P3',
    riskScore: 76,
    riskChange: 9.1,
    primaryDriver: 'Contractor Performance',
    exposure: '12.8K Cr',
    confidence: 89,
  },
  {
    name: 'Chennai Smart Grid Expansion',
    id: 'GRID-CHEN-04',
    riskScore: 68,
    riskChange: 7.3,
    primaryDriver: 'Utility Shifting',
    exposure: '1.5K Cr',
    confidence: 86,
  },
  {
    name: 'Ganges Basin Treatment Node',
    id: 'WATER-GAN-IX',
    riskScore: 72,
    riskChange: 8.5,
    primaryDriver: 'Env. Clearance',
    exposure: '0.85K Cr',
    confidence: 82,
  },
  {
    name: 'Kolkata Deep Water Port',
    id: 'PORT-KOL-EXT',
    riskScore: 62,
    riskChange: 6.8,
    primaryDriver: 'Funding Delays',
    exposure: '2.1K Cr',
    confidence: 90,
  },
]

function riskColor(score: number): string {
  if (score >= 80) return 'text-status-critical'
  if (score >= 70) return 'text-status-high'
  if (score >= 60) return 'text-status-moderate'
  return 'text-status-stable'
}

export function DeterioratingProjectsTable() {
  return (
    <Card className="flex flex-col p-0">
      <div className="flex flex-wrap items-start justify-between gap-4 px-6 pt-5 pb-4">
        <div>
          <h2 className="text-lg font-semibold text-text-primary">
            Projects With Rapid Deterioration
          </h2>
          <p className="mt-1 text-sm text-text-secondary">
            Showing projects with 5%+ risk increase this period
          </p>
        </div>
        <Badge variant="critical">Critical Monitoring Active</Badge>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[980px] text-left">
          <thead>
            <tr className="border-y border-background-border text-xs font-bold uppercase tracking-wider text-text-muted">
              <th scope="col" className="py-3 pl-6 pr-4">Project Identity</th>
              <th scope="col" className="px-4 py-3">Risk Score</th>
              <th scope="col" className="px-4 py-3">Risk Change</th>
              <th scope="col" className="px-4 py-3">Primary Driver</th>
              <th scope="col" className="px-4 py-3">Exposure</th>
              <th scope="col" className="px-4 py-3">Confidence</th>
              <th scope="col" className="py-3 pl-4 pr-6 text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {ROWS.map((project) => (
              <tr
                key={project.id}
                className="border-b border-background-border last:border-0"
              >
                <td className="py-4 pl-6 pr-4">
                  <p className="text-sm font-semibold text-text-primary">
                    {project.name}
                  </p>
                  <p className="mt-0.5 font-mono text-xs text-text-muted">
                    {project.id}
                  </p>
                </td>
                <td className="px-4 py-4">
                  <span
                    className={cn(
                      'font-mono text-sm font-bold',
                      riskColor(project.riskScore),
                    )}
                  >
                    {project.riskScore}%
                  </span>
                </td>
                <td className="px-4 py-4">
                  <span className="inline-flex items-center gap-0.5 font-mono text-sm font-bold text-status-critical">
                    <ArrowUpRight className="h-4 w-4" />
                    +{project.riskChange}%
                  </span>
                </td>
                <td className="px-4 py-4 text-sm text-text-primary">
                  {project.primaryDriver}
                </td>
                <td className="px-4 py-4 font-mono text-sm font-semibold text-text-primary">
                  {project.exposure}
                </td>
                <td className="px-4 py-4">
                  <div className="flex items-center gap-2.5">
                    <span className="font-mono text-xs font-semibold text-text-primary">
                      {project.confidence}%
                    </span>
                    <div className="h-1.5 w-20 overflow-hidden rounded-full bg-background-border">
                      <div
                        className="h-full rounded-full bg-status-stable"
                        style={{ width: `${project.confidence}%` }}
                      />
                    </div>
                  </div>
                </td>
                <td className="py-4 pl-4 pr-6 text-right">
                  <PendingAction>
                    <button
                      type="button"
                      className="text-sm font-medium text-status-info transition-colors hover:underline"
                    >
                      View
                    </button>
                  </PendingAction>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  )
}