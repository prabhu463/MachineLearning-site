import type { Incident } from '../types'

type IncidentTableProps = {
  incidents: Incident[]
  loading?: boolean
}

// Fix #12: Added empty state message and loading skeleton — previously showed a blank table
export function IncidentTable({ incidents, loading }: IncidentTableProps) {
  return (
    <div className="glass rounded-md border p-4 shadow-glow">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-100">Incidents</h2>
        <span className="text-xs uppercase tracking-[0.18em] text-slate-400">Latest 50</span>
      </div>

      {loading ? (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse rounded-md border border-slate-700/60 p-3">
              <div className="flex gap-4">
                <div className="h-3 w-16 rounded bg-slate-700" />
                <div className="h-3 w-12 rounded bg-slate-700" />
                <div className="h-3 w-32 rounded bg-slate-700" />
              </div>
            </div>
          ))}
        </div>
      ) : incidents.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-10 text-center text-sm text-slate-400">
          <div className="mb-2 text-2xl">🟢</div>
          <div className="font-medium text-slate-300">No incidents yet</div>
          <div className="mt-1 text-xs">Click "Run Simulation" to generate your first prediction and incident.</div>
        </div>
      ) : (
        <div className="overflow-hidden rounded-md border border-slate-700/60">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-900/80 text-slate-300">
              <tr>
                <th className="px-3 py-2">Severity</th>
                <th className="px-3 py-2">Risk</th>
                <th className="px-3 py-2">Root Cause</th>
                <th className="px-3 py-2">Recommendation</th>
                <th className="px-3 py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {incidents.slice(0, 8).map((incident) => (
                <tr key={incident.id} className="border-t border-slate-800/70 hover:bg-slate-800/30 transition-colors">
                  <td className="px-3 py-2">
                    <span
                      className={`inline-block rounded px-2 py-0.5 text-xs font-semibold uppercase ${
                        incident.severity === 'critical'
                          ? 'bg-danger-600/20 text-danger-500'
                          : incident.severity === 'warning'
                          ? 'bg-warn-600/20 text-warn-500'
                          : 'bg-slate-700/40 text-slate-300'
                      }`}
                    >
                      {incident.severity}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-slate-300">{incident.risk_score.toFixed(2)}</td>
                  <td className="px-3 py-2 text-slate-300">{incident.root_cause}</td>
                  <td className="px-3 py-2 text-slate-300">{incident.recommendation}</td>
                  <td className="px-3 py-2 text-calm-500">{incident.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
