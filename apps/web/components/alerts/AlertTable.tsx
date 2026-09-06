import Image from 'next/image'
import {
  ArrowDownRight,
  ArrowUpRight,
  UserPlus,
  type LucideIcon,
} from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { PendingAction } from '@/components/ui/PendingAction'
import type { RiskLevel } from '@/lib/projects'

export interface AlertRow {
  id: string
  assetId: string
  name: string
  sector: string
  severity: RiskLevel
  time: string
  delta: string
  up: boolean
  status: 'unassigned' | 'in-progress' | 'resolved'
  officer: Officer | null
}

interface Officer {
  name: string
  role: string
  avatar: string
}

export const ALERTS: AlertRow[] = [
  {
    id: 'ALT-8821',
    assetId: 'ASSET-NH44-01',
    name: 'NH-44 Expressway Extension',
    sector: 'Road Transport & Highways',
    severity: 'CRITICAL',
    time: '12m ago',
    delta: '+18%',
    up: true,
    status: 'in-progress',
    officer: {
      name: 'S. Kulkarni',
      role: 'Lead Engineer',
      avatar: 'https://i.pravatar.cc/80?img=68',
    },
  },
  {
    id: 'ALT-8819',
    assetId: 'METRO-MUM-P3',
    name: 'Mumbai Metro Phase 3 - Line',
    sector: 'Urban Development',
    severity: 'HIGH',
    time: '45m ago',
    delta: '+12.4%',
    up: true,
    status: 'unassigned',
    officer: null,
  },
  {
    id: 'ALT-8817',
    assetId: 'WATER-GAN-IX',
    name: 'Ganges Basin Treatment Plan',
    sector: 'Jal Shakti',
    severity: 'HIGH',
    time: '2h ago',
    delta: '+8.2%',
    up: true,
    status: 'in-progress',
    officer: {
      name: 'R. Mehta',
      role: 'Field Director',
      avatar: 'https://i.pravatar.cc/80?img=12',
    },
  },
  {
    id: 'ALT-8815',
    assetId: 'GRID-CHEN-04',
    name: 'Chennai Smart Grid Node Expa',
    sector: 'Power & Energy',
    severity: 'CRITICAL',
    time: '5m ago',
    delta: '+24.1%',
    up: true,
    status: 'unassigned',
    officer: null,
  },
  {
    id: 'ALT-8813',
    assetId: 'PORT-KOL-EXT',
    name: 'Kolkata Deep Water Port Expa',
    sector: 'Ports & Shipping',
    severity: 'MODERATE',
    time: '4h ago',
    delta: '-2.5%',
    up: false,
    status: 'resolved',
    officer: {
      name: 'M. Das',
      role: 'Operations Manager',
      avatar: 'https://i.pravatar.cc/80?img=32',
    },
  },
]

const SEVERITY_VARIANT: Record<
  RiskLevel,
  'critical' | 'high' | 'moderate' | 'stable'
> = {
  CRITICAL: 'critical',
  HIGH: 'high',
  MODERATE: 'moderate',
  STABLE: 'stable',
}

interface AlertTableProps {
  rows?: AlertRow[]
}

export function AlertTable({ rows = ALERTS }: AlertTableProps) {
  return (
    <Card className="p-0">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[860px] text-left">
          <thead>
            <tr className="border-b border-background-border text-xs font-bold uppercase tracking-wider text-text-muted">
              <th scope="col" className="py-4 pl-6 pr-4">Severity</th>
              <th scope="col" className="px-4 py-4">Project Identity</th>
              <th scope="col" className="px-4 py-4">Risk Delta</th>
              <th scope="col" className="px-4 py-4">Assigned Officer</th>
              <th scope="col" className="py-4 pl-4 pr-6 text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((alert) => {
              const DeltaIcon: LucideIcon = alert.up
                ? ArrowUpRight
                : ArrowDownRight
              return (
                <tr
                  key={alert.id}
                  className="border-b border-background-border last:border-0"
                >
                  <td className="py-4 pl-6 pr-4">
                    <Badge variant={SEVERITY_VARIANT[alert.severity]}>
                      {alert.severity}
                    </Badge>
                    <p className="mt-1.5 font-mono text-xs text-text-muted">
                      {alert.time}
                    </p>
                  </td>
                  <td className="px-4 py-4">
                    <p className="font-mono text-xs text-text-muted">
                      {alert.assetId}
                    </p>
                    <p className="mt-0.5 text-sm font-semibold text-text-primary">
                      {alert.name}
                    </p>
                    <p className="text-xs text-text-secondary">
                      {alert.sector}
                    </p>
                  </td>
                  <td className="px-4 py-4">
                    <span
                      className={`inline-flex items-center gap-0.5 font-mono text-sm font-bold ${
                        alert.up
                          ? 'text-status-critical'
                          : 'text-status-stable'
                      }`}
                    >
                      <DeltaIcon className="h-4 w-4" />
                      {alert.delta}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    {alert.officer ? (
                      <div className="flex items-center gap-2.5">
                        <Image
                          src={alert.officer.avatar}
                          alt={alert.officer.name}
                          width={28}
                          height={28}
                          unoptimized
                          className="h-7 w-7 rounded-full object-cover"
                        />
                        <div>
                          <p className="text-sm font-semibold text-text-primary">
                            {alert.officer.name}
                          </p>
                          <p className="text-xs text-text-secondary">
                            {alert.officer.role}
                          </p>
                        </div>
                      </div>
                    ) : (
                      <button
                        type="button"
                        className="inline-flex items-center gap-1.5 text-sm font-medium text-status-info transition-colors hover:text-sky-300"
                      >
                        <UserPlus className="h-4 w-4" />
                        Assign Officer
                      </button>
                    )}
                  </td>
                  <td className="py-4 pl-4 pr-6 text-right">
                    <PendingAction>
                      <Button variant="primary" size="sm">
                        Approve
                      </Button>
                    </PendingAction>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </Card>
  )
}