'use client'

import { useState } from 'react'
import { DashboardData } from './DashboardData'
import { FilterBar, type QuickView } from './FilterBar'
import { InterventionQueue } from './InterventionQueue'
import { RiskMatrix } from './RiskMatrix'

export function DashboardWorkspace() {
  const [quickView, setQuickView] = useState<QuickView>('portfolio')

  return (
    <>
      <FilterBar value={quickView} onChange={setQuickView} />
      <DashboardData />
      <div className="grid grid-cols-3 gap-6">
        <RiskMatrix />
        <InterventionQueue quickView={quickView} />
      </div>
    </>
  )
}