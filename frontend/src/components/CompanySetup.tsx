// src/components/CompanySetup.tsx
import { useState } from 'react'
import { createCompany } from '../services/api'

const sectors = [
  { value: "retail", label: "Retail & Commerce", icon: "🛍️" },
  { value: "manufacturing", label: "Manufacturing & Industry", icon: "🏭" },
  { value: "services", label: "Professional Services", icon: "💼" },
  { value: "technology", label: "Technology & Software", icon: "💻" },
  { value: "construction", label: "Construction & Real Estate", icon: "🏗️" },
  { value: "hospitality", label: "Hospitality & Tourism", icon: "🏨" },
  { value: "agriculture", label: "Agriculture & Food", icon: "🌾" },
  { value: "other", label: "Other", icon: "📦" },
]

const features = [
  { icon: "🤖", title: "AI Document Analysis", desc: "Classify and extract data from any financial document automatically" },
  { icon: "📊", title: "Financial Dashboard", desc: "Real-time P&L, balance sheet, and cash flow visualization" },
  { icon: "⚠️", title: "Anomaly Detection", desc: "AI flags unusual transactions and inconsistencies instantly" },
  { icon: "💬", title: "Ask Anything", desc: "Query your finances in plain English — get precise answers" },
]

function CompanySetup({ onComplete }: { onComplete: () => void }) {
  const [step, setStep] = useState<1 | 2>(1)
  const [name, setName] = useState('')
  const [sector, setSector] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit() {
    if (!name.trim()) return setError('Company name is required')
    setLoading(true)
    setError('')
    try {
      await createCompany({ name: name.trim(), sector })
      onComplete()
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">

      {/* Left panel — branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex-col justify-between p-12">

        {/* Logo */}
        <div>
          <div className="flex items-center gap-3 mb-16">
            <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center">
              <span className="text-slate-900 font-bold text-lg">C</span>
            </div>
            <span className="text-white font-bold text-xl">CFO Copilot</span>
          </div>

          <h1 className="text-5xl font-bold text-white leading-tight mb-6">
            Your AI-powered<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
              financial intelligence
            </span><br />
            platform
          </h1>
          <p className="text-slate-400 text-lg leading-relaxed">
            Upload any financial document. Our AI classifies it,
            extracts key data, detects anomalies, and answers
            your questions — in seconds.
          </p>
        </div>

        {/* Features */}
        <div className="flex flex-col gap-5">
          {features.map(f => (
            <div key={f.title} className="flex items-start gap-4">
              <div className="w-10 h-10 bg-slate-700 rounded-xl flex items-center justify-center text-lg flex-shrink-0">
                {f.icon}
              </div>
              <div>
                <p className="text-white font-semibold text-sm">{f.title}</p>
                <p className="text-slate-400 text-xs mt-0.5 leading-relaxed">{f.desc}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <p className="text-slate-600 text-xs">
          © 2026 CFO Copilot · Powered by AI
        </p>
      </div>

      {/* Right panel — form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
        <div className="w-full max-w-md">

          {/* Step indicator */}
          <div className="flex items-center gap-3 mb-10">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
              step >= 1 ? 'bg-slate-900 text-white' : 'bg-gray-200 text-gray-400'
            }`}>1</div>
            <div className={`flex-1 h-0.5 transition-all ${step >= 2 ? 'bg-slate-900' : 'bg-gray-200'}`} />
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
              step >= 2 ? 'bg-slate-900 text-white' : 'bg-gray-200 text-gray-400'
            }`}>2</div>
          </div>

          {step === 1 && (
            <div className="flex flex-col gap-6">
              <div>
                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                  Welcome aboard 👋
                </h2>
                <p className="text-gray-500">
                  Let's start by setting up your company profile.
                </p>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-3 text-sm">
                  {error}
                </div>
              )}

              <div>
                <label className="text-sm font-semibold text-gray-700 block mb-2">
                  Company Name *
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && name.trim() && setStep(2)}
                  placeholder="e.g. Atlas Cosmetics SARL"
                  autoFocus
                  className="w-full border-2 border-gray-200 rounded-xl px-4 py-3.5 text-sm focus:outline-none focus:border-slate-900 transition-colors"
                />
                <p className="text-xs text-gray-400 mt-1.5">
                  This is how your company will appear throughout the platform.
                </p>
              </div>

              <button
                onClick={() => {
                  if (!name.trim()) return setError('Company name is required')
                  setError('')
                  setStep(2)
                }}
                disabled={!name.trim()}
                className="w-full bg-slate-900 text-white py-3.5 rounded-xl font-semibold text-sm hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                Continue →
              </button>
            </div>
          )}

          {step === 2 && (
            <div className="flex flex-col gap-6">
              <div>
                <button
                  onClick={() => setStep(1)}
                  className="text-sm text-gray-400 hover:text-gray-600 transition-colors mb-4 flex items-center gap-1"
                >
                  ← Back
                </button>
                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                  What's your sector?
                </h2>
                <p className="text-gray-500">
                  This helps our AI provide more relevant insights.
                </p>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-3 text-sm">
                  {error}
                </div>
              )}

              <div className="grid grid-cols-2 gap-3">
                {sectors.map(s => (
                  <button
                    key={s.value}
                    onClick={() => setSector(s.value)}
                    className={`flex items-center gap-3 p-3.5 rounded-xl border-2 text-left transition-all ${
                      sector === s.value
                        ? 'border-slate-900 bg-slate-900 text-white'
                        : 'border-gray-200 bg-white hover:border-slate-400 text-gray-700'
                    }`}
                  >
                    <span className="text-xl">{s.icon}</span>
                    <span className="text-xs font-medium leading-tight">{s.label}</span>
                  </button>
                ))}
              </div>

              <button
                onClick={handleSubmit}
                disabled={loading}
                className="w-full bg-gradient-to-r from-slate-900 to-slate-700 text-white py-3.5 rounded-xl font-semibold text-sm hover:from-slate-800 hover:to-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Setting up your workspace...
                  </span>
                ) : (
                  `Launch CFO Copilot for ${name} →`
                )}
              </button>

              <p className="text-xs text-gray-400 text-center">
                You can skip this — sector is optional and can be changed later.
                <button
                  onClick={handleSubmit}
                  className="text-slate-600 underline ml-1 hover:text-slate-900"
                >
                  Skip for now
                </button>
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default CompanySetup