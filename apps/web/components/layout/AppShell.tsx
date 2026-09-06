import type { ReactNode } from 'react'
import { Sidebar } from './Sidebar'
import { Topbar } from './Topbar'

export interface AppShellProps {
  activeNav?: string
  breadcrumb?: string[]
  breadcrumbRight?: ReactNode
  children: ReactNode
}

export function AppShell({
  activeNav,
  breadcrumb,
  breadcrumbRight,
  children,
}: AppShellProps) {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      <Sidebar active={activeNav} />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar breadcrumb={breadcrumb} breadcrumbRight={breadcrumbRight} />
        <main className="flex-1 overflow-y-auto bg-background p-6">{children}</main>
      </div>
    </div>
  )
}