'use client'

import { useMemo, useState } from 'react'
import { AuditBanner } from './AuditBanner'
import { Filters } from './Filters'
import { ProjectTable } from './ProjectTable'
import { RiskLandscape } from './RiskLandscape'
import { RiskSummary, type AssetsView } from './RiskSummary'
import { PROJECTS } from '@/lib/projects'

export function NationalAssetsWorkspace() {
  const [view, setView] = useState<AssetsView>('table')
  const [search, setSearch] = useState('')

  const filteredProjects = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return PROJECTS
    return PROJECTS.filter(
      (project) =>
        project.name.toLowerCase().includes(q) ||
        project.id.toLowerCase().includes(q),
    )
  }, [search])

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