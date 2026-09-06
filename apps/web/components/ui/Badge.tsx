import { cva, type VariantProps } from 'class-variance-authority'
import type { HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-bold uppercase',
  {
    variants: {
      variant: {
        critical: 'bg-status-critical/15 text-status-critical',
        high: 'bg-status-high/15 text-status-high',
        moderate: 'bg-status-moderate/15 text-status-moderate',
        stable: 'bg-status-stable/15 text-status-stable',
        neutral: 'bg-text-muted/15 text-text-muted',
      },
    },
    defaultVariants: {
      variant: 'neutral',
    },
  },
)

export interface BadgeProps
  extends HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />
}