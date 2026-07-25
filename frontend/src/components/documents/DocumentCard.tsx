// src/components/documents/DocumentCard.tsx
import StatusBadge from '../ui/StatusBadge'

type DocumentCardProps = {
  id: string
  filename: string
  category: string
  processing_status: string
  uploaded_at: string
}

const categoryConfig: Record<string, { label: string; style: string }> = {
  financial_statement: { label: "Financial Statement", style: "bg-blue-100 text-blue-700" },
  tax:                 { label: "Tax Document",         style: "bg-purple-100 text-purple-700" },
  audit:               { label: "Audit Document",       style: "bg-green-100 text-green-700" },
  unknown:             { label: "Processing...",         style: "bg-gray-100 text-gray-500" },
}

function DocumentCard({ filename, category, processing_status, uploaded_at }: DocumentCardProps) {
  const cat = categoryConfig[category] ?? categoryConfig.unknown
  const ext = filename.split('.').pop()?.toUpperCase() ?? 'FILE'

  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm hover:shadow-md transition-shadow flex items-center gap-4">

      {/* File type icon */}
      <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center text-slate-600 text-xs font-bold flex-shrink-0">
        {ext}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-gray-900 truncate">{filename}</p>
        <div className="flex items-center gap-2 mt-1.5">
          <span className={`px-2 py-0.5 rounded-lg text-xs font-medium ${cat.style}`}>
            {cat.label}
          </span>
          <span className="text-xs text-gray-400">
            {new Date(uploaded_at).toLocaleDateString('en-GB', {
              day: 'numeric', month: 'short', year: 'numeric'
            })}
          </span>
        </div>
      </div>

      {/* Status */}
      <StatusBadge status={processing_status} />
    </div>
  )
}

export default DocumentCard