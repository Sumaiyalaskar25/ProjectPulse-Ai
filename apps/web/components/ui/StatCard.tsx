import { ArrowDownRight, ArrowRight, ArrowUpRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Card } from './Card'

export interface StatCardProps {
  label: string
  value: string
  delta?: number
  deltaSuffix?: string
  deltaDirection?: 'good' | 'bad'
  subLabel?: string
  subLabelClassName?: string
  className?: string
}

export function StatCard({
  label,
  value,
  delta,
  deltaSuffix,
  deltaDirection = 'good',
  subLabel,
  subLabelClassName,
  className,
}: StatCardProps) {
  const rawDelta = delta ?? 0
  const isGood = deltaDirection === 'good' ? rawDelta >= 0 : rawDelta <= 0

  let DeltaIcon = ArrowRight
  if (rawDelta > 0) DeltaIcon = ArrowUpRight
  else if (rawDelta < 0) DeltaIcon = ArrowDownRight

  return (
    <Card className={cn('flex flex-col gap-2', className)}>
      <span className="text-xs font-bold uppercase tracking-wider text-text-muted">
        {label}
      </span>
      <span className="font-mono text-3xl font-bold text-text-primary">
        {value}
      </span>
      {delta !== undefined ? (
        <span
          className={cn(
            'inline-flex items-center gap-1 text-sm font-semibold',
            rawDelta === 0
              ? 'text-text-muted'
              : isGood
                ? 'text-status-stable'
                : 'text-status-critical',
          )}
        >
          <DeltaIcon size={16} />
          {rawDelta > 0 ? '+' : ''}
          {rawDelta}
          {deltaSuffix ? deltaSuffix : ''}
        </span>
      ) : subLabel ? (
        <span
          className={cn(
            'text-xs font-medium text-text-secondary',
            subLabelClassName,
          )}
        >
          {subLabel}
        </span>
      ) : null}
    </Card>
  )
}