// src/components/layout/Header.tsx
import { useLocation } from 'react-router-dom'

const pageTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/upload': 'Upload Documents',
  '/documents': 'Documents',
  '/anomalies': 'Anomalies',
  '/chat': 'AI Assistant',
}

function Header() {
  const location = useLocation()
  const title = pageTitles[location.pathname] ?? 'CFO Copilot'

  return (
    <header className="h-16 bg-white border-b border-gray-200 px-6 flex items-center justify-between">
      {/* Page title — updates automatically based on current route */}
      <h2 className="text-lg font-semibold text-gray-800">{title}</h2>

      {/* Right side — company info and anomaly badge */}
      <div className="flex items-center gap-4">
        <span className="text-sm text-gray-500">My Company</span>
        <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center text-sm font-medium">
          C
        </div>
      </div>
    </header>
  )
}

export default Header