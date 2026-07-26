// src/components/layout/Header.tsx
import { useLocation } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { getMyCompany } from '../../services/api'

function Header() {
  const location = useLocation()
  const [company, setCompany] = useState<any>(null)

  useEffect(() => {
    getMyCompany().then(res => setCompany(res.data)).catch(() => {})
  }, [])

  return (
    <header className="h-16 bg-white border-b border-gray-100 px-6 flex items-center justify-between">
      {/* Empty left side — page title removed, shown in hero banners instead */}
      <div />

      {/* Right side — real company name */}
      <div className="flex items-center gap-3">
        <span className="text-sm text-gray-500 font-medium">
          {company ? company.name : ''}
        </span>
        <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center text-sm font-bold">
          {company ? company.name[0].toUpperCase() : 'C'}
        </div>
      </div>
    </header>
  )
}

export default Header