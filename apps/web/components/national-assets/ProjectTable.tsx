import Link from 'next/link'
import {
  ArrowDownRight,
  ArrowUpRight,
  Database,
  type LucideIcon,
} from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { PROJECTS, type Project, type ProjectStatus } from '@/lib/projects'
import { cn } from '@/lib/utils'

const RISK_VARIANT: Record<
  Project['risk'],
  'critical' | 'high' | 'moderate' | 'stable'
> = {
  CRITICAL: 'critical',
  HIGH: 'high',
  MODERATE: 'moderate',
  STABLE: 'stable',
}

const STATUS_STYLE: Record<ProjectStatus, string> = {
  'Under Construction': 'border-status-info/30 bg-status-info/10 text-status-info',
  Operational: 'border-status-stable/30 bg-status-stable/10 text-status-stable',
  Maintenance: 'border-status-high/30 bg-status-high/10 text-status-high',
}

function changeDirection(change: string): 1 | -1 | 0 {
  if (change.startsWith('+')) return 1
  if (change.startsWith('-')) return -1
  return 0
}

function confidenceColor(confidence: number): string {
  if (confidence >= 90) return '#22C55E'
  if (confidence >= 85) return '#F59E0B'
  return '#EF4444'
}

interface ProjectTableProps {
  projects?: Project[]
}

export function ProjectTable({ projects = PROJECTS }: ProjectTableProps) {
  return (
    <Card className="overflow-hidden">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-background-border pb-4">
        <div>
          <h2 className="text-lg font-semibold text-text-primary">
            PROJECT PORTFOLIO
          </h2>
          <p className="mt-1 text-sm text-text-secondary">
            Listing {projects.length} priority infrastructure assets
          </p>
        </div>
        <span className="inline-flex items-center gap-2 font-mono text-xs text-text-muted">
          <Database className="h-4 w-4" />
          LIVE_UPDATE: 14:32:01
        </span>
      </header>
      <div className="mt-4 overflow-x-auto">
        <table className="w-full min-w-[1080px] text-left">
          <thead>
            <tr className="border-b border-background-border text-xs font-bold uppercase tracking-wider text-text-muted">
              <th className="pb-3 pr-4">Project Identity</th>
              <th className="pb-3 pr-4">Ministry/Sector</th>
              <th className="pb-3 pr-4">Region</th>
              <th className="pb-3 pr-4">Risk Status</th>
              <th className="pb-3 pr-4">Exposure</th>
              <th className="pb-3 pr-4">Confidence</th>
              <th className="pb-3 pr-4">Status</th>
              <th className="pb-3">Action</th>
            </tr>
          </thead>
          <tbody>
            {projects.map((project) => {
              const dir = changeDirection(project.change)
              const ChangeIcon: LucideIcon | null =
                dir > 0 ? ArrowUpRight : dir < 0 ? ArrowDownRight : null
              return (
                <tr
                  key={project.id}
                  className="border-b border-background-border last:border-0"
                >
                  <td className="py-4 pr-4">
                    <p className="text-sm font-semibold text-text-primary">
                      {project.name}
                    </p>
                    <p className="mt-0.5 font-mono text-xs text-text-muted">
                      {project.id}
                    </p>
                  </td>
                  <td className="py-4 pr-4 text-sm text-text-secondary">
                    {project.ministry}
                  </td>
                  <td className="py-4 pr-4 text-sm text-text-secondary">
                    {project.region}
                  </td>
                  <td className="py-4 pr-4">
                    <div className="flex flex-col items-start gap-1">
                      <Badge variant={RISK_VARIANT[project.risk]}>
                        {project.risk}
                      </Badge>
                      <span
                        className={cn(
                          'inline-flex items-center gap-0.5 font-mono text-xs font-bold',
                          dir > 0
                            ? 'text-status-critical'
                            : dir < 0
                              ? 'text-status-stable'
                              : 'text-text-muted',
                        )}
                      >
                        {ChangeIcon && <ChangeIcon className="h-3 w-3" />}
                        {project.change}
                      </span>
                    </div>
                  </td>
                  <td className="py-4 pr-4 font-mono text-sm font-semibold text-text-primary">
                    {project.exposure}
                  </td>
                  <td className="py-4 pr-4">
                    <div className="flex items-center gap-2">
                      <div className="h-1 w-16 overflow-hidden rounded-full bg-background-border">
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${project.confidence}%`,
                            backgroundColor: confidenceColor(project.confidence),
                          }}
                        />
                      </div>
                      <span className="font-mono text-xs font-semibold text-text-primary">
                        {project.confidence}%
                      </span>
                    </div>
                  </td>
                  <td className="py-4 pr-4">
                    <span
                      className={cn(
                        'inline-flex rounded-full border px-2.5 py-1 text-xs font-medium',
                        STATUS_STYLE[project.status],
                      )}
                    >
                      {project.status}
                    </span>
                  </td>
                  <td className="py-4">
                    <Link
                      href={`/projects/${project.id}`}
                      className="inline-flex items-center gap-1 text-sm font-semibold text-status-info transition-colors hover:text-sky-300"
                    >
                      Deep Dive
                      <ArrowUpRight className="h-3.5 w-3.5" />
                    </Link>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </Card>
  )
}