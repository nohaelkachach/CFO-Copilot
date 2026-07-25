// src/pages/Upload.tsx
import { useState, useRef } from 'react'
import { uploadDocument, getDocumentStatus } from '../services/api'
import StatusBadge from '../components/ui/StatusBadge'
import Alert from '../components/ui/Alert'
import LoadingSpinner from '../components/ui/LoadingSpinner'

type UploadedDoc = {
  id: string
  filename: string
  status: string
  category?: string
}

function Upload() {
  const [uploading, setUploading] = useState(false)
  const [documents, setDocuments] = useState<UploadedDoc[]>([])
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Poll document status until processed or failed
  async function pollStatus(id: string) {
    const interval = setInterval(async () => {
      try {
        const res = await getDocumentStatus(id)
        const { status, category } = res.data

        setDocuments(prev =>
          prev.map(doc => doc.id === id ? { ...doc, status, category } : doc)
        )

        if (status === "processed" || status === "failed") {
          clearInterval(interval)
        }
      } catch {
        clearInterval(interval)
      }
    }, 2000) // poll every 2 seconds
  }

  async function handleUpload(file: File) {
    if (!file) return

    setError("")
    setSuccess("")
    setUploading(true)

    try {
      const res = await uploadDocument(file)
      const { id, filename, message } = res.data

      // Add to list with pending status
      setDocuments(prev => [...prev, {
        id,
        filename,
        status: "pending"
      }])

      setSuccess(message)

      // Start polling for status updates
      pollStatus(id)

    } catch (err: any) {
      setError(err.response?.data?.detail ?? "Upload failed. Please try again.")
    } finally {
      setUploading(false)
    }
  }

  function handleFileInput(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) handleUpload(file)
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files?.[0]
    if (file) handleUpload(file)
  }

  function handleDragOver(e: React.DragEvent) {
    e.preventDefault()
    setDragOver(true)
  }

    return (
    <div className="flex flex-col gap-8 max-w-3xl">

      {/* Hero */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-700 rounded-2xl p-8 text-white">
        <p className="text-slate-400 text-sm font-semibold uppercase tracking-widest mb-2">AI-Powered</p>
        <h1 className="text-3xl font-bold mb-2">Upload Documents</h1>
        <p className="text-slate-300">
          Drop any financial document. Our AI classifies it, extracts key data, and flags anomalies automatically.
        </p>
      </div>

      {/* Alerts */}
      {error && (
        <Alert type="error" message={error} onClose={() => setError("")} />
      )}
      {success && (
        <Alert type="success" message={success} onClose={() => setSuccess("")} />
      )}

      {/* Drop zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={() => setDragOver(false)}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors ${
          dragOver
            ? "border-slate-900 bg-slate-50"
            : "border-gray-300 hover:border-slate-400 hover:bg-gray-50"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.png,.jpg,.jpeg"
          onChange={handleFileInput}
          className="hidden"
        />

        {uploading ? (
          <LoadingSpinner message="Uploading and starting AI processing..." />
        ) : (
          <>
            <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <p className="text-gray-700 font-medium">
              Drop your document here or <span className="text-slate-900 underline">browse</span>
            </p>
            <p className="text-gray-400 text-sm mt-1">
              Supports PDF, PNG, JPG — max 200MB
            </p>
          </>
        )}
      </div>

      {/* Supported document types */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: "P&L Statement", icon: "📊" },
          { label: "Balance Sheet", icon: "⚖️" },
          { label: "Invoice", icon: "🧾" },
          { label: "Bank Statement", icon: "🏦" },
          { label: "Tax Document", icon: "📋" },
          { label: "Cash Flow", icon: "💰" },
          { label: "Contract", icon: "📝" },
          { label: "Payslip", icon: "💼" },
        ].map(type => (
          <div key={type.label} className="flex items-center gap-2 p-3 bg-white border border-gray-200 rounded-lg text-sm text-gray-600">
            <span>{type.icon}</span>
            <span>{type.label}</span>
          </div>
        ))}
      </div>

      {/* Uploaded documents list */}
      {documents.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="font-semibold text-gray-800">Uploaded this session</h2>
          </div>
          <div className="divide-y divide-gray-100">
            {documents.map(doc => (
              <div key={doc.id} className="px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-slate-100 rounded-lg flex items-center justify-center text-slate-600 text-xs font-medium">
                    PDF
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-800">{doc.filename}</p>
                    {doc.category && doc.category !== "unknown" && (
                      <p className="text-xs text-gray-400 mt-0.5 capitalize">{doc.category}</p>
                    )}
                  </div>
                </div>
                <StatusBadge status={doc.status} />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* How it works */}
      <div className="bg-slate-50 rounded-xl p-6">
        <h3 className="font-semibold text-gray-800 mb-4">How it works</h3>
        <div className="flex flex-col gap-3">
          {[
            { step: "1", title: "Upload", desc: "Drop your PDF or image file" },
            { step: "2", title: "AI Processing", desc: "Our AI extracts key financial data and classifies the document" },
            { step: "3", title: "Anomaly Detection", desc: "AI flags anything unusual for your review" },
            { step: "4", title: "Insights", desc: "View results on your Dashboard and ask questions via Chat" },
          ].map(item => (
            <div key={item.step} className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-slate-900 text-white text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
                {item.step}
              </div>
              <div>
                <p className="text-sm font-medium text-gray-800">{item.title}</p>
                <p className="text-xs text-gray-500">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Upload