import { Loader2 } from 'lucide-react'
import type { PredictionResponse } from '../types'

type PredictionPanelProps = {
  prediction: PredictionResponse | null
  simulating?: boolean
}

export function PredictionPanel({ prediction, simulating }: PredictionPanelProps) {
  const riskPercent = prediction ? prediction.risk_score * 100 : 0
  const riskColor =
    riskPercent >= 80 ? 'bg-danger-600' :
    riskPercent >= 55 ? 'bg-warn-600' :
    'bg-calm-600'

  return (
    <div className="glass rounded-md border p-4 shadow-glow">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-100">Risk Prediction</h2>
        <span className="text-xs uppercase tracking-[0.18em] text-slate-400">
          {simulating ? 'Running inference…' : 'Real-time inference'}
        </span>
      </div>

      {simulating ? (
        <div className="flex flex-col items-center justify-center py-10 gap-3 text-slate-400">
          <Loader2 size={28} className="animate-spin text-signal-500" />
          <div className="text-sm">Sending telemetry to ML model…</div>
        </div>
      ) : prediction ? (
        <div className="space-y-3 text-sm text-slate-300">
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-md border border-slate-700/60 p-3">
              <div className="text-slate-400">Predicted Label</div>
              <div
                className={`mt-1 text-base font-semibold capitalize ${
                  prediction.predicted_label === 'critical' ? 'text-danger-500' :
                  prediction.predicted_label === 'warning' ? 'text-warn-500' :
                  'text-calm-500'
                }`}
              >
                {prediction.predicted_label}
              </div>
            </div>
            <div className="rounded-md border border-slate-700/60 p-3">
              <div className="text-slate-400">Confidence</div>
              <div className="mt-1 text-base font-semibold text-slate-100">{(prediction.confidence * 100).toFixed(1)}%</div>
            </div>
          </div>

          <div className="rounded-md border border-slate-700/60 p-3">
            <div className="mb-2 flex items-center justify-between text-slate-400">
              <span>Risk Score</span>
              <span className="text-slate-300 font-medium">{(prediction.risk_score * 100).toFixed(0)}%</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-slate-800">
              <div
                className={`h-full rounded-full transition-all duration-500 ${riskColor}`}
                style={{ width: `${riskPercent}%` }}
              />
            </div>
          </div>

          <div className="rounded-md border border-slate-700/60 p-3">
            <div className="text-slate-400">Root Cause</div>
            <div className="mt-1 text-slate-100">{prediction.root_cause}</div>
          </div>

          <div className="rounded-md border border-slate-700/60 p-3">
            <div className="text-slate-400">Recommendation</div>
            <div className="mt-1 text-slate-100">{prediction.recommendation}</div>
          </div>

          {prediction.incident_created && (
            <div className="rounded-md border border-warn-600/30 bg-warn-600/10 px-3 py-2 text-xs text-warn-500">
              ⚠ Incident #{prediction.incident_id} created — risk score exceeded threshold
            </div>
          )}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-10 text-center text-sm text-slate-400">
          <div className="mb-2 text-2xl">🔮</div>
          <div className="font-medium text-slate-300">No prediction yet</div>
          <div className="mt-1 text-xs">Click "Run Simulation" to send a metric payload to the ML model.</div>
        </div>
      )}
    </div>
  )
}
