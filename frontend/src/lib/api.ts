import type { ActionEvent, DashboardSummary, Incident, Metric, PredictionResponse } from '../types'

const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
    ...init,
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `Request failed: ${response.status}`)
  }
  return response.json() as Promise<T>
}

export const api = {
  health: () => request<{ status: string; service: string }>('/health'),
  dashboardSummary: () => request<DashboardSummary>('/dashboard/summary'),
  metrics: () => request<Metric[]>('/metrics?limit=50'),
  incidents: () => request<Incident[]>('/incidents?limit=50'),
  actions: () => request<ActionEvent[]>('/actions?limit=50'),
  predict: (payload: Record<string, unknown>) =>
    request<PredictionResponse>('/predict?auto_execute=true', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
}
