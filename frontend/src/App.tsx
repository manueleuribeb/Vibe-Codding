import React, { useState } from 'react'
import UploadData from './components/UploadData'
import OnlineDataForm from './components/OnlineDataForm'
import ForecastChart from './components/ForecastChart'
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
        <pre style={{ background: '#f6f8fa', padding: 12 }}>{result ? JSON.stringify(result, null, 2) : 'No result yet'}</pre>
      </div>

      <div>
        <h3>Prepared chart data (for Recharts)</h3>
        <pre style={{ background: '#fff', padding: 12 }}>{JSON.stringify(series, null, 2)}</pre>
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
