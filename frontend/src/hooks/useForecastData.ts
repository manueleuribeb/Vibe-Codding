import { useMemo } from 'react'

/**
 * Hook `useForecastData` prepara la serie devuelta por el backend para ser
 * consumida por Recharts: lista de objetos `{ date, forecast }`.
 */
export function useForecastData(result: any) {
  return useMemo(() => {
    if (!result || !result.series) return []
    return result.series.map((r: any) => ({ date: r.date, forecast: r.forecast }))
  }, [result])
}
