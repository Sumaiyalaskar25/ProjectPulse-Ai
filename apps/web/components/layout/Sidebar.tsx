import {
  Activity,
  AlertTriangle,
  BarChart2,
  Database,
  LayoutGrid,
  Map,
  Settings,
  Sparkles,
  Wrench,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutGrid, href: '/dashboard' },
  { id: 'national-assets', label: 'National Assets', icon: Map, href: '/national-assets' },
  { id: 'assistant', label: 'AI Assistant', icon: Sparkles, href: '/assistant' },
  {
    id: 'risk-analytics',
    label: 'Risk Analytics',
    icon: BarChart2,
    href: '/risk-analytics',
  },
  {
    id: 'maintenance-log',
    label: 'Maintenance Log',
    icon: Wrench,
    href: '/maintenance-log',
  },
  { id: 'alerts', label: 'Alerts', icon: AlertTriangle, href: '/alerts' },
  { id: 'data-sources', label: 'Data Sources', icon: Database, href: '/sources' },
]

const navItemClasses =
  'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors'

interface SidebarProps {
  active?: string
}

export function Sidebar({ active }: SidebarProps) {
  return (
    <aside className="flex h-full w-[260px] shrink-0 flex-col border-r border-background-border bg-background-surface">
      <div className="flex items-center gap-3 px-6 py-5">
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-background-card">
          <Activity className="h-5 w-5 text-status-info" />
        </span>
        <span className="text-lg font-extrabold text-text-primary">
          ProjectPulse AI
        </span>
      </div>

      <nav className="flex flex-col gap-1 px-3">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon
          const isActive = item.id === active || item.label === active
          return (
            <a
              key={item.id}
              href={item.href}
              aria-current={isActive ? 'page' : undefined}
              className={cn(
                navItemClasses,
                isActive
                  ? 'bg-background-card text-text-primary'
                  : 'text-text-secondary hover:bg-background-card/50 hover:text-text-primary',
              )}
            >
              <Icon className="h-5 w-5" />
              {item.label}
            </a>
          )
        })}
      </nav>

      <div className="mt-auto border-t border-background-border px-3 py-3">
        <a
          href="/settings"
          className={cn(
            navItemClasses,
            'text-text-secondary hover:bg-background-card/50 hover:text-text-primary',
          )}
        >
          <Settings className="h-5 w-5" />
          System Settings
        </a>
      </div>
    </aside>
  )
}