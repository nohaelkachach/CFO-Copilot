// src/pages/Dashboard.tsx
import { useState, useEffect } from 'react'
import {
  getPnLOverview,
  getLatestBalanceSheet,
  getUnresolvedCount,
  getMyCompany,
  getCashFlow
} from '../services/api'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import KPICard from '../components/dashboard/KPICard'
import PnLChart from '../components/dashboard/PnLChart'
import CashFlowChart from '../components/dashboard/CashFlowChart'
import { Link } from 'react-router-dom'

function Dashboard() {
  const [pnlData, setPnlData] = useState<any[]>([])
  const [cashFlowData, setCashFlowData] = useState<any[]>([])
  const [balanceSheet, setBalanceSheet] = useState<any>(null)
  const [anomalyCount, setAnomalyCount] = useState(0)
  const [company, setCompany] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true)
        const [pnlRes, balanceRes, anomalyRes, companyRes, cashRes] = await Promise.allSettled([
          getPnLOverview(),
          getLatestBalanceSheet(),
          getUnresolvedCount(),
          getMyCompany(),
          getCashFlow(),
        ])
        if (pnlRes.status === "fulfilled") setPnlData(pnlRes.value.data)
        if (balanceRes.status === "fulfilled") setBalanceSheet(balanceRes.value.data)
        if (anomalyRes.status === "fulfilled") setAnomalyCount(anomalyRes.value.data.unresolved_count)
        if (companyRes.status === "fulfilled") setCompany(companyRes.value.data)
        if (cashRes.status === "fulfilled") setCashFlowData(cashRes.value.data)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  if (loading) return <LoadingSpinner message="Loading your financial overview..." />

  const totalRevenue = pnlData.reduce((sum, d) => sum + (d.revenue ?? 0), 0)
  const totalExpenses = pnlData.reduce((sum, d) => sum + (d.expenses ?? 0), 0)
  const netProfit = totalRevenue - totalExpenses
  const hasData = pnlData.length > 0

  const profitColor = netProfit >= 0 ? "green" : "red"
  const profitLabel = hasData ? (netProfit >= 0 ? "Profitable" : "Operating at a loss") : "No data"
  const anomalyColor = anomalyCount === 0 ? "green" : "yellow"
  const anomalyLabel = anomalyCount === 0 ? "All clear" : "Require attention"

  const formatMAD = (n: number) =>
    new Intl.NumberFormat('fr-MA', { style: 'currency', currency: 'MAD' }).format(n)

  return (
    <div className="flex flex-col gap-8">

      {/* Hero banner */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-700 rounded-2xl p-8 text-white">
        <p className="text-slate-400 text-sm font-semibold uppercase tracking-widest mb-1">
          Financial Overview
        </p>
        <h1 className="text-4xl font-bold mb-2">
          {company ? company.name : 'CFO Copilot'}
        </h1>
        <p className="text-slate-300 text-base">
          Your AI-powered financial intelligence platform
        </p>
        {!hasData && (
          <Link
            to="/upload"
            className="inline-block mt-4 bg-white text-slate-900 px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-slate-100 transition-colors"
          >
            Upload your first document →
          </Link>
        )}
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Revenue"
          value={hasData ? formatMAD(totalRevenue) : "—"}
          subtitle="All periods"
          color="green"
        />
        <KPICard
          title="Total Expenses"
          value={hasData ? formatMAD(totalExpenses) : "—"}
          subtitle="All periods"
          color="red"
        />
        <KPICard
          title="Net Profit"
          value={hasData ? formatMAD(netProfit) : "—"}
          subtitle={profitLabel}
          color={profitColor}
        />
        <KPICard
          title="Anomalies"
          value={anomalyCount}
          subtitle={anomalyLabel}
          color={anomalyColor}
        />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* P&L Chart — 2/3 width */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
          <h2 className="text-lg font-bold text-gray-900 mb-1">Revenue vs Expenses</h2>
          <p className="text-sm text-gray-400 mb-6">Monthly comparison</p>
          <PnLChart data={pnlData} formatMAD={formatMAD} />
        </div>

        {/* Balance Sheet — 1/3 width */}
        <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
          <h2 className="text-lg font-bold text-gray-900 mb-1">Balance Sheet</h2>
          <p className="text-sm text-gray-400 mb-6">
            {balanceSheet ? balanceSheet.period : "Latest period"}
          </p>
          {!balanceSheet ? (
            <div className="flex flex-col items-center justify-center h-40 text-gray-300">
              <p className="text-4xl mb-3">⚖️</p>
              <p className="text-xs text-gray-400 text-center">
                Upload a balance sheet to see assets vs liabilities
              </p>
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              <div className="p-4 bg-blue-50 rounded-xl">
                <p className="text-xs text-blue-500 font-semibold uppercase tracking-wide mb-1">Assets</p>
                <p className="text-xl font-bold text-blue-700">{formatMAD(balanceSheet.total_assets)}</p>
              </div>
              <div className="p-4 bg-red-50 rounded-xl">
                <p className="text-xs text-red-500 font-semibold uppercase tracking-wide mb-1">Liabilities</p>
                <p className="text-xl font-bold text-red-700">{formatMAD(balanceSheet.total_liabilities)}</p>
              </div>
              <div className="p-4 bg-green-50 rounded-xl">
                <p className="text-xs text-green-500 font-semibold uppercase tracking-wide mb-1">Equity</p>
                <p className="text-xl font-bold text-green-700">{formatMAD(balanceSheet.equity)}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Cash Flow Chart */}
      <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
        <h2 className="text-lg font-bold text-gray-900 mb-1">Cash Flow</h2>
        <p className="text-sm text-gray-400 mb-6">Bank balance over time</p>
        <CashFlowChart data={cashFlowData} formatMAD={formatMAD} />
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { to: "/upload", label: "Upload Document", desc: "Add financial documents", emoji: "📄" },
          { to: "/anomalies", label: "Review Anomalies", desc: `${anomalyCount} item${anomalyCount !== 1 ? 's' : ''} to review`, emoji: "⚠️" },
          { to: "/chat", label: "Ask AI", desc: "Query your finances", emoji: "💬" },
        ].map(action => (
          <Link
            key={action.to}
            to={action.to}
            className="bg-white rounded-2xl border border-gray-100 p-5 hover:shadow-md hover:border-slate-200 transition-all group"
          >
            <span className="text-2xl mb-3 block">{action.emoji}</span>
            <p className="font-semibold text-gray-900 group-hover:text-slate-700">{action.label}</p>
            <p className="text-sm text-gray-400 mt-0.5">{action.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default Dashboard