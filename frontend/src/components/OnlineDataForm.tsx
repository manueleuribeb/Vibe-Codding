import React, { useState } from 'react'

type Result = any

export default function OnlineDataForm({ onResult }: { onResult: (r: Result) => void }) {
  const [source, setSource] = useState<'yahoo'|'eia'|'xm'>('yahoo')
  const [symbol, setSymbol] = useState<string>('')
  const [horizon, setHorizon] = useState<number>(7)
  const [loading, setLoading] = useState(false)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    const params = new URLSearchParams()
    params.set('source', source)
    if (symbol) params.set('symbol', symbol)
    params.set('horizon', String(horizon))
    const res = await fetch('/api/online?' + params.toString())
    const data = await res.json()
    onResult(data)
    setLoading(false)
  }

  return (
    <form onSubmit={submit} style={{ marginBottom: 16 }}>
      <div>
        <label>
          Source:{' '}
          <select value={source} onChange={(e) => setSource(e.target.value as any)}>
            <option value="yahoo">yahoo (default CL=F)</option>
            <option value="eia">eia (default PET.RWTC.D)</option>
            <option value="xm">xm</option>
          </select>
        </label>
      </div>
      <div>
        <label>
          Symbol/Series (optional): <input value={symbol} onChange={(e) => setSymbol(e.target.value)} placeholder="CL=F or PET.RWTC.D" />
        </label>
      </div>
      <div>
        <label>
          Horizon (days): <input type="number" value={horizon} onChange={(e) => setHorizon(Number(e.target.value))} min={1} max={365} />
        </label>
      </div>
      <div>
        <button type="submit" disabled={loading}>{loading ? 'Loading...' : 'Fetch & Forecast'}</button>
      </div>
    </form>
  )
}
