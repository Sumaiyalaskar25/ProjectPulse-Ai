export type MaintenancePriority = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'

export type MaintenanceStatus =
  | 'OVERDUE'
  | 'IN PROGRESS'
  | 'SCHEDULED'
  | 'COMPLETED'

export type MaintenanceTabKey =
  | 'all'
  | 'overdue'
  | 'in-progress'
  | 'scheduled'
  | 'completed'

export interface MaintenanceRecord {
  logId: string
  assetId: string
  name: string
  segment: string
  taskType: string
  lastCheck: string
  due: string
  priority: MaintenancePriority
  team: string
  status: MaintenanceStatus
  tabKey: MaintenanceTabKey
}

export const MAINTENANCE_RECORDS: MaintenanceRecord[] = [
  {
    logId: 'MRT-4',
    assetId: '481-X',
    name: 'NH-44 Expressway',
    segment: 'Segment VII - Bridge',
    taskType: 'Structural Integrity Audit',
    lastCheck: '2023-08-14',
    due: '2023-10-20',
    priority: 'CRITICAL',
    team: 'Alpha-7 North',
    status: 'OVERDUE',
    tabKey: 'overdue',
  },
  {
    logId: 'MRT-8',
    assetId: 'ET-38-2',
    name: 'Mumbai Metro Phase 3',
    segment: 'Line 1 - Rolling Stock',
    taskType: 'Brake System Service',
    lastCheck: '2023-09-28',
    due: '2023-11-05',
    priority: 'HIGH',
    team: 'Metro Mech-V',
    status: 'IN PROGRESS',
    tabKey: 'in-progress',
  },
  {
    logId: 'MRT-6',
    assetId: 'RD-88-2',
    name: 'Chennai Smart Grid',
    segment: 'Substation B-12',
    taskType: 'Relay Calibration',
    lastCheck: '2023-10-01',
    due: '2023-10-31',
    priority: 'MEDIUM',
    team: 'Power Grid-S',
    status: 'SCHEDULED',
    tabKey: 'scheduled',
  },
  {
    logId: 'MRT-K',
    assetId: 'GL-55-1',
    name: 'Kolkata Port Expansion',
    segment: 'Cranes 04/05/06',
    taskType: 'Hydraulic Fluid Flush',
    lastCheck: '2023-07-20',
    due: '2023-10-25',
    priority: 'MEDIUM',
    team: 'Port Ops Tech',
    status: 'SCHEDULED',
    tabKey: 'scheduled',
  },
  {
    logId: 'MRT-G',
    assetId: 'JR-99-2',
    name: 'Ganges Treatment Node',
    segment: 'Primary Filter Array',
    taskType: 'Membrane Replacement',
    lastCheck: '2023-10-15',
    due: '2023-11-15',
    priority: 'LOW',
    team: 'Jal Shakti',
    status: 'COMPLETED',
    tabKey: 'completed',
  },
]

export const MAINTENANCE_TAB_COUNTS: Record<MaintenanceTabKey, string> = {
  all: '2,486',
  overdue: '128',
  'in-progress': '64',
  scheduled: '214',
  completed: '2,144',
}