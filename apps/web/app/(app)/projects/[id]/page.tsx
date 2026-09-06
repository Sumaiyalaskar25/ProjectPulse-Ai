import { AppShell } from '@/components/layout/AppShell'
import { EvidenceAudit } from '@/components/project-deep-dive/EvidenceAudit'
import { ProjectHeader } from '@/components/project-deep-dive/ProjectHeader'
import { RecommendationBar } from '@/components/project-deep-dive/RecommendationBar'
import { RiskDrivers } from '@/components/project-deep-dive/RiskDrivers'
import { RiskMetrics } from '@/components/project-deep-dive/RiskMetrics'
import { RiskTrajectory } from '@/components/project-deep-dive/RiskTrajectory'
import {
  FALLBACK_PROJECT_ID,
  getProjectById,
  PROJECT_META,
  RISK_PERCENT,
} from '@/lib/projects'

interface ProjectDeepDivePageProps {
  params: { id: string }
}

export default function ProjectDeepDivePage({
  params,
}: ProjectDeepDivePageProps) {
  const project =
    getProjectById(params.id) ?? getProjectById(FALLBACK_PROJECT_ID)!
  const riskPct = RISK_PERCENT[project.risk]
  const meta = PROJECT_META[project.id]

  return (
    <AppShell
      activeNav="National Assets"
      breadcrumb={['Dashboard', 'Project Deep Dive']}
      breadcrumbRight="INTERNAL REF: ASSET-NH44-EXT-001"
    >
      <div className="flex flex-col gap-6">
        <ProjectHeader
          project={project}
          riskPct={riskPct}
          baselineEnd={meta.baselineEnd}
          progress={meta.progress}
        />
        <RiskMetrics />
        <div className="grid grid-cols-2 gap-6">
          <RiskDrivers />
          <EvidenceAudit />
        </div>
        <RiskTrajectory />
        <RecommendationBar />
      </div>
    </AppShell>
  )
}