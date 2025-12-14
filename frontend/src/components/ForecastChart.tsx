import React from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts'

/**
 * `ForecastChart` renderiza la serie preparada (`date`, `forecast`) usando
 * Recharts. El componente es responsable únicamente de la visualización.
 */
export default function ForecastChart({ data }: { data: Array<{ date: string; forecast: number }> }) {
  if (!data || data.length === 0) return <div>No chart data</div>
  return (
    <div style={{ width: '100%', height: 300 }}>
      <ResponsiveContainer>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="forecast" stroke="#8884d8" dot={{ r: 2 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
