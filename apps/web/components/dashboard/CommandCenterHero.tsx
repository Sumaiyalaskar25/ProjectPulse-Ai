import { Moon, Sun } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { cn } from '@/lib/utils'

function NetworkGraphic({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 520 260"
      fill="none"
      aria-hidden="true"
      preserveAspectRatio="xMidYMid slice"
      className={className}
    >
      <g stroke="currentColor" strokeWidth="1">
        <path d="M418 36 362 92 412 148 332 160 288 96 340 40 418 36" />
        <path d="M186 36 232 84 184 124 232 152 188 200" />
        <path d="M300 208 342 172 396 200 448 160" />
        <line x1="418" y1="36" x2="448" y2="160" />
        <line x1="232" y1="84" x2="288" y2="96" />
        <line x1="232" y1="152" x2="300" y2="208" />
        <line x1="188" y1="200" x2="96" y2="184" />
        <line x1="96" y1="184" x2="120" y2="120" />
        <line x1="120" y1="120" x2="56" y2="60" />
        <line x1="96" y1="184" x2="40" y2="216" />
      </g>
      <g fill="currentColor">
        <circle cx="418" cy="36" r="3" />
        <circle cx="362" cy="92" r="2.5" />
        <circle cx="412" cy="148" r="3" />
        <circle cx="332" cy="160" r="2.5" />
        <circle cx="288" cy="96" r="3" />
        <circle cx="340" cy="40" r="2.5" />
        <circle cx="186" cy="36" r="2.5" />
        <circle cx="232" cy="84" r="3" />
        <circle cx="184" cy="124" r="2.5" />
        <circle cx="232" cy="152" r="3" />
        <circle cx="188" cy="200" r="2.5" />
        <circle cx="300" cy="208" r="3" />
        <circle cx="342" cy="172" r="2.5" />
        <circle cx="396" cy="200" r="3" />
        <circle cx="448" cy="160" r="3" />
        <circle cx="96" cy="184" r="2.5" />
        <circle cx="120" cy="120" r="3" />
        <circle cx="56" cy="60" r="2.5" />
        <circle cx="40" cy="216" r="2.5" />
      </g>
    </svg>
  )
}

function ThemeToggle() {
  return (
    <div className="flex items-center gap-1 rounded-lg border border-background-border bg-background-surface p-1">
      <button
        type="button"
        aria-label="Use light theme"
        className="flex h-7 w-7 items-center justify-center rounded-md bg-background-card text-text-primary transition-colors"
      >
        <Sun className="h-4 w-4" />
      </button>
      <button
        type="button"
        aria-label="Use dark theme"
        className="flex h-7 w-7 items-center justify-center rounded-md text-text-muted transition-colors hover:text-text-primary"
      >
        <Moon className="h-4 w-4" />
      </button>
    </div>
  )
}

export function CommandCenterHero() {
  return (
    <section className="relative overflow-hidden rounded-xl border border-background-border bg-background-card">
      <NetworkGraphic className="pointer-events-none absolute right-0 top-0 h-full w-1/2 text-text-primary opacity-20" />

      <div className="relative flex flex-col gap-4 p-6 md:gap-5 md:p-8">
        <div className="flex items-start justify-between gap-4">
          <Badge variant="neutral">STRATEGIC OVERVIEW</Badge>
          <ThemeToggle />
        </div>

        <h1 className="text-3xl font-extrabold uppercase tracking-tight text-text-primary md:text-4xl">
          PAIMANA COMMAND CENTER
        </h1>

        <p className="max-w-xl text-sm leading-relaxed text-text-secondary md:text-base">
          Unified monitoring for National Asset Portfolio. High-precision risk
          modeling and real-time intervention tracking across 1,775 active
          infrastructure units.
        </p>

        <div className="flex flex-wrap items-center gap-3">
          <span className="inline-flex items-center gap-2 rounded-full border border-background-border bg-background-surface px-3 py-1.5 text-xs font-semibold text-text-secondary">
            <span className="h-2 w-2 rounded-full bg-status-stable" />
            NETWORK INTEGRITY: 99.4%
          </span>
          <span className="inline-flex items-center gap-2 rounded-full border border-background-border bg-background-surface px-3 py-1.5 text-xs font-semibold text-text-secondary">
            <span className={cn('text-status-high')}>⚡</span>
            ACTIVE INTERVENTIONS: 24
          </span>
        </div>
      </div>
    </section>
  )
}