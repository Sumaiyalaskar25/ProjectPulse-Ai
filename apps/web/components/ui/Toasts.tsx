'use client'

import { Card } from '@/components/ui/Card'
import { useToastStore } from '@/lib/toast-store'

export function Toasts() {
  const toasts = useToastStore((state) => state.toasts)

  if (toasts.length === 0) return null

  return (
    <div className="pointer-events-none fixed bottom-4 left-1/2 z-50 flex w-full max-w-md -translate-x-1/2 flex-col items-center gap-2">
      {toasts.map((toast) => (
        <Card
          key={toast.id}
          className="w-full border-background-border bg-background-card p-3 text-center text-sm text-text-primary shadow-lg"
        >
          {toast.text}
        </Card>
      ))}
    </div>
  )
}