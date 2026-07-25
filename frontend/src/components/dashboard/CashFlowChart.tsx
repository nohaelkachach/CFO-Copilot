// src/components/dashboard/CashFlowChart.tsx
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer
} from 'recharts'

type CashFlowDataPoint = {
  period: string
  closing_balance: number
}

type CashFlowChartProps = {
  data: CashFlowDataPoint[]
  formatMAD: (n: number) => string
}

function CashFlowChart({ data, formatMAD }: CashFlowChartProps) {
  if (data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-52 text-gray-300">
        <p className="text-4xl mb-3">💰</p>
        <p className="text-sm font-medium text-gray-400">No cash flow data yet</p>
        <p className="text-xs text-gray-300 mt-1">
          Upload bank statements to see your cash flow
        </p>
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart
        data={data}
        margin={{ top: 0, right: 0, left: 0, bottom: 0 }}
      >
        <defs>
          <linearGradient id="cashGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.15} />
            <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
          </linearGradient>
        </defs>
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
        <Area
          type="monotone"
          dataKey="closing_balance"
          name="Cash Balance"
          stroke="#6366f1"
          strokeWidth={2.5}
          fill="url(#cashGradient)"
          dot={{ fill: '#6366f1', strokeWidth: 0, r: 4 }}
          activeDot={{ r: 6, strokeWidth: 0 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}

export default CashFlowChart