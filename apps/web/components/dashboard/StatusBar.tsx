import { Badge } from '@/components/ui/Badge'

export function StatusBar() {
  return (
    <div className="flex flex-wrap items-center justify-between gap-2 font-mono text-xs text-text-muted">
      <span>
        ⏱ system status:{' '}
        <span className="font-semibold text-status-stable">
          LIVE FEED ACTIVE
        </span>
      </span>
      <div className="flex flex-wrap items-center gap-3">
        <span className="text-text-secondary">data freshness:</span>
        <Badge variant="stable">99.8% Sync</Badge>
        <span>last sync: 2023-10-27 14:32:01 UTC</span>
      </div>
    </div>
  )
}