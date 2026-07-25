// src/components/anomalies/AnomalyCard.tsx

type AnomalyCardProps = {
  id: string
  description: string
  severity: string
  resolved: boolean
  created_at: string
  onResolve: (id: string) => void
}

const severityConfig: Record<string, { style: string; label: string; dot: string }> = {
  high:   { style: "bg-red-100 text-red-700 border border-red-200",    label: "High",   dot: "bg-red-500" },
  medium: { style: "bg-yellow-100 text-yellow-700 border border-yellow-200", label: "Medium", dot: "bg-yellow-500" },
  low:    { style: "bg-blue-100 text-blue-700 border border-blue-200",  label: "Low",    dot: "bg-blue-500" },
}

function AnomalyCard({ id, description, severity, resolved, created_at, onResolve }: AnomalyCardProps) {
  const config = severityConfig[severity] ?? severityConfig.low

  return (
    <div className={`bg-white rounded-2xl border border-gray-100 p-6 shadow-sm transition-all ${
      resolved ? "opacity-50" : "hover:shadow-md"
    }`}>
      <div className="flex items-start justify-between gap-4">

        {/* Left — severity + description */}
        <div className="flex items-start gap-3 flex-1">
          {/* Severity dot */}
          <div className={`w-2.5 h-2.5 rounded-full flex-shrink-0 mt-1.5 ${config.dot}`} />

          <div>
            {/* Severity badge */}
            <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold mb-2 ${config.style}`}>
              {config.label} severity
            </span>

            {/* Description */}
            <p className="text-sm font-medium text-gray-800 leading-relaxed">
              {description}
            </p>

            {/* Date */}
            <p className="text-xs text-gray-400 mt-2">
              Detected {new Date(created_at).toLocaleDateString('en-GB', {
                day: 'numeric', month: 'short', year: 'numeric'
              })}
            </p>
          </div>
        </div>

        {/* Right — action */}
        {resolved ? (
          <span className="flex-shrink-0 flex items-center gap-1.5 text-xs font-semibold text-green-600 bg-green-50 px-3 py-1.5 rounded-xl">
            ✓ Resolved
          </span>
        ) : (
          <button
            onClick={() => onResolve(id)}
            className="flex-shrink-0 text-xs font-semibold bg-slate-900 text-white px-4 py-2 rounded-xl hover:bg-slate-700 transition-colors"
          >
            Mark resolved
          </button>
        )}
      </div>
    </div>
  )
}

export default AnomalyCard