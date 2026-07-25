// src/pages/Anomalies.tsx
import { useState, useEffect } from 'react'
import { getAnomalies, resolveAnomaly } from '../services/api'
import AnomalyCard from '../components/anomalies/AnomalyCard'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import Alert from '../components/ui/Alert'

type Anomaly = {
  id: string
  description: string
  severity: string
  resolved: boolean
  created_at: string
  document_id: string
}

function Anomalies() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [filter, setFilter] = useState<"all" | "unresolved">("unresolved")

  useEffect(() => {
    loadAnomalies()
  }, [filter])

  async function loadAnomalies() {
    try {
      setLoading(true)
      const resolved = filter === "all" ? undefined : false
      const res = await getAnomalies(resolved)
      setAnomalies(res.data)
    } catch {
      setError("Failed to load anomalies.")
    } finally {
      setLoading(false)
    }
  }

  async function handleResolve(id: string) {
    try {
      await resolveAnomaly(id)
      setAnomalies(prev =>
        prev.map(a => a.id === id ? { ...a, resolved: true } : a)
      )
    } catch {
      setError("Failed to resolve anomaly.")
    }
  }

  const unresolvedCount = anomalies.filter(a => !a.resolved).length

  return (
    <div className="flex flex-col gap-8">

      {/* Hero */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-700 rounded-2xl p-8 text-white">
        <p className="text-slate-400 text-sm font-semibold uppercase tracking-widest mb-2">
          AI Detection
        </p>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Anomalies</h1>
            <p className="text-slate-300">
              Issues flagged by AI that require your attention
            </p>
          </div>
          {unresolvedCount > 0 && (
            <span className="bg-red-500 text-white text-sm font-bold px-4 py-2 rounded-xl">
              {unresolvedCount} unresolved
            </span>
          )}
        </div>
      </div>

      {error && (
        <Alert type="error" message={error} onClose={() => setError("")} />
      )}

      {/* Filter tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-xl p-1 w-fit">
        {(["unresolved", "all"] as const).map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-5 py-2 text-sm font-medium rounded-lg transition-all ${
              filter === f
                ? "bg-white text-slate-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {f === "unresolved" ? "Unresolved" : "All anomalies"}
          </button>
        ))}
      </div>

      {loading ? (
        <LoadingSpinner message="Scanning for anomalies..." />
      ) : anomalies.length === 0 ? (
        <div className="bg-white rounded-2xl border border-gray-100 p-16 text-center shadow-sm">
          <p className="text-5xl mb-4">✅</p>
          <p className="text-xl font-bold text-gray-800 mb-1">
            {filter === "unresolved" ? "All clear" : "No anomalies found"}
          </p>
          <p className="text-sm text-gray-400">
            {filter === "unresolved"
              ? "No unresolved issues — your documents look good"
              : "Upload documents to start AI anomaly detection"}
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {anomalies.map(anomaly => (
            <AnomalyCard
              key={anomaly.id}
              {...anomaly}
              onResolve={handleResolve}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default Anomalies