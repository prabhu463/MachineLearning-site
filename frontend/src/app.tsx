import { useEffect, useState } from 'react'
import { AlertTriangle, PlayCircle, RefreshCw, Loader2 } from 'lucide-react'
import { api } from './lib/api'
import type { ActionEvent, DashboardSummary, Incident, Metric, PredictionResponse } from './types'
import { ActionHistory } from './components/ActionHistory'
import { IncidentTable } from './components/IncidentTable'
import { MetricChart } from './components/MetricChart'
import { Overview } from './components/Overview'
import { PredictionPanel } from './components/PredictionPanel'

// Fix #9: This payload is sent ONLY when the user clicks "Run Simulation",
// NOT on every page load — preventing garbage DB rows on every refresh.
const SIMULATION_PAYLOAD = {
  service_name: 'checkout',
  cpu_usage: 84,
  memory_usage: 78,
  disk_usage: 66,
  network_latency_ms: 260,
  request_count: 980,
  error_rate: 0.18,
  response_time_ms: 730,
}

export default function App() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [metrics, setMetrics] = useState<Metric[]>([])
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [actions, setActions] = useState<ActionEvent[]>([])
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null)
  // Fix #11: Track loading state separately for dashboard data vs simulation
  const [loading, setLoading] = useState(true)
  const [simulating, setSimulating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [simError, setSimError] = useState<string | null>(null)

  // Load dashboard data (metrics, incidents, actions, summary) — no prediction call here
  async function loadData() {
    setLoading(true)
    setError(null)
    try {
      const [summaryData, metricData, incidentData, actionData] = await Promise.all([
        api.dashboardSummary(),
        api.metrics(),
        api.incidents(),
        api.actions(),
      ])
      setSummary(summaryData)
      setMetrics(metricData)
      setIncidents(incidentData)
      setActions(actionData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard')
    } finally {
      setLoading(false)
    }
  }

  // Fix #17: "Run Simulation" button is now wired up and triggers prediction only on click
  async function runSimulation() {
    setSimulating(true)
    setSimError(null)
    try {
      const pred = await api.predict(SIMULATION_PAYLOAD)
      setPrediction(pred)
      // Refresh dashboard data to show new incident/action rows in the tables
      const [summaryData, incidentData, actionData] = await Promise.all([
        api.dashboardSummary(),
        api.incidents(),
        api.actions(),
      ])
      setSummary(summaryData)
      setIncidents(incidentData)
      setActions(actionData)
    } catch (err) {
      setSimError(err instanceof Error ? err.message : 'Simulation failed')
    } finally {
      setSimulating(false)
    }
  }

  useEffect(() => {
    void loadData()
  }, [])

  return (
    <main className="min-h-screen px-4 py-6 text-slate-100">
      <div className="mx-auto flex max-w-[1440px] flex-col gap-6">
        <header className="glass rounded-md border px-5 py-4 shadow-glow">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.28em] text-signal-500">PredictiveOps AI</div>
              <h1 className="mt-1 text-2xl font-semibold">Intelligent Incident Prediction and Self-Healing</h1>
              <p className="mt-2 max-w-3xl text-sm text-slate-400">
                Predict failure before it happens, surface likely causes, and simulate remediation from one control room.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                className="inline-flex items-center gap-2 rounded-md border border-slate-700/70 bg-slate-900/80 px-4 py-2 text-sm disabled:opacity-50"
                onClick={() => void loadData()}
                disabled={loading}
              >
                {loading ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}
                Refresh
              </button>
              {/* Fix #17: wired up onClick handler */}
              <button
                className="inline-flex items-center gap-2 rounded-md bg-signal-600 px-4 py-2 text-sm font-medium text-slate-950 disabled:opacity-60 disabled:cursor-not-allowed"
                onClick={() => void runSimulation()}
                disabled={simulating}
              >
                {simulating ? <Loader2 size={16} className="animate-spin" /> : <PlayCircle size={16} />}
                {simulating ? 'Running…' : 'Run Simulation'}
              </button>
            </div>
          </div>
        </header>

        {/* Dashboard-level error */}
        {error ? (
          <div className="rounded-md border border-danger-600/40 bg-danger-600/10 px-4 py-3 text-sm text-danger-500">
            ⚠ {error}
          </div>
        ) : null}

        {/* Simulation-level error */}
        {simError ? (
          <div className="rounded-md border border-warn-600/40 bg-warn-600/10 px-4 py-3 text-sm text-warn-500">
            ⚠ Simulation error: {simError}
          </div>
        ) : null}

        {/* Fix #11: show skeleton when loading instead of misleading 0s */}
        <Overview summary={loading ? null : summary} loading={loading} />

        <div className="grid gap-6 xl:grid-cols-[1.4fr_0.9fr]">
          <MetricChart metrics={metrics} loading={loading} />
          <PredictionPanel prediction={prediction} simulating={simulating} />
        </div>

        <div className="grid gap-6 xl:grid-cols-[1.4fr_0.9fr]">
          <IncidentTable incidents={incidents} loading={loading} />
          <ActionHistory actions={actions} loading={loading} />
        </div>

        <section className="glass rounded-md border p-4 shadow-glow">
          <div className="mb-4 flex items-center gap-2">
            <AlertTriangle size={18} className="text-warn-500" />
            <h2 className="text-lg font-semibold text-slate-100">Model and Prediction Confidence</h2>
          </div>
          {loading ? (
            <div className="grid gap-4 md:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="animate-pulse rounded-md border border-slate-700/60 p-4">
                  <div className="h-3 w-24 rounded bg-slate-700" />
                  <div className="mt-3 h-8 w-16 rounded bg-slate-700" />
                </div>
              ))}
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-md border border-slate-700/60 p-4">
                <div className="text-sm text-slate-400">Latest Active Service</div>
                <div className="mt-2 text-2xl font-semibold text-slate-100">
                  {summary?.latest_metric?.service_name ?? '—'}
                </div>
              </div>
              <div className="rounded-md border border-slate-700/60 p-4">
                <div className="text-sm text-slate-400">Latest Incident Severity</div>
                <div className="mt-2 text-2xl font-semibold capitalize text-slate-100">
                  {summary?.latest_incident?.severity ?? 'None'}
                </div>
              </div>
              <div className="rounded-md border border-slate-700/60 p-4">
                <div className="text-sm text-slate-400">Prediction Confidence</div>
                <div className="mt-2 text-2xl font-semibold text-slate-100">
                  {prediction ? `${(prediction.confidence * 100).toFixed(1)}%` : 'Run simulation →'}
                </div>
              </div>
            </div>
          )}
        </section>
      </div>
    </main>
  )
}
