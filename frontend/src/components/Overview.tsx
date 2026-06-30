import { Activity, AlertTriangle, ShieldAlert, Gauge } from 'lucide-react'
import type { DashboardSummary } from '../types'
import { StatCard } from './StatCard'

type OverviewProps = {
  summary: DashboardSummary | null
  loading?: boolean
}

// Fix #11: Added loading prop so stat cards show skeletons during data fetch
// instead of misleading "0" values
export function Overview({ summary, loading }: OverviewProps) {
  const risk = summary ? (summary.average_risk_score * 100).toFixed(1) : '0.0'

  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="glass animate-pulse rounded-md border p-4 shadow-glow">
            <div className="h-2 w-20 rounded bg-slate-700" />
            <div className="mt-4 h-9 w-12 rounded bg-slate-700" />
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <StatCard label="Total Metrics" value={summary ? String(summary.total_metrics) : '0'} tone="signal" icon={<Activity size={16} />} />
      <StatCard label="Open Incidents" value={summary ? String(summary.open_incidents) : '0'} tone="warn" icon={<AlertTriangle size={16} />} />
      <StatCard label="Critical Incidents" value={summary ? String(summary.critical_incidents) : '0'} tone="danger" icon={<ShieldAlert size={16} />} />
      <StatCard label="Average Risk" value={`${risk}%`} tone="calm" icon={<Gauge size={16} />} />
    </div>
  )
}
