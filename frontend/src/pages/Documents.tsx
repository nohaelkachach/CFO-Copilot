// src/pages/Documents.tsx
import { useState, useEffect } from 'react'
import { getAllDocuments } from '../services/api'
import DocumentCard from '../components/documents/DocumentCard'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import Alert from '../components/ui/Alert'
import { Link } from 'react-router-dom'

type Document = {
  id: string
  filename: string
  category: string
  processing_status: string
  uploaded_at: string
}

function Documents() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    async function load() {
      try {
        const res = await getAllDocuments()
        setDocuments(res.data)
      } catch {
        setError("Failed to load documents.")
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const processed = documents.filter(d => d.processing_status === "processed").length
  const processing = documents.filter(d =>
    d.processing_status === "pending" || d.processing_status === "processing"
  ).length

  return (
    <div className="flex flex-col gap-8">

      {/* Hero */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-700 rounded-2xl p-8 text-white">
        <p className="text-slate-400 text-sm font-semibold uppercase tracking-widest mb-2">
          Document Library
        </p>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Your Documents</h1>
            <p className="text-slate-300">
              All uploaded documents and their AI processing status
            </p>
          </div>
          <Link
            to="/upload"
            className="bg-white text-slate-900 px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-slate-100 transition-colors"
          >
            + Upload New
          </Link>
        </div>
      </div>

      {error && (
        <Alert type="error" message={error} onClose={() => setError("")} />
      )}

      {/* Stats */}
      {documents.length > 0 && (
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm text-center">
            <p className="text-3xl font-bold text-gray-900">{documents.length}</p>
            <p className="text-xs text-gray-400 uppercase tracking-widest mt-1">Total</p>
          </div>
          <div className="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm text-center">
            <p className="text-3xl font-bold text-green-600">{processed}</p>
            <p className="text-xs text-gray-400 uppercase tracking-widest mt-1">Processed</p>
          </div>
          <div className="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm text-center">
            <p className="text-3xl font-bold text-yellow-500">{processing}</p>
            <p className="text-xs text-gray-400 uppercase tracking-widest mt-1">Processing</p>
          </div>
        </div>
      )}

      {loading ? (
        <LoadingSpinner message="Loading documents..." />
      ) : documents.length === 0 ? (
        <div className="bg-white rounded-2xl border border-dashed border-gray-300 p-16 text-center">
          <p className="text-5xl mb-4">📂</p>
          <p className="text-xl font-bold text-gray-800 mb-1">No documents yet</p>
          <p className="text-sm text-gray-400 mb-6">
            Upload your first financial document to get started
          </p>
          <Link
            to="/upload"
            className="inline-block bg-slate-900 text-white px-6 py-2.5 rounded-xl text-sm font-semibold hover:bg-slate-700 transition-colors"
          >
            Upload Document
          </Link>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {documents.map(doc => (
            <DocumentCard key={doc.id} {...doc} />
          ))}
        </div>
      )}
    </div>
  )
}

export default Documents