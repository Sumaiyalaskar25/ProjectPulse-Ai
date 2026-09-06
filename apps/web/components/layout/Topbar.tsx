import { Fragment, type ReactNode } from 'react'
import Image from 'next/image'
import { Bell, ChevronDown, MessageSquare, Search } from 'lucide-react'
import { cn } from '@/lib/utils'

const DEFAULT_AVATAR = 'https://i.pravatar.cc/80?img=47'

export interface TopbarProps {
  breadcrumb?: string[]
  breadcrumbRight?: ReactNode
  userName?: string
  userRole?: string
  userAvatarUrl?: string
}

export function Topbar({
  breadcrumb = [],
  breadcrumbRight,
  userName = 'Elena Vance',
  userRole = 'Senior Director',
  userAvatarUrl = DEFAULT_AVATAR,
}: TopbarProps) {
  const lastIndex = breadcrumb.length - 1

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-background-border bg-background-surface px-6">
      <nav aria-label="Breadcrumb" className="flex flex-1 items-center gap-2">
        {breadcrumb.map((segment, i) => (
          <Fragment key={`${segment}-${i}`}>
            <span
              className={cn(
                'text-sm',
                i === lastIndex
                  ? 'font-semibold text-text-primary'
                  : 'text-text-secondary',
              )}
            >
              {segment}
            </span>
            {i < lastIndex && <span className="text-text-muted">/</span>}
          </Fragment>
        ))}
        {breadcrumbRight && (
          <span className="ml-auto font-mono text-xs text-text-muted">
            {breadcrumbRight}
          </span>
        )}
      </nav>

      <div className="flex items-center gap-4">
        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
          <input
            type="search"
            aria-label="Search"
            placeholder="Search resources, sites..."
            className="h-9 w-64 rounded-lg border border-background-border bg-background-card pl-9 pr-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-status-info/50"
          />
        </div>

        <button
          type="button"
          aria-label="Notifications"
          className="relative text-text-secondary transition-colors hover:text-text-primary"
        >
          <Bell className="h-5 w-5" />
          <span className="absolute right-0 top-0 h-2 w-2 rounded-full bg-status-critical" />
        </button>

        <button
          type="button"
          aria-label="Messages"
          className="text-text-secondary transition-colors hover:text-text-primary"
        >
          <MessageSquare className="h-5 w-5" />
        </button>

        <div className="flex items-center gap-3 border-l border-background-border pl-4">
          <Image
            src={userAvatarUrl}
            alt={userName}
            width={36}
            height={36}
            unoptimized
            className="h-9 w-9 rounded-full object-cover"
          />
          <div className="flex flex-col">
            <span className="text-sm font-semibold text-text-primary">
              {userName}
            </span>
            <span className="text-xs text-text-secondary">{userRole}</span>
          </div>
          <ChevronDown className="h-4 w-4 text-text-muted" />
        </div>
      </div>
    </header>
  )
}