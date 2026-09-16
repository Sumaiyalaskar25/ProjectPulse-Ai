'use client'

import { Badge } from '@/components/ui/Badge'
import { useToastStore } from '@/lib/toast-store'

interface ResultsTableProps {
  data?: Record<string, unknown>[]
}

export function ResultsTable({ data }: ResultsTableProps) {
  const showToast = useToastStore((state) => state.show)

  if (!data || data.length === 0) {
    return null
  }

  const columns = Object.keys(data[0])

  const handleExport = () => {
    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [
        columns.join(','),
        ...data.map((row) =>
          columns
            .map((col) => `"${String(row[col] ?? '').replace(/"/g, '""')}"`)
            .join(','),
        ),
      ].join('\n')

    const encodedUri = encodeURI(csvContent)
    const link = document.createElement('a')
    link.setAttribute('href', encodedUri)
    link.setAttribute('download', `query_result_${Date.now()}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    showToast('Data exported as CSV successfully.')
  }

  return (
    <div className="mt-3 overflow-hidden rounded-lg border border-background-border">
      <div className="flex items-center justify-between gap-3 bg-background-surface px-4 py-3">
        <p className="text-sm font-bold text-text-primary">
          ▦ Structured Query Result ({data.length} records)
        </p>
        <button
          type="button"
          onClick={handleExport}
          className="text-xs font-semibold text-status-info transition-colors hover:text-sky-300"
        >
          Export CSV
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-y border-background-border bg-background-card text-xs font-bold uppercase tracking-wider text-text-muted">
              {columns.map((col) => (
                <th key={col} scope="col" className="px-3 py-2">
                  {col.replace(/_/g, ' ')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr
                key={idx}
                className="border-b border-background-border last:border-0"
              >
                {columns.map((col) => {
                  const val = String(row[col] ?? '')
                  const isStatus =
                    col.toLowerCase().includes('status') ||
                    col.toLowerCase().includes('tier') ||
                    col.toLowerCase().includes('risk')
                  return (
                    <td
                      key={col}
                      className="px-3 py-2.5 font-mono text-sm text-text-secondary"
                    >
                      {isStatus && val.toUpperCase() === 'CRITICAL' ? (
                        <Badge variant="critical">{val}</Badge>
                      ) : isStatus && val.toUpperCase() === 'HIGH' ? (
                        <Badge variant="high">{val}</Badge>
                      ) : isStatus && val.toUpperCase() === 'MODERATE' ? (
                        <Badge variant="moderate">{val}</Badge>
                      ) : isStatus && val.toUpperCase() === 'STABLE' ? (
                        <Badge variant="stable">{val}</Badge>
                      ) : (
                        val
                      )}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}