// src/components/dashboard/PnLChart.tsx
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts'

type PnLDataPoint = {
  period: string
  revenue: number
  expenses: number
  net_profit?: number
}

type PnLChartProps = {
  data: PnLDataPoint[]
  formatMAD: (n: number) => string
}

function PnLChart({ data, formatMAD }: PnLChartProps) {
  if (data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-52 text-gray-300">
        <p className="text-4xl mb-3">📊</p>
        <p className="text-sm font-medium text-gray-400">No financial data yet</p>
        <p className="text-xs text-gray-300 mt-1">
          Upload a P&L statement to see your chart
        </p>
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart
        data={data}
        margin={{ top: 0, right: 0, left: 0, bottom: 0 }}
      >
        <CartesianGrid
          strokeDasharray="3 3"
          stroke="#f5f5f5"
          vertical={false}
        />
        <XAxis
          dataKey="period"
          tick={{ fontSize: 12, fill: '#9ca3af' }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fontSize: 11, fill: '#9ca3af' }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
        />
        <Tooltip
          formatter={(value: any) => formatMAD(value as number)}
          contentStyle={{
            borderRadius: '12px',
            border: 'none',
            boxShadow: '0 4px 24px rgba(0,0,0,0.08)'
          }}
          labelStyle={{ fontWeight: 600, marginBottom: 4 }}
        />
        <Legend
          wrapperStyle={{ fontSize: '12px', paddingTop: '16px' }}
        />
        <Bar
          dataKey="revenue"
          name="Revenue"
          fill="#10b981"
          radius={[6, 6, 0, 0]}
        />
        <Bar
          dataKey="expenses"
          name="Expenses"
          fill="#f43f5e"
          radius={[6, 6, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  )
}

export default PnLChart