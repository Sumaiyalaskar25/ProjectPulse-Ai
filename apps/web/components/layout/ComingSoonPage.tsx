import Link from 'next/link'
import { Construction } from 'lucide-react'
import { AppShell } from './AppShell'
import { Button } from '@/components/ui/Button'
import { pageTitle } from '@/lib/design-tokens'
import { cn } from '@/lib/utils'

interface ComingSoonPageProps {
  title: string
  description: string
  activeNav: string
}

export function ComingSoonPage({
  title,
  description,
  activeNav,
}: ComingSoonPageProps) {
  return (
    <AppShell activeNav={activeNav}>
      <div className="flex h-full flex-col items-center justify-center gap-4">
        <span className="flex h-14 w-14 items-center justify-center rounded-xl border border-background-border bg-background-surface">
          <Construction className="h-6 w-6 text-text-muted" />
        </span>
        <h1 className={cn(pageTitle, 'text-center')}>{title}</h1>
        <p className="max-w-md text-center text-text-secondary">{description}</p>
        <Button asChild variant="secondary">
          <Link href="/dashboard">Back to Dashboard</Link>
        </Button>
      </div>
    </AppShell>
  )
}
