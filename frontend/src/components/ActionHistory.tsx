import type { ActionEvent } from '../types'

type ActionHistoryProps = {
  actions: ActionEvent[]
  loading?: boolean
}

// Fix #13: Added empty state message and loading skeleton — previously showed nothing with no explanation
export function ActionHistory({ actions, loading }: ActionHistoryProps) {
  return (
    <div className="glass rounded-md border p-4 shadow-glow">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-100">Automated Action History</h2>
        <span className="text-xs uppercase tracking-[0.18em] text-slate-400">Simulated execution</span>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[1, 2].map((i) => (
            <div key={i} className="animate-pulse rounded-md border border-slate-700/60 px-4 py-3">
              <div className="flex items-center justify-between">
                <div className="h-3 w-32 rounded bg-slate-700" />
                <div className="h-3 w-16 rounded bg-slate-700" />
              </div>
              <div className="mt-2 h-3 w-48 rounded bg-slate-700" />
            </div>
          ))}
        </div>
      ) : actions.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-10 text-center text-sm text-slate-400">
          <div className="mb-2 text-2xl">⚡</div>
          <div className="font-medium text-slate-300">No automated actions yet</div>
          <div className="mt-1 text-xs">Actions are triggered automatically when a simulation creates a high-risk incident.</div>
        </div>
      ) : (
        <div className="space-y-3">
          {actions.slice(0, 6).map((action) => (
            <div key={action.id} className="rounded-md border border-slate-700/60 px-4 py-3 hover:border-slate-600/80 transition-colors">
              <div className="flex items-center justify-between gap-3">
                <div className="font-medium text-slate-100">{action.action_name}</div>
                <div
                  className={`text-xs uppercase tracking-[0.18em] ${
                    action.status === 'simulated' ? 'text-calm-500' :
                    action.status === 'executed' ? 'text-signal-500' :
                    'text-warn-500'
                  }`}
                >
                  {action.status}
                </div>
              </div>
              <div className="mt-1 text-sm text-slate-400">{action.details}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
