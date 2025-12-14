import React, { useState } from 'react'

type Result = any

export default function UploadData({ onResult }: { onResult: (r: Result) => void }) {
  const [file, setFile] = useState<File | null>(null)
  const [horizon, setHorizon] = useState(7)
  const [method, setMethod] = useState<'auto'|'naive'|'moving_average'|'ewm'>('auto')
  const [loading, setLoading] = useState(false)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    if (!file) return
    setLoading(true)
    const fd = new FormData()
    fd.append('file', file)
    fd.append('horizon', String(horizon))
    if (method !== 'auto') fd.append('method', method)
    try {
      const res = await fetch('/api/upload', { method: 'POST', body: fd })
      const data = await res.json()
      if (!res.ok) {
        onResult({ error: data?.detail ?? data?.error ?? JSON.stringify(data) })
      } else {
        onResult(data)
      }
    } catch (err: any) {
      onResult({ error: err?.message ?? String(err) })
    }
    setLoading(false)
  }

  return (
    <form onSubmit={submit} style={{ marginBottom: 16 }}>
      <div>
        <label>
          File: <input type="file" accept=".csv,.xlsx" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        </label>
      </div>
      <div style={{ marginTop: 8 }}>
        <label>
          Method:{' '}
          <select value={method} onChange={(e) => setMethod(e.target.value as any)}>
            <option value="auto">Auto (best)</option>
            <option value="naive">Naive</option>
            <option value="moving_average">Moving average</option>
            <option value="ewm">EWMA</option>
          </select>
        </label>
      </div>

      <div style={{ marginTop: 8 }}>
        <label>
          Horizon (days): <input type="range" value={horizon} onChange={(e) => setHorizon(Number(e.target.value))} min={1} max={90} /> <strong>{horizon}</strong>
        </label>
      </div>
      <div>
        <button type="submit" disabled={!file || loading}>{loading ? 'Uploading...' : 'Upload & Forecast'}</button>
      </div>
    </form>
  )
}
