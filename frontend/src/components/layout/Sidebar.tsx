import { Link } from 'react-router-dom'

function Sidebar() {
  return (
    <div className="w-64 min-h-screen bg-slate-900 text-white p-6 flex flex-col gap-2">
      <h1 className="text-xl font-bold text-white mb-6">CFO Copilot</h1>
      <Link to="/" className="px-4 py-2 rounded-lg hover:bg-slate-700 text-slate-300 hover:text-white transition-colors">Dashboard</Link>
      <Link to="/upload" className="px-4 py-2 rounded-lg hover:bg-slate-700 text-slate-300 hover:text-white transition-colors">Upload</Link>
      <Link to="/documents" className="px-4 py-2 rounded-lg hover:bg-slate-700 text-slate-300 hover:text-white transition-colors">Documents</Link>
      <Link to="/anomalies" className="px-4 py-2 rounded-lg hover:bg-slate-700 text-slate-300 hover:text-white transition-colors">Anomalies</Link>
      <Link to="/chat" className="px-4 py-2 rounded-lg hover:bg-slate-700 text-slate-300 hover:text-white transition-colors">Chat</Link>
    </div>
  )
}

export default Sidebar