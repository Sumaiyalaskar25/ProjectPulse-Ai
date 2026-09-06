import Image from 'next/image'
import Link from 'next/link'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { PendingAction } from '@/components/ui/PendingAction'
import type { Project } from '@/lib/projects'

const BANNER_IMAGE =
  'https://images.unsplash.com/photo-1541888946425-d81bb19240f5?auto=format&fit=crop&w=1920&q=66'

interface ProjectHeaderProps {
  project: Project
  riskPct: number
  baselineEnd: string
  progress: number
}

const RISK_BADGE_VARIANT: Record<
  Project['risk'],
  'critical' | 'high' | 'moderate' | 'stable'
> = {
  CRITICAL: 'critical',
  HIGH: 'high',
  MODERATE: 'moderate',
  STABLE: 'stable',
}

export function ProjectHeader({
  project,
  riskPct,
  baselineEnd,
  progress,
}: ProjectHeaderProps) {
  return (
    <div className="relative h-64 overflow-hidden rounded-xl">
      <Image
        src={BANNER_IMAGE}
        alt={`${project.name} construction site`}
        fill
        unoptimized
        priority
        className="object-cover"
      />
      <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-black/20" />

      <div className="absolute inset-0 flex flex-col justify-between p-6">
        <div className="flex justify-end">
          <div className="flex items-center gap-2">
            <PendingAction>
              <Button variant="secondary" size="sm">
                Export Dossier
              </Button>
            </PendingAction>
            <Button asChild variant="primary" size="sm">
              <Link href={`/projects/${project.id}/simulate`}>
                ▶ Run Intervention Simulation
              </Link>
            </Button>
          </div>
        </div>

        <div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant={RISK_BADGE_VARIANT[project.risk]}>
              {project.risk} RISK ({riskPct}%)
            </Badge>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-white/20 bg-black/40 px-3 py-0.5 text-xs font-medium text-white">
              📍 {project.region}
            </span>
          </div>
          <h1 className="mt-3 text-4xl font-extrabold uppercase tracking-tight text-white">
            {project.name}
          </h1>
          <div className="mt-3 flex flex-wrap gap-x-6 gap-y-1 text-sm font-medium text-white/85">
            <span>🕐 Baseline End: {baselineEnd}</span>
            <span>📈 Current Progress: {progress}%</span>
          </div>
        </div>
      </div>
    </div>
  )
}