export type DataSourceStatus = 'healthy' | 'warning'

export interface DataSource {
  ref: string
  title: string
  status: DataSourceStatus
  description: string
  dataType: string
  records: string
  lastUpdate: string
}

export const SOURCES: DataSource[] = [
  {
    ref: 'DS-001',
    title: 'Monthly Flash Reports',
    status: 'healthy',
    description:
      'Executive summary reports on national infrastructure milestones and rapid project assessments.',
    dataType: 'PDF/DOCX',
    records: '1,248',
    lastUpdate: '12h ago',
  },
  {
    ref: 'DS-002',
    title: 'Dashboard Data',
    status: 'healthy',
    description:
      'Direct API feeds from regional command centers providing real-time KPI telemetry.',
    dataType: 'JSON API',
    records: '842K',
    lastUpdate: 'Just now',
  },
  {
    ref: 'DS-003',
    title: 'Project Progress Reports',
    status: 'warning',
    description:
      'Detailed site-level progress data including material logs and labor force distribution.',
    dataType: 'Structured XLS',
    records: '15.4K',
    lastUpdate: '3h ago',
  },
  {
    ref: 'DS-004',
    title: 'Financial Audit Reports',
    status: 'healthy',
    description:
      'Verified institutional expenditure logs and fiscal compliance certifications.',
    dataType: 'Secure DB',
    records: '5.3K',
    lastUpdate: '18h ago',
  },
  {
    ref: 'DS-005',
    title: 'Land Registry Records',
    status: 'healthy',
    description:
      'National land acquisition status, ownership mapping, and legal clearance timelines.',
    dataType: 'GeoJSON',
    records: '340K',
    lastUpdate: '48h ago',
  },
  {
    ref: 'DS-006',
    title: 'Environmental Clearance Records',
    status: 'healthy',
    description:
      'Ecological impact assessments and regulatory clearance status for protected zones.',
    dataType: 'Spatial API',
    records: '4.1M',
    lastUpdate: '48h ago',
  },
]