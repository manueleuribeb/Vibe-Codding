import React, { useState } from 'react'

/**
 * Aplicación principal `App` — componente superior que alterna entre el
 * formulario de upload y el formulario de fuentes online, y presenta resultados
 * y la visualización del forecast.
 */
import UploadData from './components/UploadData'
import OnlineDataForm from './components/OnlineDataForm'
import ForecastChart from './components/ForecastChart'
import ResultsTable from './components/ResultsTable'
import { useForecastData } from './hooks/useForecastData'

export default function App() {
  const [mode, setMode] = useState<'upload' | 'online'>('upload')
  const [result, setResult] = useState<any>(null)
  const series = useForecastData(result)

  return (
    <div style={{ padding: 20 }}>
      <h1>Energia Forecast — Demo</h1>
      <div style={{ marginBottom: 12 }}>
        <button onClick={() => setMode('upload')} disabled={mode === 'upload'}>Upload data</button>
        <button onClick={() => setMode('online')} disabled={mode === 'online'} style={{ marginLeft: 8 }}>Online source</button>
      </div>

      {mode === 'upload' ? (
        <UploadData onResult={setResult} />
      ) : (
        <OnlineDataForm onResult={setResult} />
      )}

      <div>
        <h3>Result</h3>
        <ResultsTable result={result} />
      </div>

      <div>
        <h3>Prepared chart data (for Recharts)</h3>
        {series.length === 0 ? (
          <div className="muted">No prepared chart data</div>
        ) : (
          <table className="series-table" style={{ background: '#fff', padding: 12 }}>
            <thead>
              <tr><th>Date</th><th>Forecast</th></tr>
            </thead>
            <tbody>
              {series.map((r: any, i: number) => (
                <tr key={i}><td>{r.date}</td><td>{typeof r.forecast === 'number' ? r.forecast.toFixed(4) : r.forecast}</td></tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div style={{ marginTop: 16 }}>
        <h3>Forecast chart</h3>
        {/* lazy load chart */}
        {series.length > 0 ? (
          <ForecastChart data={series} />
        ) : (
          <div>No forecast to display</div>
        )}
      </div>
    </div>
  )
}
