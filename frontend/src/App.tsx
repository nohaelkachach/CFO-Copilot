// src/App.tsx
import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/layout/Sidebar'
import Header from './components/layout/Header'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import Documents from './pages/Documents'
import Anomalies from './pages/Anomalies'
import Chat from './pages/Chat'
import CompanySetup from './components/CompanySetup'
import { getMyCompany } from './services/api'
import LoadingSpinner from './components/ui/LoadingSpinner'

function App() {
  const [hasCompany, setHasCompany] = useState<boolean | null>(null)

  useEffect(() => {
    async function checkCompany() {
      try {
        await getMyCompany()
        setHasCompany(true)
      } catch {
        setHasCompany(false)
      }
    }
    checkCompany()
  }, [])

  // Still checking
  if (hasCompany === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <LoadingSpinner message="Loading CFO Copilot..." />
      </div>
    )
  }

  // No company yet — show setup
  if (!hasCompany) {
    return <CompanySetup onComplete={() => setHasCompany(true)} />
  }

  // Company exists — show main app
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-gray-50">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-y-auto p-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/upload" element={<Upload />} />
              <Route path="/documents" element={<Documents />} />
              <Route path="/anomalies" element={<Anomalies />} />
              <Route path="/chat" element={<Chat />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App