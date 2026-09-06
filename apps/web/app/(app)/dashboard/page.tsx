import { AppShell } from '@/components/layout/AppShell'
import { ComplianceFooter } from '@/components/dashboard/ComplianceFooter'
import { CommandCenterHero } from '@/components/dashboard/CommandCenterHero'
import { DashboardWorkspace } from '@/components/dashboard/DashboardWorkspace'
import { StatusBar } from '@/components/dashboard/StatusBar'

export default function DashboardPage() {
  return (
    <AppShell
      activeNav="Dashboard"
      breadcrumb={['Portfolio', 'National Infrastructure']}
    >
      <div className="flex flex-col gap-6">
        <CommandCenterHero />
        <StatusBar />
        <DashboardWorkspace />
        <ComplianceFooter />
      </div>
    </AppShell>
  )
}