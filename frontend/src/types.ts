export type Metric = {
  id: number
  service_name: string
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  network_latency_ms: number
  request_count: number
  error_rate: number
  response_time_ms: number
  created_at: string
}

export type Incident = {
  id: number
  metric_id: number
  severity: string
  risk_score: number
  predicted_label: string
  root_cause: string
  recommendation: string
  status: string
  notes: string
  created_at: string
}

export type ActionEvent = {
  id: number
  incident_id: number
  action_name: string
  executed_by: string
  status: string
  details: string
  created_at: string
}

export type DashboardSummary = {
  total_metrics: number
  total_incidents: number
  open_incidents: number
  critical_incidents: number
  average_risk_score: number
  latest_metric: Metric | null
  latest_incident: Incident | null
}

export type PredictionResponse = {
  predicted_label: string
  risk_score: number
  confidence: number
  root_cause: string
  recommendation: string
  incident_created: boolean
  incident_id: number | null
  created_at: string
}
