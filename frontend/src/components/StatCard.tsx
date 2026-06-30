import type { ReactNode } from 'react'

type StatCardProps = {
  label: string
  value: string
  delta?: string
  tone?: 'calm' | 'warn' | 'danger' | 'signal'
  icon?: ReactNode
}

const toneClasses = {
  calm: 'border-calm-600/30 text-calm-500',
  warn: 'border-warn-600/30 text-warn-500',
  danger: 'border-danger-600/30 text-danger-500',
  signal: 'border-signal-600/30 text-signal-500',
}

const iconToneClasses = {
  calm: 'text-calm-500',
  warn: 'text-warn-500',
  danger: 'text-danger-500',
  signal: 'text-signal-500',
}

export function StatCard({ label, value, delta, tone = 'signal', icon }: StatCardProps) {
  return (
    <div className="glass rounded-md border p-4 shadow-glow transition-all hover:shadow-[0_0_0_1px_rgba(125,211,252,0.3),0_24px_48px_rgba(0,0,0,0.4)]">
      <div className="flex items-center justify-between">
        <div className="text-xs uppercase tracking-[0.18em] text-slate-400">{label}</div>
        {icon ? <div className={iconToneClasses[tone]}>{icon}</div> : null}
      </div>
      <div className={`mt-3 text-3xl font-semibold ${toneClasses[tone]}`}>{value}</div>
      {delta ? <div className="mt-2 text-sm text-slate-400">{delta}</div> : null}
    </div>
  )
}
