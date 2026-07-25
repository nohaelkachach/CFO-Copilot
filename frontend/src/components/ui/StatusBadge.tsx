// src/components/ui/StatusBadge.tsx

type Status = "pending" | "processing" | "processed" | "failed" | "unknown"

const styles: Record<Status, string> = {
  pending:    "bg-yellow-100 text-yellow-800 border border-yellow-200",
  processing: "bg-blue-100 text-blue-800 border border-blue-200",
  processed:  "bg-green-100 text-green-800 border border-green-200",
  failed:     "bg-red-100 text-red-800 border border-red-200",
  unknown:    "bg-gray-100 text-gray-600 border border-gray-200",
}

const labels: Record<Status, string> = {
  pending:    "Pending",
  processing: "Processing...",
  processed:  "Processed",
  failed:     "Failed",
  unknown:    "Unknown",
}

function StatusBadge({ status }: { status: string }) {
  const s = (status as Status) in styles ? (status as Status) : "unknown"

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[s]}`}>
      {s === "processing" && (
        <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse mr-1.5" />
      )}
      {labels[s]}
    </span>
  )
}

export default StatusBadge