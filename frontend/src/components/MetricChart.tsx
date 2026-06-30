import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts'
import type { Metric } from '../types'

type MetricChartProps = {
  metrics: Metric[]
  loading?: boolean
}

export function MetricChart({ metrics, loading }: MetricChartProps) {
  const series = [...metrics].slice(0, 20).reverse().map((metric) => ({
    time: new Date(metric.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    cpu: metric.cpu_usage,
    memory: metric.memory_usage,
    latency: metric.network_latency_ms,
  }))

  return (
    <div className="glass rounded-md border p-4 shadow-glow">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-100">Live Metrics</h2>
        <span className="text-xs uppercase tracking-[0.18em] text-slate-400">CPU / Memory / Latency</span>
      </div>

      {loading ? (
        <div className="flex h-72 items-center justify-center">
          <div className="animate-pulse text-sm text-slate-400">Loading telemetry data…</div>
        </div>
      ) : metrics.length === 0 ? (
        <div className="flex h-72 flex-col items-center justify-center text-center text-sm text-slate-400">
          <div className="mb-2 text-2xl">📊</div>
          <div className="font-medium text-slate-300">No metric data yet</div>
          <div className="mt-1 text-xs">Run a simulation to populate the chart.</div>
        </div>
      ) : (
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={series}>
              <CartesianGrid stroke="rgba(148,163,184,0.14)" strokeDasharray="4 4" />
              <XAxis dataKey="time" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: '#0d1728', border: '1px solid rgba(148,163,184,0.2)', borderRadius: '6px' }}
                labelStyle={{ color: '#e2e8f0' }}
              />
              <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
              <Line type="monotone" dataKey="cpu" name="CPU %" stroke="#38bdf8" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="memory" name="Memory %" stroke="#34d399" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="latency" name="Latency ms" stroke="#fbbf24" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
