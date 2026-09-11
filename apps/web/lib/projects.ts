export type RiskLevel = 'CRITICAL' | 'HIGH' | 'MODERATE' | 'STABLE'
export type ProjectStatus = 'Under Construction' | 'Operational' | 'Maintenance'

export interface Project {
  id: string
  name: string
  ministry: string
  region: string
  risk: RiskLevel
  change: string
  exposure: string
  confidence: number
  status: ProjectStatus
}

export interface ProjectMeta {
  baselineEnd: string
  progress: number
}

export const PROJECTS: Project[] = [
  {
    id: 'ASSET-NH44-001',
    name: 'NH-44 Expressway Extension (VII)',
    ministry: 'Road Transport & Highways',
    region: 'Northern Corridor',
    risk: 'CRITICAL',
    change: '+18%',
    exposure: '1.2B Cr',
    confidence: 92,
    status: 'Under Construction',
  },
  {
    id: 'METRO-MUM-P3',
    name: 'Mumbai Metro Phase 3 - Line 1',
    ministry: 'Urban Development',
    region: 'Maharashtra',
    risk: 'HIGH',
    change: '+12.4%',
    exposure: '4.8B Cr',
    confidence: 88,
    status: 'Under Construction',
  },
  {
    id: 'GRID-CHEN-04',
    name: 'Chennai Smart Grid Expansion',
    ministry: 'Power & Energy',
    region: 'Tamil Nadu',
    risk: 'MODERATE',
    change: '-2.1%',
    exposure: '0.8B Cr',
    confidence: 94,
    status: 'Operational',
  },
  {
    id: 'PORT-KOL-EXT',
    name: 'Kolkata Deep Water Port',
    ministry: 'Ports & Shipping',
    region: 'West Bengal',
    risk: 'STABLE',
    change: '-5.0%',
    exposure: '2.1B Cr',
    confidence: 96,
    status: 'Maintenance',
  },
  {
    id: 'WATER-GAN-IX',
    name: 'Ganges Basin Treatment Node',
    ministry: 'Jal Shakti',
    region: 'Uttar Pradesh',
    risk: 'HIGH',
    change: '+4.2%',
    exposure: '0.5B Cr',
    confidence: 82,
    status: 'Under Construction',
  },
  {
    id: 'SOLAR-PUNE-01',
    name: 'Pune Photovoltaic Cluster',
    ministry: 'New & Renewable Energy',
    region: 'Maharashtra',
    risk: 'STABLE',
    change: '0.0%',
    exposure: '0.3B Cr',
    confidence: 98,
    status: 'Operational',
  },
  {
    id: 'RAIL-DFCC-EAST',
    name: 'Dedicated Freight Corridor',
    ministry: 'Railways',
    region: 'Pan-India (East)',
    risk: 'MODERATE',
    change: '+1.5%',
    exposure: '12.5B Cr',
    confidence: 90,
    status: 'Under Construction',
  },
]

export const FALLBACK_PROJECT_ID = 'ASSET-NH44-001'

export const RISK_PERCENT: Record<RiskLevel, number> = {
  CRITICAL: 88,
  HIGH: 74,
  MODERATE: 58,
  STABLE: 34,
}

export const PROJECT_META: Record<string, ProjectMeta> = {
  'ASSET-NH44-001': { baselineEnd: 'Dec 2024', progress: 64.2 },
  'METRO-MUM-P3': { baselineEnd: 'Jun 2025', progress: 58.4 },
  'GRID-CHEN-04': { baselineEnd: 'Mar 2025', progress: 91.7 },
  'PORT-KOL-EXT': { baselineEnd: 'Dec 2024', progress: 84.0 },
  'WATER-GAN-IX': { baselineEnd: 'Sep 2025', progress: 47.8 },
  'SOLAR-PUNE-01': { baselineEnd: 'Oct 2024', progress: 95.1 },
  'RAIL-DFCC-EAST': { baselineEnd: 'Mar 2026', progress: 52.9 },
}

export function getProjectById(id: string): Project | undefined {
  return PROJECTS.find((project) => project.id === id)
}