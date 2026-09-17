'use client'

import { useMemo, useState } from 'react'
import { AuditBanner } from './AuditBanner'
import { Filters } from './Filters'
import { ProjectTable } from './ProjectTable'
import { RiskLandscape } from './RiskLandscape'
import { RiskSummary, type AssetsView } from './RiskSummary'
import { PROJECTS, type Project } from '@/lib/projects'
import { useProjects } from '@/hooks/use-projects'

export function NationalAssetsWorkspace() {
  const [view, setView] = useState<AssetsView>('table')
  const [search, setSearch] = useState('')

  const { data: backendProjects, isLoading } = useProjects()

  const allProjects = useMemo((): Project[] => {
    if (backendProjects && Array.isArray(backendProjects) && backendProjects.length > 0) {
      return backendProjects.map((p, idx): Project => {
        const costCr = p.original_cost ? (p.original_cost / 10000000).toFixed(1) : '1,200'
        return {
          id: p.project_id,
          name: p.project_name || `Project ${p.project_id}`,
          ministry: p.ministry || p.sector || 'MoRTH',
          region: p.state || 'National',
          risk: idx % 4 === 0 ? 'CRITICAL' : idx % 3 === 0 ? 'HIGH' : idx % 2 === 0 ? 'MODERATE' : 'STABLE',
          change: idx % 2 === 0 ? `+${(idx * 2.3 + 1.2).toFixed(1)}%` : `-${(idx * 1.1 + 0.5).toFixed(1)}%`,
          exposure: `${costCr} Cr`,
          confidence: Math.min(99, Math.max(75, 94 - idx * 2)),
          status: idx % 3 === 0 ? 'Under Construction' : idx % 2 === 0 ? 'Operational' : 'Maintenance',
        }
      })
    }
    return PROJECTS
  }, [backendProjects])

  const filteredProjects = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return allProjects
    return allProjects.filter(
      (project) =>
        project.name.toLowerCase().includes(q) ||
        project.id.toLowerCase().includes(q) ||
        project.ministry.toLowerCase().includes(q) ||
        project.region.toLowerCase().includes(q),
    )
  }, [search, allProjects])

  return (
    <>
      <Filters search={search} onSearchChange={setSearch} />
      <RiskSummary view={view} onChange={setView} />
      {view === 'table' ? (
        <ProjectTable projects={filteredProjects} />
      ) : (
        <RiskLandscape projects={filteredProjects} />
      )}
      <AuditBanner />
    </>
  )
}