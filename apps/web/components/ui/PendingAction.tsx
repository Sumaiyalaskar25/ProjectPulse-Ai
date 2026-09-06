'use client'

import type { ReactNode } from 'react'
import { backendPendingMessage, useToastStore } from '@/lib/toast-store'

interface PendingActionProps {
  children: ReactNode
}

export function PendingAction({ children }: PendingActionProps) {
  const show = useToastStore((state) => state.show)
  return (
    <span
      className="contents"
      onClick={() => show(backendPendingMessage)}
      role="button"
      tabIndex={-1}
    >
      {children}
    </span>
  )
}