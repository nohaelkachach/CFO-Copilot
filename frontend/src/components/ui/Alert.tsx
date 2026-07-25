// src/components/ui/Alert.tsx

type AlertType = "success" | "error" | "warning" | "info"

const config: Record<AlertType, { style: string; icon: string }> = {
  success: { style: "bg-green-50 border-green-200 text-green-800",  icon: "✓" },
  error:   { style: "bg-red-50 border-red-200 text-red-800",        icon: "✕" },
  warning: { style: "bg-yellow-50 border-yellow-200 text-yellow-800", icon: "⚠" },
  info:    { style: "bg-blue-50 border-blue-200 text-blue-800",     icon: "ℹ" },
}

function Alert({
  type = "info",
  message,
  onClose
}: {
  type?: AlertType
  message: string
  onClose?: () => void
}) {
  const { style, icon } = config[type]

  return (
    <div className={`border rounded-2xl p-4 flex items-start gap-3 ${style}`}>
      <span className="flex-shrink-0 w-5 h-5 rounded-full border border-current flex items-center justify-center text-xs font-bold mt-0.5">
        {icon}
      </span>
      <p className="text-sm flex-1">{message}</p>
      {onClose && (
        <button
          onClick={onClose}
          className="flex-shrink-0 opacity-60 hover:opacity-100 transition-opacity text-lg leading-none"
        >
          ×
        </button>
      )}
    </div>
  )
}

export default Alert