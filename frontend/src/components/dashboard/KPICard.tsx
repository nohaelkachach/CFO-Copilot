// src/components/dashboard/KPICard.tsx

type KPICardProps = {
  title: string
  value: string | number
  subtitle?: string
  color?: "blue" | "green" | "red" | "yellow"
}

const borders = {
  blue:   "border-blue-500",
  green:  "border-green-500",
  red:    "border-red-500",
  yellow: "border-yellow-500",
}

const texts = {
  blue:   "text-blue-600",
  green:  "text-green-600",
  red:    "text-red-600",
  yellow: "text-yellow-600",
}

function KPICard({ title, value, subtitle, color = "blue" }: KPICardProps) {
  return (
    <div className={`bg-white rounded-2xl border-l-4 ${borders[color]} p-6 shadow-sm hover:shadow-md transition-shadow`}>
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">
        {title}
      </p>
      <p className={`text-3xl font-bold ${texts[color]} mb-1`}>
        {value}
      </p>
      {subtitle && (
        <p className="text-sm text-gray-500">{subtitle}</p>
      )}
    </div>
  )
}

export default KPICard