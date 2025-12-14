import React from 'react'

export default function ResultsTable({ result }: { result: any }) {
  if (!result) return <div>No result yet</div>
  if (result.error || result.detail) {
    return (
      <div className="error-message">
        <strong>Error:</strong> {result.error ?? result.detail}
      </div>
    )
  }

  const { best_method, mape, rmse, series } = result

  const valueOf = (row: any) => {
    if (row == null) return ''
    return row.forecast ?? row.price ?? row.value ?? row[1] ?? ''
  }

  return (
    <div className="results-container">
      <table className="summary-table">
        <tbody>
          <tr><th>Best method</th><td>{best_method}</td></tr>
          <tr><th>MAPE</th><td>{typeof mape === 'number' ? mape.toFixed(4) : mape}</td></tr>
          <tr><th>RMSE</th><td>{typeof rmse === 'number' ? rmse.toFixed(4) : rmse}</td></tr>
        </tbody>
      </table>

      <div style={{ marginTop: 12 }}>
        <h4>Forecast series</h4>
        <table className="series-table">
          <thead>
            <tr><th>Date</th><th>Value</th></tr>
          </thead>
          <tbody>
            {Array.isArray(series) && series.length > 0 ? (
              series.map((row: any, i: number) => (
                <tr key={i}><td>{row.date ?? row[0]}</td><td>{typeof valueOf(row) === 'number' ? (valueOf(row) as number).toFixed(4) : valueOf(row)}</td></tr>
              ))
            ) : (
              <tr><td colSpan={2}>No series data</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
