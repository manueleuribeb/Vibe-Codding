import React, { useState, useEffect } from 'react'

type Result = any

export default function OnlineDataForm({ onResult }: { onResult: (r: Result) => void }) {
  const [source, setSource] = useState<'yahoo'|'eia'|'xm'>('yahoo')
  const [symbol, setSymbol] = useState<string>('')
  const [preset, setPreset] = useState<string>('')
  const [method, setMethod] = useState<'auto'|'naive'|'moving_average'|'ewm'>('auto')
  const [horizon, setHorizon] = useState<number>(7)
  const [loading, setLoading] = useState(false)
  const [eiaPresent, setEiaPresent] = useState<boolean | null>(null)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    if (source === 'eia' && eiaPresent === false) {
      onResult({ error: 'EIA API key missing in backend environment. See README for troubleshooting.' })
      setLoading(false)
      return
    }
    const params = new URLSearchParams()
    params.set('source', source)
    // apply preset if selected
    if (preset) {
      if (preset === 'wti') params.set('symbol', 'CL=F')
      if (preset === 'brent') params.set('symbol', 'BZ=F')
      if (preset === 'henry') params.set('symbol', 'NG=F')
    } else if (symbol) params.set('symbol', symbol)
    if (method !== 'auto') params.set('method', method)
    params.set('horizon', String(horizon))
    const res = await fetch(`/api/online?${params.toString()}`)
    const data = await res.json()
    if (!res.ok) {
      onResult({ error: data?.detail ?? data?.error ?? JSON.stringify(data) })
    } else {
      onResult(data)
    }
    setLoading(false)
  }

  async function checkEiaStatus() {
    try {
      const r = await fetch('/api/eia_status')
      const data = await r.json()
      setEiaPresent(Boolean(data?.eia_key_present))
    } catch (err) {
      setEiaPresent(false)
    }
  }

  useEffect(() => {
    if (source === 'eia') checkEiaStatus()
  }, [source])

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

      <div style={{ marginTop: 8 }}>
        <label style={{ marginRight: 8 }}>Presets:</label>
        <button type="button" onClick={() => { setPreset('wti'); setSymbol('CL=F') }} style={{ marginRight: 6 }}>WTI (CL=F)</button>
        <button type="button" onClick={() => { setPreset('brent'); setSymbol('BZ=F') }} style={{ marginRight: 6 }}>Brent</button>
        <button type="button" onClick={() => { setPreset('henry'); setSymbol('NG=F') }} style={{ marginRight: 6 }}>Henry Hub</button>
        <button type="button" onClick={() => { setPreset(''); setSymbol('') }}>Clear</button>
      </div>

      <div style={{ marginTop: 8 }}>
        <label>
          Symbol/Series (optional): <input value={symbol} onChange={(e) => { setSymbol(e.target.value); setPreset('') }} placeholder="CL=F or PET.RWTC.D" />
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
        <button type="submit" disabled={loading || eiaPresent === false}>{loading ? 'Loading...' : 'Fetch & Forecast'}</button>
        {source === 'eia' && eiaPresent === false && (
          <div style={{ marginTop: 8 }}>
            <div className="error-message">Error: EIA API key missing in backend environment. Add `EIA_API_KEY` to your environment or Codespaces secrets and restart the container.</div>
            <button type="button" onClick={checkEiaStatus} style={{ marginTop: 8 }}>Check again</button>
          </div>
        )}
        {source === 'eia' && eiaPresent === null && (
          <div className="muted" style={{ marginTop: 8 }}>Checking EIA key...</div>
        )}
      </div>
    </form>
  )
}
