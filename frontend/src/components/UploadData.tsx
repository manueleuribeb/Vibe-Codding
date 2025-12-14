import React, { useState } from 'react'

type Result = any

export default function UploadData({ onResult }: { onResult: (r: Result) => void }) {
  const [file, setFile] = useState<File | null>(null)
  const [horizon, setHorizon] = useState(7)
  const [loading, setLoading] = useState(false)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    if (!file) return
    setLoading(true)
    const fd = new FormData()
    fd.append('file', file)
    fd.append('horizon', String(horizon))
    const res = await fetch('/api/upload', { method: 'POST', body: fd })
    const data = await res.json()
    onResult(data)
    setLoading(false)
  }

  return (
    <form onSubmit={submit} style={{ marginBottom: 16 }}>
      <div>
        <label>
          File: <input type="file" accept=".csv,.xlsx" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        </label>
      </div>
      <div>
        <label>
          Horizon (days): <input type="number" value={horizon} onChange={(e) => setHorizon(Number(e.target.value))} min={1} max={365} />
        </label>
      </div>
      <div>
        <button type="submit" disabled={!file || loading}>{loading ? 'Uploading...' : 'Upload & Forecast'}</button>
      </div>
    </form>
  )
}
